import ROOT
from ROOT import TFile, gROOT, gStyle
import numpy as np
import math
from optparse import OptionParser
import root_numpy as rnp
import glob
import os

parser = OptionParser()
parser.add_option("-s", "--signal", action="store", type="string", dest="signalName",
    default="all", help="Name of signal root file to use as input (Use all to produce all data cards)")
parser.add_option("-H", "--histogram", action="store", type="string", dest="histoName",
    default="all", help="Name of histogram to make data card (Use all to produce all histograms)")
parser.add_option("-n", "--numBin", action="store", type="int", dest="numBin",
     default="5", help="Desired number of bins (results in n^2 bins)")

(options, args) = parser.parse_args()

datasets = {
    "RPV350" ,
    "RPV550" ,
    "RPV850" ,
    "SYY350" ,
    "SYY550" ,
    "SYY850" ,
    "SHH350" ,
    "SHH550" ,
    "SHH850" ,
}

histos = {
    #Stop1 vs Stop2 Mass
    "h_Mass_stop1vsstop2_PtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,
    "h_Mass_stop1vsstop2_MassRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,
    "h_Mass_stop1vsstop2_ScalarPtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" , 
    
    #Diff vs Avg
    "h_stopMasses_diffVSavg_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,

    # stops MassVsPt
    "h_stop1_MassVsPt_PtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,
    "h_stop2_MassVsPt_PtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,
    "h_stop1_MassVsPt_MassRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,
    "h_stop2_MassVsPt_MassRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,
    "h_stop1_MassVsPt_ScalarPtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,
    "h_stop2_MassVsPt_ScalarPtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,
    "h_stop1_MassVsScalarPt_ScalarPtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,
    "h_stop2_MassVsScalarPt_ScalarPtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets" ,
}


histoNames = {
    #Stop1 vs Stop2 Mass
    "h_Mass_stop1vsstop2_PtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"             : "stop12_Pt",
    "h_Mass_stop1vsstop2_MassRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"           : "stop12_Mass",
    "h_Mass_stop1vsstop2_ScalarPtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"       : "stop12_SPt", 
    
    #Diff vs Avg
    "h_stopMasses_diffVSavg_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"                 : "diffavg",

    # stops MassVsPt
    "h_stop1_MassVsPt_PtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"                : "m1vsPt_Pt",
    "h_stop2_MassVsPt_PtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"                : "m2vsPt_Pt",
    "h_stop1_MassVsPt_MassRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"              : "m1vsPt_Mass",
    "h_stop2_MassVsPt_MassRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"              : "m2vsPt_Mass",
    "h_stop1_MassVsPt_ScalarPtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"          : "m1vsPt_SPt",
    "h_stop2_MassVsPt_ScalarPtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"          : "m2vsPt_SPt",
    "h_stop1_MassVsScalarPt_ScalarPtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"    : "m1vsSPt_SPt",
    "h_stop2_MassVsScalarPt_ScalarPtRank_0l_HT500_ge2b_ge6j_ge2t_ge1dRbjets"    : "m2vsSPt_SPt",
}


