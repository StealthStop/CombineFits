#!/bin/bash

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

base_dir=`pwd`
rMax="20"
rMin="-20"

rMinLim="0"
rMaxLim="2"

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

if [ ${signalType} == "RPV" ]
then
    signalType="RPV"
else
    signalType=${signalType}
fi

# Determine value for "inject" flag based on "dataType"
# This flag is used for fits to Asimov data sets
inject=0
if [ ${dataType} == "pseudoDataS" ]
then
    inject=1
fi

# Make a workspace ROOT file for Higgs Combine to process
stubName=${year}_${signalType}_${mass}_${dataType}_${channel}
tagName=${year}${signalType}${mass}${dataType}_${channel}
ws=ws_${tagName}.root

echo "text2workspace.py cards/${stubName}.txt -o ${ws} -m ${mass} --keyword-value MODEL=${signalType}\n"
text2workspace.py cards/${stubName}.txt -o ${ws} -m ${mass} --keyword-value MODEL=${signalType}


# Additional fit options for more robust fitting
fallBack="--cminDefaultMinimizerStrategy 1 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --cminFallbackAlgo Minuit2,Migrad,1:1.0 --cminFallbackAlgo Minuit2,Migrad,0:1.0 --X-rtd MINIMIZER_MaxCalls=999999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH"
fitOptions="${ws} -m ${mass} --keyword-value MODEL=${signalType} ${fallBack}"
echo "Running with fit options: ${fitOptions}\n"

# Run the asympotic fits for the limit plots and significance/p-value calculations for top panel of p-value plots
if [ $doAsym == 1 ] 
then

    # Calculate expected limit using both Asimov data set and observation
    # Note: Asimov data set is not used by default as your observed number of events in AsymptoticLimits mode
    # However, the Asimov data set is used in both modes when determining confidence intervals
    echo "Running Asymptotic fits"
    if [ $asimov == 1 ]
    then
        combine -M AsymptoticLimits ${fitOptions} --verbose 2 --rMin $rMinLim --rMax $rMaxLim -t -1 --expectSignal=${inject} -n ${tagName}_AsymLimit_Asimov > log_${tagName}_Asymp.txt
    else
        combine -M AsymptoticLimits ${fitOptions} --verbose 2 --rMin $rMinLim --rMax $rMaxLim                                -n ${tagName}_AsymLimit > log_${tagName}_Asymp.txt
    fi    

    # Calculate significance using Asimov data set and actual observation
    echo "Running Significance calculations"
    if [ $asimov == 1 ]
    then
        combine -M Significance ${fitOptions} --verbose 2 --rMin $rMin --rMax $rMax -t -1 --expectSignal=${inject} -n ${tagName}_SignifExp_Asimov > log_${tagName}_Sign_Asimov.txt
    else
        combine -M Significance ${fitOptions} --verbose 2 --rMin $rMin --rMax $rMax                                -n ${tagName}_SignifExp > log_${tagName}_Sign.txt
    fi
fi

# Run the fit diagnostics fits to calculate signal strength and uncertainty in bottom ratio panel of the p-value plots
if [ $doFitDiag == 1 ] 
then

    # Perform fit diagnostics using Asimov data set and observation
    echo "Running FitDiagnostics"
    if [ $asimov == 1 ]
    then
        combine -M FitDiagnostics ${fitOptions} --verbose 2 --rMin $rMin --rMax $rMax --robustFit=1 --plots --saveShapes --saveNormalizations --saveWithUncertainties -n ${tagName}_Asimov -t -1 --toysFrequentist --expectSignal=${inject} > log_${tagName}_FitDiag_Asimov.txt
    else
        combine -M FitDiagnostics ${fitOptions} --verbose 2 --rMin $rMin --rMax $rMax --robustFit=1 --plots --saveShapes --saveNormalizations --saveWithUncertainties -n ${tagName}  > log_${tagName}_FitDiag.txt
    fi
fi

# Run asymptotic likihood scan
if [ $doMulti == 1 ] 
then
    echo "Running MultiDimFit"
    combine -M MultiDimFit ${fitOptions} --verbose 0 --rMin -0.2 --rMax 5.0 --algo=grid --points=260 -n ${tagName}SCAN_r_wSig > /dev/null
fi

# Run fits for making impact plots (using the CombineHarvester repo)
if [ $doImpact == 1 ] 
then
    echo "Running Impacts"
    # Generate impacts based on Asimov data set
    if [ $asimov == 1 ]
    then
        combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --expectSignal=${inject} --rMin ${rMin} --rMax ${rMax} ${fallBack} --robustFit 1 --doInitialFit > log_${tagName}_step1_Asimov.txt
        combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --expectSignal=${inject} --rMin ${rMin} --rMax ${rMax} ${fallBack} --robustFit 1 --doFits --parallel 4 > log_${tagName}_step2_Asimov.txt
        combineTool.py -M Impacts -d ${ws} -m ${mass} -t -1 --expectSignal=${inject} --rMin ${rMin} --rMax ${rMax}             --robustFit 1 -o impacts_${tagName}_Asimov.json > log_${tagName}_step3_Asimov.txt
        plotImpacts.py -i impacts_${tagName}_Asimov.json -o impacts_${year}${signalType}${mass}_${channel}_${dataType}_Asimov
    else
        # Generate impacts based on observation
        combineTool.py -M Impacts -d ${ws} -m ${mass} --rMin ${rMin} --rMax ${rMax} ${fallBack} --robustFit 1 --doInitialFit > log_${tagName}_step1.txt
        combineTool.py -M Impacts -d ${ws} -m ${mass} --rMin ${rMin} --rMax ${rMax} ${fallBack} --robustFit 1 --doFits --parallel 4 > log_${tagName}_step2.txt
        combineTool.py -M Impacts -d ${ws} -m ${mass} --rMin ${rMin} --rMax ${rMax}             --robustFit 1 -o impacts_${tagName}.json > log_${tagName}_step3.txt
        plotImpacts.py -i impacts_${tagName}.json -o impacts_${year}${signalType}${mass}_${channel}_${dataType}
    fi

    rm higgsCombine_paramFit_Test_*root
    rm higgsCombine_initialFit_Test.MultiDimFit.*.root
    rm log_step1.txt log_step2.txt log_step3.txt
fi

ls -l

mv *.root ${base_dir}
mv log*.txt ${base_dir}
mv *.pdf ${base_dir}
mv *.json ${base_dir}

cd ${base_dir}
