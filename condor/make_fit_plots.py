import ROOT
import copy
import time
import os
from math import sqrt
from ROOT import kRed, kBlue, kBlack, kCyan, kGreen
from optparse import OptionParser
from collections import OrderedDict

parser = OptionParser()
parser.add_option("-s", "--signal",   action="store", type="string", dest="signal",     default="StealthSYY",         help="Signal process name"                                                               )
parser.add_option("-y", "--year",     action="store", type="string", dest="year",       default="Run2UL",             help="Year for data used"                                                                )
parser.add_option("-m", "--mass",     action="store", type="string", dest="mass",       default="350",                help="Mass of stop in GeV"                                                               )
parser.add_option("-d", "--dataType", action="store", type="string", dest="dataType",   default="pseudoData",         help="Mass of stop in GeV"                                                               )
parser.add_option("--channel",        action="store", type="string", dest="channel",    default="0l",                 help="Suffix to specify number of final state leptons (0l, 1l, or combo)"                )
parser.add_option("-p", "--path",     action="store", type="string", dest="path",       default="../condor/Fit_2016", help="Path to Fit Diagnostics input condor directory"                                    )
parser.add_option("--setClosure",     action="store_true",           dest="setClosure", default=False,                help="Use fit files with perfect closure asserted"                                       )
parser.add_option("-n", "--njets",    action="store", type="string", dest="njets",      default="7-12",               help="Range of Njets bins to plot (separated by a dash)"                                 )
parser.add_option("--plotb",          action="store_true",           dest="plotb",      default=False,                help="Plot background only fit"                                                          )
parser.add_option("--plotsb",         action="store_true",           dest="plotsb",     default=False,                help="Plot signal plus background fit"                                                   )
parser.add_option("--plotsig",        action="store_true",           dest="plotsig",    default=False,                help="Plot signal component of fit"                                                      )
parser.add_option("--plotdata",       action="store_true",           dest="plotdata",   default=False,                help="Plot distributions observed in data"                                               )
parser.add_option("--all",            action="store_true",           dest="all",        default=False,                help="Make all pre and post fit distributions (for 0l and 1l, pseudoData/S, RPV and SYY)")

(options, args) = parser.parse_args()


ROOT.TH1.AddDirectory(False)
ROOT.TH1.SetDefaultSumw2(1)
ROOT.TH2.SetDefaultSumw2()
ROOT.gStyle.SetOptStat("")
ROOT.gStyle.SetPaintTextFormat("3.2f")
ROOT.gStyle.SetFrameLineWidth(3)
ROOT.gStyle.SetLineWidth(3)
ROOT.gROOT.ForceStyle()

if options.all:
    ROOT.gROOT.SetBatch(True)

borderSize   = 0.20
pad1and4Size = 1.0 + borderSize
pad2and3Size = 1.0
totalPadSize = 2 * pad1and4Size + 2 * pad2and3Size

