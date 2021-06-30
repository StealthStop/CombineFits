from dataCardProducer import dataCardMaker as dcm
from optparse import OptionParser
import importlib
import os

def main():
    parser = OptionParser()
    parser.add_option("-c", "--config",   action="store",  type="string",   dest="config", default = "None", help = "Config file for the data card [REQUIRED].")
    parser.add_option("-o", "--output",   action="store",  type="string",   dest="outpath", default = "datacard.txt", help = "Output path for data card")
    parser.add_option("-t", "--dataType", dest="dataType", type='string',   default = 'data', help="Specify if running over data or pseudo data")
    parser.add_option("--all", dest="all", action="store_true",   default = False, help="Make all data cards (all signal models, PseudoData w/ and w/o Signal injected, 0l and 1l)")
    parser.add_option("--setClosure", dest="setClosure", action="store_true",   default = False, help="Set perfect closure for datacards in the A region")
    parser.add_option("-a", "--ABCD",     action="store_true", dest="ABCD", default=False, help = "Switch to make card for ABCD method in Combine")
    parser.add_option("-s", "--signal",     action="store", type='string', dest="signal", default="RPV_550", help = "Name of signal and mass for card separated by \'_\' (e.g. RPV_550)")
    parser.add_option("-l", "--leptons", action="store", type="string", dest="leptons", default="None", help = "Number of leptons in final state (0 or 1)")
    parser.add_option("-p", "--path",     action="store", type='string', dest="path", default=".", help = "Path to root files")
    (options, args) = parser.parse_args()
    
    if "8Jet" in options.config:
        min_nj = 8
    else:
        min_nj = 7
    max_nj = 12
    
    if options.config == "None":
        parser.error('Config file not given, specify with -c')
    elif options.all:
        if options.path == ".":
            parser.error('Input path not given, specify with -p')
        configfile = importlib.import_module(options.config)
 
        signals = ["RPV", "StealthSYY"]
        masses = [x for x in range(300, 1450, 50)]
        dataTypes = ["pseudoData", "pseudoDataS"]       
        leptons = ["0l", "1l", "combo"]
        close = ""
        if options.setClosure:
            close = "_perfectClose"

        for s in signals:
            for m in masses:
                for d in dataTypes:
                    for l in leptons:
                        year = configfile.year
                        if l == "combo":
                            os.system("combineCards.py HADRONIC=cards/{0}_{1}_{2}_{3}_0l{4}.txt SEMILEPTONIC=cards/{0}_{1}_{2}_{3}_1l{4}.txt > cards/{0}_{1}_{2}_{3}_combo{4}.txt".format(year, s, m, d, close))
                        else:
                            model = s + "_2t6j"

                            signal = {
                                "%s_%s" % (s, m) : {
                                    "path" : "%s_%s_mStop-%s.root" % (year, model, m),
                                    "sys"  : "1.05"
                                }
                            }
                            
                            outpath = "cards/{}_{}_{}_{}_{}{}.txt".format(year, s, m, d, l, close)

                            print("Writing data card to {}".format(outpath))
                            dcm(options.path, signal, configfile.observed, configfile.histos, configfile.lumi, outpath, configfile.othersys, options.ABCD, d, "_" + l, year, options.setClosure, min_nj, max_nj)
                        
    elif options.leptons == "None":
        parser.error('Please specify number of final state leptons with -l')
    else:
        configfile = importlib.import_module(options.config)
       
        if(options.signal.find("SYY") != -1):
            model = "Stealth" + options.signal.split("_")[0] + "_2t6j"    
        elif options.signal.find("RPV") != -1:
            model = options.signal.split('_')[0] + "_2t6j"


        mass = options.signal.split('_')[1]
        year = configfile.year

        signal = {
            "%s" % (options.signal) : {
                "path" : "%s_%s_mStop-%s.root" % (year, model, mass),
                "sys"  : "1.05"
            }
        }

        print("Writing data card to "+options.outpath)
        dcm(options.path, signal, configfile.observed, configfile.histos, configfile.lumi, options.outpath, configfile.othersys, options.ABCD, options.dataType, "_" + options.leptons + "l", year, options.setClosure, min_nj, max_nj)

if __name__ == "__main__":
    main()
