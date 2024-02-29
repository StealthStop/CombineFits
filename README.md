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

```
cd $CMSSW_BASE/src
git clone git@github.com:StealthStop/CombineFits.git
cd CombineFits
cmsenv
```

### Producing Data Cards

Production of data cards can typically proceed manually in the `DataCardsProducer` area of the `CombineFits` area.
Ultimately, production is driven by the `produceDataCard.py` script, which references the `dataCardProducer.py` script for core machinery of reading ROOT files, computing values, etc.
Likewise, these scripts depend on config files in the `configs` folder, which specify ROOT files where specific systematics can be taken from, which systematics to include, analysis bin info, etc.
The python production scripts are steered by a main bash script `makeDataCards.sh` for easy producing in bulk by the user.
The current help docs for the main bash script are:

```
How run this script:
./makeDataCards.sh [OPTIONS]
[OPTIONS]
    --models mod1 mod2 ...      : list of the models to process
    --channels chan1 chan2 ...  : list of the channels to process ('combo' allowed)
    --dataTypes type1 type2 ... : list of the data types to process
    --lowMass ...               : make cards for low mass optimization
    --highMass ...              : make cards for high mass optimization
    --inputsTag myAnaOuptut ... : tag for specifying input ROOT files
    --scaleSyst 2 ...           : scale systematics by some amount including removing them
    --systsToScale fsr isr ...  : list of certain systs to scale only
    --injectIntoData ...        : Inject signal into data with strength r
    --cardsTag myCardsTag ...   : Custom tag for naming output cards folder
    --doCombo ...               : Do combo of all three channels
    --dryRun ...                : Print production commands to be run only
```

An example calling of the bash script for making a full set of data cards would be:

```
./makeDataCards.sh --models RPV StealthSYY --channels 0l 1l 2l combo --dataTypes Data --inputsTag bryansLatestAnaOutput --cardsTag joshsLatestCards
```

Note that in wrapping the `produceDataCards.py` script, some assumptions are hard-coded about which configs to use, and the naming of analysis output folder.

### Submitting Fit Jobs to Condor

The core script for submitting fit jobs to the LPC Condor grid is the `condorSubmit.py` script.
For easy submitting of different types of jobs in bulk, a steering bash shell script is provided for the user `submitFitJobs.sh`
The help menu for possible options reads

```
How to run this script:
./submitFitJobs.sh [OPTIONS]
[OPTIONS]
    --models mod1 mod2 ...      : list of the models to process
    --channels chan1 chan2 ...  : list of the channels to process ('combo' allowed)
    --dataTypes type1 type2 ... : list of the data types to process
    --asimovInjs 0.0 0.2 ...    : values of expected signal for Asimov-style fits
    --impacts                   : run impacts
    --asympLimits               : run asymptotic limits
    --fitDiags                  : run fit diagnostics
    --dLLscans                  : run log likelihood scans
    --lowMasses                 : run low-mass optimization fits
    --highMasses                : run high-mass optimization fits
    --massRange 400-600         : specific specific masses to run on
    --maskABCD A B C D ...      : list of ABCD regions to exclude
    --maskNjets 9 10 ...        : list of Njets bins to exclude
    --maskChannels 0l ...       : for combo fit, list of channels to exclude
    --fitsTag myFitResults      : tag for customizing fit outputs name
    --cardsTag myDataCards      : tag for grabbing specific cards
    --dryRun                    : do not run condor submit
```

An example for running the full set of fits would be:

```
./submitFitJobs.sh --models RPV StealthSYY --channel 0l 1l 2l combo --dataTypes Data --cardsTag joshsLatestCards --fitstag joshsLatestFits
```

Note that by default, all fit types are run (impacts, asymp. limits, significance, log likelihood scans) and both mass optimizations

### Making Plots from Fit Results

Finally, the making of various plots from the output fit results is steered by `makeFitResultPlots.sh`.
The help menu for the script is:

```
How run this script:
./makeFitResultPlots.sh [OPTIONS]
[OPTIONS]
    --models mod1 mod2 ...      : list of the models to process
    --masses mass1 mass2 ...    : list of the masses to process
    --channels chan1 chan2 ...  : list of the channels to process ('combo' allowed)
    --dataTypes type1 type2 ... : list of the data types to process
    --impacts                   : make the impacts plots
    --fits                      : make the fits bonly and sb ABCD-njets plots
    --pvalues                   : make the pvalues/signal strength plots
    --limits                    : make the expected and observed limits plots
    --npComps                   : make the nuisance parameter comparison plots
    --dLLscans                  : make the dLL vs r scan plots
    --noGraft                   : make pvalues and limits with a single optimization
    --asimovInjs 0.0 0.2 ...    : get the asimov version of applicable plots with injected signal strengths
    --fitsTag                   : name for choosing particular fit results
```

Currently, there are six unique plots that can be made from the fit output.
The impacts and log likelihood plots are made using built-in plotting scripts from Combine.
The four remaining plots are made using custom plotting scripts:

```
--fits: runs make_fit_plots.py
--pvalues: runs make_Pvalue_PlotsTables.py
--limits: runs make_Limit_Plots.py
--npComps: runs makeNPplots.py
```
