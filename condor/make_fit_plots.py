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
ROOT.gStyle.SetFrameLineWidth(1)
ROOT.gStyle.SetLineWidth(1)
ROOT.gStyle.SetEndErrorSize(0)
ROOT.gROOT.ForceStyle()
ROOT.gStyle.SetHatchesLineWidth(1)

if options.all:
    ROOT.gROOT.SetBatch(True)

borderSizeL  = 0.20
borderSizeR  = 0.10
pad1Size     = 0.2866
pad2Size     = 0.2293
pad3Size     = 0.2293
pad4Size     = 0.2548

textSizeM = [pad1Size / pad2Size, 1.0, 1.0, pad4Size / pad2Size]
textSizeP = [1.0, 1.0, 1.0, -1.0]
padRatio = 0.3 / 0.7

#qcdgreen = ROOT.TColor.GetColor("#006d2c")

#fitcol     = ROOT.TColor.GetColor("#ce1256")
#fitcol     = ROOT.kBlue
fitcol     = ROOT.TColor.GetColor("#8B2D8F")
#sigpredcol = ROOT.TColor.GetColor("#99d8c9")
sigobscol  = ROOT.TColor.GetColor("#2ca25f")
sigpredcol = ROOT.TColor.GetColor("#85c2a3")

#bkgobscol  = ROOT.TColor.GetColor("#807dba")
#bkgobscol  = ROOT.TColor.GetColor("#ce1256")
bkgobscol   = ROOT.TColor.GetColor("#5cb4e8")

