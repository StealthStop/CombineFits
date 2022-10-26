from dataCardProducer import dataCardMaker as dcm
from optparse import OptionParser
import importlib
import copy
import os

def main():
    parser = OptionParser()
    parser.add_option("-c", "--config",          dest="config",         action="store",      default="None",     type="string", help="Config file for the data card [REQUIRED].")
    parser.add_option("-o", "--outpath",         dest="outpath",        action="store",      default="cards",    type="string", help="Output path for data card")
    parser.add_option("-t", "--dataType",        dest="dataType",                            default='data',     type='string', help="Specify if running over data or pseudo data")
    parser.add_option("--all",                   dest="all",            action="store_true", default=False,                     help="Make all data cards (all signal models, PseudoData w/ and w/o Signal injected, 0l and 1l)")
    parser.add_option("--Run2",                  dest="Run2",           action="store_true", default=False,                     help="Scale 2016 pseudodata to full Run 2 lumi")
    parser.add_option("-s", "--signal",          dest="signal",         action="store",      default="RPV_550",  type='string', help="Name of signal and mass for card separated by \'_\' (e.g. RPV_550)")
    parser.add_option("-I", "--injectedSignal",  dest="injectedSignal", action="store",      default="SAME",     type='string', help="Name of signal and mass to inject for all cards")
    parser.add_option("-l", "--leptons",         dest="leptons",        action="store",      default="Nonetype", type="string", help="Number of leptons in final state (0 or 1)")
    parser.add_option("-p", "--path",            dest="path",           action="store",      default="./",       type='string', help="Path to root files")
    parser.add_option("-y", "--year",            dest="year",           action="store",      default="Run2UL",   type='string', help="Year for producing datacards")
    parser.add_option("--minNjet",               dest="minNjet",        action="store",      default=7,          type="int",    help="Min Njet bin to use")
    parser.add_option("--maxNjet",               dest="maxNjet",        action="store",      default=12,         type="int",    help="Max Njet bin to use")
    parser.add_option("--NoMCcorr",              dest="NoMCcorr",       action="store_true", default=False,                     help="Do not use MC correction factor in ABCD calculation for TT")
    (options, args) = parser.parse_args()
    
    # Must specify cardConfig to load info about histograms, ROOT files, bkg and sig processes, systematics, etc.
    if options.config == "None":
        parser.error('Config file not given, specify with -c')

    # Shorthand option for generating datacards for all channels, signals, masses, datatypes, and years
    elif options.all:
        if options.path == "./":
            parser.error('Input path not given, specify with -p')
        print(options.config)
        configfile = importlib.import_module(options.config)
 
        signals = ["RPV", "StealthSYY"]
        masses = [x for x in range(300, 1450, 50)]
        dataTypes = ["pseudoData", "pseudoDataS"]       
        #leptons = ["0l", "1l", "combo"]
        leptons = ["1l"]

        for s in signals:
            for m in masses:
                for d in dataTypes:
                    for l in leptons:
                        year = options.year

                        # Based on ordering of "leptons" list, 0l and 1l cards are made first, so
                        # when the "combo" string is reached in the list, the individual channel cards
                        # are guaranteed to already exist
                        if l == "combo":
                            os.system("combineCards.py HADRONIC={4}/{0}_{1}_{2}_{3}_0l.txt SEMILEPTONIC={4}/{0}_{1}_{2}_{3}_1l.txt > {4}/{0}_{1}_{2}_{3}_combo.txt".format(year, s, m, d, options.outpath))
                        else:
                            model = s + "_2t6j"

                            if not os.path.isdir(options.outpath):
                                os.makedirs(options.outpath)

                            outpath = "{}/{}_{}_{}_{}_{}.txt".format(options.outpath, year, s, m, d, l)

                            print("Writing data card to {}".format(outpath))

                            # Determine if the injected signal model and mass should be the same
                            # as the signal component used in the fit, or some other component
                            injectedModel = model
                            injectedMass  = m
                            if options.injectedSignal != "SAME":
                                injectedModel = options.signal.split("_")[0] + "_2t6j"
                                if(options.signal.find("SYY") != -1):
                                    injectedModel = "Stealth" + injectedModel 

                                injectedMass = options.injectedSignal.split('_')[1]
    
                            # Must make copy of dictionary to do repeated string replacements in for loop key
                            tempObs = copy.copy(configfile.observed)
                            tempSys = copy.copy(configfile.systematics)

                            # Construct DataCardProducer class instance, which automatically calls member functions for writing out datacards
                            dcm(options.path, tempObs, outpath, tempSys, d, l, year, options.Run2, options.NoMCcorr, options.minNjet, options.maxNjet, model, str(m), injectedModel, str(injectedMass))
                        
    # Must specify a channel to generate datacards for
    elif options.leptons == "None":
        parser.error('Please specify number of final state leptons with -l')
    else:
        configfile = importlib.import_module(options.config)
   
        if(options.signal.find("SYY") != -1):
            model = "Stealth" + options.signal.split("_")[0] + "_2t6j"    
        elif options.signal.find("RPV") != -1:
            model = options.signal.split('_')[0] + "_2t6j"

        mass = options.signal.split('_')[1]
        year = options.year

        # Determine if the injected signal model and mass should be the same
        # as the signal component used in the fit, or some other component
        injectedModel = model
        injectedMass  = mass
        if options.injectedSignal != "SAME":
            injectedModel = options.signal.split("_")[0] + "_2t6j"
            if(options.signal.find("SYY") != -1):
                injectedModel = "Stealth" + injectedModel 

            injectedMass = options.injectedSignal.split('_')[1]

        print("Writing data card to "+options.outpath)
        # Construct DataCardProducer class instance, which automatically calls member functions for writing out datacards
        dcm(options.path, configfile.observed, options.outpath, configfile.systematics, options.dataType, options.leptons + "l", year, options.Run2, options.NoMCcorr, options.minNjet, options.maxNjet, model, mass, injectedModel, injectedMass)

if __name__ == "__main__":
    main()
