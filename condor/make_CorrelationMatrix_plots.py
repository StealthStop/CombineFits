import ROOT
import math
import os
from math import sqrt
from optparse import OptionParser
from collections import OrderedDict

parser = OptionParser()
parser.add_option("-s", "--signal",   action="store", type="string", dest="signal",     default="StealthSYY",         help="Signal process name"                                                               )
parser.add_option("-y", "--year",     action="store", type="string", dest="year",       default="Run2UL",             help="Year for data used"                                                                )
parser.add_option("-m", "--mass",     action="store", type="string", dest="mass",       default="400",                help="Mass of stop in GeV"                                                               )
parser.add_option("-d", "--dataType", action="store", type="string", dest="dataType",   default="Data",               help="type of data being fit"                                                               )
parser.add_option("--channel",        action="store", type="string", dest="channel",    default="0l",                 help="Suffix to specify number of final state leptons (0l, 1l, or combo)"                )
parser.add_option("-p", "--path",     action="store", type="string", dest="path",       default="../condor/Fit_2016", help="Path to Fit Diagnostics input condor directory"                                    )
parser.add_option('--asimov',         action="store_true",           dest='asimov',     default=False,                help = 'Is plot w/wo asimov style'       )

(options, args) = parser.parse_args()

ROOT.TH1.AddDirectory(False)
ROOT.TH1.SetDefaultSumw2(1)
ROOT.TH2.SetDefaultSumw2()
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetEndErrorSize(0)
ROOT.gStyle.SetFrameLineWidth(1)
ROOT.gStyle.SetLineScalePS(2)
ROOT.gROOT.ForceStyle()

def reformat(histo, channel, fit):

    niceNames = {
        "lumi"                 : "Lumi NP",
        "CorrectedDataClosure" : "Res. Non-Closure NP A",
        "Other"                : "Other Bkg xsec NP",
        "QCD_TF_%s"%(channel)  : "QCD TF (%s) NP"%(channel),
        "TTX"                  : "TTX Bkg xsec NP",
        "btg"                  : "b tagging NP",
        "ttg"                  : "top tagging NP",
        "fsr"                  : "FSR NP",
        "isr"                  : "ISR NP",
        "lep"                  : "Lepton NP",
        "pdf"                  : "PDF NP",
        "prf"                  : "Prefiring NP",
        "jet"                  : "Jet Trig NP",
        "pu"                   : "Pileup NP",
        "scl"                  : "Scale NP",
        "JEC"                  : "JES NP",
        "JER"                  : "JER NP",
    }

    if histo == None:
        return None

    njetsList = ["6", "7", "8", "9", "10", "11", "12"]
    if channel == "0l":
        njetsList = njetsList[2:]
    elif channel == "1l":
        njetsList = njetsList[1:-1]
    elif channel == "2l":
        njetsList = njetsList[0:-2]

    xBins = range(1, histo.GetNbinsX()+1)
    yBins = range(1, histo.GetNbinsY()+1)

    rawLabels = []; correlations = []
    for xBin in xBins:
        xLabel = histo.GetXaxis().GetBinLabel(xBin)
        if "Stat" not in xLabel and ("np" in xLabel or "beta" in xLabel or "gamma" in xLabel or "delta" in xLabel or xLabel == "r"):
            for yBin in yBins:
                yLabel = histo.GetYaxis().GetBinLabel(yBin)
                if "Stat" not in yLabel and ("np" in yLabel or "beta" in yLabel or "gamma" in yLabel or "delta" in yLabel or yLabel == "r"):
                    correlations.append(histo.GetBinContent(xBin, yBin))
                    rawLabels.append(xLabel+yLabel)

    nGoodParams = int(round(len(rawLabels)**0.5))

    newHisto = ROOT.TH2F(histo.GetName() + "reformat%s"%(fit), "", nGoodParams, 0, nGoodParams, nGoodParams, 0, nGoodParams)
    newHisto.SetDirectory(0)

    orderedLabels = ["r"] + ["beta%s_%s"%(njets,channel) for njets in njetsList] + ["gamma%s_%s"%(njets,channel) for njets in njetsList] \
                          + ["delta%s_%s"%(njets,channel) for njets in njetsList] + ["CorrectedDataClosureA%s_%s"%(njets,channel) for njets in njetsList] \
                          + ["lumi", "Other", "TTX", "QCD_TF_%s"%(channel), "btg", "ttg", "fsr", "isr", "lep", "jet", "pdf", "prf", "pu", "scl", "JEC", "JER"]

    def getLabels(Label):
        theLabel = None
        theLabelRaw = Label
        if not any(name in Label for name in ["beta", "gamma", "delta"]):
            if Label == "r":
                theLabelRaw = "r"
                theLabel = "r"
            else:
                theLabelRaw = "np_" + Label

                if "Closure" in Label:
                    theLabel = niceNames[Label.split("A")[0]] + Label.split("A")[-1].split("_")[0]
                else:
                    theLabel = niceNames[Label]
        else:
            theLabel = "TT Rate " + Label.split("_")[0].replace("beta","B").replace("gamma","C").replace("delta","D")

        return theLabel, theLabelRaw

    ixLabel = 1
    for aLabel in orderedLabels:

        xLabel, xLabelRaw = getLabels(aLabel)
        if xLabelRaw+xLabelRaw not in rawLabels:
            continue

        newHisto.GetXaxis().SetBinLabel(ixLabel, xLabel)
            
        iyLabel = 1 
        for bLabel in orderedLabels:

            yLabel, yLabelRaw = getLabels(bLabel)
            if yLabelRaw+yLabelRaw not in rawLabels:
                continue

            newHisto.GetYaxis().SetBinLabel(iyLabel, yLabel)

            index = rawLabels.index(xLabelRaw+yLabelRaw)
            corr = correlations[index]
            newHisto.SetBinContent(ixLabel, iyLabel, corr)

            iyLabel += 1
        ixLabel += 1
            
    return newHisto

