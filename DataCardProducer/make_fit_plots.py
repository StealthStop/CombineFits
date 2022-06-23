from optparse import OptionParser

parser = OptionParser()
parser.add_option("-s", "--signal", action="store", type="string", dest="signal", default="StealthSYY", help="Signal process name")
parser.add_option("-y", "--year", action="store", type="string", dest="year", default="2016", help="Year for data used")
parser.add_option("-m", "--mass", action="store", type="string", dest="mass", default="350", help="Mass of stop in GeV")
parser.add_option("-d", "--dataType", action="store", type="string", dest="dataType", default="pseudoData", help="Mass of stop in GeV")
parser.add_option("--suffix", action="store", type="string", dest="suffix", default="0l", help="Suffix to specify number of final state leptons (0l, 1l, or combo)")
parser.add_option("-p", "--path", action="store", type="string", dest="path", default="../condor/Fit_2016", help="Path to Fit Diagnostics input condor directory")
parser.add_option("--setClosure", action="store_true", dest="setClosure", default=False, help="Use fit files with perfect closure asserted")
parser.add_option("-n", "--njets", action="store", type="string", dest="njets", default="7-12", help="Range of Njets bins to plot (separated by a dash)")
parser.add_option("--plotb", action="store_true", dest="plotb", default=False, help="Plot background only fit")
parser.add_option("--plotsb", action="store_true", dest="plotsb", default=False, help="Plot signal plus background fit")
parser.add_option("--plotsig", action="store_true", dest="plotsig", default=False, help="Plot signal component of fit")
parser.add_option("--plotdata", action="store_true", dest="plotdata", default=False, help="Plot distributions observed in data")
parser.add_option("--all", action="store_true", dest="all", default=False, help="Make all pre and post fit distributions (for 0l and 1l, pseudoData/S, RPV and SYY)")

(options, args) = parser.parse_args()

import ROOT
import copy
import time
import os
from math import sqrt

from ROOT import kRed, kBlue, kBlack, kCyan, kGreen
from ROOT import gStyle

gStyle.SetOptStat(0)
ROOT.TH1.AddDirectory(False)
ROOT.TH1.SetDefaultSumw2(1)
ROOT.TH2.SetDefaultSumw2()
ROOT.gStyle.SetEndErrorSize(0)

if options.all:
    ROOT.gROOT.SetBatch(True)

borderSize = 0.20
pad1and4Size = 1.0 + borderSize
pad2and3Size = 1.0
totalPadSize = 2 * pad1and4Size + 2 * pad2and3Size

def getFitInfo(fitDiag_path, pre_path, signal, year, suf, njets):
    f_fit = ROOT.TFile.Open(fitDiag_path, "READ")
    f_pre = ROOT.TFile.Open(pre_path)

    w = f_pre.Get("w")

    data = {}
    data_unc = {}

    prefit_sb = {} 
    prefit_b = {}
    postfit_sb = {}
    postfit_b = {}
    postfit_sig = {}

    for reg in ["A", "B", "C", "D"]:
        prefit_sb[reg] = []
        prefit_b[reg] = []
        postfit_sb[reg] = []
        postfit_b[reg] = []
        postfit_sig[reg] = []       
 
        data[reg] = []

        for i in range(njets[0],njets[1]):
            try:
                postfit_sb[reg].append((i, 
                    f_fit.Get("shapes_fit_s/Y{}_{}{}_{}/total".format(year[-2:],reg,i,suf)).GetBinContent(1),
                    f_fit.Get("shapes_fit_s/Y{}_{}{}_{}/total".format(year[-2:],reg,i,suf)).GetBinError(1)
                    ))
                postfit_b[reg].append((i, 
                    f_fit.Get("shapes_fit_b/Y{}_{}{}_{}/total".format(year[-2:],reg,i,suf)).GetBinContent(1),
                    f_fit.Get("shapes_fit_b/Y{}_{}{}_{}/total".format(year[-2:],reg,i,suf)).GetBinError(1)
                    ))
                #prefit_sb[reg].append((i, w_pre.function("shapes_prefit/{}{}/".format(reg,i))))
                prefit_b[reg].append((i, 
                    f_fit.Get("shapes_prefit/Y{}_{}{}_{}/total".format(year[-2:],reg,i,suf)).GetBinContent(1),
                    f_fit.Get("shapes_prefit/Y{}_{}{}_{}/total".format(year[-2:],reg,i,suf)).GetBinError(1)
                    ))
                postfit_sig[reg].append((i, 
                    f_fit.Get("shapes_fit_s/Y{}_{}{}_{}/total_signal".format(year[-2:],reg,i,suf)).GetBinContent(1),
                    f_fit.Get("shapes_fit_s/Y{}_{}{}_{}/total_signal".format(year[-2:],reg,i,suf)).GetBinError(1)
                    ))
            except Exception as e:
                print("Fit for {}_{}_{} Failed".format(year, signal, suf))
                return
            data[reg].append((i, 
                w.set("observables").getRealValue("n_obs_binY{}_{}{}_{}".format(year[-2:],reg,i,suf)),
                sqrt(w.set("observables").getRealValue("n_obs_binY{}_{}{}_{}".format(year[-2:],reg,i,suf))),
                ))

    f_fit.Close()
    f_pre.Close()

    return prefit_b, postfit_b, postfit_sb, postfit_sig, data

