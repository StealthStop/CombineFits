CombineFits
===========================

### Official documentation

[Manual to run combine](https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/wiki)

### Stealth Stop Group Setup `(LPC)`
```
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_10_2_13
cd CMSSW_10_2_13/src
cmsenv
git clone git@github.com:StealthStop/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
scram b -j4
```

Add CombineTools from CombineHarvester to your work area:
 (this is needed for impact plots, and possible crab submission)
```
cd $CMSSW_BASE/src 
cmsenv
mkdir CombineHarvester 
cd CombineHarvester
git init
git remote add origin git@github.com:StealthStop/CombineHarvester.git 
git config core.sparsecheckout true; echo CombineTools/ >> .git/info/sparse-checkout
git pull origin master
cd $CMSSW_BASE/src
scram b -j4
```

Now copy input root files from eos (only needed for local, condor jobs copy the inputs from eos)
```
cd $CMSSW_BASE/src
git clone git@github.com:StealthStop/CombineFits.git
cd CombineFits
cmsenv
cp -r /eos/uscms/store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/Keras_2016_v1.2 .
cp -r /eos/uscms/store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/Keras_2017_v1.2 .
cp -r /eos/uscms/store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/Keras_2018pre_v1.2 .
cp -r /eos/uscms/store/user/lpcsusyhad/StealthStop/FitInputs_FullRun2/Keras_2018post_v1.2 .
```

### Running Unblinded Data Fits

The following steps can be used to make all of the datacards and run the final fits:
```
# Make data cards with no A region for first step of unblinding
for ch in 0l 2l; do for sig in RPV StealthSYY; do for type in MassExclusion MaxSign; do python produceDataCard.py --config configs/v3_5_1_Data_NoAReg/cardConfig_${ch}_${sig}_v3_5_1_${type}_Min3 --inpath DisCo_outputs_0l_1l_2l_${type}_Fix_11_05_23/ --outpath ./cards_${type}_Data_NoAReg/ --year Run2UL --channel ${ch} --model ${sig} --dataType Data; done; done; done


# Make data cards for final fits
for ch in 0l 2l; do for sig in RPV StealthSYY; do for type in MassExclusion MaxSign; do python produceDataCard.py --config configs/v3_5_1_Data/cardConfig_${ch}_${sig}_v3_5_1_${type}_Min3 --inpath DisCo_outputs_0l_1l_2l_${type}_Fix_11_05_23/ --outpath ./cards_${type}_Data/ --year Run2UL --channel ${ch} --model ${sig} --dataType Data; done; done; done

# Run all fits
cd ../condor/
./AllFits_Data_NoAReg.sh; ./AllFits_Data.sh 

# Making final fit plots
./make_FitPvalueLimit_Plots_Data.sh all

```

Note that we are only running the first set of fits (i.e. NoAReg) to satisfy our initial unblinding policy. These fits may be bypassed later and are not necessary to get the full results. 
### Running Local Examples

To combine the datacards for 2016 and 2017:
```
combineCards.py Y16=dataCards/Card2016.txt Y17=dataCards/Card2017.txt                                                 > dataCards/Card2016_2017.txt
combineCards.py                                   Y18pre=dataCards/Card2018pre.txt Y18post=dataCards/Card2018post.txt > dataCards/Card2018pre_2018post.txt
combineCards.py Y16=dataCards/Card2016.txt Y17=dataCards/Card2017.txt Y18pre=dataCards/Card2018pre.txt                          > dataCards/Card2016_2017_2018pre.txt
combineCards.py Y16=dataCards/Card2016.txt Y17=dataCards/Card2017.txt Y18pre=dataCards/Card2018pre.txt Y18post=dataCards/Card2018post.txt > dataCards/Card2016_2017_2018pre_2018post.txt
combineCards.py Y16=dataCards/Card2016.txt Y17=dataCards/Card2017.txt Y18pre=dataCards/Card2018pre.txt Y18post=dataCards/Card2018post.txt > dataCards/CardCombo.txt

```

To make a RooFit workspace that contains our PDF definitions and input histograms:

