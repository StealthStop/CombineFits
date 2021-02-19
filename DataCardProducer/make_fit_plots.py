import ROOT
import copy
from optparse import OptionParser

from ROOT import kRed, kBlue, kBlack
from ROOT import gStyle

parser = OptionParser()
parser.add_option("-p", "--path",   action="store",  type="string",  dest="path", default="fitDiagnostics.root", help = "Path to fitDiagnostics root file containing post-fit event counts")

(options, args) = parser.parse_args()

gStyle.SetOptStat(0)

borderSize = 0.20
pad1and4Size = 1.0 + borderSize
pad2and3Size = 1.0
totalPadSize = 2 * pad1and4Size + 2 * pad2and3Size

def getFitInfo(pre_path, post_path, w_name):
    f_pre = ROOT.TFile.Open(pre_path, "READ")
    f_post = ROOT.TFile.Open(post_path, "READ")

    w_pre = f_pre.Get(w_name)
    w_post = f_post.Get(w_name)

    prefit_sb = {} 
    prefit_b = {}

    postfit_sb = {}
    postfit_b = {}

    for reg in ["A", "B", "C", "D"]:
        prefit_sb[reg] = []
        prefit_b[reg] = []
        
        postfit_sb[reg] = []
        postfit_b[reg] = []
        
        for i in range(7,12):
            postfit_sb[reg].append((i, w_post.function("n_exp_bin{}{}".format(reg,i))))
            postfit_b[reg].append((i, w_post.function("n_exp_bin{}{}_bonly".format(reg,i))))
            prefit_sb[reg].append((i, w_pre.function("n_exp_bin{}{}".format(reg,i))))
            prefit_b[reg].append((i, w_pre.function("n_exp_bin{}{}_bonly".format(reg,i))))

    f_pre.Close()
    f_post.Close()

    return prefit_b, prefit_sb, postfit_b, postfit_sb 

def makeHist(reg, bin_info):
    h = ROOT.TH1D("Region {}".format(reg), "Region {}".format(reg), 5, 7, 12)

    bins = bin_info["{}".format(reg)]

    for b in bins:
        h.Fill(b[0], b[1].getVal())

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

def main():
    pre_path = "/uscms/home/bcrossma/nobackup/analysis/CMSSW_10_2_13/src/CombineFits/DataCardProducer/myDataCard.root"
    post_path = "/uscms/home/bcrossma/nobackup/analysis/CMSSW_10_2_13/src/CombineFits/DataCardProducer/higgsCombineTest.FitDiagnostics.mH550.root"

    ROOT.TH1.AddDirectory(False)

    pre_b, pre_sb, post_b, post_sb = getFitInfo(pre_path, post_path, 'w')

    hlist_pre_b = []
    hlist_post_b = []
    hlist_pre_sb = []
    hlist_post_sb = []

    for reg in ["A", "B", "C", "D"]:
        hlist_pre_b.append(makeHist(reg, pre_b))
        hlist_post_b.append(makeHist(reg, post_b))
        hlist_pre_sb.append(makeHist(reg, pre_sb))
        hlist_post_sb.append(makeHist(reg, post_sb))


    for i in range(len(hlist_pre_b)):
        hlist_post_sb[i].SetLineColor(kRed)
        hlist_pre_b[i].SetLineColor(kBlack)

    hlist_ratio = []
    for i in range(0,4):
        h_temp = copy.copy(hlist_post_sb[i])
        h_temp.Divide(hlist_post_b[i])
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
        l.AddEntry(hlist_post_sb[i], "Post S+B", "l")
        l.AddEntry(hlist_post_b[i], "Post B", "l")
        l.AddEntry(hlist_pre_b[i], "Pre B", "l")
        l.Draw()
    
        leg_list.append(l)

    for i in range(len(p1_list)):
        p1_list[i].cd()
        
        hlist_post_sb[i].GetYaxis().SetTitle("Num. Events (A.U.)")
        hlist_post_sb[i].GetXaxis().SetTitle("N Jets")

        hlist_post_sb[i].Draw("HIST SAME")
        hlist_post_b[i].Draw("HIST SAME")
        hlist_pre_b[i].Draw("HIST SAME")
        leg_list[i].Draw()

        p2_list[i].cd()
        hlist_ratio[i].SetTitle("")
        hlist_ratio[i].GetYaxis().SetRangeUser(0.6, 1.4)
        hlist_ratio[i].GetYaxis().SetTitle("S+B/B")
        hlist_ratio[i].GetYaxis().SetTitleSize(0.1)
        hlist_ratio[i].GetYaxis().SetLabelSize(0.05)
        hlist_ratio[i].GetXaxis().SetTitle("N Jets")        
        hlist_ratio[i].GetXaxis().SetLabelSize(0.05)
        hlist_ratio[i].GetXaxis().SetTitleSize(0.1)        
       
        hlist_ratio[i].Draw("p")
        
        c1.Update()

    c1.SaveAs("test.png")

if __name__ == '__main__':
    main()


