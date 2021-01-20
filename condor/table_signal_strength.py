# make a table of the signal strength and associated signifances. 
# Do this for every signal point

# First do it in Data, for 2016, 2017, 2018pre, 2018post, and Combo
import optparse
import ROOT
from array import array

def makePValuePlot(dataSet, approved):
    # CL observed pvalues
    pvalue_2016 = dataSet["data"]["2016"]["pList"]
    pvalue_2017 = dataSet["data"]["2017"]["pList"]
    pvalue_2018pre = dataSet["data"]["2018pre"]["pList"]
    pvalue_2018post = dataSet["data"]["2018post"]["pList"]
    pvalue_Combo = dataSet["data"]["Combo"]["pList"]
    print pvalue_2016
    print pvalue_2017
    print pvalue_2018pre
    print pvalue_2018post
    print pvalue_Combo
    xpoints = dataSet["data"]["2016"]["mList"]
    npoints = len(pvalue_2016)
    Xmin = 300
    Xmax = 1200
    Ymin = 0.00005
    #if dataSet["runtype"].find("pseudoDataS") != -1 or dataSet["runtype"].find("pseudodataS") != -1 or dataSet["runtype"] == "Data":
    if dataSet["runtype"].find("pseudoDataS") != -1 or dataSet["runtype"].find("pseudodataS") != -1:
        Ymin = 5.0e-37
    Ymax = 1

    numSigma = 3
    if dataSet["runtype"].find("pseudoData") != -1: numSigma = 8

    c1 = ROOT.TCanvas("c1","PValues",1000,1000)
    c1.Divide(1, 2)    
    c1.SetFillColor(0)
    c1.cd(1)
    ROOT.gPad.SetPad("p1", "p1", 0, 2.5 / 9.0, 1, 1, ROOT.kWhite, 0, 0)
    ROOT.gPad.SetBottomMargin(0.01)
    ROOT.gPad.SetLeftMargin(0.11)
    ROOT.gPad.SetRightMargin(0.04)
    ROOT.gPad.SetTopMargin(0.06 * (8.0 / 6.5))
    ROOT.gPad.SetLogy()
    ROOT.gPad.SetTicks(1,1)

    h = ROOT.TH1F("dummy","dummy",1, Xmin, Xmax)
    h.SetMaximum(Ymax)
    h.SetMinimum(Ymin)
    h.SetTitle("")
    h.SetStats(0)
    h.GetXaxis().SetLimits(Xmin,Xmax)
    h.GetXaxis().SetLabelSize(0.05)
    h.GetXaxis().SetTitleSize(0.05)
    h.GetYaxis().SetLabelSize(0.05)
    h.GetYaxis().SetTitleSize(0.05)
    h.GetYaxis().SetTitleOffset(1.1)
    h.GetXaxis().SetTitle("m_{#tilde{t}} [GeV]")
    h.GetYaxis().SetTitle("Local p-value")
    h.GetYaxis().SetNdivisions(4,2,0)
    h.Draw()

    gr_Combo = ROOT.TGraph(npoints, array('d', xpoints), array('d', pvalue_Combo))
    gr_Combo.SetLineColor(ROOT.kBlack)
    gr_Combo.SetLineWidth(3)
    gr_Combo.Draw("same")

    gr_2016 = ROOT.TGraph(npoints, array('d', xpoints), array('d', pvalue_2016))
    gr_2016.SetLineColor(ROOT.kRed+1)
    gr_2016.SetLineStyle(4)
    gr_2016.SetLineWidth(3)

    gr_2017 = ROOT.TGraph(npoints, array('d', xpoints), array('d', pvalue_2017))
    gr_2017.SetLineColor(ROOT.kBlue+1)
    gr_2017.SetLineStyle(3)
    gr_2017.SetLineWidth(3)

    gr_2018pre = ROOT.TGraph(npoints, array('d', xpoints), array('d', pvalue_2018pre))
    gr_2018pre.SetLineColor(ROOT.kGreen+1)
    gr_2018pre.SetLineStyle(2)
    gr_2018pre.SetLineWidth(3)

    gr_2018post = ROOT.TGraph(npoints, array('d', xpoints), array('d', pvalue_2018post))
    gr_2018post.SetLineColor(ROOT.kOrange+1)
    gr_2018post.SetLineStyle(7)
    gr_2018post.SetLineWidth(3)

    # Draw the 1sigma, 2sigma, and 3sigma lines
    # For 1 sigma: s = 0.68
    #   1 - (0.5 + s/2) = 0.5 - s/2
    entries = []
    for s in range(1, numSigma+1):
        sigma = 0.5 - ROOT.TMath.Erf(float(s)/ROOT.TMath.Sqrt(2.0))/2.0
        L = ROOT.TLine(Xmin, sigma, Xmax, sigma)
        L.SetLineColor(2)
        L.SetLineWidth(2)
        L.Draw("same")

        S = ROOT.TPaveText(Xmax+16,sigma-0.25*sigma,Xmax+30,sigma+0.5*sigma,"")
        S.SetBorderSize(0)
        S.SetFillStyle(0)
        S.SetTextColor(2)
        S.SetTextSize(0.045)
        S.AddText( str(s)+"#sigma" )
        S.Draw("same")
        entries.append((L,S))

    gr_2016.Draw("L,same")
    gr_2017.Draw("L,same")
    gr_2018pre.Draw("L,same")
    gr_2018post.Draw("L,same")
    gr_Combo.Draw("L,same")

    #process = ROOT.TLatex()
    #process.SetTextSize(0.056)

    legend1 = ROOT.TLegend(0.20, 0.03, 0.83, 0.29,"")
    legend1.SetNColumns(2)
    legend1.SetTextSize(0.05)
    if   dataSet["model"]=="RPV": legend1.SetHeader("pp #rightarrow #tilde{t} #bar{#tilde{t}}, #tilde{t} #rightarrow t #tilde{#chi}^{0}_{1},  #tilde{#chi}^{0}_{1} #rightarrow jjj");
    elif dataSet["model"]=="StealthSYY": legend1.SetHeader("pp #rightarrow #tilde{t} #bar{#tilde{t}}, #tilde{t} #rightarrow t#tilde{S}g, #tilde{S} #rightarrow S#tilde{G}, S #rightarrow gg");
    elif dataSet["model"]=="StealthSHH": legend1.SetHeader("pp #rightarrow #tilde{t} #bar{#tilde{t}}, SHH coupling");
    legend1.AddEntry(gr_Combo, "All Years (137 fb^{-1})", "l")
    legend1.AddEntry(gr_Combo, " ", "")
    legend1.AddEntry(gr_2016, "2016 (35.9 fb^{-1})", "l")
    legend1.AddEntry(gr_2018pre, "2018A (21.1 fb^{-1})", "l")
    legend1.AddEntry(gr_2017, "2017 (41.5 fb^{-1})", "l")
    legend1.AddEntry(gr_2018post, "2018B (38.7 fb^{-1})", "l")
    legend1.SetBorderSize(0)
    legend1.SetFillStyle(0)
    legend1.Draw("same")

    #legend2 = ROOT.TLegend(0.35, 0.31, 0.80, 0.58, "")
    #legend2.SetNColumns(2)
    #legend2.SetTextSize(0.04)
    #legend2.AddEntry(gr_Combo, "L_{Int} = 137 fb^{-1}", "l")
    #legend2.AddEntry(gr_Combo, " ", "")
    #legend2.AddEntry(gr_2016, "L_{Int} = 35.9 fb^{-1}", "l")
    #legend2.AddEntry(gr_2018pre, "L_{Int} = 21.1 fb^{-1}", "l")
    #legend2.AddEntry(gr_2017, "L_{Int} = 41.5 fb^{-1}", "l")
    #legend2.AddEntry(gr_2018post, "L_{Int} = 38.7 fb^{-1}", "l")
    #legend2.SetBorderSize(0)
    #legend2.SetFillStyle(0)
    #legend2.Draw("same")

    cmstext = ROOT.TLatex()
    cmstext.SetNDC(True)

    cmstext.SetTextAlign(11)
    cmstext.SetTextSize(0.060)
    cmstext.SetTextFont(61)
    cmstext.DrawLatex(ROOT.gPad.GetLeftMargin(), 1 - (ROOT.gPad.GetTopMargin() - 0.017), "CMS")
    cmstext.SetTextFont(52)
    if not approved: cmstext.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.095, 1 - (ROOT.gPad.GetTopMargin() - 0.017), "Preliminary")

    cmstext.SetTextFont(42)
    cmstext.SetTextAlign(31)
    cmstext.DrawLatex(1 - ROOT.gPad.GetRightMargin(), 1 - (ROOT.gPad.GetTopMargin() - 0.017), "137 fb^{-1} (13 TeV)")

    c1.Update()
    c1.cd(2)
    ROOT.gPad.SetPad("p2", "p2", 0, 0, 1, 2.5 / 9.0, ROOT.kWhite, 0, 0)
    ROOT.gPad.SetLeftMargin(0.11)
    ROOT.gPad.SetRightMargin(0.04)
    ROOT.gPad.SetTopMargin(0.01)
    ROOT.gPad.SetBottomMargin(0.37)
    ROOT.gPad.SetTicks(1,1)

    # Make ratio of Data over total stack
    hr = ROOT.TH1F("dummyr","dummyr",1, Xmin, Xmax)
    hr.SetStats(0)
    hr.SetTitle("")
    hr.GetXaxis().SetTitle("m_{ #tilde{t}} [GeV]")
    hr.GetYaxis().SetTitle("#sigma_{meas.}/#sigma_{pred.}")
    hr.GetXaxis().SetLimits(Xmin,Xmax)
    hr.GetXaxis().SetLabelSize(0.14)
    hr.GetXaxis().SetTitleSize(0.15)
    hr.GetYaxis().SetLabelSize(0.13)
    hr.GetYaxis().SetTitleSize(0.15)
    hr.GetYaxis().SetTitleOffset(0.3)
    hr.SetLineWidth(0)
    maxR = 1.0 
    hr.GetYaxis().SetRangeUser(-0.1, maxR*1.3)
    hr.GetYaxis().SetNdivisions(4, 2, 0)
    hr.Draw()
    
    rvalue_Combo = array('d', dataSet["data"]["Combo"]["rList"])
    rpvalue_Combo = array('d',dataSet["data"]["Combo"]["rpList"])
    rmvalue_Combo = array('d', dataSet["data"]["Combo"]["rmList"])
    zero = array('d', dataSet["data"]["2016"]["zero"])
    rband = ROOT.TGraphAsymmErrors(npoints, array('d', xpoints), rvalue_Combo, zero, zero, rmvalue_Combo, rpvalue_Combo)
    rband.SetFillColor(ROOT.kGreen+1)
    rband.Draw("3 same")
    r = ROOT.TGraph(npoints, array('d', xpoints), rvalue_Combo)
    r.SetLineColor(ROOT.kBlack)
    r.SetLineStyle(ROOT.kDashed)
    r.SetLineWidth(3)
    r.Draw("PL same")
    c1.Update()
    
    line = ROOT.TF1("line", "1", Xmin, Xmax)
    line.SetLineColor(ROOT.kRed)
    line.Draw("same")
    
    line2 = ROOT.TF1("line", "1", Xmin, Xmax)
    line2.SetLineColor(ROOT.kBlack)
    line2.Draw("same")

    if approved:
        c1.Print(dataSet["runtype"]+"_"+dataSet["model"]+dataSet["pdfName"]+".pdf")
    else:
        c1.Print(dataSet["runtype"]+"_"+dataSet["model"]+dataSet["pdfName"]+"_prelim.pdf")
    del c1

