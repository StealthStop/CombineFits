import argparse
parser = argparse.ArgumentParser(description='List of options', add_help=True)
parser.add_argument("-c", "--config", action="store", dest="config", default="cardConfigGoodClose", help="Name of config file for data card production [REQUIRED]")
parser.add_argument("-i", "--input", action="store", dest="inroot", default="2016_DisCo/", help="Path to input root files for data card [REQUIRED]")
parser.add_argument("-m", "--method", action="store", dest="method", default="pseudoData", help="Fit type (e.g. pseudoData or pseudoDataS [REQUIRED]")
parser.add_argument("-y", "--year", action="store", dest="year", default="2016", help="Year for data used")
parser.add_option("-l", "--leptons", action="store", type="string", dest="leptons", default="None", help = "Number of leptons in final state (0 or 1)")
parser.add_argument("-s", "--signal", action="store", dest="signal", default="SYY_550", help="Name of signal model separated by an underscore (e.g. RPV_550) [REQUIRED]")
parser.add_argument("--bonly", action="store_true", dest="bonly", default=False, help="Carry out background only fit")
parser.add_argument("--sb", action="store_true", dest="sb", default=False, help="Carry out signal + background fit")
parser.add_argument("--toys", action="store_true", dest="toys", default=False, help="Throw toys for testing fit")
parser.add_argument("--all", action="store_true", dest="All", default=False, help="Run all fits")
parser.add_argument("--cards", action="store_true", dest="cards", default=False, help="Only make datacards (don't run fits)")
parser.add_argument("--test", action="store_true", dest="test", default=False, help="Run combine with test cards")
args = parser.parse_args()

from dataCardProducer import dataCardMaker as dcm
from make_fit_plots import make_fit_plots

import importlib
import os
import ROOT
from math import sqrt

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

test_list = [pseudoData_bonly, pseudoData_sb, pseudoDataS_bonly, pseudoDataS_sb]

def getObs(card):
    with open(card, "r") as f:
        lines = f.readlines()

        data_temp = []

        for l in lines:
            if l.find("observation") != -1:
                data_temp = l.split(" ")[1:-1]

        data = {'A': [], 'B': [], 'C': [], 'D': []}
        ABCD = ['A','B','C','D']
        
        for j in range(0,5):
            i = 0
            for reg in ABCD:
                data[reg].append((7+j,float(data_temp[j*4+i]), sqrt(float(data_temp[i*4+j]))))

                i += 1

        return data

def getSignal(signal_str):
    if signal_str.find("SYY") != -1:
        model = "Stealth" +  signal_str.split("_")[0] + "_2t6j"
    elif signal_str.find("RPV") != -1:
        model = signal_str.split('_')[0] + "_2t6j"
    
    if signal_str.find("_") != -1:
        mass = signal_str.split("_")[1]
    
        signal = {
                "%s" % (signal_str) : {
                    "path" : "2016_%s_mStop-%s.root" % (model, mass),
                    "sys"  : "--"
                }
            }
        
        return [signal, mass]
    else:
        signals = []
        for m in range(300, 1450, 50):
            signal = {
                    "%s_%s" % (signal_str, m) : {
                        "path" : "2016_%s_mStop-%s.root" % (model, m),
                        "sys"  : "--"
                    }
                }
            signals.append([signal, m])
        return signals

def makeDataCard(card_cfg, signal, fit_cfg):
    if args.test:
        cardPath = "cards/pseudoDataS_test_10x.txt"
    else:
        if signal.keys()[0].find("SHH") != -1 or signal.keys()[0].find("SYY") != -1:
            cardPath = args.year + "_Stealth" + signal.keys()[0] + "_" + fit_cfg["dataType"] + ".txt"
        else:
            cardPath = args.year + "_" + signal.keys()[0] + "_" + fit_cfg["dataType"] + ".txt"
            
    print("Writing data card to {}".format(cardPath))
    if not args.test:
        dcm(args.inroot, signal, card_cfg.observed, card_cfg.histos, card_cfg.lumi, cardPath, card_cfg.othersys, True, fit_cfg["dataType"], "_" + options.leptons + "l")

    data = getObs(cardPath)
    
    print("Converting data card to input workspace")
    wsPath = "ws_" + cardPath[:-4] + ".root"
    os.system('text2workspace.py {} -o {}'.format(cardPath, wsPath))

    os.system("mv {} ./prefit".format(wsPath))
    os.system("mv {} ./cards".format(cardPath))
    
    return cardPath, wsPath, data

