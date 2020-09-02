#!/bin/bash

inputRoot2016=$1
inputRoot2017=$2
inputRoot2018pre=$3
inputRoot2018post=$4
signalType=$5
mass=$6
year=$7
dataType=$8
doAsym=$9
doFitDiag=${10}
doMulti=${11}
doImpact=${12}
inject=${13}
syst=${14}
base_dir=`pwd`
rMax=10

if [ $syst == None ] 
then
    syst=""
fi

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc6_amd64_gcc530
tar -xf CMSSW_8_1_0.tar.gz
cd CMSSW_8_1_0/src/HiggsAnalysis/CombinedLimit
scram b ProjectRename
eval `scramv1 runtime -sh`
cp ${base_dir}/exestuff.tar.gz .
tar xzvf exestuff.tar.gz
mv exestuff/* .
export LD_LIBRARY_PATH=${PWD}:${LD_LIBRARY_PATH}
ls -l

mkdir ${inputRoot2016}
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2016}/njets_for_Aron.root         ${inputRoot2016}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2016}/ttbar_systematics.root      ${inputRoot2016}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2016}/qcdcr-syst-parameters.root  ${inputRoot2016}/.

mkdir ${inputRoot2017}
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2017}/njets_for_Aron.root         ${inputRoot2017}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2017}/ttbar_systematics.root      ${inputRoot2017}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2017}/qcdcr-syst-parameters.root  ${inputRoot2017}/.

mkdir ${inputRoot2018pre}
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2018pre}/njets_for_Aron.root         ${inputRoot2018pre}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2018pre}/ttbar_systematics.root      ${inputRoot2018pre}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2018pre}/qcdcr-syst-parameters.root  ${inputRoot2018pre}/.

mkdir ${inputRoot2018post}
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2018post}/njets_for_Aron.root         ${inputRoot2018post}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2018post}/ttbar_systematics.root      ${inputRoot2018post}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/${inputRoot2018post}/qcdcr-syst-parameters.root  ${inputRoot2018post}/.

eval `scramv1 runtime -sh`

combineCards.py Y16=Card2016.txt Y17=Card2017.txt                                                 > Card2016_2017.txt
combineCards.py Y16=Card2016.txt                  Y18pre=Card2018pre.txt                          > Card2016_2018pre.txt
combineCards.py Y16=Card2016.txt                                         Y18post=Card2018post.txt > Card2016_2018post.txt
combineCards.py                  Y17=Card2017.txt Y18pre=Card2018pre.txt                          > Card2017_2018pre.txt
combineCards.py                  Y17=Card2017.txt                        Y18post=Card2018post.txt > Card2017_2018post.txt
combineCards.py                                   Y18pre=Card2018pre.txt Y18post=Card2018post.txt > Card2018pre_2018post.txt
combineCards.py Y16=Card2016.txt                  Y18pre=Card2018pre.txt Y18post=Card2018post.txt > Card2016_2018pre_2018post.txt
combineCards.py Y16=Card2016.txt Y17=Card2017.txt                        Y18post=Card2018post.txt > Card2016_2017_2018post.txt
combineCards.py Y16=Card2016.txt Y17=Card2017.txt Y18pre=Card2018pre.txt                          > Card2016_2017_2018pre.txt
combineCards.py                  Y17=Card2017.txt Y18pre=Card2018pre.txt Y18post=Card2018post.txt > Card2017_2018pre_2018post.txt
combineCards.py Y16=Card2016.txt Y17=Card2017.txt Y18pre=Card2018pre.txt Y18post=Card2018post.txt > Card2016_2017_2018pre_2018post.txt
combineCards.py Y16=Card2016.txt Y17=Card2017.txt Y18pre=Card2018pre.txt Y18post=Card2018post.txt > CardCombo.txt
root -l -q -b 'make_MVA_8bin_ws.C("2016",    "'${inputRoot2016}'",    "'${signalType}'","'${mass}'","'${dataType}'","'${syst}'")'
root -l -q -b 'make_MVA_8bin_ws.C("2017",    "'${inputRoot2017}'",    "'${signalType}'","'${mass}'","'${dataType}'","'${syst}'")'
root -l -q -b 'make_MVA_8bin_ws.C("2018pre", "'${inputRoot2018pre}'", "'${signalType}'","'${mass}'","'${dataType}'","'${syst}'")'
root -l -q -b 'make_MVA_8bin_ws.C("2018post","'${inputRoot2018post}'","'${signalType}'","'${mass}'","'${dataType}'","'${syst}'")'
text2workspace.py Card${year}.txt -o ws_${year}_${signalType}_${mass}.root -m ${mass} --keyword-value MODEL=${signalType}
ws=ws_${year}_${signalType}_${mass}.root
fallBack="--cminDefaultMinimizerStrategy 1 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --cminFallbackAlgo Minuit2,Migrad,1:1.0 --cminFallbackAlgo Minuit2,Migrad,0:1.0 --X-rtd MINIMIZER_MaxCalls=999999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH"
fitOptions="${ws} -m ${mass} --keyword-value MODEL=${signalType} ${fallBack}"

# Run the asympotic fits
if [ $doAsym == 1 ] 
then
    echo "Running Asymptotic fits"
    combine -M AsymptoticLimits ${fitOptions} --verbose 2 --rMax $rMax                        -n ${year}                               > log_${year}${signalType}${mass}_Asymp.txt
    combine -M Significance     ${fitOptions} --verbose 2 --rMax $rMax -t -1 --expectSignal=1 -n ${year}${signalType}${mass}_SignifExp > log_${year}${signalType}${mass}_Sign_sig.txt
    combine -M Significance     ${fitOptions} --verbose 2 --rMax $rMax                        -n ${year}${signalType}${mass}_SignifExp > log_${year}${signalType}${mass}_Sign_noSig.txt
fi

# Run the fit diagnostics fits (takes forever to run)
if [ $doFitDiag == 1 ] 
then
    echo "Running FitDiagnostics"
    if [ $inject == 0 ] 
    then
        combine -M FitDiagnostics ${fitOptions} --verbose 2 --rMax $rMax --robustFit=1 --plots --saveShapes --saveNormalizations -n ${year}${signalType}${mass} > log_${year}${signalType}${mass}_FitDiag.txt
    else
        combine -M FitDiagnostics ${fitOptions} --verbose 2 --rMax $rMax --robustFit=1 --plots --saveShapes --saveNormalizations -n ${year}${signalType}${mass} -t -1 --toysFrequentist --expectSignal=${inject} > log_${year}${signalType}${mass}_FitDiag.txt
    fi
fi

# Run asymptotic likihood scan
if [ $doMulti == 1 ] 
then
    echo "Running MultiDimFit"
    combine -M MultiDimFit ${fitOptions} --verbose 0 --rMin -0.2 --rMax 2.0 --algo=grid --points=100 -n SCAN_r_wSig > /dev/null
fi

# Run impact plots from the CombineHarvester repo
if [ $doImpact == 1 ] 
then
    echo "Running Impacts"
    ../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ${ws} -m ${mass} --doInitialFit --robustFit 1 ${fallBack} > log_step1.txt
    ../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ${ws} -m ${mass} --doFits --parallel 4 ${fallBack} > log_step2.txt
    ../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ${ws} -m ${mass} -o impacts_${year}${signalType}${mass}.json > log_step3.txt
    ../../CombineHarvester/CombineTools/scripts/plotImpacts.py -i impacts_${year}${signalType}${mass}.json -o impacts_${year}${signalType}${mass}_${dataType}
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
