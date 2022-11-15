import os
import copy
import importlib
import argparse

from dataCardProducer import dataCardMaker 

def main():

    usage  = "usage: %prog [options]"
    parser = argparse.ArgumentParser(usage)
    parser.add_argument("--config",          dest="config",         action="store",      required=True,                                type=str, help="Config file for each 0l, 1l, 2l"                 )
    parser.add_argument("--inpath",          dest="inpath",         action="store",      required=True,                                type=str, help="input path to get root files"                    )
    parser.add_argument("--outpath",         dest="outpath",        action="store",      default="cards",                              type=str, help="Output path for data card"                       )
    parser.add_argument("--year",            dest="year",           action="store",      default="Run2UL",                             type=str, help="Year for producing datacards"                    )
    parser.add_argument("--lepton",          dest="lepton",         action="store",      required=True,                                type=str, help="Number of leptons in final state (0,1,2,combo)"  )
    parser.add_argument("--dataType",        dest="dataType",       nargs="+",           default=["pseudoData", "pseudoDataS"],        type=str, help="Data types: pseudoData, pseudoDataS, Data"       )
    parser.add_argument("--model",           dest="model",          nargs="+",           default=["RPV", "SYY"],                       type=str, help="Signal models: RPV, SYY"                         )
    parser.add_argument("--mass",            dest="mass",           nargs="+",           default=map(str, list(range(300, 1450, 50))), type=str, help="All mass points"                                 )    
    parser.add_argument("--injectedSignal",  dest="injectedSignal", action="store",      default="SAME",                               type=str, help="Name of signal and mass to inject for all cards" )
    parser.add_argument("--minNjet",         dest="minNjet",        action="store",      default=7,                                    type=int, help="Min Njet bin to use"                             )
    parser.add_argument("--maxNjet",         dest="maxNjet",        action="store",      default=12,                                   type=int, help="Max Njet bin to use"                             )
    parser.add_argument("--NoMCcorr",        dest="NoMCcorr",       action="store_true", default=False,                                help="Do not use MC correction factor in ABCD calculation for TT")
    args = parser.parse_args()   
 
    # ---------------------------------------------
    # make the datacards by config files & leptons:
    #   -- cardConfig_0l.py & 0l 
    #   -- cardConfig_1l.py & 1l
    #   -- cardConfig_2l.py & 2l  
    # ---------------------------------------------
    configfile = importlib.import_module(args.config)
    channels   = ["0l", "1l", "2l", "combo"]

    # loop over to make the cards
    for model in args.model:

        for mass in args.mass:

            for data in args.dataType:

                for channel in channels:

                    year = args.year
            
                    # combine 0l, 1l, 2l cards as "combo" card
                    if args.lepton == "combo":
                        os.system("combineCards.py HADRONIC={4}/{0}_{1}_{2}_{3}_0l.txt SEMILEPTONIC={4}/{0}_{1}_{2}_{3}_1l.txt > LEPTONIC={4}/{0}_{1}_{2}_{3}_1l.txt > {4}/{0}_{1}_{2}_{3}_combo.txt".format(year, model, mass, data, args.outpath))
                    
                    else:
                        Model = model + "_2t6j"

                        if not os.path.isdir(args.outpath):
                            os.makedirs(args.outpath)

                        outpath = "{}/{}_{}_{}_{}_{}.txt".format(args.outpath, year, model, mass, data, channel)

                        print("Writing data card to {}".format(outpath))

                        # determine if the injected signal model and mass should be the same
                        # as the signal component used in the fit, or some other component
                        injectedModel = Model
                        injectedMass  = mass

                        if args.injectedSignal != "SAME":
                            injectedModel = args.model.split("_")[0] + "_2t6j"

                            if(args.model.find("SYY") != -1):
                                injectedModel = "Stealth" + injectedModel 

                            injectedMass = args.injectedSignal.split('_')[1]
    
                        # Must make copy of dictionary to do repeated string replacements in for loop key
                        tempObs = copy.copy(configfile.observed)
                        tempSys = copy.copy(configfile.systematics)

                        # Construct DataCardProducer class instance, which automatically calls member functions for writing out datacards
                        things = dataCardMaker(args.inpath, tempObs, outpath, tempSys, data, channel, year, args.NoMCcorr, args.minNjet, args.maxNjet, Model, str(mass), injectedModel, str(injectedMass))
                    

if __name__ == "__main__":
    main()