def runFitDiagnostics(cardPath, wsPath, data, signal, mass, fit_cfg):
    print("Getting fit diagnostics for fit type {}".format(fit_cfg["name"]))   
    if fit_cfg["toys"]:
        ntoys = 10
        os.system('combine -M FitDiagnostics -d {} -m {} -t {} --forceRecreateNLL --saveWorkspace --saveToys --toysNoSystematics'.format(fit_cfg["cardWS"], mass, ntoys))
        print("Collecting fits and plotting")
        #os.system('hadd {} fitDiagnostics.root higgsCombineTest.FitDiagnostics.mH{}.123456.root'.format(fit_cfg["outroot"],mass))
        

    else:
        if args.test:
            os.system('combine -M FitDiagnostics -d cards/pseudoDataS_test_10x.txt -m {} --rMin -1 --forceRecreateNLL --saveWorkspace --saveShapes --saveWithUncertainties'.format(mass))
        else:
            os.system('combine -M FitDiagnostics -d cards/{} -m {} --rMin -1 --forceRecreateNLL --saveWorkspace --saveShapes --saveWithUncertainties -n {}{}{}{}'.format(cardPath, mass, args.year, signal.keys()[0][:3], mass, fit_cfg["dataType"]))

        print("Collecting fits and plotting")
        #os.system('hadd {} fitDiagnostics.root higgsCombineTest.FitDiagnostics.mH{}.root'.format(fit_cfg["outroot"], mass))

        if args.test:
            make_fit_plots(signal.keys()[0], args.year, "cards/pseudoDataS_test_10x.root", "fitDiagnostics.root", True, True, True, True, "pseudoDataS_test_10x", "resultsPseudoDataS_test_10x.root", data)
        else:
            make_fit_plots(signal.keys()[0], args.year, "prefit/" + wsPath, "fitDiagnostics{}{}{}{}.root".format(args.year, signal.keys()[0][:3], mass, fit_cfg["dataType"]), fit_cfg["plotb"], fit_cfg["plotsb"], fit_cfg["plotdata"], fit_cfg["plotsig"], fit_cfg["name"], args.year + "_" + signal.keys()[0] + "_" + fit_cfg["outroot"], data)

        print("Plot saved as image {}.png".format(cardPath[:-4]))
    
    #clean up directory
    if not os.path.exists("figures"):
        os.makedirs("figures")

    if not os.path.exists("prefit"):
        os.makedirs("prefit")

    if not os.path.exists("cards"):
        os.makedirs("cards")

    if not os.path.exists("results"):
        os.makedirs("results")

    os.system("mv {}_{}_{}*.png ./figures".format(args.year, signal.keys()[0], fit_cfg["name"])) 
    os.system("mv *resultsPseudoData*.root ./results")
    os.system("mv fitDiagnostics{}*{}*.root ./results".format(args.year, mass))   
    os.system("mv higgsCombine*FitDiagnostics*.root ./results")   
 
def main():

    #Identify fit type from command line args
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
   
    os.system('rm ./results/{}'.format(fit_cfg["outroot"]))
 
    #Load config file with fit information
    if args.config == "None":
        parser.error('Config file for data card not given, specify with -c')
    else:
        card_cfg = importlib.import_module(args.config)

    #Parse signal from command line args and setup for data card
    sig_list = getSignal(args.signal)

    #Make data card(s) for the signal model chosen
    if len(sig_list) == 2:
        cardPath, wsPath, data = makeDataCard(card_cfg, sig_list[0], fit_cfg)
        if not args.cards:
            runFitDiagnostics(cardPath, wsPath, data, sig_list[0], sig_list[1], fit_cfg)
    else:
        for s in sig_list:
            print("Running Fit Dianostics for {}".format(s[0].keys()[0]))
            cardPath, wsPath, data = makeDataCard(card_cfg, s[0], fit_cfg)
        if not args.cards:
            runFitDiagnostics(cardPath, wsPath, data, s[0], s[1], fit_cfg)

    print("Fit complete")

if __name__ == "__main__":
    main()
