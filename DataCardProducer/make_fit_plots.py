import ROOT
import copy
import time
#from optparse import OptionParser
from math import sqrt

from ROOT import kRed, kBlue, kBlack, kCyan, kGreen
from ROOT import gStyle
'''
parser = OptionParser()
parser.add_option("-s", "--signal", action="store", type="string", dest="signal", default="StealthSYY_550", help="Signal name with mass separated by \'_\'(e.g. StealthSYY_550)")
parser.add_option("-p", "--pre", action="store", type="string", dest="prefit", default="myDataCard.root", help="Name of prefit data card")
parser.add_option("--plotb", action="store_true", dest="plotb", default=False, help="Plot background only fit")
parser.add_option("--plotsb", action="store_true", dest="plotsb", default=False, help="Plot signal plus background fit")
parser.add_option("--plotsig", action="store_true", dest="plotsig", default=False, help="Plot signal component of fit")
parser.add_option("--plotdata", action="store_true", dest="plotdata", default=False, help="Plot distributions observed in data")

(options, args) = parser.parse_args()
'''
gStyle.SetOptStat(0)
ROOT.TH1.AddDirectory(False)
ROOT.TH1.SetDefaultSumw2(1)

borderSize = 0.20
pad1and4Size = 1.0 + borderSize
pad2and3Size = 1.0
totalPadSize = 2 * pad1and4Size + 2 * pad2and3Size

def getFitInfo(pre_path, post_path, fitDiag_path, w_name, signal):
    f_pre = ROOT.TFile.Open(pre_path, "READ")
    f_post = ROOT.TFile.Open(post_path, "READ")
    f_fit = ROOT.TFile.Open(fitDiag_path, "READ")

    w_pre = f_pre.Get(w_name)
    w_post = f_post.Get(w_name)

    fit_b = f_fit.Get("fit_b")
    fit_s = f_fit.Get("fit_s")

    data = {}
    data_unc = {}

    prefit_sb = {} 
    prefit_b = {}
    postfit_sb = {}
    postfit_b = {}
    postfit_sig = {}

    postfit_sig_unc = {}
    postfit_sb_unc = {}
    postfit_b_unc = {}

    for reg in ["A", "B", "C", "D"]:
        prefit_sb[reg] = []
        prefit_b[reg] = []
        postfit_sb[reg] = []
        postfit_b[reg] = []
        postfit_sig[reg] = []       
 
        postfit_sig_unc[reg] = []
        postfit_sb_unc[reg] = []
        postfit_b_unc[reg] = []

        data[reg] = []
        data_unc[reg] = []

        for i in range(7,12):
            postfit_sb[reg].append((i, w_post.function("n_exp_bin{}{}".format(reg,i))))
            postfit_b[reg].append((i, w_post.function("n_exp_bin{}{}_bonly".format(reg,i))))
            prefit_sb[reg].append((i, w_pre.function("n_exp_bin{}{}".format(reg,i))))
            prefit_b[reg].append((i, w_pre.function("n_exp_bin{}{}_bonly".format(reg,i))))
            postfit_sig[reg].append((i, w_post.function("n_exp_bin{}{}_proc_{}".format(reg,i,signal))))
            
            postfit_sig_unc[reg].append((i,w_post.function("n_exp_bin{}{}_proc_{}".format(reg,i,signal)).getPropagatedError(fit_s)))
            postfit_sb_unc[reg].append((i,w_post.function("n_exp_bin{}{}".format(reg,i)).getPropagatedError(fit_s)))
            postfit_b_unc[reg].append((i, w_post.function("n_exp_bin{}{}_bonly".format(reg,i)).getPropagatedError(fit_b)))

            data[reg].append((i, w_pre.data("data_obs").get(0).getRealValue("n_obs_bin{}{}".format(reg,i))))
            data_unc[reg].append((i, sqrt(w_pre.data("data_obs").get(0).getRealValue("n_obs_bin{}{}".format(reg,i)))))

    f_pre.Close()
    f_post.Close()
    f_fit.Close()

    return prefit_b, prefit_sb, postfit_b, postfit_sb, postfit_sig, postfit_b_unc, postfit_sb_unc, postfit_sig_unc, data, data_unc

def makeHist(reg, bin_info, tag):
    h = ROOT.TH1D("Region{}{}".format(reg, tag), "Region {}".format(reg), 5, 7, 12)

    bins = bin_info["{}".format(reg)]

    for b in bins:
        if type(b[1]) != float:
            h.Fill(b[0], b[1].getVal())
        else:
            h.Fill(b[0], b[1])

    return h

