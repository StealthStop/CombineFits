from dataCardProducer import dataCardMaker as dcm
from optparse import OptionParser
import importlib

def main():
    parser = OptionParser()
    parser.add_option("-c", "--config", action="store", type="string", dest="config", default = "None", help = "Config file for the data card [REQUIRED].")
    parser.add_option("-o", "--output", action="store", type="string", dest="outpath", default = "datacard.txt", help = "Output path for data card")
    (options, args) = parser.parse_args()
    if options.config == "None":
        parser.error('Config file not given, specify with -c')
    else:
        configfile = importlib.import_module(options.config)
        print("Writing data card to "+options.outpath)
        dcm(configfile.path, configfile.signal, configfile.background, configfile.histos, configfile.lumi, options.outpath, configfile.othersys)


if __name__ == "__main__":
    main()