def makePValuePlotAlt(dataSet):
    tm = 0.30; bm = 0.23; lm = 0.11; rm = 0.03

    #split4 = 0.318792; split1 = 0.234899; split2 = 0.223154
    #ratio4 = split2 / split4; ratio1 = split2 / split1

    split4 = 0.360825; split1 = 0.206186; split2 = 0.14433
    ratio4 = split2 / split4; ratio1 = split2 / split1

    xl = 0.20; yl = 0.20; zl = 0.20; xt = 0.25; yt = 0.22; zt = 0.25; xo = 0.40; yo = 0.25; zo = 0.4 

    # CL observed pvalues
    pvalue_2016 = dataSet["data"]["2016"]["pList"]
    pvalue_2017 = dataSet["data"]["2017"]["pList"]
    pvalue_2018pre = dataSet["data"]["2018pre"]["pList"]
    pvalue_2018post = dataSet["data"]["2018post"]["pList"]
    pvalue_Combo = dataSet["data"]["Combo"]["pList"]
    print pvalue_2016
    print pvalue_2017
    print pvalue_2018pre
    print pvalue_2018post
    print pvalue_Combo
    xpoints = dataSet["data"]["2016"]["mList"]
    npoints = len(pvalue_2016)
    Xmin = 300
    Xmax = 1200
    Ymin = 0.00005
    numSig = 3
    #if dataSet["runtype"].find("pseudoDataS") != -1 or dataSet["runtype"].find("pseudodataS") != -1 or dataSet["runtype"] == "Data":
    if dataSet["runtype"].find("pseudoDataS") != -1 or dataSet["runtype"].find("pseudodataS") != -1:
        Ymin = 1.0e-26
        numSig = 8
    Ymax = 0.99 

    c1 = ROOT.TCanvas("c1","PValues",2000,1800)
    c1.Divide(1, 5)    
    c1.SetFillColor(0)

    # Make ratio of Data over total stack
    hr = ROOT.TH1F("dummyr","dummyr",1, Xmin, Xmax)
    hr.SetStats(0)
    hr.SetTitle("")
    hr.SetLineWidth(0)
    hr.GetXaxis().SetTitle("m_{ #tilde{t}} [GeV]")
    hr.GetYaxis().SetTitle("#sigma_{meas.}/#sigma_{pred.}")
    hr.GetXaxis().SetLimits(Xmin,Xmax)
    hr.GetXaxis().SetLabelSize(0.14)
    hr.GetXaxis().SetTitleSize(0.15)
    hr.GetYaxis().SetLabelSize(0.13)
    hr.GetYaxis().SetTitleSize(0.15)
    hr.GetYaxis().SetTitleOffset(yo)
    hr.SetLineWidth(0)
    maxR = 1.0 
    hr.GetYaxis().SetRangeUser(-0.1, maxR*1.3)
    hr.GetYaxis().SetNdivisions(4, 2, 0)

    hr2017 = hr.Clone("2017"); hr2018pre = hr.Clone("2018pre"); hr2018post = hr.Clone("2018post")

    h = ROOT.TH1F("dummy","dummy",1, Xmin, Xmax)
    h.SetMaximum(Ymax)
    h.SetMinimum(Ymin)
    h.SetTitle("")
    h.SetStats(0)
    h.SetLineWidth(0)
    h.GetXaxis().SetLimits(Xmin,Xmax)
    h.GetXaxis().SetLabelSize(xl*ratio4)
    h.GetXaxis().SetTitleSize(xt*ratio4)
    h.GetYaxis().SetLabelSize(yl*ratio4)
    h.GetYaxis().SetTitleSize(yt*ratio4)
    h.GetYaxis().SetTitleOffset(yo/ratio4)
    h.GetXaxis().SetTitleOffset(xo/ratio4)
    h.GetXaxis().SetTitle("m_{#tilde{t}} [GeV]")
    h.GetYaxis().SetTitle("Local p-value")
    h.GetYaxis().SetNdivisions(6, 1, 0, False)

    c1.cd(5)
    ROOT.gPad.SetLogy()
    ROOT.gPad.SetPad(0, 0.0, 1, split4)
    ROOT.gPad.SetTopMargin(0.0)
    ROOT.gPad.SetBottomMargin(bm)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)
    h.Draw()

    gr_Combo = ROOT.TGraph(npoints, array('d', xpoints), array('d', pvalue_Combo))
    gr_Combo.SetLineColor(ROOT.kBlack)
    gr_Combo.SetLineWidth(3)
    gr_Combo.Draw("same")

    gr_2016 = ROOT.TGraph(npoints, array('d', xpoints), array('d', pvalue_2016))
    gr_2016.SetLineColor(ROOT.kRed+1)
    gr_2016.SetLineStyle(4)
    gr_2016.SetLineWidth(3)

    gr_2017 = ROOT.TGraph(npoints, array('d', xpoints), array('d', pvalue_2017))
    gr_2017.SetLineColor(ROOT.kBlue+1)
    gr_2017.SetLineStyle(1)
    gr_2017.SetLineWidth(3)

    gr_2018pre = ROOT.TGraph(npoints, array('d', xpoints), array('d', pvalue_2018pre))
    gr_2018pre.SetLineColor(ROOT.kGreen+1)
    gr_2018pre.SetLineStyle(2)
    gr_2018pre.SetLineWidth(3)

    gr_2018post = ROOT.TGraph(npoints, array('d', xpoints), array('d', pvalue_2018post))
    gr_2018post.SetLineColor(ROOT.kOrange+1)
    gr_2018post.SetLineStyle(3)
    gr_2018post.SetLineWidth(3)

    legend1 = ROOT.TLegend(0.50, 0.26, 0.95, 0.46,"")
    legend1.SetNColumns(2)
    if dataSet["model"]=="RPV":
        legend1.AddEntry(ROOT.TObject(), "pp #rightarrow #tilde{t}#bar{#tilde{t}}, #tilde{t} #rightarrow t #tilde{#chi}^{0}_{1},  #tilde{#chi}^{0}_{1} #rightarrow jjj", "");
    elif dataSet["model"]=="StealthSYY":
        legend1.AddEntry(ROOT.TObject(), "pp #rightarrow #tilde{t}#bar{#tilde{t}}, SYY coupling", "");
    elif dataSet["model"]=="StealthSHH":
        legend1.AddEntry(ROOT.TObject(), "pp #rightarrow #tilde{t}#bar{#tilde{t}}, SHH coupling", "");

    legend1.AddEntry(gr_Combo, "Combined, L_{Int}=137.2 fb^{-1}", "l")
    legend1.AddEntry(gr_2016, "2016, L_{Int}=35.9 fb^{-1}", "l")
    legend1.AddEntry(gr_2017, "2017, L_{Int}=41.5 fb^{-1}", "l")
    #legend1.AddEntry(ROOT.TObject(), "                                        ", " ")
    legend1.AddEntry(gr_2018pre, "2018pre Observed, L_{Int}=21.1 fb^{-1}", "l")
    legend1.AddEntry(gr_2018post, "2018post Observed, L_{Int}=38.7 fb^{-1}", "l")
    legend1.SetBorderSize(0)
    legend1.SetFillStyle(0)
    legend1.Draw("same")

    # Draw the 1sigma, 2sigma, and 3sigma lines
    # For 1 sigma: s = 0.68
    #   1 - (0.5 + s/2) = 0.5 - s/2
    entries = []
    for s in range(1, numSig+1):
        sigma = 0.5 - ROOT.TMath.Erf(float(s)/ROOT.TMath.Sqrt(2.0))/2.0
        L = ROOT.TLine(Xmin, sigma, Xmax, sigma)
        L.SetLineColor(2)
        L.SetLineWidth(2)
        L.Draw("same")

        S = ROOT.TPaveText(Xmax-11,sigma-0.25*sigma,Xmax+30,sigma+0.5*sigma,"")
        S.SetBorderSize(0)
        S.SetFillStyle(0)
        S.SetTextColor(2)
        S.SetTextSize(0.045)
        S.AddText( str(s)+"#sigma" )
        S.Draw("same")
        entries.append((L,S))

    gr_2016.Draw("L,same")
    gr_2017.Draw("L,same")
    gr_2018pre.Draw("L,same")
    gr_2018post.Draw("L,same")
    gr_Combo.Draw("L,same")

    # 2018post is first
    c1.cd(4)
    ROOT.gPad.SetPad(0, split4, 1, split4+split2)
    ROOT.gPad.SetTopMargin(0.0)
    ROOT.gPad.SetBottomMargin(0.0)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    hr2018post.GetXaxis().SetLabelSize(xl)
    hr2018post.GetXaxis().SetTitleSize(0.0*xt)
    hr2018post.GetYaxis().SetLabelSize(yl)
    hr2018post.GetYaxis().SetTitleSize(0.0*yt)
    hr2018post.GetYaxis().SetTitleOffset(yo/ratio4)
    hr2018post.Draw()

    rvalue_Combo = array('d', dataSet["data"]["2018post"]["rList"])
    rpvalue_Combo = array('d',dataSet["data"]["2018post"]["rpList"])
    rmvalue_Combo = array('d', dataSet["data"]["2018post"]["rmList"])
    zero = array('d', dataSet["data"]["2018post"]["zero"])
    rband2018post = ROOT.TGraphAsymmErrors(npoints, array('d', xpoints), rvalue_Combo, zero, zero, rmvalue_Combo, rpvalue_Combo)
    rband2018post.SetFillColor(ROOT.kOrange+1)
    rband2018post.Draw("3 same")
    r2018post = ROOT.TGraph(npoints, array('d', xpoints), rvalue_Combo)
    r2018post.SetLineColor(ROOT.kBlack)
    r2018post.SetLineStyle(4)
    r2018post.SetLineWidth(3)
    r2018post.Draw("PL same")

    # 2018pre is first
    c1.cd(3)
    ROOT.gPad.SetPad(0, split4+split2, 1, 2.0*split2+split4)
    ROOT.gPad.SetTopMargin(0.0)
    ROOT.gPad.SetBottomMargin(0.0)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    hr2018pre.GetXaxis().SetLabelSize(xl)
    hr2018pre.GetXaxis().SetTitleSize(0.0*xt)
    hr2018pre.GetYaxis().SetLabelSize(yl)
    hr2018pre.GetYaxis().SetTitleSize(0.0*yt)
    hr2018pre.GetYaxis().SetTitleOffset(yo)

    hr2018pre.Draw()

    rvalue_Combo = array('d', dataSet["data"]["2018pre"]["rList"])
    rpvalue_Combo = array('d',dataSet["data"]["2018pre"]["rpList"])
    rmvalue_Combo = array('d', dataSet["data"]["2018pre"]["rmList"])
    zero = array('d', dataSet["data"]["2018pre"]["zero"])
    rband2018pre = ROOT.TGraphAsymmErrors(npoints, array('d', xpoints), rvalue_Combo, zero, zero, rmvalue_Combo, rpvalue_Combo)
    rband2018pre.SetFillColor(ROOT.kGreen+1)
    rband2018pre.Draw("3 same")
    r2018pre = ROOT.TGraph(npoints, array('d', xpoints), rvalue_Combo)
    r2018pre.SetLineColor(ROOT.kBlack)
    r2018pre.SetLineStyle(3)
    r2018pre.SetLineWidth(3)
    r2018pre.Draw("PL same")

    # 2017 is first
    c1.cd(2)
    ROOT.gPad.SetPad(0, 2.0*split2+split4, 1, 3.0*split2+split4)
    ROOT.gPad.SetTopMargin(0.0)
    ROOT.gPad.SetBottomMargin(0.0)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    hr2017.GetXaxis().SetLabelSize(xl)
    hr2017.GetXaxis().SetTitleSize(0.0*xt)
    hr2017.GetYaxis().SetLabelSize(yl)
    hr2017.GetYaxis().SetTitleSize(0.0*yt)
    hr2017.GetYaxis().SetTitleOffset(yo)

    hr2017.Draw()

    rvalue_Combo = array('d', dataSet["data"]["2017"]["rList"])
    rpvalue_Combo = array('d',dataSet["data"]["2017"]["rpList"])
    rmvalue_Combo = array('d', dataSet["data"]["2017"]["rmList"])
    zero = array('d', dataSet["data"]["2017"]["zero"])
    rband2017 = ROOT.TGraphAsymmErrors(npoints, array('d', xpoints), rvalue_Combo, zero, zero, rmvalue_Combo, rpvalue_Combo)
    rband2017.SetFillColor(ROOT.kBlue+1)
    rband2017.Draw("3 same")
    r2017 = ROOT.TGraph(npoints, array('d', xpoints), rvalue_Combo)
    r2017.SetLineColor(ROOT.kBlack)
    r2017.SetLineStyle(2)
    r2017.SetLineWidth(3)
    r2017.Draw("PL same")

    # 2016 is first
    c1.cd(1)
    ROOT.gPad.SetPad(0, 1.0-split1, 1, 1.0)
    ROOT.gPad.SetTopMargin(tm)
    ROOT.gPad.SetBottomMargin(0.0)
    ROOT.gPad.SetLeftMargin(lm)
    ROOT.gPad.SetRightMargin(rm)

    hr.GetXaxis().SetLabelSize(ratio1*xl)
    hr.GetXaxis().SetTitleSize(ratio1*xt)
    hr.GetYaxis().SetLabelSize(ratio1*yl)
    hr.GetYaxis().SetTitleSize(ratio1*yt)
    hr.GetYaxis().SetTitleOffset(yo/ratio1)

    hr.Draw()

    rvalue_Combo = array('d', dataSet["data"]["2016"]["rList"])
    rpvalue_Combo = array('d',dataSet["data"]["2016"]["rpList"])
    rmvalue_Combo = array('d', dataSet["data"]["2016"]["rmList"])
    zero = array('d', dataSet["data"]["2016"]["zero"])
    rband2016 = ROOT.TGraphAsymmErrors(npoints, array('d', xpoints), rvalue_Combo, zero, zero, rmvalue_Combo, rpvalue_Combo)
    rband2016.SetFillColor(ROOT.kRed+1)
    rband2016.Draw("3 same")
    r2016 = ROOT.TGraph(npoints, array('d', xpoints), rvalue_Combo)
    r2016.SetLineColor(ROOT.kBlack)
    r2016.SetLineStyle(1)
    r2016.SetLineWidth(3)
    r2016.Draw("PL same")

    mark = ROOT.TLatex()
    mark.SetNDC(True);
    mark.SetTextAlign(11)
    mark.SetTextSize(0.20)
    mark.SetTextFont(61)
    mark.DrawLatex(lm, 1-tm+0.07, "CMS")
    mark.SetTextFont(42)
    mark.DrawLatex(1-rm-0.28, 1-tm+0.07, "137 fb^{-1} (13 TeV)")
    mark.SetTextFont(52)
    mark.DrawLatex(lm+0.085, 1-tm+0.07, "Preliminary")
    mark.Draw("same")

    #line = ROOT.TF1("line", "1", Xmin, Xmax)
    #line.SetLineColor(ROOT.kRed)
    #line.Draw("same")
    #
    #line2 = ROOT.TF1("line", "1", Xmin, Xmax)
    #line2.SetLineColor(ROOT.kBlack)
    #line2.Draw("same")

    c1.SaveAs(dataSet["runtype"]+"_"+dataSet["model"]+dataSet["pdfName"]+".pdf")
    c1.SaveAs(dataSet["runtype"]+"_"+dataSet["model"]+dataSet["pdfName"]+".C")