# -------------------
# get fit information
# -------------------
def getCorrelationMatrices(fitDiag_path, signal, year, channel, fitChannel, component = "NotCombo"):

    try:
        f_fit = ROOT.TFile.Open(fitDiag_path, "READ")
    except:
        print("Could not find file {}. Exiting.".format(fitDiag_path))

    covb = reformat(f_fit.Get("covariance_fit_b"), channel, "b")
    covs = reformat(f_fit.Get("covariance_fit_s"), channel, "s")

    covb.SetDirectory(0)
    covs.SetDirectory(0)

    f_fit.Close()

    return covb, covs

# -----------------
# draw lumi and CMS
# -----------------
def draw_LumiCMS(canvas, iPad, year, approved = False, wip = True):

    if iPad > 0 and iPad < 3:
        return

    canvas.cd()

    lumiText = ""
    if   year == "2016preVFP":
        lumiText = "19.5 fb^{-1}"
    elif year == "2016postVFP":
        lumiText = "16.8 fb^{-1}"
    elif year == "2016":
        lumiText = "36.3 fb^{-1}"
    elif year == "2017":
        lumiText = "41.5 fb^{-1}"
    elif year == "2018":
        lumiText = "59.8 fb^{-1}"
    elif year == "Run2UL":
        lumiText = "138 fb^{-1}"

    lumiText += " (13 TeV)"

    cmsTextSize = 1.0

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(ROOT.kBlack)

    # Text sizes and text offsets with respect to the top frame
    # in unit of the top margin size
    leftMargin   = canvas.GetLeftMargin()
    topMargin    = canvas.GetTopMargin()
    rightMargin  = canvas.GetRightMargin()
    bottomMargin = canvas.GetBottomMargin()

    # Text font/style in ROOT
    # https://root.cern.ch/doc/master/classTAttText.html#ATTTEXT5
    latex.SetTextFont(42)
    latex.SetTextAlign(31)
    latex.SetTextSize(0.7 * cmsTextSize * topMargin)

    if iPad == 3:
        latex.DrawLatex(1.0 - rightMargin, 1.0 - topMargin + 0.2 * topMargin, lumiText)

    textXposition = leftMargin
    textYposition = 1.0 - topMargin + 0.2 * topMargin

    # Text alignment in ROOT
    # https://root.cern.ch/doc/master/classTAttText.html#ATTTEXT1
    textAlignment = 11

    latex.SetTextFont(61)
    latex.SetTextSize(cmsTextSize * topMargin)
    latex.SetTextAlign(textAlignment)

    if iPad == 0:
        latex.DrawLatex(textXposition, textYposition, "CMS")

    # Label with "Prelimiary" if not approved and "work in progress" is WIP
    if not approved:

        latex.SetTextFont(52)
        latex.SetTextAlign(textAlignment)
        latex.SetTextSize(0.6 * cmsTextSize * topMargin)

        extraText = ""
        if not wip:
            extraText = "Preliminary"
        else:
            extraText = "Work in Progress"

        if iPad == 0:
            latex.DrawLatex(textXposition + 0.21, textYposition, extraText) 