For 2016, 2017, 2018pre/post RPV 350:
```
root -l -q 'make_MVA_8bin_ws.C("2016",    "Keras_2016_v1.2",    "RPV","350","pseudodata","")'
root -l -q 'make_MVA_8bin_ws.C("2017",    "Keras_2017_v1.2",    "RPV","350","pseudodataS_0.3xRPV_350","")'
root -l -q 'make_MVA_8bin_ws.C("2018pre", "Keras_2018pre_v1.2", "RPV","350","pseudodataS_0.3xRPV_350","")'
root -l -q 'make_MVA_8bin_ws.C("2018post","Keras_2018post_v1.2","RPV","350","pseudodataS_0.3xRPV_350","")'
```

Can substitute other input directories, models, and mass points,
The last arguement can be:  pseudodata, pseudodataS, or data
The workspace goes into a file called MVA_<year>_<model>_<mass>_ws.root

--------------------------------------------------

Convert the card file (and the PDFs and input histograms references therein) into a workspace:

For 2016 RPV 350:
```
text2workspace.py dataCards/Card2016.txt -o ws_2016_RPV_350.root -m 350 --keyword-value MODEL=RPV
```

For 2016 + 2017 + 2018pre + 2018post RPV 350:
```
text2workspace.py dataCards/CardCombo.txt -o ws_Combo_RPV_350.root -m 350 --keyword-value MODEL=RPV
```

Can substitute other models.
The above command produces a file called ws_<year>_<model>_<mass>.root and will be
fed to combine in the following commands.

--------------------------------------------------

Calculate quick asymptotic limits:

For 2016 RPV 350:
```
combine -M AsymptoticLimits ws_2016_RPV_350.root -m 350 --keyword-value MODEL=RPV --verbose 2 -n 2016 > log_2016RPV350_Asymp.txt
```

For 2016 + 2017 + 2018pre + 2018post RPV 350:
```
combine -M AsymptoticLimits ws_Combo_RPV_350.root -m 350 --keyword-value MODEL=RPV --verbose 2 -n Combo > log_ComboRPV350_Asymp.txt
```

Outputs files with names such as:
higgsCombine2017.AsymptoticLimits.mH550.MODELRPV.root
which contains the expected (and observed) limits,
and a log file with a name such as log_2017RPV650_Asymp.txt

--------------------------------------------------

To make a limit plot:

Collect the above asymptotic limit root files for all mass points into a results directory, such as fit_results_v5_Jan17_2019