def makeSigTex(name, l):    
    f = open(name, 'w')

    f.write( "\\documentclass[12pt]{article}\n" )
    f.write( "\n" ) 
    f.write( "\\begin{document}\n" )
    f.write( "\\pagenumbering{gobble}\n" )
    f.write( "\n" )

    for dic in l:
        caption = ""
        if dic["runtype"] == "pseudoDataS": 
            caption = "Best fit signal strengths for %s model in MC with signal injection" % dic["model"] 
        elif dic["runtype"] == "pseudoData": 
            caption = "Best fit signal strengths for %s model in MC" % dic["model"] 
        elif dic["runtype"] == "Data":
            caption = "Best fit signal strengths for %s model in data" % dic["model"]
        else:
            caption = "Best fit signal strengths for %s in $%s$ data type" % (dic["model"],dic["runtype"]) 
        f.write( "\\begin{table}[p]\n" )
        f.write( "\\centering\n" )
        f.write( "\\caption{%s}\n" % caption )
        f.write( "\\input{%s}\n" % dic["outFileName"] )
        f.write( "\\end{table}\n" )
        f.write( "\n" )

    f.write( "\\end{document}\n" )
    f.close()

def main():
    parser = optparse.OptionParser("usage: %prog [options]\n")
    parser.add_option ('--basedir', dest='basedir',  type='string', default = '.', help="Path to output files")
    parser.add_option ('--pdfName', dest='pdfName',  type='string', default = '',  help="name to add at the end of pdf")
    parser.add_option ('--approved', dest='approved', default = False, action='store_true', help = 'Is plot approved')
    options, args = parser.parse_args()
    pdfName = "_"+options.pdfName if options.pdfName != '' else options.pdfName

    ROOT.gROOT.SetBatch(True)

    pre_tabular = """\\begin{tabular}{l l l l}
    Mass & Best fit signal strength & Observed Significance & p-value\\\\ \hline
    """    
    path = options.basedir
    #runtypes = [
    #    ("pseudoDataS",["2016","2017"]), ("pseudoDataS",["2018pre", "2018post", "Combo"]),
    #    #("pseudoData", ["2016","2017"]), ("pseudoData", ["2018pre", "2018post", "Combo"]),
    #    ]
    runtypes = [
        ("pseudoDataS",["2016","2017","2016_2017"]), ("pseudoDataS",["2018pre", "2018post", "Combo"]),
        #("pseudoData", ["2016","2017","2016_2017"]), ("pseudoData", ["2018pre", "2018post", "Combo"]),
        #("Data",       ["2016","2017","2016_2017"]), ("Data",       ["2018pre", "2018post", "Combo"]),
        ]
    #runtypes = ["Data", "pseudoData", "pseudoDataS"]
    #runtypes = ["Data", "pseudoData", "pseudoDataS", "pseudodataS_0.3xRPV_350"]
    #runtypes = ["Data", "pseudoDataS", "pseudoDataS_RPV_350", "pseudoDataS_RPV_550", "pseudoData", "pseudoData_JECUp"]
    #runtypes = ["pseudoDataS", "pseudoDataS_RPV_350", "pseudoDataS_RPV_550", "pseudoData", "pseudoData_JECUp"]
    #runtypes = ["pseudodataS_0.3xRPV_350"]
    #runtypes = ["pseudoDataS", "pseudoDataS_RPV_350", "pseudoDataS_RPV_550", "pseudoData", "pseudoData_JECUp", 
    #            "pseudodata_qcdCR", "pseudodata_2xqcdCR", "pseudodata_JECUp_JERDown_FSR", "pseudodataS_0.3xRPV_350",
    #            "pseudodata_0.2xLine", "pseudodata_0.05-0.2xLine", "pseudodata_0.05-0.2xLineNorm", "pseudodata_0.2-0.05xLine", 
    #            "pseudodataTTJets", "pseudodata_qcdCR_0.05-0.2xLine", "pseudodata_qcdCR_0.2xLine"]
    models = ["RPV","StealthSYY","StealthSHH"]
    masses = ["300","350","400","450","500","550","600","650","700","750","800","850","900","950","1000","1050","1100","1150","1200","1250","1300","1350","1400"]
    #masses = ["300","350","400","450","500","550","600","650","700","750","800","850","900"]

    # Loop over all jobs in get the info needed
    l=[]
    d=[]
    fNumber=0
    for t in runtypes:
        runtype = t[0]
        years = t[1]
        for model in models:
            outFileName = "table_signal_strength_%s_%s_%s_%i.tex" % (model, runtype, "SUX", fNumber)
            fNumber+=1
            file_table = open(outFileName,'w')
            file_table.write(pre_tabular)
            dataSet={"runtype":runtype,"model":model,"data":{},"pdfName":pdfName}
            for year in years:
                data={"mList":[],"rList":[],"rmList":[],"rpList":[],"sList":[],"pList":[],"zero":[]}
                file_table.write("\\multicolumn{4}{c}{$%s$} \\\\ \\hline \n"%year)
                for mass in masses:
                    print "Year %s, Model %s, Mass %s"%(year, model, mass)
                    filename_r = "%s/Fit_%s_%s/output-files/%s_%s_%s/log_%s%s%s_FitDiag.txt" % (path,runtype, year, model, mass, year, year, model, mass)
    
                    # Get r from fit jobs
                    info_r = ["-1","0","0"]
                    line_r = ""
                    if not ((model=="RPV" and year=="Combo" and mass=="0") or (model=="StealthSYY" and year=="Combo" and mass=="0") ):
                        file_r=-1
                        try:
                            file_r = open(filename_r)
                            for line in file_r:
                                if "Best fit r" in line:        
                                    if "Fit failed" in line:
                                        info_r = ["Fit failed"]
                                    else:
                                        line_r = line.replace("Best fit r: ","").replace("(68% CL)","").strip().replace("/", " ")
                                        info_r = line_r.split() # best fit r, -error, +error
                        except:
                            print "File not found:",filename_r 

                    # Get sigma and p-value from fit jobs
                    line_sig = "-1"
                    line_pvalue = "10"
                    if not ((model=="RPV" and year=="Combo" and mass=="0") or (model=="StealthSYY" and year=="2017" and mass in ["0"])):
                        filename_sig = "%s/Fit_%s_%s/output-files/%s_%s_%s/log_%s%s%s_Sign_sig.txt" % (path,runtype, year, model, mass, year, year, model, mass)
                        file_sig=-1
                        try:
                            file_sig = open(filename_sig)
                            for line in file_sig:
                                if "Significance:" in line:
                                    line_sig = line.replace("Significance:", "").strip()
                                elif "p-value" in line:
                                    line_pvalue = line.replace("       (p-value =", "").strip()
                                    line_pvalue = line_pvalue.replace(")","").strip()
                        except:
                            print "File not found:",filename_sig
    
                    # Fill lists of data
                    data["mList"].append(abs(float(mass)))
                    data["rList"].append(float(info_r[0]))
                    data["rmList"].append(abs(float(info_r[1])))
                    data["rpList"].append(abs(float(info_r[2])))
                    data["sList"].append(abs(float(line_sig)))
                    data["pList"].append(abs(float(line_pvalue)))
                    data["zero"].append(0.0)
    
                    # Write out r, sigma, and p-value to file
                    if len(info_r) < 3:
                        file_table.write("%s & %s & %s & %s\\\\ \n" % (mass, info_r[0], line_sig, line_pvalue))
                    elif "#" in info_r[0]:
                        file_table.write("%s & Fit failed &  \\\\ \n" % (mass))
                    elif line_sig == "":
                        file_table.write("%s & $%.2f_{%.2f}^{%.2f}$ & %s & %s\\\\ \n" % (mass, float(info_r[0]), float(info_r[1]), float(info_r[2].replace("+-","+")), line_sig, line_pvalue))
                    else:
                        file_table.write("%s & $%.2f_{%.2f}^{%.2f}$ & %.2f & %s\\\\ \n" % (mass, float(info_r[0]), float(info_r[1]), float(info_r[2].replace("+-","+")), float(line_sig), line_pvalue))

                file_table.write("\\hline \n")
                dataSet["data"][year]=data
            file_table.write("\\end{tabular}\n")
            file_table.close()
            l.append({"model":model, "runtype":runtype, "outFileName":outFileName})
            d.append(dataSet)
    
    # Make tex file with all signal strengths
    makeSigTex("table_signal_strength.tex", l)

    allData=[]
    print d
    for dataSet1 in d:
        for dataSet2 in d:
            if dataSet1["runtype"] == dataSet2["runtype"] and dataSet1["model"] == dataSet2["model"] and dataSet1["data"] != dataSet2["data"]:
                dataSet1["data"].update(dataSet2["data"])
            else:
                continue
        if dataSet1 not in allData:
            allData.append(dataSet1)

    for dataSet in allData:        
        #if not (dataSet["runtype"] == "pseudoData" or dataSet["runtype"] == "pseudoDataS"):
            print "------------------------------------------"
            print dataSet["runtype"], dataSet["model"]        
            #makePValuePlotAlt(dataSet)
            makePValuePlot(dataSet, options.approved)

if __name__ == '__main__':
    main()
