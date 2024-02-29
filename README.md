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