def makeHistUnc(reg, bin_info, unc_info, tag):
    h = ROOT.TH1D("Region{}{}".format(reg, tag), "Region {}".format(reg), 5, 7, 12)

    bins = bin_info[reg]
    unc = unc_info[reg]

    for i in range(len(bins)):
        if type(bins[i][1]) != float:
            h.Fill(bins[i][0], bins[i][1].getVal())
        else:
            h.Fill(bins[i][0], bins[i][1])
        h.SetBinError(i+1, unc[i][1])

    return h

def makeCanvasAndPads():
    c1 = ROOT.TCanvas("c1", "c1", 0, 0, 1200, 480)
    
    p1_A = ROOT.TPad("p1_A", "p1_A", 0, 0.3, pad1and4Size/totalPadSize, 1.0)
    p2_A = ROOT.TPad("p2_A", "p2_A", 0, 0, pad1and4Size/totalPadSize, 0.3)
    
    p1_B = ROOT.TPad("p1_B", "p1_B", pad1and4Size/totalPadSize, 0.3, (pad1and4Size + pad2and3Size) / totalPadSize, 1.0)
    p2_B = ROOT.TPad("p2_B", "p2_B", pad1and4Size/totalPadSize, 0, (pad1and4Size + pad2and3Size) / totalPadSize, 0.3)
    
    p1_C = ROOT.TPad("p1_C", "p1_C", (pad1and4Size + pad2and3Size) / totalPadSize, 0.3, (pad1and4Size + 2*pad2and3Size) / totalPadSize, 1.0)
    p2_C = ROOT.TPad("p2_C", "p2_C", (pad1and4Size + pad2and3Size) / totalPadSize, 0, (pad1and4Size + 2*pad2and3Size) / totalPadSize, 0.3)
    
    p1_D = ROOT.TPad("p1_D", "p1_D", (pad1and4Size + 2*pad2and3Size) / totalPadSize, 0.3, 1.0, 1.0)
    p2_D = ROOT.TPad("p2_D", "p2_D", (pad1and4Size + 2*pad2and3Size) / totalPadSize, 0, 1.0, 0.3)

    return c1, [p1_A, p1_B, p1_C, p1_D], [p2_A, p2_B, p2_C, p2_D]

def formatCanvasAndPads( c1, topPadArray, ratioPadArray ) :

    borderSize = 0.2

    for iPad in xrange( 0, len(topPadArray) ) :
        topPadArray[iPad].SetLogy(1)
        topPadArray[iPad].SetBottomMargin(0.0)

        if iPad == 0 :
            topPadArray[iPad].SetLeftMargin( borderSize )
            ratioPadArray[iPad].SetLeftMargin( borderSize )
        else :
            topPadArray[iPad].SetLeftMargin( 0.0 )
            ratioPadArray[iPad].SetLeftMargin( 0.0 )

        if iPad == (len(topPadArray) - 1) :
            topPadArray[iPad].SetRightMargin( borderSize )
            ratioPadArray[iPad].SetRightMargin( borderSize )
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

def save_to_root(hlist, outfile):
    out = ROOT.TFile(outfile, 'UPDATE')    

    for h in hlist:
        h.Write()

    out.Close()

