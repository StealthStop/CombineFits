from dataCardProducer import dataCardMaker as dcm
from optparse import OptionParser
import importlib

def main():
    parser = OptionParser()
    parser.add_option("-c", "--config",   action="store",  type="string",   dest="config", default = "None", help = "Config file for the data card [REQUIRED].")
    parser.add_option("-o", "--output",   action="store",  type="string",   dest="outpath", default = "datacard.txt", help = "Output path for data card")
    parser.add_option("-t", "--dataType", dest="dataType", type='string',   default = 'data', help="Specify if running over data or pseudo data")
    parser.add_option("-a", "--ABCD",     action="store_true", dest="ABCD", default=False, help = "Switch to make card for ABCD method in Combine")
    (options, args) = parser.parse_args()
    if options.config == "None":
        parser.error('Config file not given, specify with -c')
    else:
        configfile = importlib.import_module(options.config)

        print("Writing data card to "+options.outpath)
        dcm(configfile.path, configfile.signal, configfile.observed, configfile.histos, configfile.lumi, options.outpath, configfile.othersys, options.ABCD, options.dataType)

if __name__ == "__main__":
    main()
