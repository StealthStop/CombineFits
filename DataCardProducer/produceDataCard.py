import os
import sys
import copy
import importlib
import argparse

from dataCardProducer import dataCardMaker 
#from dataCardProducer_scan import dataCardMaker 

def main():

    usage  = "usage: %prog [options]"
    parser = argparse.ArgumentParser(usage)
    parser.add_argument("--config",          dest="config",         action="store",      default="cardConfig",                         type=str, help="Config file for each 0l, 1l, 2l"                 )
    parser.add_argument("--inpath",          dest="inpath",         action="store",      default="inputs",                             type=str, help="input path to get root files"                    )
    parser.add_argument("--outpath",         dest="outpath",        action="store",      default="cards",                              type=str, help="Output path for data card"                       )
    parser.add_argument("--year",            dest="year",           action="store",      default="Run2UL",                             type=str, help="Year for producing datacards"                    )
    parser.add_argument("--channel",         dest="channel",        action="store",      default="0l",                                 type=str, help="Which final state channel (0l, 1l, 2l)"  )
    parser.add_argument("--dataType",        dest="dataType",       nargs="+",           default=["pseudoData", "pseudoDataS"],        type=str, help="Data types: pseudoData, pseudoDataS, Data"       )
    parser.add_argument("--model",           dest="model",          nargs="+",           default=["RPV", "StealthSYY"],                       type=str, help="Signal models: RPV, SYY"                         )
    parser.add_argument("--mass",            dest="mass",           nargs="+",           default=map(str, list(range(300, 1450, 50))), type=str, help="All mass points"                                 )    
    parser.add_argument("--combo",           dest="combo",          nargs="+",           default=[],                                   type=str, help="Which channels to include in combo datacard"     )    
    parser.add_argument("--injectedSignal",  dest="injectedSignal", action="store",      default="SAME",                               type=str, help="Name of signal and mass to inject for all cards" )
    parser.add_argument("--injectIntoData",  dest="injectIntoData", action="store",      default=0.0,                                  type=float, help="inject signal with signal strength specified" )
    parser.add_argument("--minNjet",         dest="minNjet",        action="store",      default=5,                                    type=int, help="Min Njet bin to use"                             )
    parser.add_argument("--maxNjet",         dest="maxNjet",        action="store",      default=14,                                   type=int, help="Max Njet bin to use"                             )
    parser.add_argument("--NoMCcorr",        dest="NoMCcorr",       action="store_true", default=False,                                help="Do not use Closure Correction in ABCD calculation for TT")
    parser.add_argument("--binEdges",        dest="binEdges",       nargs="+",           default=None,                              type=int, help="Do not use Closure Correction in ABCD calculation for TT")
    parser.add_argument("--singleBE",        dest="singleBE",       action="store",      default=None,                                 type=str, help="Single bin edge combo to make cards for (e.g. 60_60)")
    parser.add_argument("--fixedCloseSys",   dest="fixedCloseSys",  action="store",      default=None,                                 type=str, help="Replace closure correction with flat value (for studies)")
    parser.add_argument("--CloseSys",        dest="CloseSys",       action="store",      default=None,                                 type=str, help="Use first bin (None), all bins (all), or all bins outside of coverage by the first (allWorse)")
    parser.add_argument("--scaleSyst",       dest="scaleSyst",      action="store",      default=None,                                 type=float, help="Scale systs by some number, 0 will turn off systs")

    args = parser.parse_args()   
 
    # ---------------------------------------------
    # make the datacards by config files & leptons:
    #   -- cardConfig_0l.py & 0l 
    #   -- cardConfig_1l.py & 1l
    #   -- cardConfig_2l.py & 2l  
    # ---------------------------------------------

    configfile = None

    masses = args.mass

    outdir = args.outpath
    if args.injectIntoData > 0.0:
        outdir += "_sigInjectedAt%s"%(str(args.injectIntoData).replace(".","p"))

    # If running with --combo flag, then we don't need to load
    # a config file, we are just going to combine cards that should already exist
    if not args.combo:
        path = "/".join(args.config.split("/")[:-1])
        sys.path.append(path)
        module = args.config.split("/")[-1]
        configfile = importlib.import_module(module)

    if args.singleBE is None and args.binEdges is not None:
        # loop over to make the cards
        for disc1 in range(args.binEdges[0], args.binEdges[1], args.binEdges[2]):

            for disc2 in range(args.binEdges[0], args.binEdges[1], args.binEdges[2]):

                for model in args.model:

                    for mass in masses:

                        for data in args.dataType:

                            year = args.year
                        
                            # combine 0l, 1l, 2l cards as "combo" card
                            if args.combo:

                                comboStr = ""
                                for channel in args.combo:
                                    comboStr += "CH{5}={4}/{0}_{1}_{2}_{3}_{5}_{6}_{7}.txt ".format(year, model, mass, data, outdir, channel, disc1, disc2)
                                comboStr += "> {4}/{0}_{1}_{2}_{3}_combo_{5}_{6}.txt".format(year, model, mass, data, outdir, disc1, disc2)
                                
                                print("combineCards.py {}".format(comboStr))
                                os.system("combineCards.py {0}".format(comboStr))
                            
                            else:
                                Model = model + "_2t6j"
                                    

                                if not os.path.isdir(outdir):
                                    os.makedirs(outdir)

                                outpath = "{}/{}_{}_{}_{}_{}_{}_{}.txt".format(outdir, year, model, mass, data, args.channel, disc1, disc2)

                                print("Writing data card to {}".format(outpath))

                                # determine if the injected signal model and mass should be the same
                                # as the signal component used in the fit, or some other component
                                if "_" in args.injectedSignal:
                                    injectedModel = args.injectedSignal.split("_")[0]
                                    injectedMass = args.injectedSignal.split("_")[1]
                                else:
                                    injectedModel = Model
                                    injectedMass  = mass

                                #if args.injectedSignal != "SAME":
                                #    injectedModel = args.model.split("_")[0] + "_2t6j"

                                #    if(args.model.find("SYY") != -1):
                                #        injectedModel = "Stealth" + injectedModel 

                                #    injectedMass = args.injectedSignal.split('_')[1]
                
                                # Must make copy of dictionary to do repeated string replacements in for loop key
                                tempObs = copy.copy(configfile.observed)
                                tempSys = copy.copy(configfile.systematics)
                                tempMinNjet = copy.copy(configfile.obs_start)
                                tempMaxNjet = copy.copy(configfile.obs_end)
                                tempSpecial = copy.copy(configfile.special)

                                # Construct DataCardProducer class instance, which automatically calls member functions for writing out datacards
                                dataCardMaker(args.inpath, tempObs, outpath, tempSys, data, args.channel, year, args.NoMCcorr, tempMinNjet, tempMaxNjet, Model, str(mass), injectedModel, str(injectedMass), args.injectIntoData, tempSpecial, disc1, disc2, args.scaleSyst, args.minNjet, args.maxNjet)
    elif args.singleBE is not None:
        if args.singleBE.split("_")[0] == "":
            disc1 = args.singleBE.split("_")[1]
            disc2 = args.singleBE.split("_")[2]
        else:    
            disc1 = args.singleBE.split("_")[0]
            disc2 = args.singleBE.split("_")[1]
        # loop over to make the cards
        for model in args.model:

            for mass in masses:

                for data in args.dataType:

                    year = args.year
                
                    # combine 0l, 1l, 2l cards as "combo" card
                    if args.combo:

                        comboStr = ""
                        for channel in args.combo:
                            comboStr += "CH{5}={4}/{0}_{1}_{2}_{3}_{5}_{6}_{7}.txt ".format(year, model, mass, data, outdir, channel, disc1, disc2)
                        comboStr += "> {4}/{0}_{1}_{2}_{3}_combo_{5}_{6}.txt".format(year, model, mass, data, outdir, disc1, disc2)
                        
                        print("combineCards.py {}".format(comboStr))
                        os.system("combineCards.py {0}".format(comboStr))
                    
                    else:
                        Model = model + "_2t6j"
                            

                        if not os.path.isdir(outdir):
                            os.makedirs(outdir)

                        outpath = "{}/{}_{}_{}_{}_{}_{}_{}.txt".format(outdir, year, model, mass, data, args.channel, disc1, disc2)

                        print("Writing data card to {}".format(outpath))

                        # determine if the injected signal model and mass should be the same
                        # as the signal component used in the fit, or some other component
                        if "_" in args.injectedSignal:
                            injectedModel = args.injectedSignal.split("_")[0]
                            injectedMass = args.injectedSignal.split("_")[1]
                        else:
                            injectedModel = Model
                            injectedMass  = mass

                        #injectedModel = Model
                        #injectedMass  = mass

                        #if args.injectedSignal != "SAME":
                        #    injectedModel = args.model.split("_")[0] + "_2t6j"

                        #    if(args.model.find("SYY") != -1):
                        #        injectedModel = "Stealth" + injectedModel 

                        #    injectedMass = args.injectedSignal.split('_')[1]
        
                        # Must make copy of dictionary to do repeated string replacements in for loop key
                        tempObs = copy.copy(configfile.observed)
                        tempSys = copy.copy(configfile.systematics)
                        tempMinNjet = copy.copy(configfile.obs_start)
                        tempMaxNjet = copy.copy(configfile.obs_end)
                        tempSpecial = copy.copy(configfile.special)

                        # Construct DataCardProducer class instance, which automatically calls member functions for writing out datacards
                        dataCardMaker(args.inpath, tempObs, outpath, tempSys, data, args.channel, year, args.NoMCcorr, tempMinNjet, tempMaxNjet, Model, str(mass), injectedModel, str(injectedMass), args.injectIntoData, tempSpecial, disc1, disc2, args.minNjet, args.maxNjet, args.scaleSyst, None, args.CloseSys)
    else:
        # loop over to make the cards
        for model in args.model:

            for mass in masses:

                for data in args.dataType:

                    year = args.year
                
                    fixedCloseSysStr = ""
                    if args.fixedCloseSys is not None:
                        fixedCloseSysStr = "_{}".format(args.fixedCloseSys)
                    # combine 0l, 1l, 2l cards as "combo" card
                    if args.combo:

                        comboStr = ""
                        for channel in args.combo:
                            comboStr += "CH{5}={4}/{0}_{1}_{2}_{3}_{5}{6}.txt ".format(year, model, mass, data, outdir, channel, fixedCloseSysStr)
                        comboStr += "> {4}/{0}_{1}_{2}_{3}_combo{5}.txt".format(year, model, mass, data, outdir, fixedCloseSysStr)
                        
                        print("combineCards.py {}".format(comboStr))
                        os.system("combineCards.py {0}".format(comboStr))
                    
                    else:
                        Model = model + "_2t6j"
                            

                        if not os.path.isdir(outdir):
                            os.makedirs(outdir)

                        outpath = "{}/{}_{}_{}_{}_{}{}.txt".format(outdir, year, model, mass, data, args.channel, fixedCloseSysStr)

                        print("Writing data card to {}".format(outpath))

                        # determine if the injected signal model and mass should be the same
                        # as the signal component used in the fit, or some other component
                        if "_" in args.injectedSignal:
                            injectedModel = args.injectedSignal.split("_")[0]
                            injectedMass = args.injectedSignal.split("_")[1]
                        else:
                            injectedModel = Model
                            injectedMass  = mass

                        #injectedModel = Model
                        #injectedMass  = mass

                        #if args.injectedSignal != "SAME":
                        #    injectedModel = args.model.split("_")[0] + "_2t6j"

                        #    if(args.model.find("SYY") != -1):
                        #        injectedModel = "Stealth" + injectedModel 

                        #    injectedMass = args.injectedSignal.split('_')[1]
        
                        # Must make copy of dictionary to do repeated string replacements in for loop key
                        tempObs = copy.copy(configfile.observed)
                        tempSys = copy.copy(configfile.systematics)
                        tempMinNjet = copy.copy(configfile.obs_start)
                        tempMaxNjet = copy.copy(configfile.obs_end)
                        tempSpecial = copy.copy(configfile.special)

                        # Construct DataCardProducer class instance, which automatically calls member functions for writing out datacards
                        dataCardMaker(args.inpath, tempObs, outpath, tempSys, data, args.channel, year, args.NoMCcorr, tempMinNjet, tempMaxNjet, Model, str(mass), injectedModel, str(injectedMass), args.injectIntoData, tempSpecial, None, None, args.minNjet, args.maxNjet, args.scaleSyst, args.fixedCloseSys, args.CloseSys)

if __name__ == "__main__":
    main()