def makeHist(reg, bin_info, tag, njets):
    h = ROOT.TH1D("Region{}{}".format(reg, tag), "Region {}".format(reg), njets[1]-njets[0], njets[0], njets[1])

    bins = bin_info[reg]

    for i in range(len(bins)):
        if type(bins[i][1]) != float:
            h.Fill(bins[i][0], bins[i][1])
        else:
            h.Fill(bins[i][0], bins[i][1])
        h.SetBinError(i+1, bins[i][2])

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

def make_fit_plots(signal, year, pre_path, fitDiag_path, suf, plotb, plotsb, plotdata, plotsig, fitName, outfile, obs, njets, path):
    close = ""
    if pre_path.find("perfectClose") != -1:
        close += "_perfectClose"
    im = ROOT.TImageDump(path + "/figures/" + year + "_" + signal + "_" + fitName + "_" + suf + close + ".png")
    try: 
        pre_b, post_b, post_sb, post_sig, data = getFitInfo(fitDiag_path, pre_path, signal, year, suf, njets)
    except:
        print("Fit for {}_{}_{} Failed".format(year, signal, suf))
        return
    hlist_data = []
    hlist_pre_b = []
    hlist_post_b = []
    hlist_post_sb = []
    hlist_post_sig = []

    for reg in ["A", "B", "C", "D"]:
        hlist_data.append(makeHist(reg, obs, "_data", njets))
        hlist_pre_b.append(makeHist(reg, pre_b, "_pre_bonly", njets))
        hlist_post_b.append(makeHist(reg, post_b, "_post_bonly", njets))
        hlist_post_sb.append(makeHist(reg, post_sb, "_post_sb", njets))
        hlist_post_sig.append(makeHist(reg, post_sig, "_post_signal", njets))

    #save_to_root(hlist_data, outfile)
    #save_to_root(hlist_pre_b, outfile)
    #save_to_root(hlist_post_b, outfile)
    #save_to_root(hlist_post_sb, outfile)
    #save_to_root(hlist_post_sig, outfile)
 
    for i in range(len(hlist_pre_b)):
        hlist_post_b[i].SetLineColor(kBlue)
        hlist_post_sb[i].SetLineColor(kRed)
        hlist_post_b[i].SetFillColor(kBlue)
        hlist_post_sb[i].SetFillColor(kRed)
        hlist_post_b[i].SetFillStyle(3001)
        hlist_post_sb[i].SetFillStyle(3001)
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
            if data_e == 0.0:
                pull = 0
            else:
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
            l.AddEntry(hlist_data[i], "Data", "p")
        if plotsig:
            l.AddEntry(hlist_post_sig[i], "{}".format(signal), "l")
    
        leg_list.append(l)

    for i in range(len(p1_list)):
        p1_list[i].cd()
        
        hlist_post_sig[i].GetYaxis().SetTitle("Num. Events (A.U.)")
        hlist_post_sig[i].GetXaxis().SetTitle("N Jets")
        hlist_post_sig[i].GetYaxis().SetRangeUser(10, 2E5)
        
        hlist_post_sb[i].GetYaxis().SetTitle("Num. Events (A.U.)")
        hlist_post_sb[i].GetXaxis().SetTitle("N Jets")
        hlist_post_sb[i].GetYaxis().SetRangeUser(10, 2E5)
        
        hlist_post_b[i].GetYaxis().SetTitle("Num. Events (A.U.)")
        hlist_post_b[i].GetXaxis().SetTitle("N Jets")
        hlist_post_b[i].GetYaxis().SetRangeUser(10, 2E5)
        
        if plotsig:
            hlist_post_sig[i].Draw("HIST E SAME")
        if plotb:
            hlist_post_b[i].Draw("E2 SAME")
        if plotsb:
            hlist_post_sb[i].Draw("E2 SAME")
        hlist_data[i].SetMarkerStyle(8)
        hlist_data[i].SetMarkerSize(0.8)
        if plotdata:
            hlist_data[i].Draw("SAME E")
        leg_list[i].Draw()

        p2_list[i].cd()
        hlist_ratio[i].SetTitle("")
        hlist_ratio[i].GetYaxis().SetRangeUser(-1.2,1.2)
        hlist_ratio[i].GetYaxis().SetTitle("(Fit-Data)/Sqrt(Data)")
        hlist_ratio[i].GetYaxis().SetTitleSize(0.1)
        hlist_ratio[i].GetYaxis().SetLabelSize(0.05)
        hlist_ratio[i].GetXaxis().SetTitle("N Jets")        
        hlist_ratio[i].GetXaxis().SetLabelSize(0.05)
        hlist_ratio[i].GetXaxis().SetTitleSize(0.1)        
       
        hlist_ratio[i].Draw("p")
        
        c1.Update()
        c1.Paint()

    im.Close()
    #c1.SaveAs("figures/" + year + "_" + signal + "_" + fitName + "_" + suf + ".png")