def make_fit_plots(prefit, signal, pre_path, post_path, fitDiag_path, plotb, plotsb, plotdata, plotsig, fitName, outfile):
    pre_b, pre_sb, post_b, post_sb, post_sig, post_b_unc, post_sb_unc, post_sig_unc, data, data_sqrt = getFitInfo(pre_path, post_path, fitDiag_path, 'w', signal)

    hlist_data = []
    hlist_pre_b = []
    hlist_post_b = []
    hlist_pre_sb = []
    hlist_post_sb = []
    hlist_post_sig = []

    for reg in ["A", "B", "C", "D"]:
        hlist_data.append(makeHistUnc(reg, data, data_sqrt, "_data"))
        hlist_pre_b.append(makeHist(reg, pre_b, "_pre_bonly"))
        hlist_post_b.append(makeHistUnc(reg, post_b, post_b_unc, "_post_bonly"))
        hlist_pre_sb.append(makeHist(reg, pre_sb, "_pre_sb"))
        hlist_post_sb.append(makeHistUnc(reg, post_sb, post_sb_unc, "_post_sb"))
        hlist_post_sig.append(makeHistUnc(reg, post_sig, post_sig_unc, "_post_signal"))

    save_to_root(hlist_data, outfile)
    save_to_root(hlist_pre_b, outfile)
    save_to_root(hlist_post_b, outfile)
    save_to_root(hlist_pre_sb, outfile)
    save_to_root(hlist_post_sb, outfile)
    save_to_root(hlist_post_sig, outfile)
 
    for i in range(len(hlist_pre_b)):
        hlist_post_b[i].SetLineColor(kBlue)
        hlist_post_sb[i].SetLineColor(kRed)
        hlist_post_sig[i].SetLineColor(kGreen)
        hlist_data[i].SetLineColor(kBlack)

    hlist_ratio = []
    for i in range(0,4):
        if plotsb:
            h_temp = copy.copy(hlist_post_sb[i])
        else:
            h_temp = copy.copy(hlist_post_b[i])
        h_temp.Add(hlist_data[i], -1)
        for j in range(hlist_data[i].GetNbinsX()):
            b = h_temp.GetBinContent(j+1)
            e = h_temp.GetBinError(j+1)
            data_e = hlist_data[i].GetBinError(j+1)
            pull = b/data_e
            pull_unc = e/data_e
            h_temp.SetBinContent(j+1, pull)
            h_temp.SetBinError(j+1, pull_unc)
        h_temp.SetLineColor(kBlack)
        hlist_ratio.append(h_temp)

    c1, p1_list, p2_list = makeCanvasAndPads()

    c1, p1_list, p2_list = formatCanvasAndPads(c1, p1_list, p2_list)

    leg_list = []
    for i in range(len(p1_list)): 
        if i == 3:
            l = ROOT.TLegend(0.5, 0.7, 0.8, 0.9)
        else:
            l = ROOT.TLegend(0.7, 0.7, 1, 0.9)
        if plotsb:
            l.AddEntry(hlist_post_sb[i], "Post S+B", "l")
        if plotb:
            l.AddEntry(hlist_post_b[i], "Post B", "l")
        if plotdata:
            l.AddEntry(hlist_data[i], "Data", "lp")
        if plotsig:
            l.AddEntry(hlist_post_sig[i], "{}".format(signal), "l")
        l.Draw()
    
        leg_list.append(l)

    for i in range(len(p1_list)):
        p1_list[i].cd()
        
        hlist_post_sb[i].GetYaxis().SetTitle("Num. Events (A.U.)")
        hlist_post_sb[i].GetXaxis().SetTitle("N Jets")
        hlist_post_sb[i].GetYaxis().SetRangeUser(10, 2E5)
        
        hlist_post_b[i].GetYaxis().SetTitle("Num. Events (A.U.)")
        hlist_post_b[i].GetXaxis().SetTitle("N Jets")
        hlist_post_b[i].GetYaxis().SetRangeUser(10, 2E5)
        
        if plotsb:
            hlist_post_sb[i].Draw("HIST E SAME") 
        if plotb:
            hlist_post_b[i].Draw("HIST E SAME")
        if plotsig:
            hlist_post_sig[i].Draw("HIST E SAME")
        hlist_data[i].SetMarkerStyle(8)
        hlist_data[i].SetMarkerSize(0.8)
        if plotdata:
            hlist_data[i].Draw("SAME")
        leg_list[i].Draw()

        p2_list[i].cd()
        hlist_ratio[i].SetTitle("")
        hlist_ratio[i].GetYaxis().SetRangeUser(-8,8)
        hlist_ratio[i].GetYaxis().SetTitle("(Fit-Data)/Sqrt(Data)")
        hlist_ratio[i].GetYaxis().SetTitleSize(0.1)
        hlist_ratio[i].GetYaxis().SetLabelSize(0.05)
        hlist_ratio[i].GetXaxis().SetTitle("N Jets")        
        hlist_ratio[i].GetXaxis().SetLabelSize(0.05)
        hlist_ratio[i].GetXaxis().SetTitleSize(0.1)        
       
        hlist_ratio[i].Draw("p")
        
        c1.Update()

    c1.SaveAs(fitName + ".png")

if __name__ == '__main__':
    prefit = "pseudoDataS.root"
    pre_path = "/uscms/home/bcrossma/nobackup/analysis/CMSSW_10_2_13/src/CombineFits/DataCardProducer/{}".format(prefit)
    post_path = "/uscms/home/bcrossma/nobackup/analysis/CMSSW_10_2_13/src/CombineFits/DataCardProducer/higgsCombineTest.FitDiagnostics.mH550.root"
    fitDiag_path = "/uscms/home/bcrossma/nobackup/analysis/CMSSW_10_2_13/src/CombineFits/DataCardProducer/fitDiagnostics.root"
    signal = "SYY_550"

    make_fit_plots(prefit, signal, pre_path, post_path, fitDiag_path, True, True, True, True, "pseudoDataS", "test.root")


