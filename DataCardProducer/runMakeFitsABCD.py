import argparse
parser = argparse.ArgumentParser(description='List of options', add_help=True)
parser.add_argument("-c", "--config", action="store", dest="config", default="cardConfigGoodClose", help="Name of config file for data card production [REQUIRED]")
parser.add_argument("-i", "--input", action="store", dest="inroot", default="2016_DisCo/", help="Path to input root files for data card [REQUIRED]")
parser.add_argument("-m", "--method", action="store", dest="method", default="pseudoData", help="Fit type (e.g. pseudoData or pseudoDataS [REQUIRED]")
parser.add_argument("-s", "--signal", action="store", dest="signal", default="SYY_550", help="Name of signal model separated by an underscore (e.g. RPV_550) [REQUIRED]")
parser.add_argument("--bonly", action="store_true", dest="bonly", default=False, help="Carry out background only fit")
parser.add_argument("--sb", action="store_true", dest="sb", default=False, help="Carry out signal + background fit")
parser.add_argument("--toys", action="store_true", dest="toys", default=False, help="Throw toys for testing fit")
parser.add_argument("--all", action="store_true", dest="All", default=False, help="Run all fits")

args = parser.parse_args()


from dataCardProducer import dataCardMaker as dcm
from make_fit_plots import make_fit_plots

import importlib
import os
import ROOT

ROOT.gStyle.SetOptStat(0)
ROOT.TH1.AddDirectory(False)
ROOT.TH1.SetDefaultSumw2(1)
    
#Information that is needed for any type of fit

pseudoData_bonly = {
    "name"      :   "pseudoData_bonly",
    "outroot"   :   "resultsPseudoData_bonly.root",
    "cardWS"    :   "pseudoData_bonly.root",
    "dataType"  :   "pseudoData",
    "toys"      :   False,
    "plotb"     :   True,
    "plotsb"    :   False,
    "plotdata"  :   True,
    "plotsig"   :   False,
    "suf"       :   "_bonly",
}

pseudoData_sb = {
    "name"      :   "pseudoData_sb",
    "outroot"   :   "resultsPseudoData_sb.root",
    "cardWS"    :   "pseudoData_sb.root",
    "dataType"  :   "pseudoData",
    "toys"      :   False,
    "plotb"     :   True,
    "plotsb"    :   True,
    "plotdata"  :   True,
    "plotsig"   :   True,
    "suf"       :   "_sb",
}

pseudoDataS_bonly = {
    "name"      :   "pseudoDataS_bonly",
    "outroot"   :   "resultsPseudoData_sb.root",
    "cardWS"    :   "pseudoDataS_bonly.root",
    "dataType"  :   "pseudoDataS",
    "toys"      :   False,
    "plotb"     :   True,
    "plotsb"    :   False,
    "plotdata"  :   True,
    "plotsig"   :   False,
    "suf"       :   "_bonly",
}

pseudoDataS_sb = {
    "name"      :   "pseudoDataS_sb",
    "outroot"   :   "resultsPseudoData_sb.root",
    "cardWS"    :   "pseudoDataS_sb.root",
    "dataType"  :   "pseudoDataS",
    "toys"      :   False,
    "plotb"     :   True,
    "plotsb"    :   True,
    "plotdata"  :   True,
    "plotsig"   :   True,
    "suf"       :   "_sb",
}

pseudoData_toys = {
    "name"      :   "pseudoData_toys",
    "outroot"   :   "resultsPseudoData_toys.root",
    "cardWS"    :   "pseudoData_toys.root",
    "dataType"  :   "pseudoData",
    "toys"      :   True,
    "plotb"     :   True,
    "plotsb"    :   False,
    "plotdata"  :   True,
    "plotsig"   :   False,
    "suf"       :   "_toys",
}

