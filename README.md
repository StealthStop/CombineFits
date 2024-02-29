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