# --------------
# make fit plots
# --------------
def make_CorrelationMatrix_plots(signal, year, fitDiag_path, channel, fitChannel, sigStr, asimovStr, outPath):

    LM = 0.25
    RM = 0.12
    BM = 0.25
    TM = 0.04

    covb, covs = getCorrelationMatrices(fitDiag_path, signal, year, channel, fitChannel)

    canvasb = ROOT.TCanvas("covb", "covb", 600, 600)
    canvasb.SetLeftMargin(LM)
    canvasb.SetRightMargin(RM)
    canvasb.SetTopMargin(TM)
    canvasb.SetBottomMargin(BM)

    canvasb.cd()

    covb.GetXaxis().LabelsOption("v")
    covb.GetZaxis().SetTitleSize(0)
    covb.GetZaxis().SetRangeUser(-1.0, 1.0)

    covb.SetTitle("")
    
    covb.Draw("COLZ")

    ROOT.gPad.Update()
    palette = covb.GetListOfFunctions().FindObject("palette")

    palette.SetX1NDC(1.0-RM+0.005)
    palette.SetX2NDC(1.0-RM+0.005+0.04)

    ROOT.gPad.Modified()
    ROOT.gPad.Update()

    canvasb.SaveAs("%s/CovarianceMatrixB_%s_%s.pdf"%(outPath,signal,channel))

    canvass = ROOT.TCanvas("covs", "covs", 600, 600)
    canvass.SetLeftMargin(LM)
    canvass.SetRightMargin(RM)
    canvass.SetTopMargin(TM)
    canvass.SetBottomMargin(BM)

    canvass.cd()

    covs.GetXaxis().LabelsOption("v")
    covs.GetZaxis().SetTitleSize(0)
    covs.GetZaxis().SetRangeUser(-1,1)

    covs.SetTitle("")

    covs.Draw("COLZ")

    ROOT.gPad.Update()
    palette = covs.GetListOfFunctions().FindObject("palette")

    palette.SetX1NDC(1.0-RM+0.005)
    palette.SetX2NDC(1.0-RM+0.005+0.04)

    canvass.SaveAs("%s/CovarianceMatrixS_%s_%s.pdf"%(outPath,signal,channel))

# -------------
# main function
# -------------
def main():   

    ROOT.gROOT.SetBatch(True)

    # ------------------------------------------------------
    # make fit plots for any model, mass, channel, data type
    # ------------------------------------------------------
    signal   = options.signal
    mass     = int(options.mass)
    dataType = options.dataType
    channel  = options.channel

    # For combo fit, need to get channel fits for all three channels
    fitChannels = [channel]
    if channel == "combo":
        fitChannels = ["0l", "1l", "2l"]

    sigStr = ""
    if "RPV" in signal:
        sigStr = "RPV"
    elif "SYY" in signal:
        sigStr = "SYY"

    sigStr += " m_{ #tilde{t}} = %d GeV"%(mass)

    asimovStr = ""
    if options.asimov:
        asimovStr = "_Asimov"
        if options.expSig != "None":
            asimovStr += "_%s"%(options.expSig)

    shortSig = signal[-3:]

    path    = "{}/output-files/{}_{}_{}".format(options.path, signal, mass, options.year)
    fitDiag = "fitDiagnostics{}{}{}{}_{}{}.root".format(options.year, signal, mass, dataType, channel, asimovStr)
    
    fitDiag_path = "{}/{}".format(path, fitDiag)
    signalName   = "{}_{}".format(signal, mass)
    
    outPath = "%s/corrMatrix_plots/"%(options.path)
    if not os.path.isdir(outPath):
        os.makedirs(outPath)
    
    print("Making correlation matrix for:")
    print("Year: {}\t Signal: {}\t Mass: {}\t Final State: {}\t Data Type: {}".format(options.year, signal, mass, channel, dataType))

    for fitChannel in fitChannels:
        make_CorrelationMatrix_plots(signalName, options.year, fitDiag_path, channel, fitChannel, sigStr, asimovStr, outPath)

if __name__ == '__main__':
    main()