pseudoDataS_toys = {
    "name"      :   "pseudoData_toys",
    "outroot"   :   "resultsPseudoDataS_toys.root",
    "cardWS"    :   "pseudoDataS_toys.root",
    "dataType"  :   "pseudoDataS",
    "toys"      :   True,
    "plotb"     :   True,
    "plotsb"    :   True,
    "plotdata"  :   True,
    "plotsig"   :   True,
    "suf"       :   "_toys",
}

test_list = [pseudoData_bonly, pseudoData_sb, pseudoDataS_bonly, pseudoDataS_sb, pseudoData_toys, pseudoDataS_toys]

def main():
    
    fit_string = args.method

    if args.bonly:
        fit_string += "_bonly"
    
    if args.sb:
        fit_string += "_sb"

    if args.toys:
        fit_string += "_toys"
    
    if args.All:
        fit_string = "all"

    fit_cfg = [f for f in test_list if f["name"] == fit_string][0]
   
    os.system('rm {}'.format(fit_cfg["outroot"]))
 
    if args.config == "None":
        parser.error('Config file for data card not given, specify with -c')
    else:
        card_cfg = importlib.import_module(args.config)

    if(args.signal.find("SYY") != -1 or args.signal.find("RPV") != -1):
        model = "Stealth" +  args.signal.split("_")[0] + "_2t6j"
    else:
        model = args.signal.split('_')[0] + "_2t4b"

    
    mass = args.signal.split("_")[1]
    
    signal = {
            "%s" % (args.signal) : {
                "path" : "2016_%s_mStop-%s.root" % (model, mass),
                "sys"  : "--"
            }
        }

    cardPath = fit_cfg["name"] + ".txt"

    print("Writing data card to {}".format(cardPath))
    dcm(args.inroot, signal, card_cfg.observed, card_cfg.histos, card_cfg.lumi, cardPath, card_cfg.othersys, True, fit_cfg["dataType"])
    
    print("Converting data card to input workspace")
    os.system('text2workspace.py {}'.format(cardPath))

    if fit_cfg["name"].find("bonly") != -1:
        ES = 0
    else:
        ES = 1

    print("Getting fit diagnostics for fit type {}".format(fit_cfg["name"]))   
    if fit_cfg["toys"]:
        ntoys = 10
        os.system('combine -M FitDiagnostics -d {} -m {} --expectSignal={} -t {} --forceRecreateNLL --saveWorkspace --saveToys --toysNoSystematics'.format(fit_cfg["cardWS"], mass, ES, ntoys))
        print("Collecting fits and plotting")
        os.system('hadd {} fitDiagnostics.root higgsCombineTest.FitDiagnostics.mH{}.123456.root'.format(fit_cfg["outroot"],mass,  ))
        

    else:
        os.system('combine -M FitDiagnostics -d {} -m {} --expectSignal={} -t -1 --forceRecreateNLL --saveWorkspace'.format(fit_cfg["cardWS"], mass, ES))

        print("Collecting fits and plotting")
        os.system('hadd {} fitDiagnostics.root higgsCombineTest.FitDiagnostics.mH{}.root'.format(fit_cfg["outroot"], mass))

        make_fit_plots(fit_cfg["cardWS"], args.signal, fit_cfg["cardWS"], "higgsCombineTest.FitDiagnostics.mH{}.root".format(mass), "fitDiagnostics.root", fit_cfg["plotb"], fit_cfg["plotsb"], fit_cfg["plotdata"],fit_cfg["plotsig"], fit_cfg["name"], fit_cfg["outroot"])

        print("Plot saved as image {}.png".format(fit_cfg["name"]))
    
        #clean up directory
        if not os.path.exists("figures"):
            os.makedirs("figures")

        if not os.path.exists("prefit"):
            os.makedirs("prefit")

        if not os.path.exists("cards"):
            os.makedirs("cards")

        if not os.path.exists("results"):
            os.makedirs("results")

        os.system("mv pseudoData*.png ./figures") 
        os.system("mv pseudoData*.root ./prefit")
        os.system("mv pseudoData*.txt ./cards")
        os.system("mv resultsPseudoData*.root ./results")

    print("Fit complete")

if __name__ == "__main__":
    main()