def writeDataCard(binVals, dataset, histo):
    processNames = [options.signalName, "QCD", "TT"]

    with open("Cards/Card%s_%s.txt" % (dataset,histoNames[histo]), 'w') as f:
        f.write("Datacard for 2016 %s" % dataset)
        f.write( "\n" )
        f.write( "imax %d number of bins\n" % len(binVals[0]) )
        f.write( "jmax 2 number of processes minus 1\n" )
        f.write( "kmax 3 number of nuisance parameters\n" )
        f.write( "\n" )
        f.write( "-------------------------------------------------------------------------------------------------------------------------------------------\n" )
        f.write( "\n" )
        bins        = "bin         "
        observation = "observation "
        for i in range(len(binVals[0])):
            bins        += "D{0: <9}".format(i)
            observation += "{0: <10}".format(round((binVals[0][i]+binVals[1][i]+binVals[2][i]),1))
        f.write( bins+"\n" )
        f.write( observation+"\n" )
        f.write( "-------------------------------------------------------------------------------------------------------------------------------------------\n" )
        f.write( "# background rate taken from events in bin\n" )
        bins      = "bin              "
        process1 = "process          "
        process2 = "process          "
        rate     = "rate             "
        f.write( "" )
        for i in range(len(binVals[0])):
            for j in range(3):
                bins      += "{0: <16} ".format("D"+str(i))
                process1 += "{0: <16} ".format(processNames[j])
                process2 += "{0: <16} ".format(j)
                rate     += "{0: <16} ".format(binVals[j][i])
        f.write( bins+"\n" )
        f.write( process1+"\n" )
        f.write( process2+"\n" )
        f.write( rate+"\n" )
        f.write( "-------------------------------------------------------------------------------------------------------------------------------------------\n" )
        f.write( "# Normal uncertainties in the signal region\n" )
        lumiSys  = "lumi_13TeV      lnN  "
        ttbarSys = "ttbar_unc       lnN  "
        qcdSys   = "qcd_unc         lnN  "
        for i in range(len(binVals[0])):
            for j in range(3):
                if(j == 0):
                    lumiSys += "{0: <5} ".format("1.05")
                else:
                    lumiSys += "{0: <5} ".format("-")
                if(j == 1):
                    ttbarSys += "{0: <5}".format("1.20")
                else:
                    ttbarSys += "{0: <5} ".format("-")
                if(j == 2):
                    qcdSys += "{0: <5}".format("1.20")
                else:
                    qcdSys += "{0: <5} ".format("-")
        f.write( lumiSys+"\n" )
        f.write( ttbarSys+"\n" )
        f.write( qcdSys+"\n" )
        f.write( "-------------------------------------------------------------------------------------------------------------------------------------------\n" )

def getCard(dataset, histo):
    #gROOT.SetBatch(True)
    gStyle.SetOptStat(0)

    # Create list of histograms that we will need to pull data from
    flist = []
    hlist = []

    for f in glob.glob("/uscms/home/bcrossma/nobackup/SL7/CMSSW_10_2_9/src/RootWorkingArea/Hemisphere_Significance/TopSeed/*.root"):
        if(f.find(dataset) != -1):
            flist = [ROOT.TFile.Open(f)] + flist
        elif (f.find("TT") != -1 or f.find("QCD") != -1):
            flist.append(ROOT.TFile.Open(f))

    for f in flist:
        hlist.append(f.Get(histo))

    # Define array of bin boundaries
    binVals = [[],[],[]]
    binInt = 0
    i = 0

    binXSize = 1500 / hlist[0].GetNbinsX()
    binYSize = 1500 / hlist[0].GetNbinsY()

#    print "Bin Edges (prints bottom left corner of bins that are kept): "
    for x in range(0, hlist[0].GetNbinsX()-1, (hlist[0].GetNbinsX()/options.numBin)):
        for y in range(0, hlist[0].GetNbinsY()-1, (hlist[0].GetNbinsY()/options.numBin)):
            i = 0
            temp_binVals = []
            for h in hlist:
                binInt = h.Integral(x, x+10, y, y+10)
                if (round(binInt,1) < 0.1):
                    temp_binVals.append(0.1) #Used to correct any zero bins
                else:
                    temp_binVals.append(round(binInt,1))
                i += 1
            j = 0
            for b in temp_binVals:
                if (len(temp_binVals) == len(flist)):
                    binVals[j].append(b)
                j += 1
    
    writeDataCard(binVals, dataset, histo)

def main():
    if not os.path.exists("Cards"):
        os.mkdir("Cards")

    if(options.signalName == "all"):
        for d in datasets:
            print "Making data cards for signal model %s" % d
            if (d == "TT" or d == "QCD"):
                break
            if(options.histoName == "all"):
                for h in histos:
                    getCard(d,h)
            else:
                getCard(d,options.histoName)

    else:
        if(options.histoName == "all"):
            for h in histos:
                getCard(options.signalName,h)
        else:
            getCard(options.signalName,options.histoName)

if __name__ == "__main__":
    main()