# -------------------
# get fit information
# -------------------
def getFitInfo(fitDiag_path, pre_path, signal, year, channel, njets):

    f_fit = ROOT.TFile.Open(fitDiag_path, "READ")
    f_pre = ROOT.TFile.Open(pre_path)

    w = f_pre.Get("w")

    data      = {}; data_unc = {}
    prefit_sb = OrderedDict(); prefit_b = OrderedDict(); postfit_sb = OrderedDict(); postfit_b = OrderedDict(); postfit_sig = OrderedDict()
    prefit_sig = OrderedDict(); postfit_sb_b = OrderedDict()

    regs =["A", "B", "C", "D"] 
    if channel == "combo":
        regs =["A0", "B0", "C0", "D0", "A1", "B1", "C1", "D1", "A2", "B2", "C2", "D2"] 
        njets = [8, 13]

    for reg in regs:
        prefit_sb[reg]   = []
        prefit_b[reg]    = []
        prefit_sig[reg]  = []
        postfit_sb[reg]  = []
        postfit_sb_b[reg]  = []
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
                postfit_sb_b[reg].append((i, 
                     f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/total_background".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinContent(1),
                     f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/total_background".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinError(1)
                     ))
                postfit_b[reg].append((i, 
                     f_fit.Get("shapes_fit_b/{}Y{}_{}{}_{}/total".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinContent(1),
                     f_fit.Get("shapes_fit_b/{}Y{}_{}{}_{}/total".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinError(1)
                     ))
                postfit_sig[reg].append((i, 
                    f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/total_signal".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinContent(1),
                    f_fit.Get("shapes_fit_s/{}Y{}_{}{}_{}/total_signal".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinError(1)
                    ))

                #prefit_sb[reg].append((i, w_pre.function("shapes_prefit/{}{}/".format(reg,i))))
                prefit_b[reg].append((i, 
                    f_fit.Get("shapes_prefit/{}Y{}_{}{}_{}/total".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinContent(1),
                    f_fit.Get("shapes_prefit/{}Y{}_{}{}_{}/total".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinError(1)
                    ))
                prefit_sig[reg].append((i, 
                    f_fit.Get("shapes_prefit/{}Y{}_{}{}_{}/total_signal".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinContent(1),
                    f_fit.Get("shapes_prefit/{}Y{}_{}{}_{}/total_signal".format(ch,year[-2:],reg_temp,i,channel_temp)).GetBinError(1)
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

    return prefit_b, postfit_b, postfit_sb, postfit_sb_b, postfit_sig, prefit_sig, data

# ---------------
# make histograms
# ---------------
def makeHist(reg, bin_info, tag, njets, combo=False):

    k = 0
    if combo:
        k = int(reg[1:])

    h = ROOT.TH1D("Region{}{}".format(reg, tag), "", njets[1]-njets[0] + 1, njets[0] - k, njets[1] + 1 - k)

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
    tag = "TEST" 

    c1                          = ROOT.TCanvas( "c1_%s"%(tag), "c1_%s"%(tag), 0, 0, 1200, 480 )
    
    p1_A1                       = ROOT.TPad( "p1_D1_%s"%(tag), "p1_D1_%s"%(tag), 0, 0.30, pad1Size, 1.0 )
    p2_A1                       = ROOT.TPad( "p2_D1_%s"%(tag), "p2_D1_%s"%(tag), 0,    0, pad1Size, 0.30 )
    
    p1_B2                       = ROOT.TPad( "p1_D2_%s"%(tag), "p1_D2_%s"%(tag), pad1Size, 0.30, pad1Size + pad2Size, 1.0 )
    p2_B2                       = ROOT.TPad( "p2_D2_%s"%(tag), "p2_D2_%s"%(tag), pad1Size,    0, pad1Size + pad2Size, 0.30 )
    
    p1_C3                       = ROOT.TPad( "p1_D3_%s"%(tag), "p1_D3_%s"%(tag), pad1Size + pad2Size, 0.30, pad1Size + 2*pad2Size, 1.0 )
    p2_C3                       = ROOT.TPad( "p2_D3_%s"%(tag), "p2_D3_%s"%(tag), pad1Size + pad2Size,    0, pad1Size + 2*pad2Size, 0.30 )
    
    p1_D4                       = ROOT.TPad( "p1_D4_%s"%(tag), "p1_D4_%s"%(tag), pad1Size + 2*pad2Size, 0.30, 1.0, 1.0 )
    p2_D4                       = ROOT.TPad( "p2_D4_%s"%(tag), "p2_D4_%s"%(tag), pad1Size + 2*pad2Size,    0, 1.0, 0.30 )

    return c1, [p1_A1, p1_B2, p1_C3, p1_D4], [p2_A1, p2_B2, p2_C3, p2_D4]

# ---------------------
# format canvas and pad
# ---------------------
def formatCanvasAndPads( c1, topPadArray, ratioPadArray ):

    for iPad in xrange( 0, len(topPadArray) ) :
        topPadArray[iPad].SetLogy(1)
        topPadArray[iPad].SetBottomMargin(0.0)

        if iPad == 0 :
            topPadArray[iPad].SetLeftMargin( borderSizeL )
            ratioPadArray[iPad].SetLeftMargin( borderSizeL )
        else :
            topPadArray[iPad].SetLeftMargin( 0.0 )
            ratioPadArray[iPad].SetLeftMargin( 0.0 )

        if iPad == (len(topPadArray) - 1) :
            topPadArray[iPad].SetRightMargin( borderSizeR )
            ratioPadArray[iPad].SetRightMargin( borderSizeR )
        else :
            topPadArray[iPad].SetRightMargin( 0.0 )
            ratioPadArray[iPad].SetRightMargin( 0.0 )
        
        topPadArray[iPad].Draw()

        ratioPadArray[iPad].SetTopMargin( 0.0 )
        ratioPadArray[iPad].SetBottomMargin( 0.40 )
        ratioPadArray[iPad].SetGridx(1)
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

def draw_ExtraInfo(canvas, iPad, packedInfo):

    canvas.cd()

    channelStr = ""
    if "0l" in packedInfo:
        channelStr = "Fully-Hadronic"
    elif "1l" in packedInfo:
        channelStr = "Semi-Leptonic"
    elif "2l" in packedInfo:
        channelStr = "Fully-Leptonic"

    modelStr = ""
    if "SYY" in packedInfo:
        modelStr = "Stealth SYY"
    elif "RPV" in packedInfo:
        modelStr = "RPV"

    regionStr = ""
    textSizeF = 1.0
    marginR   = 0.0
    marginL   = 0.2
    extraL    = 0.0
    extraR    = 0.0
    if iPad == 0:
        extraR = 0.025
        regionStr = "Region A"
        textSizeF = pad1Size / pad2Size
    elif iPad == 1:
        extraR = 0.03
        marginL = 0.0
        extraL = 0.04
        regionStr = "Region B"
    elif iPad == 2:
        extraR = 0.03
        marginL = 0.0
        extraL = 0.04
        regionStr = "Region C"
    elif iPad == 3:
        marginL = 0.0
        marginR = 0.1
        extraL = 0.04
        regionStr = "Region D"
        textSizeF = pad4Size / pad2Size

    text = ROOT.TLatex()
    text.SetNDC(True)

    text.SetTextSize(0.070 / textSizeF)
    text.SetTextFont(62)
    text.SetTextColor(ROOT.TColor.GetColor("#7C99D1"))
    #text.SetTextColor(ROOT.TColor.GetColor("#88258c"))
    #text.SetTextColor(ROOT.kBlack)

    if regionStr != "":
        text.SetTextAlign(33)
        text.DrawLatex(1.0 - marginR - 0.2 * marginR - extraR, 0.88, regionStr)
    text.SetTextAlign(13)
    if modelStr != "" and iPad == 0:
        text.DrawLatex(marginL + 0.2 * marginL + extraL, 0.88, modelStr)
    if channelStr != "" and iPad == 0:
        text.DrawLatex(marginL + 0.2 * marginL + extraL, 0.80, channelStr)

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

def drawWithNoYerr(c, h, color):
    c.cd()
 
    lines = []
    for i in range(h.GetNbinsX()):
        y = h.GetBinContent(i+1)
        x1 = h.GetBinLowEdge(i+1)
        x2 = h.GetBinWidth(i+1)+x1
        l = ROOT.TLine(x1,y,x2,y)
        l.SetLineColor(color)
        l.SetLineWidth(2)
        l.Draw("SAME")
        lines.append(l)

    return lines

# --------------
# make fit plots
# --------------
def make_fit_plots(signal, year, pre_path, fitDiag_path, channel, sigStr, plotb, plotsb, plotdata, plotsig, plotsigref, fitName, outfile, obs, njets, path):

    nLegItems = 0
    if plotb:
        nLegItems += 1
    if plotsb:
        nLegItems += 1
    if plotdata:
        nLegItems += 1
    if plotsig:
        nLegItems += 1
    if plotsigref:
        nLegItems += 1
    
    close  = ""

    if pre_path.find("perfectClose") != -1:
        close += "_perfectClose"
    try: 
        pre_b, post_b, post_sb, post_sb_b, post_sig, pre_sig, data = getFitInfo(fitDiag_path, pre_path, signal, year, channel, njets)
    except:
        print("Fit for {}_{}_{} Failed".format(year, signal, channel))
        print(e)
        return

    hlist_data = []
    hlist_pre_b = []
    hlist_pre_sig = []
    hlist_post_b = []
    hlist_post_sb = []
    hlist_post_sb_b = []
    hlist_post_sig = []

    regs = data.keys()

    for reg in regs:
        hlist_data.append(makeHist(    reg, obs,      "_data",        njets, channel == "combo") )
        hlist_pre_b.append(makeHist(   reg, pre_b,    "_pre_bonly",   njets, channel == "combo") )
        hlist_post_b.append(makeHist(  reg, post_b,   "_post_bonly",  njets, channel == "combo") )
        hlist_post_sb.append(makeHist( reg, post_sb,  "_post_sb",     njets, channel == "combo") )
        hlist_post_sb_b.append(makeHist( reg, post_sb_b,  "_post_sb_b",     njets, channel == "combo") )
        hlist_post_sig.append(makeHist(reg, post_sig, "_post_signal", njets, channel == "combo") )
        hlist_pre_sig.append(makeHist(reg, pre_sig, "_pre_signal", njets, channel == "combo") )

    #save_to_root(hlist_data, outfile)
    #save_to_root(hlist_pre_b, outfile)
    #save_to_root(hlist_post_b, outfile)
    #save_to_root(hlist_post_sb, outfile)
    #save_to_root(hlist_post_sig, outfile)
 
    for i in range(len(hlist_pre_b)):
        hlist_post_b[i].SetLineColor(fitcol)
        hlist_post_b[i].SetFillColorAlpha(fitcol, 0.30)
        #hlist_post_b[i].SetFillColorAlpha(ROOT.kGray, 0.90)
        hlist_post_b[i].SetFillStyle(3744)

        hlist_post_sb_b[i].SetLineColor(bkgobscol)
        hlist_post_sb_b[i].SetMarkerColor(bkgobscol)

        hlist_post_sb[i].SetLineColor(fitcol)
        hlist_post_sb[i].SetFillColorAlpha(fitcol, 0.30)
        #hlist_post_sb[i].SetFillColorAlpha(ROOT.kGray, 0.90)
        hlist_post_sb[i].SetFillStyle(3744)

        hlist_pre_sig[i].SetLineColor(sigpredcol)
        hlist_pre_sig[i].SetMarkerColor(sigpredcol)
        hlist_post_sig[i].SetLineColor(sigobscol)
        hlist_post_sig[i].SetMarkerColor(sigobscol)

        hlist_data[i].SetLineColor(kBlack)
    
    hlist_ratio = []
    pull_unc_list = []
    for i in range(len(hlist_pre_b)):
        if plotsb:
            h_temp = copy.copy(hlist_post_sb[i])
            h_temp2 = copy.copy(hlist_post_sb[i])
        else:
            h_temp = copy.copy(hlist_post_b[i])
            h_temp2 = copy.copy(hlist_post_b[i])

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
            pull_unc = 1.0
            h_temp.SetBinContent(j+1, pull)
            h_temp.SetBinError(j+1, pull_unc)
            h_temp2.SetBinContent(j+1, 0)
            h_temp2.SetBinError(j+1, e/data_e)
        h_temp.SetLineColor(kBlack)
        hlist_ratio.append(h_temp)
        pull_unc_list.append(h_temp2)

    c1, p1_list, p2_list = makeCanvasAndPads(channel == "combo")

    c1, p1_list, p2_list = formatCanvasAndPads(c1, p1_list, p2_list)
    
    survival = []
    for i in range(len(p1_list)):
        p1_list[i].cd()
        
        if i == 0:

            for hist in [hlist_post_sig[i], hlist_pre_sig[i], hlist_post_sb[i], hlist_post_b[i]]:
                hist.GetYaxis().SetTitle("Number of Events")
                hist.GetYaxis().SetTitleSize(0.175 * padRatio)
                hist.GetYaxis().SetLabelSize(0.145 * padRatio)

            hlist_ratio[i].GetYaxis().SetTitle("(val - fit) / #delta")
            hlist_ratio[i].GetYaxis().SetTitleSize(0.175)
            hlist_ratio[i].GetYaxis().SetTitleOffset(0.55)
            hlist_ratio[i].GetYaxis().SetLabelSize(0.155)

            pull_unc_list[i].GetYaxis().SetTitle("(val - fit) / #delta")
            pull_unc_list[i].GetYaxis().SetTitleSize(0.175)
            pull_unc_list[i].GetYaxis().SetTitleOffset(0.55)
            pull_unc_list[i].GetYaxis().SetLabelSize(0.145)

        elif i == 3:
            hlist_ratio[i].GetXaxis().SetTitle("Number of Jets")        
            hlist_ratio[i].GetXaxis().SetTitleOffset(0.0)
            pull_unc_list[i].GetXaxis().SetTitle("Number of Jets")        
            pull_unc_list[i].GetXaxis().SetTitleOffset(0.0)

        hlist_post_sig[i].GetYaxis().SetRangeUser(2, 2E6)
        hlist_post_sig[i].SetLineWidth(2)
        
        hlist_pre_sig[i].GetYaxis().SetRangeUser(2, 2E6)
        hlist_pre_sig[i].SetLineWidth(2)

        hlist_post_sb[i].GetYaxis().SetRangeUser(2, 2E6)
        hlist_post_sb[i].SetLineWidth(2)
        
        hlist_post_sb_b[i].GetYaxis().SetRangeUser(2, 2E6)
        hlist_post_sb_b[i].SetLineWidth(2)

        hlist_post_b[i].GetYaxis().SetRangeUser(2, 2E6)
        hlist_post_b[i].SetLineWidth(2)
        
        if plotsigref:
            hlist_pre_sig[i].Draw("L SAME")
        if plotsig:
            hlist_post_sig[i].Draw("L SAME")
        if plotb and plotsb:
            hlist_post_sb_b[i].Draw("L SAME")
            #survival.append(drawWithNoYerr(p1_list[i], hlist_post_b[i], fitcol))
        if plotb and not plotsb:
            hlist_post_b[i].Draw("E2 SAME")
            survival.append(drawWithNoYerr(p1_list[i], hlist_post_b[i], fitcol))
        if plotsb:
            hlist_post_sb[i].Draw("E2 SAME")
            survival.append(drawWithNoYerr(p1_list[i], hlist_post_sb[i], fitcol))
        hlist_data[i].SetMarkerStyle(8)
        hlist_data[i].SetMarkerSize(1)
        hlist_data[i].SetLineWidth(2)
        if plotdata:
            hlist_data[i].Draw("E1 X0 SAME")

        if i == 3:
            l = None
            if plotsigref:
                l = ROOT.TLegend(0.32, 0.88 - nLegItems*0.075, 0.90, 0.81)
            else:
                l = ROOT.TLegend(0.52, 0.88 - nLegItems*0.075, 0.90, 0.81)
            l.SetNColumns(1)
            l.SetTextSize(0.05)
            l.SetBorderSize(0)
            l.SetFillStyle(0)

            if plotsb:
                l.AddEntry(hlist_post_sb[i], "Bkg+Sig Fit", "l")
            if plotb and not plotsb:
                l.AddEntry(hlist_post_b[i], "Bkg Fit", "l")
            if plotdata:
                l.AddEntry(hlist_data[i], "N observed", "pe")
            if plotb and plotsb:
                l.AddEntry(hlist_post_sb_b[i], "Bkg Obs.", "l")
            if plotsig:
                l.AddEntry(hlist_post_sig[i], "Signal Obs.", "l")
            if plotsigref:
                l.AddEntry(hlist_pre_sig[i], sigStr, "l")
   
            l.Draw("SAME")

        p2_list[i].cd()
        hlist_ratio[i].SetTitle("")
        hlist_ratio[i].SetLineWidth(2)
        hlist_ratio[i].SetMarkerStyle(8)
        hlist_ratio[i].SetMarkerSize(1)

        hlist_ratio[i].GetYaxis().SetRangeUser(-2.4, 2.4)
        hlist_ratio[i].GetXaxis().SetLabelSize(0.2)
        hlist_ratio[i].GetXaxis().SetTitleSize(0.145)        
        hlist_ratio[i].GetXaxis().SetLabelOffset(0.027)
        hlist_ratio[i].GetYaxis().SetNdivisions(5, 5, 0)

        pull_unc_list[i].GetYaxis().SetRangeUser(-2.4, 2.4)
        pull_unc_list[i].GetXaxis().SetLabelSize(0.23)
        pull_unc_list[i].GetXaxis().SetTitleSize(0.145 * pad1Size/pad4Size)        
        pull_unc_list[i].GetXaxis().SetLabelOffset(0.020)
        pull_unc_list[i].GetXaxis().SetTitleOffset(1.1)
        pull_unc_list[i].GetYaxis().SetNdivisions(5, 5, 0)

        pull_unc_list[i].SetLineWidth(0)

        for bin in range(1, hlist_ratio[i].GetNbinsX()+1):
    
            label = str(njets[0] + bin - 1)
            if label == str(njets[-1]):
                label = "#geq " + str(njets[0] + bin - 1)

            hlist_ratio[i].GetXaxis().SetBinLabel(bin, label)
            pull_unc_list[i].GetXaxis().SetBinLabel(bin, label)

        pull_unc_list[i].Draw("E2")
        hlist_ratio[i].Draw("E0P SAME")
        hlist_ratio[i].Draw("AXIG SAME")
        hlist_ratio[i].Draw("AXIS SAME")

        draw_LumiCMS(p1_list[i], i, year, approved = False, wip = True)
        draw_ExtraInfo(p1_list[i], i, channel+signal)
   
    for ext in ["pdf"]:
        c1.SaveAs("%s/output-files/plots_dataCards_TT_allTTvar/fit_plots/"%(options.path) + year + "_" + signal + "_" + channel + "_" + fitName + ".%s"%(ext))

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
        channels  = ["0l", "1l", "2l"]
        #channels  = ["combo"]

        close     = ""
        if options.setClosure:
            close = "_perfectClose"

        for c in channels:
            for d in dataTypes:
                for s in signals:
                    for m in masses:

                        sigStr = ""
                        if "RPV" in s:
                            sigStr = "RPV"
                        elif "SYY" in s:
                            sigStr = "SYY"

                        sigStr += " m_{ #tilde{t}} = %d GeV"%(m)

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

                        # make_fit_plots(... plotb, plotsb, plotdata, plotsig, plotsigref ...)
                        if d == "pseudoData":
                            make_fit_plots(signal, options.year, pre_path, fitDiag_path, c, sigStr, True, False, True, False, True,  "{}_bonly".format(d), "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)
                            make_fit_plots(signal, options.year, pre_path, fitDiag_path, c, sigStr, False, True, True, True,  False,  "{}_sb".format(d),    "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)
                        elif d == "pseudoDataS":
                            make_fit_plots(signal, options.year, pre_path, fitDiag_path, c, sigStr, True, False, True,  False,  True,  "{}_bonly".format(d),    "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)
                            make_fit_plots(signal, options.year, pre_path, fitDiag_path, c, sigStr, True, True, True,  True,  False,  "{}_sb".format(d),    "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)

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
