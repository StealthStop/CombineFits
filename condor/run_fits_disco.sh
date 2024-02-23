#!/bin/bash

# Argument order as specified in condorSubmit.py
cardPath=$1
shift
signalType=$1
shift
mass=$1
shift
year=$1
shift
dataType=$1
shift
doAsym=$1
shift
doFitDiag=$1
shift
doMulti=$1
shift
doImpact=$1
shift
channel=$1
shift
asimov=$1
shift
binEdgeName=$1
shift 
makeCards=$1
shift
binMask=$1

runToys=0

if [ $binEdgeName == 0 ]
then
    binEdgeName=""
fi

base_dir=`pwd`

# Setup the working area on the remote job node.
# Initialize a CMSSW environment and copy tar inputs into it
source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
tar -xf CMSSW_10_2_13.tar.gz
cd CMSSW_10_2_13/src/HiggsAnalysis/CombinedLimit
scram b ProjectRename
eval `scramv1 runtime -sh`
cp ${base_dir}/exestuff.tar.gz .
tar xzvf exestuff.tar.gz
mv exestuff/* .
export LD_LIBRARY_PATH=${PWD}:${LD_LIBRARY_PATH}
ls -l

eval `scramv1 runtime -sh`

# Setup a mask for the A regions for running FitDiagnostics while masking
MASKFLAG=""
if [[ "$binMask" != "None" ]]; then
    MASKFLAG="--setParameters ${binMask}"
fi

# Determine value for "inject" flag based on "dataType"
# This flag is used for fits to Asimov data sets
inject=0
if [ ${dataType} == "pseudoDataS" ]
then
    inject=1.0
fi

# Make the datacard before we run combine
if [ $makeCards == 1 ]
then
    if [ ${channel} == "combo" ]
    then
        python produceDataCard.py --model ${signalType} --mass ${mass} --config cardConfig_0l_${configSuffix} --channel 0l --inpath inputsAll/ --outpath cards/ 
        python produceDataCard.py --model ${signalType} --mass ${mass} --config cardConfig_1l_${configSuffix} --channel 1l --inpath inputsAll/ --outpath cards/ 
        python produceDataCard.py --model ${signalType} --mass ${mass} --config cardConfig_2l_${configSuffix} --channel 2l --inpath inputsAll/ --outpath cards/ 
        python produceDataCard.py --model ${signalType} --mass ${mass} --combo 0l 1l 2l --inpath inputsAll/ --outpath cards/
    else
        python produceDataCard.py --model ${signalType} --mass ${mass} --config cardConfig_${channel}_scan --channel ${channel} --inpath inputsAll/ --outpath cards/ --singleBE ${binEdgeName}
    fi
fi

# Make a workspace ROOT file for Higgs Combine to process
if [ $asimov == 1 ]
then
    stubName=${year}_${signalType}_${mass}_${dataType}_${channel}${binEdgeName}
else
    stubName=${year}_${signalType}_${mass}_${dataType}_${channel}${binEdgeName}
fi
tagName=${year}${signalType}${mass}${dataType}_${channel}${binEdgeName}
ws=ws_${tagName}.root

echo "text2workspace.py ${cardPath}/${stubName}.txt -o ${ws} -m ${mass} --keyword-value MODEL=${signalType}\n"

# The --channel-masks option allows for masking of any bin - masking is off by default
text2workspace.py ${cardPath}/${stubName}.txt -o ${ws} -m ${mass} --keyword-value MODEL=${signalType} --channel-masks


# Additional fit options for more robust fitting
fallBack="--cminDefaultMinimizerStrategy 1 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --cminFallbackAlgo Minuit2,Migrad,1:1.0 --cminFallbackAlgo Minuit2,Migrad,0:1.0 --X-rtd MINIMIZER_MaxCalls=999999999 --X-rtd MINIMIZER_analytic  --X-rtd FAST_VERTICAL_MORPH"
fitOptions="${ws} -m ${mass} --keyword-value MODEL=${signalType} ${fallBack}"
fitOptionsNoFallBack="${ws} -m ${mass} --keyword-value MODEL=${signalType} --cminDefaultMinimizerStrategy 1"
fitOptionsToys="${fitOptions} --saveToys --saveHybridResult"
echo "Running with fit options: ${fitOptions}\n"

# Run the asympotic fits for the limit plots and significance/p-value calculations for top panel of p-value plots
if [ $doAsym == 1 ] 
then

    rMinLim="0"
    rMaxLim="20"

    # Calculate expected limit using both Asimov data set and observation
    # Note: Asimov data set is not used by default as your observed number of events in AsymptoticLimits mode
    # However, the Asimov data set is used in both modes when determining confidence intervals
    echo "Running Asymptotic fits"
    if [ $asimov == 1 ]
    then
        combine -M AsymptoticLimits ${fitOptions} ${MASKFLAG} --rMin $rMinLim --rMax $rMaxLim -t -1 --expectSignal=0 -n ${tagName}_AsymLimit_Asimov > log_${tagName}_Asymp_Asimov.txt
    else
        combine -M AsymptoticLimits ${fitOptions} ${MASKFLAG} --rMin $rMinLim --rMax $rMaxLim                        -n ${tagName}_AsymLimit > log_${tagName}_Asymp.txt
    fi    

    rMinSign="-20.0"
    rMaxSign="20.0"

    # Calculate significance using Asimov data set and actual observation
    echo "Running Significance calculations"
    if [ $asimov == 1 ]
    then
        combine -M Significance ${fitOptions} ${MASKFLAG} --rMin $rMinSign --rMax $rMaxSign -t -1 --expectSignal=${inject} -n ${tagName}_SignifExp_Asimov > log_${tagName}_Sign_Asimov.txt
        if [ ${dataType} == "Data" ] || [ ${dataType} == "pseudoData" ]
        then
            combine -M Significance ${fitOptions} ${MASKFLAG} --rMin $rMinSign --rMax $rMaxSign -t -1 --expectSignal=1.0 -n ${tagName}_SignifExp_Asimov_1p0 > log_${tagName}_Sign_Asimov_1p0.txt
            combine -M Significance ${fitOptions} ${MASKFLAG} --rMin $rMinSign --rMax $rMaxSign -t -1 --expectSignal=0.2 -n ${tagName}_SignifExp_Asimov_0p2 > log_${tagName}_Sign_Asimov_0p2.txt
        fi          
    else
        combine -M Significance ${fitOptions} ${MASKFLAG} --rMin $rMinSign --rMax $rMaxSign                                -n ${tagName}_SignifExp > log_${tagName}_Sign.txt
    fi
fi

# Run the fit diagnostics fits to calculate signal strength and uncertainty in bottom ratio panel of the p-value plots
if [ $doFitDiag == 1 ] 
then

    rMinDiag="-20.0"
    rMaxDiag="20.0"

    # Perform fit diagnostics using Asimov data set and observation
    echo "Running FitDiagnostics"
    if [ $asimov == 1 ]
    then
        combine -M FitDiagnostics ${fitOptionsNoFallBack} ${MASKFLAG} -v 2 --rMin $rMinDiag --rMax $rMaxDiag --plots --saveShapes --saveNormalizations --saveWithUncertainties -n ${tagName}_Asimov -t -1 --expectSignal=${inject} > log_${tagName}_FitDiag_Asimov.txt
        if [ ${dataType} == "Data" || ${dataType} == "pseudoData" ]
        then
            combine -M FitDiagnostics ${fitOptionsNoFallBack} ${MASKFLAG} -v 2 --rMin $rMinDiag --rMax $rMaxDiag --plots --saveShapes --saveNormalizations --saveWithUncertainties -n ${tagName}_Asimov_1p0 -t -1 --expectSignal=1.0 > log_${tagName}_FitDiag_Asimov_1p0.txt
            combine -M FitDiagnostics ${fitOptionsNoFallBack} ${MASKFLAG} -v 2 --rMin $rMinDiag --rMax $rMaxDiag --plots --saveShapes --saveNormalizations --saveWithUncertainties -n ${tagName}_Asimov_0p2 -t -1 --expectSignal=0.2 > log_${tagName}_FitDiag_Asimov_0p2.txt
        fi
    else
        combine -M FitDiagnostics ${fitOptionsNoFallBack} ${MASKFLAG} -v 2 --rMin $rMinDiag --rMax $rMaxDiag --plots --saveShapes --saveNormalizations --saveWithUncertainties -n ${tagName}  > log_${tagName}_FitDiag.txt
    fi
fi

# Run asymptotic likihood scan
if [ $doMulti == 1 ] 
then
    echo "Running MultiDimFit"
    combine -M MultiDimFit ${fitOptions} ${MASKFLAG} --verbose 0 --rMin -20.0 --rMax 20.0 --autoRange 10 --algo=grid --points=100 -n ${tagName}_dLLscan > /dev/null
fi

# Run fits for making impact plots (using the CombineHarvester repo)
if [ $doImpact == 1 ] 
then

    rMinImp="-20.0"
    rMaxImp="20.0"

    echo "Running Impacts"
    # Generate impacts based on Asimov data set
    if [ $asimov == 1 ]
    then
        combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --rMin ${rMinImp} --rMax ${rMaxImp} --expectSignal=${inject} ${fallBack} ${MASKFLAG} --robustFit 1 --doInitialFit -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step1_Asimov.txt
        combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --rMin ${rMinImp} --rMax ${rMaxImp} --expectSignal=${inject} ${fallBack} ${MASKFLAG} --robustFit 1 --doFits --parallel 8 -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step2_Asimov.txt
        combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --rMin ${rMinImp} --rMax ${rMaxImp} --expectSignal=${inject}             ${MASKFLAG} --robustFit 1 -o impacts_${tagName}_Asimov.json -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step3_Asimov.txt
        if [ ${dataType} == "Data" ] || [ ${dataType} == "pseudoData" ]
        then
            combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --rMin ${rMinImp} --rMax ${rMaxImp} --expectSignal=1.0 ${fallBack} ${MASKFLAG} --robustFit 1 --doInitialFit -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step1_Asimov_1p0.txt
            combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --rMin ${rMinImp} --rMax ${rMaxImp} --expectSignal=1.0 ${fallBack} ${MASKFLAG} --robustFit 1 --doFits --parallel 8 -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step2_Asimov_1p0.txt
            combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --rMin ${rMinImp} --rMax ${rMaxImp} --expectSignal=1.0             ${MASKFLAG} --robustFit 1 -o impacts_${tagName}_Asimov_1p0.json -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step3_Asimov_1p0.txt

            combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --rMin ${rMinImp} --rMax ${rMaxImp} --expectSignal=0.2 ${fallBack} ${MASKFLAG} --robustFit 1 --doInitialFit -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step1_Asimov_0p2.txt
            combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --rMin ${rMinImp} --rMax ${rMaxImp} --expectSignal=0.2 ${fallBack} ${MASKFLAG} --robustFit 1 --doFits --parallel 8 -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step2_Asimov_0p2.txt
            combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --rMin ${rMinImp} --rMax ${rMaxImp} --expectSignal=0.2             ${MASKFLAG} --robustFit 1 -o impacts_${tagName}_Asimov_0p2.json -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step3_Asimov_0p2.txt
        fi
    else
        # Generate impacts based on observation
        combineTool.py -M Impacts -d ${ws} -m ${mass} ${fallBack} ${MASKFLAG} --rMin ${rMinImp} --rMax ${rMaxImp} --robustFit 1 --doInitialFit -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step1.txt
        combineTool.py -M Impacts -d ${ws} -m ${mass} ${fallBack} ${MASKFLAG} --rMin ${rMinImp} --rMax ${rMaxImp} --robustFit 1 --doFits --parallel 8 -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step2.txt
        combineTool.py -M Impacts -d ${ws} -m ${mass}             ${MASKFLAG} --rMin ${rMinImp} --rMax ${rMaxImp} --robustFit 1 -o impacts_${tagName}.json -v 2 --exclude 'rgx{.*mcStat[A-D]*}' > log_${tagName}_step3.txt
    fi

    rm higgsCombine_paramFit_Test_*root
    rm higgsCombine_initialFit_Test.MultiDimFit.*.root
    rm log_step1.txt log_step2.txt log_step3.txt
fi

if [ $runToys == 1 ] 
then
    printf "\n\n Running sig. toys\n"
    combine -M HybridNew --LHCmode LHC-significance ${fitOptionsToys} -T ${numToys} -s ${seed} --fullBToys -i ${iterations} > log_tmp.txt
    printf "\n\n Running limit toys\n"
    combine -M HybridNew --LHCmode LHC-limits       ${fitOptionsToys} -T ${numToys} -s ${seed} --fullBToys --singlePoint ${rVal} --clsAcc 0 > log_tmp.txt 
fi

mv *.root ${base_dir}
mv log*.txt ${base_dir}
mv *.pdf ${base_dir}
mv *.json ${base_dir}
rm -r ${cardPath}

cd ${base_dir}
ls -l
