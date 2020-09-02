#!/bin/bash

inputRoot2016=$1
inputRoot2017=$2
inputRoot2018pre=$3
inputRoot2018post=$4
signalType=$5
mass=$6
year=$7
dataType=$8
rVal=$9
seed=${10}
numToys=${11}
iterations=${12}
doToyS=${13}
syst=${14}
base_dir=`pwd`

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
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs/${inputRoot2016}/njets_for_Aron.root        ${inputRoot2016}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs/${inputRoot2016}/ttbar_systematics.root     ${inputRoot2016}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs/${inputRoot2016}/qcdcr-syst-parameters.root ${inputRoot2016}/.

mkdir ${inputRoot2017}
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs/${inputRoot2017}/njets_for_Aron.root        ${inputRoot2017}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs/${inputRoot2017}/ttbar_systematics.root     ${inputRoot2017}/.
xrdcp root://cmseos.fnal.gov//store/user/lpcsusyhad/StealthStop/FitInputs/${inputRoot2017}/qcdcr-syst-parameters.root ${inputRoot2017}/.

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
fitOptions="${ws} -m ${mass} --keyword-value MODEL=${signalType} -n ${year} --saveToys --saveHybridResult"

if [ $doToyS == 1 ] 
then
    printf "\n\n Running sig. toys\n"
    combine -M HybridNew --LHCmode LHC-significance ${fitOptions} -T ${numToys} -s ${seed} --fullBToys -i ${iterations} > log_tmp.txt
else
    printf "\n\n Running limit toys\n"
    combine -M HybridNew --LHCmode LHC-limits       ${fitOptions} -T ${numToys} -s ${seed} --fullBToys --singlePoint ${rVal} --clsAcc 0 > log_tmp.txt 
fi

#removing log files because they can be larger than 1G
rm log_tmp.txt

mv *.root ${base_dir}
mv log*.txt ${base_dir}

cd ${base_dir}
