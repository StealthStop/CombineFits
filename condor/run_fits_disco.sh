#!/bin/bash

inputRoot2016=$1
inputRoot2017=$2
inputRoot2018pre=$3
inputRoot2018post=$4
signalType=$5
mass=$6
year=$7
dataType=$8
setClose=$9
doAsym=${10}
doFitDiag=${11}
doMulti=${12}
doImpact=${13}
inject=${14}
syst=${15}
suffix=${16}
base_dir=`pwd`
rMax=20
rMin=-20

if [ $syst == None ] 
then
    syst=""
fi

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
    ${signalType} = "RPV"
else
    ${signalType} = "Stealth" + ${signalType}
fi

if [ $setClose == 1 ]
then
    echo "Running fits with perfect closure asserted"
    close="_perfectClose"
    close1="perfectClose"
else
    close=""
    close1=""
fi

echo ${close}
echo ${close1}

text2workspace.py cards/${year}_${signalType}_${mass}_${dataType}_${suffix}${close}.txt -o ws_${year}_${signalType}_${mass}_${dataType}_${suffix}${close}.root -m ${mass} --keyword-value MODEL=${signalType}

echo "text2workspace.py cards/${year}_${signalType}_${mass}_${dataType}_${suffix}${close}.txt -o ws_${year}_${signalType}_${mass}_${dataType}_${suffix}${close}.root -m ${mass} --keyword-value MODEL=${signalType}"

ws=ws_${year}_${signalType}_${mass}_${dataType}_${suffix}${close}.root

#fallBack="--cminDefaultMinimizerStrategy 1 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --cminFallbackAlgo Minuit2,Migrad,1:1.0 --cminFallbackAlgo Minuit2,Migrad,0:1.0 --X-rtd MINIMIZER_MaxCalls=999999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH"
fallBack=""
fitOptions="${ws} -m ${mass} --keyword-value MODEL=${signalType} ${fallBack}" # --freezeNuisanceGroup=closure"
echo ${fitOptions}
# Run the asympotic fits
if [ $doAsym == 1 ] 
then
    echo "Running Asymptotic fits"
    combine -M AsymptoticLimits ${fitOptions} --verbose 2 --rMax $rMax --rMin $rMin --robustFit=1 -n ${year}${signalType}${mass}${dataType}${suffix}${close1}_AsymLimit > log_${year}${signalType}${mass}${dataType}${suffix}${close1}_Asymp.txt
    combine -M Significance ${fitOptions} --verbose 2 --rMax $rMax --rMin $rMin -t -1 --expectSignal=1 --robustFit=1 -n ${year}${signalType}${mass}${dataType}${suffix}${close1}_SignifExp > log_${year}${signalType}${mass}${dataType}${suffix}${close1}_Sign_sig.txt
    combine -M Significance ${fitOptions} --verbose 2 --rMax $rMax --rMin $rMin --robustFit=1 -n ${year}${signalType}${mass}${dataType}${suffix}${close1}_SignifExp > log_${year}${signalType}${mass}${dataType}${suffix}${close1}_Sign_noSig.txt
fi

# Run the fit diagnostics fits (takes forever to run)
if [ $doFitDiag == 1 ] 
then
    echo "Running FitDiagnostics"
    if [ $inject == 0 ] 
    then
        combine -M FitDiagnostics ${fitOptions} --verbose 2 --rMax $rMax --rMin $rMin --robustFit=1 --plots --saveShapes --saveNormalizations --saveWithUncertainties -n ${year}${signalType}${mass}${dataType}${suffix}${close1} > log_${year}${signalType}${mass}${dataType}${suffix}${close1}_FitDiag.txt
    else
        combine -M FitDiagnostics ${fitOptions} --verbose 2 --rMax $rMax --rMin $rMin --robustFit=1 --plots --saveShapes --saveNormalizations --saveWithUncertainties -n ${year}${signalType}${mass}${dataType}${suffix}${close1} -t -1 --toysFrequentist --expectSignal=${inject} > log_${year}${signalType}${mass}${dataType}${suffix}${close1}_FitDiag.txt
    fi
fi

# Run asymptotic likihood scan
if [ $doMulti == 1 ] 
then
    echo "Running MultiDimFit"
    combine -M MultiDimFit ${fitOptions} --verbose 0 --rMin -0.2 --rMax 5.0 --algo=grid --points=260 -n ${year}${signalType}${mass}${dataType}${suffix}${close1}SCAN_r_wSig > /dev/null
fi

# Run impact plots from the CombineHarvester repo
if [ $doImpact == 1 ] 
then
    echo "Running Impacts"
    ../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ${ws} -m ${mass} --doInitialFit --robustFit 1 --rMin -20 --rMax 20 ${fallBack} > log_${year}${signalType}${mass}${dataType}${suffix}${close1}step1.txt
    ../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ${ws} -m ${mass} --doFits --parallel 4 --robustFit 1 --rMin -20 --rMax 20 ${fallBack} > log_${year}${signalType}${mass}${dataType}${suffix}${close1}step2.txt
    ../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ${ws} -m ${mass}  --rMin -20 --rMax 20 --robustFit 1 -o impacts_${year}${signalType}${mass}${suffix}${close1}.json > log_${year}${signalType}${mass}${dataType}${suffix}${close1}step3.txt
    ../../CombineHarvester/CombineTools/scripts/plotImpacts.py -i impacts_${year}${signalType}${mass}${suffix}${close1}.json -o impacts_${year}${signalType}${mass}${suffix}${close1}_${dataType}
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