def getObs(card, njets):
    with open(card, "r") as f:
        lines = f.readlines()

        data_temp = []

        for l in lines:
            if l.find("observation") != -1:
                data_temp = l.split(" ")[1:-1]
        
        data = {'A': [], 'B': [], 'C': [], 'D': []}
        ABCD = ['A','B','C','D']
       
        for i, reg in enumerate(ABCD):
            for j in range(0,njets[1]-njets[0]):
                data[reg].append((njets[0]+j,float(data_temp[i*(njets[1]-njets[0])+j]), sqrt(float(data_temp[i*(njets[1]-njets[0])+j]))))

        return data

def main():    
    if not os.path.exists("figures"):
        os.makedirs("figures")

    if not os.path.exists("results"):
        os.makedirs("results")

    ROOT.gROOT.SetBatch(True)

    njets = [int(options.njets[:options.njets.find("-")]),int(options.njets[options.njets.find("-")+1:])+1]

    print("Making pre and post fit distributions for:")
    if options.all:
        signals = ["RPV", "StealthSYY"]
        masses = [m for m in range(300, 1450, 50)]
        dataTypes = ["pseudoData", "pseudoDataS"]
        suffixes = ["0l", "1l"]
        close = ""
        if options.setClosure:
            close = "_perfectClose"
        for suf in suffixes:
            for d in dataTypes:
                for s in signals:
                    for m in masses:
                        print("Year: {}\t Signal: {}\t Mass: {}\t Final State: {}\t Data Type: {}".format(options.year, s, m, suf, d))
                        card = "{}/output-files/cards/{}_{}_{}_{}_{}{}.txt".format(options.path, options.year, s, m, d, suf, close)
                        obs = getObs(card, njets)
                        path = "{}/output-files/{}_{}_{}".format(options.path, s, m, options.year)
                        prefit = "ws_{}_{}_{}_{}_{}{}.root".format(options.year, s, m, d, suf, close)
                        postfit = "higgsCombine{}{}{}{}{}{}.FitDiagnostics.mH{}.MODEL{}.root".format(options.year, s, m, d, suf, m, s, close[1:])
                        fitDiag = "fitDiagnostics{}{}{}{}{}{}.root".format(options.year, s, m, d, suf, close[1:])
                        
                        pre_path = "{}/{}".format(path, prefit)
                        post_path = "{}/{}".format(path, postfit) 
                        fitDiag_path = "{}/{}".format(path, fitDiag)
                        signal = "{}_{}".format(s, m)
                        
                        name = "{}_{}_{}_{}_{}{}".format(options.year, s, m, d, suf, close)

                        if not os.path.isdir(path + "/figures/"):
                            os.makedirs(path + "/figures/")

                        make_fit_plots(signal, options.year, pre_path, fitDiag_path, suf, True, False, True, False, "{}_bonly".format(d), "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)
                        make_fit_plots(signal, options.year, pre_path, fitDiag_path, suf, True, True, True, True, "{}_sb".format(d), "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)
    else:
        signals = ["RPV"]
        masses = [350, 550, 850]
        dataTypes = ["pseudoData", "pseudoDataS"]
        suffixes = ["1l"]
        close = ""
        if options.setClosure:
            close = "_perfectClose"
        
        for suf in suffixes:
            for d in dataTypes:
                for s in signals:
                    for m in masses:
                        print("Year: {}\t Signal: {}\t Mass: {}\t Final State: {}\t Data Type: {}".format(options.year, s, m, suf, d))
                        card = "{}_{}_{}_{}_{}{}.txt".format(options.year, s, m, d, suf, close)
                        obs = getObs(card, njets)
                        path = "{}/output-files/{}_{}_{}".format(options.path, s, m, options.year)
                        prefit = "ws_{}_{}_{}_{}_{}{}.root".format(options.year, s, m, d, suf, close)
                        postfit = "higgsCombine{}{}{}{}{}{}.FitDiagnostics.mH{}.MODEL{}.root".format(options.year, s, m, d, suf, close[1:], m, s)
                        fitDiag = "fitDiagnostics{}{}{}{}{}{}.root".format(options.year, s, m, d, suf, close[1:])
                        
                        pre_path = "{}/{}".format(path, prefit)
                        post_path = "{}/{}".format(path, postfit) 
                        fitDiag_path = "{}/{}".format(path, fitDiag)
                        signal = "{}_{}".format(s, m)
                        
                        name = "{}_{}_{}_{}_{}{}".format(options.year, s, m, d, suf, close)

                        make_fit_plots(signal, options.year, pre_path, fitDiag_path, suf, True, False, True, False, "{}_bonly".format(d), "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)
                        make_fit_plots(signal, options.year, pre_path, fitDiag_path, suf, True, True, True, True, "{}_sb".format(d), "{}/results/{}_FitPlots.root".format(path, name), obs, njets, path)
        
    
                
if __name__ == '__main__':
    main()