```
root -l -q 'makePlots.C+("Jan17_2019","fit_results_v5_Jan17_2019","2017","RPV")'
```
(the first arguement above is just intended to be today's date, or other tag)

--------------------------------------------------


Calculate the significance using the asimov dataset and expected signal strength of 1.
Significance is printed to screen and is available in the file
higgsCombineTest.Significance.mH550.MODELRPV.root
```
combine -M Significance ws_2017_RPV_550.root -t -1 --expectSignal=1 -m 550 --keyword-value MODEL=RPV -n 2017RPV550_SignifExp
```

Calculate the observed significance:
```
combine -M ProfileLikelihood ws_2017_RPV_550.root --significance -m 550 --keyword-value MODEL=RPV -n 2017RPV550_SignifObs
```

--------------------------------------------------

Run the full fitDiagnostics:

```
combine -M FitDiagnostics ws_2017_RPV_550.root --plots --saveShapes --saveNormalizations -m 550 --keyword-value MODEL=RPV -n 2017RPV550 > log_2017RPV550.txt
```

The above command produces a root file called fitDiagnostics2017RPV550.root that contains RooPlots and RooFitResults.
It also produces a file called higgsCombine2017RPV550.FitDiagnostics.mH550.MODELRPV.root that has the signal strength.
It also produces a log file called log_2017RPV550.txt (yields and best fit signal strength are at the end of this log file).

Produce formatted plots of fit results for each MVA bin:
```
root -q -l fit_report_ESM.C("fitDiagnostics2017RPV550.root")
```
or do the same but without yellow fit uncertainty:
```
root -q -l fit_report_ESM.C("fitDiagnostics2017RPV550.root",false)
```

Print the parameters resulting from the fit:
```
python test/diffNuisances.py --all --abs fitDiagnostics2017RPV550.root
```

--------------------------------------------------

Study the impacts:
  (you need CombineTools from CombineHarvester for this step to work, see instructions above)

Impacts using Azimov, on data, with expected signal 0

```
root -l -q 'make_MVA_8bin_ws.C("2016","Keras_V1.2.6_v1_DataQCDShape","RPV","350","data")'
text2workspace.py dataCards/Card2016.txt -o ws_2016_RPV_350.root -m 350 --keyword-value MODEL=RPV
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350.root -m 350 --doInitialFit --robustFit 1 --rMin -10 -t -1 --expectSignal 0
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350.root -m 350 --doFits --parallel 4 --rMin -10 -t -1 --expectSignal 0
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350.root -m 350 -o impacts.json
../../CombineHarvester/CombineTools/scripts/plotImpacts.py -i impacts.json -o impacts_2016RPV350_ExpSig0
```

Impacts using Azimov, on data, with expected signal 1
```
root -l -q 'make_MVA_8bin_ws.C("2016","Keras_V1.2.6_v1_DataQCDShape","RPV","350","data")'
text2workspace.py dataCards/Card2016.txt -o ws_2016_RPV_350.root -m 350 --keyword-value MODEL=RPV
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350.root -m 350 --doInitialFit --robustFit 1 -t -1 --expectSignal 1
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350.root -m 350 --doFits --parallel 4 -t -1 --expectSignal 1
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350.root -m 350 -o impacts.json
../../CombineHarvester/CombineTools/scripts/plotImpacts.py -i impacts.json -o impacts_2016RPV350_ExpSig1
```

Impacts on data  (add the --rMin -10 option if best fit is close to zero)
```
root -l -q 'make_MVA_8bin_ws.C("2016","Keras_V1.2.6_v1_DataQCDShape","RPV","350","data")'
text2workspace.py dataCards/Card2016.txt -o ws_2016_RPV_350.root -m 350 --keyword-value MODEL=RPV
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350.root -m 350 --doInitialFit --robustFit 1
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350.root -m 350 --doFits --parallel 4
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350.root -m 350 -o impacts.json
../../CombineHarvester/CombineTools/scripts/plotImpacts.py -i impacts.json -o impacts_RPV350_data
```

Impacts on pseudodata without signal:
```
root -l -q 'make_MVA_8bin_ws.C("2016","Keras_V1.2.6_v1_DataQCDShape","RPV","350","pseudodata")'
text2workspace.py dataCards/Card2016.txt -o ws_2016_RPV_350_pseudo.root -m 350 --keyword-value MODEL=RPV
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350_pseudo.root -m 350 --doInitialFit --robustFit 1 --rMin -10
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350_pseudo.root -m 350 --doFits --parallel 4 --rMin -10
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350_pseudo.root -m 350 -o impacts.json
../../CombineHarvester/CombineTools/scripts/plotImpacts.py -i impacts.json -o impacts_RPV350_pseudodata
```

Impacts on pseudodata with signal:
```
root -l -q 'make_MVA_8bin_ws.C("2016","Keras_V1.2.6_v1_DataQCDShape","RPV","350","pseudodataS")'
text2workspace.py dataCards/Card2016.txt -o ws_2016_RPV_350_pseudoS.root -m 350 --keyword-value MODEL=RPV
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350_pseudoS.root -m 350 --doInitialFit --robustFit 1
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350_pseudoS.root -m 350 --doFits --parallel 4
../../CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d ws_2016_RPV_350_pseudoS.root -m 350 -o impacts.json
../../CombineHarvester/CombineTools/scripts/plotImpacts.py -i impacts.json -o impacts_RPV350_pseudodataS
```


--------------------------------------------------

Background-only fits to tt background, before and after systematic variations:
```
root -l
.x make_BkgOnly_ws.C("_btgUp");
combine -M FitDiagnostics RPV_550_BkgOnlyCard.txt --plots --saveShapes --saveNormalizations -n _btgUp
root -l fitDiagnostics_btgUp.root
shapes_fit_b->cd();
D1->cd();
TT->Draw();
etc.
```


### Running Fits on condor

Running all of the fits using condor

```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/condor
python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2016 -t data        --output Fit_Data_2016
python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2016 -t pseudodata  --output Fit_pseudoData_2016
python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2016 -t pseudodataS --output Fit_pseudoDataS_2016

python condorSubmit.py --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 300,350,400,450,500,550,600,650,700,750,800,850,900 -y 2017 -t data        --output Fit_Data_2017
python condorSubmit.py --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 300,350,400,450,500,550,600,650,700,750,800,850,900 -y 2017 -t pseudodata  --output Fit_pseudoData_2017
python condorSubmit.py --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 300,350,400,450,500,550,600,650,700,750,800,850,900 -y 2017 -t pseudodataS --output Fit_pseudoDataS_2017

python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y Combo -t data        --output Fit_Data_Combo
python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y Combo -t pseudodata  --output Fit_pseudoData_Combo
python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y Combo -t pseudodataS --output Fit_pseudoDataS_Combo

```

Making limit plots from condor output

```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
root -l -q 'makePlots.C("<date>_data2016","condor/Fit_Data_2016/output-files","2016","RPV")'
root -l -q 'makePlots.C("<date>_data2016","condor/Fit_Data_2016/output-files","2016","SYY")'
root -l -q 'makePlots.C("<date>_data2016","condor/Fit_Data_2016/output-files","2016","SHH")'

root -l -q 'makePlots.C("<date>_pseudodata2016","condor/Fit_pseudoData_2016/output-files","2016","RPV")'
root -l -q 'makePlots.C("<date>_pseudodata2016","condor/Fit_pseudoData_2016/output-files","2016","SYY")'
root -l -q 'makePlots.C("<date>_pseudodata2016","condor/Fit_pseudoData_2016/output-files","2016","SHH")'

root -l -q 'makePlots.C("<date>_data2017","condor/Fit_Data_2017/output-files","2017","RPV")'
root -l -q 'makePlots.C("<date>_data2017","condor/Fit_Data_2017/output-files","2017","SYY")'
root -l -q 'makePlots.C("<date>_data2017","condor/Fit_Data_2017/output-files","2017","SHH")'

root -l -q 'makePlots.C("<date>_pseudodata2017","condor/Fit_pseudoData_2017/output-files","2017","RPV")'
root -l -q 'makePlots.C("<date>_pseudodata2017","condor/Fit_pseudoData_2017/output-files","2017","SYY")'
root -l -q 'makePlots.C("<date>_pseudodata2017","condor/Fit_pseudoData_2017/output-files","2017","SHH")'
``` 

Making profile scan from condor output

```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
python make_profile_plot.py --model RPV --year 2016 --data 0 --basedir condor --masses 350 450 550 650 750 850
python make_profile_plot.py --model SYY --year 2016 --data 0 --basedir condor --masses 350 450 550 650 750 850
python make_profile_plot.py --model SHH --year 2016 --data 0 --basedir condor --masses 350 450 550 650 750 850

python make_profile_plot.py --model RPV --year 2016 --data 1 --basedir condor --masses 350 450 550 650 750 850
python make_profile_plot.py --model SYY --year 2016 --data 1 --basedir condor --masses 350 450 550 650 750 850
python make_profile_plot.py --model SHH --year 2016 --data 1 --basedir condor --masses 350 450 550 650 750 850

python make_profile_plot.py --model RPV --year 2017 --data 0 --basedir condor --masses 300 350 400 450 500 550 600 650 700 750 800 850 900
python make_profile_plot.py --model SYY --year 2017 --data 0 --basedir condor --masses 300 350 400 450 500 550 600 650 700 750 800 850 900
python make_profile_plot.py --model SHH --year 2017 --data 0 --basedir condor --masses 300 350 400 450 500 550 600 650 700 750 800 850 900

python make_profile_plot.py --model RPV --year 2017 --data 1 --basedir condor --masses 300 350 400 450 500 550 600 650 700 750 800 850 900
python make_profile_plot.py --model SYY --year 2017 --data 1 --basedir condor --masses 300 350 400 450 500 550 600 650 700 750 800 850 900
python make_profile_plot.py --model SHH --year 2017 --data 1 --basedir condor --masses 300 350 400 450 500 550 600 650 700 750 800 850 900
```

Making fit results plots from condor output

```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
python make_fit_report_plot.py
```

### Running toys on condor

Similar to running the normal set of fits but add extra flags

```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/condor
python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2016 -t data        --output Fit_Data_2016        --toy --rMin 0.15 --rMax 0.3 --rStep 0.01 --jPerR 5 -T 500
python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2016 -t pseudodata  --output Fit_pseudoData_2016  --toy --rMin 0.15 --rMax 0.3 --rStep 0.01 --jPerR 5 -T 500
python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2016 -t pseudodataS --output Fit_pseudoDataS_2016 --toy --rMin 0.15 --rMax 0.3 --rStep 0.01 --jPerR 5 -T 500

python condorSubmit.py --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 300,350,400,450,500,550,600,650,700,750,800,850,900 -y 2017 -t data        --output Fit_Data_2017        --toy --rMin 0.15 --rMax 0.3 --rStep 0.01 --jPerR 5 -T 500
python condorSubmit.py --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 300,350,400,450,500,550,600,650,700,750,800,850,900 -y 2017 -t pseudodata  --output Fit_pseudoData_2017  --toy --rMin 0.15 --rMax 0.3 --rStep 0.01 --jPerR 5 -T 500
python condorSubmit.py --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 300,350,400,450,500,550,600,650,700,750,800,850,900 -y 2017 -t pseudodataS --output Fit_pseudoDataS_2017 --toy --rMin 0.15 --rMax 0.3 --rStep 0.01 --jPerR 5 -T 500

python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y Combo -t data        --output Fit_Data_Combo        --toy --rMin 0.15 --rMax 0.3 --rStep 0.01 --jPerR 5 -T 500
python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y Combo -t pseudodata  --output Fit_pseudoData_Combo  --toy --rMin 0.15 --rMax 0.3 --rStep 0.01 --jPerR 5 -T 500
python condorSubmit.py --inPut_2016 Keras_V1.2.8_Approval_StatErrPlusFullDev_12JetFix --inPut_2017 Keras_V3.0.4_Approval_StatErrPlusFullDev_12JetFix -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y Combo -t pseudodataS --output Fit_pseudoDataS_Combo --toy --rMin 0.15 --rMax 0.3 --rStep 0.01 --jPerR 5 -T 500

```

Now hadd output of all of these toy jobs

```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/condor
python hadder.py -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2016 -t data -p Fit_Data_2016
python hadder.py -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2016 -t data -p Fit_pseudoData_2016
python hadder.py -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2016 -t data -p Fit_pseudoDatas_2016

python hadder.py -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2017 -t data -p Fit_Data_2016
python hadder.py -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2017 -t data -p Fit_pseudoData_2016
python hadder.py -d RPV,SYY,SHH -m 350,450,550,650,750,850 -y 2017 -t data -p Fit_pseudoDatas_2016

python hadder.py -d RPV,SYY,SHH -m 300,350,400,450,500,550,600,650,700,750,800,850,900 -y Combo -t data -p Fit_Data_2016
python hadder.py -d RPV,SYY,SHH -m 300,350,400,450,500,550,600,650,700,750,800,850,900 -y Combo -t data -p Fit_pseudoData_2016
python hadder.py -d RPV,SYY,SHH -m 300,350,400,450,500,550,600,650,700,750,800,850,900 -y Combo -t data -p Fit_pseudoDatas_2016

```

Now can make limit plots with toy output

```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
root -l -q 'makePlots.C("<date>_data2016","condor/Fit_Data_2016/output-files","2016","RPV","HybridNew")'
root -l -q 'makePlots.C("<date>_data2016","condor/Fit_Data_2016/output-files","2016","SYY","HybridNew")'
root -l -q 'makePlots.C("<date>_data2016","condor/Fit_Data_2016/output-files","2016","SHH","HybridNew")'

root -l -q 'makePlots.C("<date>_pseudodata2016","condor/Fit_pseudoData_2016/output-files","2016","RPV","HybridNew")'
root -l -q 'makePlots.C("<date>_pseudodata2016","condor/Fit_pseudoData_2016/output-files","2016","SYY","HybridNew")'
root -l -q 'makePlots.C("<date>_pseudodata2016","condor/Fit_pseudoData_2016/output-files","2016","SHH","HybridNew")'

root -l -q 'makePlots.C("<date>_data2017","condor/Fit_Data_2017/output-files","2017","RPV","HybridNew")'
root -l -q 'makePlots.C("<date>_data2017","condor/Fit_Data_2017/output-files","2017","SYY","HybridNew")'
root -l -q 'makePlots.C("<date>_data2017","condor/Fit_Data_2017/output-files","2017","SHH","HybridNew")'

root -l -q 'makePlots.C("<date>_pseudodata2017","condor/Fit_pseudoData_2017/output-files","2017","RPV","HybridNew")'
root -l -q 'makePlots.C("<date>_pseudodata2017","condor/Fit_pseudoData_2017/output-files","2017","SYY","HybridNew")'
root -l -q 'makePlots.C("<date>_pseudodata2017","condor/Fit_pseudoData_2017/output-files","2017","SHH","HybridNew")'

```

### Examples for making pull plots

The first script run is `draw_hist_and_pull_plot.C` and the output of this script is run over by `makeFitPlots.py`. A couple of example calls are given below.

```
root -q -l -b 'draw_fit_hist_and_pull.c("condor/FullRun2_Unblinded_Jun15/Fit_Data_Combo/output-files/", "RPV_450_Combo/fitDiagnosticsComboRPV450.root", "RPV 450", "Y16_",     "RPV450Combo16s", 1, 1, 1, "RPV_850_Combo/fitDiagnosticsComboRPV850.root", "RPV 850")'

python makeFitPlots.py  --plotbkg --mass1 450 --model1 RPV
```
This would extract the Combo signal+background fit for 2016 as well as the RPV 450 signal shape and RPV 850 signal shape. All of these histograms get put into a ROOT file called `KELVIN_RPV450Combo16s.root`. Then we call `makeFitPlots.py` and ask for it to plot the background and pass the information about the signal used in the fit. Since we are running on a signal+background fit (RPV 450), the signal fit component is plotted rather than the raw shape.

```
root -q -l -b 'draw_fit_hist_and_pull.c("condor/FullRun2_Unblinded_Jun15/Fit_Data_Combo/output-files/", "RPV_450_Combo/fitDiagnosticsComboRPV450.root", "RPV 450", "Y16_",     "RPV450Combo16b", 0, 1, 1, "RPV_850_Combo/fitDiagnosticsComboRPV850.root", "RPV 850")'

python makeFitPlots.py --twosigfit --bkgonlyfit --mass1 450 --model1 RPV --mass2 850 --model2 RPV
```

This would extract the background-only fit as well as RPV 450 signal shape and RPV 850 signal shape. All these histograms get put into a ROOT file called `KELVIN_RPV450Combo16b.root`. Then we call `makeFitPlots.py` and ask it to show both signal shapes (thus we pass information about both signals---model and mass) and explicitly say we want the background-only fit.

### Using produceDataCard.py

`produceDataCard.py` is a script for making data cards using our ABCD regions from the neural network. It takes a configuration file as an input in the style of `DataCardProducer/cardConfig.py` and outputs the data card to submit to Combine.

Arguments:

- `-c, --config [config file]` configuration file in the style of `DataCardProducer/cardConfig.py`.
- `-o, --output [output path]` path to output destination. Writes to `datacard.txt` by default.
- `-t, --dataType [dataType]` specify whether the data card constains pseudodata (pseudoData), pseudodata with signal injected (pseudoDataS), or data (data).
- `-a, --ABCD` use the ABCD regions from neural network output to create data card.
- `-s, --signal [model_mass]` used for making a specific data card for a given mass and signal model (separated by underscore).
- `-l, --leptons [number of final state leptons]` specify which decay topology for which the cards should be made.
- `-p, --path [NN inputs]` path to the neural network inputs for the data cards
- `--all` produce all data cards for a given year (all models, all mass points, all final states, pseudodata with/without signal injected.
- `--setClosure` force perfect ABCD closure for ttbar (only to be used with MC)

Example usage for a single data card:
```
cd DataCardProducer
python produceDataCard.py -c cardConfig -o mydatacard.txt --ABCD -s RPV_550 -l 0 -t pseudoDataS -p ../2016_DisCo_0l_1l_Inputs/
```

Or to make all data cards with MC event yields:
```
python produceDataCard.py -c cardConfigGoodClose -p ../2016_DisCo_0l_1l_Inputs/ --all 
```

### Running fits with Condor

After the necessary data cards have been produced, `CombineFits/condor/condorSubmit.py` can be used to run various types of fitting procedures. 

Relevant arguments:

- `-d [Signals]` List of signal models, comma separated
- `-t [DataType]` Specify whether running over pseudoData, pseudoDataS, or data
- `-s [Suffix]` Specify the final state by number of leptons (e.g. 0l or 1l)
- `-m [Masses]` List or range of masses (list: comma separated, range: inclusive on endpoints, separated by dash)
- `-y [Year]` Desired year for fits
- `--setClosure` Run fits using perfect closure data cards (must already be produced)
- `-F` Run FitDiagnostics fitting method
- `-A` Run AsymptoticLimit and Significance fitting methods
- `--output [Outpath]` Name of directory where output of each condor job goes 

Example usage:
```
python condorSubmit.py -y 2016 -d RPV,SYY -m 300-1400 -t pseudoDataS -F -A --output Fit_2016
```

### Making pre- and post-fit Njet distributions

`CombineFits/DataCardProducer/make_fit_plots.py` is a script for making pre- and post-fit Njet distributions. It requires the output of the FitDiagnostics combine method.

Relevant arguments:

- `-s, --signal [Signal model]` Name of signal process
- `-y, --year [Year]` Year for data cards used in fit
- `-m, --mass [Mass]` Mass for data cards used in fit
- `-d, --dataType [Data Type]` Specify whether fit was run over pseudoData, pseudoDataS, or data
- `-p, --path [Path to Condor directory]` Path to the condor directory with the FitDiagnostics results
- `-s, --suffix [Number of final state leptons]` Specify the number of final state leptons as 0l or 1l
- `-n, --njets [Njet range in data cards]` Specify the range of Njets for the bins in data cards (separated with a dash, e.g. 7-12)
- `--plotb/--plotsb/--plotsig/--plotdata` Include background fit, signal+background fit, signal component, or observed data in plots
- `--all` Make the pre- and post-fit Njets distributions for all signal models, masses, and final states for both pseudoData and pseudoDataS

Example usage:

```
python make_fit_plots.py -y 2016 --path ../condor/Fit_2016 -s RPV -m 550 -d pseudoDataS --plotsb --plotb --plotdata --plotsig
```

The pre- and post-fit distributions will be saved in the `figures` directory and the raw histograms will be saved in the `resutls` directory.

### Making p-value plots

`tabel_signal_strength.py` is a script that will produce p-value plots using the fit results from a condor directory as input. The script presumes that the name of this directory is `CombineFits/condor/Fit_<year>`.

Relavent arguments:
- `--basedir` Name of base condor directory containing fit results
- `--pdfName` Name to add to the end of each p-value plot pdf (usually the date)
- `--perfectClosure` Use the perfect closure fit results when making p-value plots
- `--approved` Is the plot approved

Example usage:
```
python table_signal_string.py --pdfName=Jan12021
```