# -------------------
# get fit information
# -------------------
def getFitInfo(fitDiag_path, pre_path, signal, year, channel, njets):

    f_fit = ROOT.TFile.Open(fitDiag_path, "READ")
    f_pre = ROOT.TFile.Open(pre_path)

    w = f_pre.Get("w")

    data      = {}; data_unc = {}
    prefit_sb = OrderedDict(); prefit_b = OrderedDict(); postfit_sb = OrderedDict(); postfit_b = OrderedDict(); postfit_sig = OrderedDict()

    regs =["A", "B", "C", "D"] 
    if channel == "combo":
        regs =["A0", "B0", "C0", "D0", "A1", "B1", "C1", "D1", "A2", "B2", "C2", "D2"] 
        njets = [8, 13]

    for reg in regs:
        prefit_sb[reg]   = []
        prefit_b[reg]    = []
        postfit_sb[reg]  = []
        postfit_b[reg]   = []
        postfit_sig[reg] = []       

        k = 0
        ch = ""
        channel_temp = channel
        reg_temp = reg
 
        if channel == "combo":
            k = int(reg[1:])
            ch = "CH{}l_".format(k)
            reg_temp = reg[:1]
            channel_temp = "{}l".format(k)

        data[reg] = []

        for i in range(njets[0]-k,njets[1]+1-k):
            try:
                postfit_sb[reg].append((i, 
                    f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/total".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinContent(1),
                    f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/total".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinError(1)
                    ))
                postfit_b[reg].append((i, 
                    f_fit.Get("shapes_fit_b/{}Y{}_{}{}_{}/total".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinContent(1),
                    f_fit.Get("shapes_fit_b/{}Y{}_{}{}_{}/total".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinError(1)
                    ))
                #prefit_sb[reg].append((i, w_pre.function("shapes_prefit/{}{}/".format(reg,i))))
                prefit_b[reg].append((i, 
                    f_fit.Get("shapes_prefit/{}Y{}_{}{}_{}/total".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinContent(1),
                    f_fit.Get("shapes_prefit/{}Y{}_{}{}_{}/total".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinError(1)
                    ))
                postfit_sig[reg].append((i, 
                    f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/total_signal".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinContent(1),
                    f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/total_signal".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinError(1)
                    ))
            except Exception as e:
                print("Fit for {}_{}_{} Failed".format(year, signal, channel))
                print(e)
                return
            data[reg].append((i, 
                f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/data".format(ch, year[-2:], reg_temp, i, channel_temp)).Eval(0.5),
                #f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/data".format(ch, year[-2:], reg_temp, i, channel_temp)).GetBinErrorLow(1),
                #f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/data".format(ch, year[-2:], reg_temp, i, channel_temp)).GetBinErrorHigh(1),
                ))

    f_fit.Close()
    f_pre.Close()

    return prefit_b, postfit_b, postfit_sb, postfit_sig, data

# ---------------
# make histograms
# ---------------
def makeHist(reg, bin_info, tag, njets, combo=False):

    k = 0
    if combo:
        k = int(reg[1:])

    h = ROOT.TH1D("Region{}{}".format(reg, tag), "Region {}".format(reg), njets[1]-njets[0] + 1, njets[0] - k, njets[1] + 1 - k)

    bins = bin_info[reg]

    for i in range(len(bins)):
        if type(bins[i][1]) != float:
            h.Fill(bins[i][0], bins[i][1])
        else:
            h.Fill(bins[i][0], bins[i][1])
        h.SetBinError(i, bins[i][2])

    return h

# -----------
# make canvas
# -----------
def makeCanvasAndPads(combo=False):

    topPadList = []
    ratioPadList = []

    if combo:
        c1 = ROOT.TCanvas("c1", "c1", 3600, 3000)
    
        for i in range(0,3):
            topPadList.append(ROOT.TPad("p1_A{}".format(i), "p1_A{}".format(i), 0, 0.666 - 0.333 * i + 0.333 * 2.5 / 9.0, 0.25, 1.0 - i * 0.333, ROOT.kWhite, 0, 0))
            ratioPadList.append(ROOT.TPad("p2_A{}".format(i), "p2_A{}".format(i), 0, 0.666 - 0.333 * i + 0.333 * 0.01, 0.25, 0.666 - 0.333 * i + 0.333 * 2.5 / 9.0, ROOT.kWhite, 0, 0))

            topPadList.append(ROOT.TPad("p1_B{}".format(i), "p1_B{}".format(i), 0.25, 0.666 - 0.333 * i + 0.333 * 2.5 / 9.0, 0.5, 1 - 0.333 * i, ROOT.kWhite, 0, 0))
            ratioPadList.append(ROOT.TPad("p2_B{}".format(i), "p2_B{}".format(i), 0.25, 0.666 - 0.333 * i + 0.333 * 0.01, 0.5, 0.666 - 0.333 * i + 0.333 * 2.5 / 9.0, ROOT.kWhite, 0, 0))

            topPadList.append(ROOT.TPad("p1_C{}".format(i), "p1_C{}".format(i), 0.5, 0.666 - 0.333 * i + 0.333 * 2.5 / 9.0, 0.75, 1 - 0.333 * i, ROOT.kWhite, 0, 0))
            ratioPadList.append(ROOT.TPad("p2_C{}".format(i), "p2_C{}".format(i), 0.5, 0.666 - 0.333 * i + 0.333 * 0.01,   0.75, 0.666 - 0.333 * i + 0.333 * 2.5 / 9.0, ROOT.kWhite, 0, 0))

            topPadList.append(ROOT.TPad("p1_D{}".format(i), "p1_D{}".format(i), 0.75, 0.666 - 0.333 * i + 0.333 * 2.5 / 9.0, 1.0, 1 - 0.333 * i, ROOT.kWhite, 0, 0))
            ratioPadList.append(ROOT.TPad("p2_D{}".format(i), "p2_D{}".format(i), 0.75, 0.666 - 0.333 * i + 0.333 * 0.01, 1.0, 0.666 - 0.333 * i + 0.333 * 2.5 / 9.0, ROOT.kWhite, 0, 0))

    else:
        c1 = ROOT.TCanvas("c1", "c1", 3600, 1000)
    
        topPadList.append(ROOT.TPad("p1_A", "p1_A", 0, 2.5 / 9.0, 0.25, 1.0, ROOT.kWhite, 0, 0))
        ratioPadList.append(ROOT.TPad("p2_A", "p2_A", 0, 0.05, 0.25, 2.5 / 9.0, ROOT.kWhite, 0, 0))

        topPadList.append(ROOT.TPad("p1_B", "p1_B", 0.25, 2.5 / 9.0, 0.5, 1.0, ROOT.kWhite, 0, 0))
        ratioPadList.append(ROOT.TPad("p2_B", "p2_B", 0.25, 0.05, 0.5, 2.5 / 9.0, ROOT.kWhite, 0, 0))

        topPadList.append(ROOT.TPad("p1_C", "p1_C", 0.5, 2.5 / 9.0, 0.75, 1.0, ROOT.kWhite, 0, 0))
        ratioPadList.append(ROOT.TPad("p2_C", "p2_C", 0.5, 0.05,   0.75, 2.5 / 9.0, ROOT.kWhite, 0, 0))

        topPadList.append(ROOT.TPad("p1_D", "p1_D", 0.75, 2.5 / 9.0, 1.0, 1.0, ROOT.kWhite, 0, 0))
        ratioPadList.append(ROOT.TPad("p2_D", "p2_D", 0.75, 0.05, 1.0, 2.5 / 9.0, ROOT.kWhite, 0, 0))

    return c1, topPadList, ratioPadList

# ---------------------
# format canvas and pad
# ---------------------
def formatCanvasAndPads( c1, topPadArray, ratioPadArray ):

    for iPad in range( len(topPadArray) ) :

        topPadArray[iPad].SetLogy()
        topPadArray[iPad].SetBottomMargin(0.01 )

        topPadArray[iPad].SetLeftMargin(0.11)
        topPadArray[iPad].SetRightMargin(0.04)
        topPadArray[iPad].SetTopMargin(0.06 * (8.0 / 6.5))
        ratioPadArray[iPad].SetLeftMargin(0.11)
        ratioPadArray[iPad].SetRightMargin(0.04)
        ratioPadArray[iPad].SetTopMargin(0.06 * (8.0 / 6.5))

        topPadArray[iPad].Draw()

        ratioPadArray[iPad].SetGridy(1)
        ratioPadArray[iPad].Draw()

    return c1, topPadArray, ratioPadArray

# ------------
# save to root
# ------------
def save_to_root(hlist, outfile):

    out = ROOT.TFile(outfile, 'UPDATE')    

    for h in hlist:
        h.Write()

    out.Close()

# -----------------
# draw lumi and CMS
# -----------------
def draw_LumiCMS(canvas, year, approved = False, wip = True):

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
    latex.SetTextSize(0.65 * topMargin)
    latex.DrawLatex(1.0 - rightMargin, 1.0 - topMargin + 0.2 * topMargin, lumiText)

    textXposition = leftMargin + 0.045 * (1.0 - leftMargin - rightMargin)
    textYposition = 1.0 - topMargin - 0.045 * (1 - topMargin - bottomMargin)

    # Text alignment in ROOT
    # https://root.cern.ch/doc/master/classTAttText.html#ATTTEXT1
    textAlignment = 13
    cmsTextSize = 0.8

    latex.SetTextFont(61)
    latex.SetTextSize(cmsTextSize * topMargin)
    latex.SetTextAlign(textAlignment)
    latex.DrawLatex(textXposition, textYposition, "CMS")

    # Label with "Prelimiary" if not approved and "work in progress" is WIP
    if not approved:

        latex.SetTextFont(52)
        latex.SetTextAlign(textAlignment)
        latex.SetTextSize(0.5 * cmsTextSize * topMargin)

        extraText = ""
        if not wip:
            extraText = "Preliminary"
        else:
            extraText = "Work in Progress"

        latex.DrawLatex(textXposition, textYposition - 1.2 * cmsTextSize * topMargin, extraText) 

# --------------
# make fit plots
# --------------
def make_fit_plots(signal, year, pre_path, fitDiag_path, channel, plotb, plotsb, plotdata, plotsig, fitName, outfile, obs, njets, path):
    
    close  = ""

    if pre_path.find("perfectClose") != -1:
        close += "_perfectClose"
    try: 
        pre_b, post_b, post_sb, post_sig, data = getFitInfo(fitDiag_path, pre_path, signal, year, channel, njets)
    except Exception as e:
        print("Fit for {}_{}_{} Failed".format(year, signal, channel))
        print(e)
        return

    hlist_data = []
    hlist_pre_b = []
    hlist_post_b = []
    hlist_post_sb = []
    hlist_post_sig = []

    regs = data.keys()

    for reg in regs:
        hlist_data.append(makeHist(    reg, obs,      "_data",        njets, channel == "combo") )
        hlist_pre_b.append(makeHist(   reg, pre_b,    "_pre_bonly",   njets, channel == "combo") )
        hlist_post_b.append(makeHist(  reg, post_b,   "_post_bonly",  njets, channel == "combo") )
        hlist_post_sb.append(makeHist( reg, post_sb,  "_post_sb",     njets, channel == "combo") )
        hlist_post_sig.append(makeHist(reg, post_sig, "_post_signal", njets, channel == "combo") )



    #save_to_root(hlist_data, outfile)
    #save_to_root(hlist_pre_b, outfile)
    #save_to_root(hlist_post_b, outfile)
    #save_to_root(hlist_post_sb, outfile)
    #save_to_root(hlist_post_sig, outfile)
 
    for i in range(len(hlist_pre_b)):
        hlist_post_b[i].SetLineColor(kBlue)
        hlist_post_b[i].SetFillColor(kBlue)
        hlist_post_b[i].SetFillStyle(3001)

        hlist_post_sb[i].SetLineColor(kRed)
        hlist_post_sb[i].SetFillColor(kRed)
        hlist_post_sb[i].SetFillStyle(3002)

        hlist_post_sig[i].SetLineColor(kGreen)

        hlist_data[i].SetLineColor(kBlack)
    
    hlist_ratio = []
    for i in range(len(hlist_pre_b)):
        if plotsb:
            h_temp = copy.copy(hlist_post_sb[i])
        else:
            h_temp = copy.copy(hlist_post_b[i])
        h_temp.Add(hlist_data[i], -1)
        for j in range(hlist_data[i].GetNbinsX()):
            b = h_temp.GetBinContent(j+1)
            e = h_temp.GetBinError(j+1)
            data_b = hlist_data[i].GetBinContent(j+1)
            data_e = hlist_data[i].GetBinError(j+1)
            if data_e == 0.0:
                pull = 0
            else:
                pull = b/data_e
            if b == 0 or data_b == 0:
                pull_unc = 1.0
            else:
                pull_unc = abs(pull) * sqrt((e/b)**2 + (data_e/data_b)**2)
            h_temp.SetBinContent(j+1, pull)
            h_temp.SetBinError(j+1, pull_unc)
        h_temp.SetLineColor(kBlack)
        hlist_ratio.append(h_temp)

    c1, p1_list, p2_list = makeCanvasAndPads(channel == "combo")

    c1, p1_list, p2_list = formatCanvasAndPads(c1, p1_list, p2_list)
    
    leg_list = []
    for i in range(len(p1_list)): 
        l = ROOT.TLegend(0.33, 0.75, 0.9, 0.9)
        l.SetNColumns(2)
        l.SetTextSize(0.05)
        l.SetBorderSize(0)
        l.SetFillStyle(0)

        if plotsb:
            l.AddEntry(hlist_post_sb[i], "Post S+B", "l")
        if plotb:
            l.AddEntry(hlist_post_b[i], "Post B", "l")
        if plotdata:
            l.AddEntry(hlist_data[i], "Data", "p")
        if plotsig:
            l.AddEntry(hlist_post_sig[i], "{}".format(signal), "l")
    
        leg_list.append(l)

    for i in range(len(p1_list)):
        p1_list[i].cd()
        
        hlist_post_sig[i].SetTitleSize(0.1)
        hlist_post_sig[i].GetYaxis().SetTitle("Num. Events (A.U.)")
        hlist_post_sig[i].GetXaxis().SetTitle("N Jets")
        hlist_post_sig[i].GetYaxis().SetRangeUser(1, 2E6)
        hlist_post_sig[i].SetLineWidth(3)
        
        hlist_post_sb[i].SetTitleSize(0.1)
        hlist_post_sb[i].GetYaxis().SetTitle("Num. Events (A.U.)")
        hlist_post_sb[i].GetXaxis().SetTitle("N Jets")
        hlist_post_sb[i].GetYaxis().SetRangeUser(1, 2E6)
        hlist_post_sb[i].SetLineWidth(3)
        
        hlist_post_b[i].SetTitleSize(0.1)
        hlist_post_b[i].GetYaxis().SetTitle("Num. Events (A.U.)")
        hlist_post_b[i].GetXaxis().SetTitle("N Jets")
        hlist_post_b[i].GetYaxis().SetRangeUser(1, 2E6)
        hlist_post_b[i].SetLineWidth(3)
        
        if plotsig:
            hlist_post_sig[i].Draw("E0P SAME")
        if plotb:
            hlist_post_b[i].Draw("E1 SAME")
        if plotsb:
            hlist_post_sb[i].Draw("E1 SAME")
        hlist_data[i].SetMarkerStyle(8)
        hlist_data[i].SetMarkerSize(0.8)
        if plotdata:
            hlist_data[i].Draw("E1 X0 SAME")
        leg_list[i].Draw()

        p2_list[i].cd()
        hlist_ratio[i].SetTitle("")
        hlist_ratio[i].SetLineWidth(3)
        hlist_ratio[i].GetYaxis().SetRangeUser(-2, 2)
        hlist_ratio[i].GetYaxis().SetTitle("Fit-Data/#sigma_{Data}")
        hlist_ratio[i].GetYaxis().SetTitleSize(0.1)
        hlist_ratio[i].GetYaxis().SetTitleOffset(0.4)
        hlist_ratio[i].GetYaxis().SetLabelSize(0.1)
        hlist_ratio[i].GetXaxis().SetTitle("N_{Jets}")        
        hlist_ratio[i].GetXaxis().SetLabelSize(0.1)
        hlist_ratio[i].GetXaxis().SetTitleSize(0.1)        
        hlist_ratio[i].GetXaxis().SetTitleOffset(0.0)
       
        hlist_ratio[i].Draw("E0P")
        
    for p in p1_list:
        draw_LumiCMS(p, year, approved = False, wip = True)
    
        #c1.Update()
        #c1.Paint()

    c1.SaveAs("%s/output-files/plots_dataCards_TT_allTTvar/fit_plots/"%(options.path) + year + "_" + signal + "_" + channel + "_" + fitName + ".png")

# ---------------
# ---------------
def getObs(card, njets, combo=False):

    if combo:
        njets = [8,13]

    with open(card, "r") as f:

        lines = f.readlines()

        data_temp = []

        for l in lines:

            if l.find("observation") != -1:

                data_temp = l.split(" ")[1:-1] 
    
        if "" in data_temp:
            data_temp = list(filter(lambda a: a is not "", data_temp))

        ABCD = ["A", "B", "C", "D"] 
        if combo:
            ABCD = ["A0", "B0", "C0", "D0", "A1", "B1", "C1", "D1", "A2", "B2", "C2", "D2"] 
        data = OrderedDict()

        for reg in ABCD:
            data[reg] = []

        for i,reg in enumerate(ABCD):

            k = 0
            if combo:
                k = int(reg[1:])

            for j in range(0,njets[1]-njets[0] + 1):

                data[reg].append( ( njets[0]-k+j, float(data_temp[i*(njets[1]-njets[0]+1)+j]), sqrt(float(data_temp[i*(njets[1]-njets[0]+1)+j])) ) )

        return data

# -------------
# main function
# -------------
def main():   

    #dirTag = options.path.split("_")[-1]
    dirTag = "cards"

    if not os.path.exists("%s/output-files/plots_dataCards_TT_allTTvar/fit_plots/"%(options.path)):
        os.makedirs("%s/output-files/plots_dataCards_TT_allTTvar/fit_plots/"%(options.path))

    if not os.path.exists("results"):
        os.makedirs("results")

    ROOT.gROOT.SetBatch(True)

    print("Making pre and post fit distributions for:")
    
    # ------------------------------------------------------
    # make fit plots for any model, mass, channel, data type
    # ------------------------------------------------------
    if options.all:

        #signals   = ["RPV", "StealthSYY"            ]
        signals   = ["StealthSYY"]
        #masses    = [m for m in range(300, 1450, 50)]
        masses    = [350, 550, 850, 1150]
        dataTypes = ["pseudoData", "pseudoDataS"]
        channels  = ["0l", "1l", "2l", "combo"]
        #channels  = ["combo"]

        close     = ""
        if options.setClosure:
            close = "_perfectClose"

        for c in channels:
            for d in dataTypes:
                for s in signals:
                    for m in masses:

                        if c == "2l":
                            njets = [6, 11]
                        elif c == "1l":
                            njets = [7, 12]
                        elif c == "0l":
                            njets = [8, 13]
                        elif c == "combo":
                            njets = [8, 13]
             
                        shortSig = s[-3:]

                        print("Year: {}\t Signal: {}\t Mass: {}\t Final State: {}\t Data Type: {}".format(options.year, s, m, c, d))
                        card    = "{}/output-files/{}/{}_{}_{}_{}_{}{}.txt".format(options.path, dirTag, options.year, s, m, d, c, close)
                        obs     = getObs(card, njets, c == "combo")
                        path    = "{}/output-files/{}_{}_{}".format(options.path, s, m, options.year)
                        prefit  = "ws_{}{}{}{}_{}{}.root".format(options.year, s, m, d, c, close)
                        postfit = "higgsCombine{}{}{}{}_{}{}.FitDiagnostics.mH{}.MODEL{}.root".format(options.year, s, m, d, c, m, s, close[1:])
                        fitDiag = "fitDiagnostics{}{}{}{}_{}{}.root".format(options.year, s, m, d, c, close[1:])
                        
                        pre_path     = "{}/{}".format(path, prefit)
                        post_path    = "{}/{}".format(path, postfit) 
                        fitDiag_path = "{}/{}".format(path, fitDiag)
                        signal       = "{}_{}".format(s, m)
                        
                        name = "{}_{}_{}_{}_{}{}".format(options.year, s, m, d, c, close)

                        if not os.path.isdir("%s/fit_plots/%s/"%(options.path,dirTag)):
                            os.makedirs("%s/fit_plots/%s/"%(options.path,dirTag))

                        make_fit_plots(signal, options.year, pre_path, fitDiag_path, c, True, False, True, False, "{}_bonly".format(d), "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)
                        make_fit_plots(signal, options.year, pre_path, fitDiag_path, c, True, True,  True, True,  "{}_sb".format(d),    "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)

    # ---------------------------------------------------------------
    # make fit plots for specific model, mass, channel, any data type
    # ---------------------------------------------------------------
    else:
        signals   = ["StealthSYY"]
        masses    = [350, 550, 850, 1150]
        dataTypes = ["pseudoData", "pseudoDataS"]
        channels  = [options.channel]
       
        close     = ""

        if options.setClosure:
            close = "_perfectClose"
 
        for c in channels:
            for d in dataTypes:
                for s in signals:
                    for m in masses:

                        if c == "0l":
                            njets = [6, 11]
                        elif c == "1l":
                            njets = [7, 12]
                        elif c == "2l":
                            njets = [8, 13]

                        print("Year: {}\t Signal: {}\t Mass: {}\t Final State: {}\t Data Type: {}".format(options.year, s, m, c, d))
                        card    = "{}_{}_{}_{}_{}{}.txt".format(options.year, s, m, d, c, close)
                        obs     = getObs(card, njets)
                        path    = "{}/output-files/{}_{}_{}".format(options.path, s, m, options.year)
                        prefit  = "ws_{}{}{}{}_{}{}.root".format(options.year, s, m, d, c, close)
                        postfit = "higgsCombine{}{}{}{}{}_{}.FitDiagnostics.mH{}.MODEL{}.root".format(options.year, s, m, d, c, close[1:], m, s)
                        fitDiag = "fitDiagnostics{}{}{}{}_{}{}.root".format(options.year, s, m, d, c, close[1:])
                        
                        pre_path     = "{}/{}".format(path, prefit)
                        post_path    = "{}/{}".format(path, postfit) 
                        fitDiag_path = "{}/{}".format(path, fitDiag)
                        signal       = "{}_{}".format(s, m)
                        
                        name = "{}_{}_{}_{}_{}{}".format(options.year, s, m, d, c, close)

                        make_fit_plots(signal, options.year, pre_path, fitDiag_path, c, True, False, True, False, "{}_bonly".format(d), "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)
                        make_fit_plots(signal, options.year, pre_path, fitDiag_path, c, True, True,  True, True,  "{}_sb".format(d),    "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)
        
    
                
if __name__ == '__main__':
    main()
