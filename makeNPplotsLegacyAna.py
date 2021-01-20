#!/usr/bin/env python
import re
from sys import argv, stdout, stderr, exit
import datetime
from optparse import OptionParser
import HiggsAnalysis.CombinedLimit.calculate_pulls as CP 

# tool to compare fitted nuisance parameters to prefit values.
#
# Also used to check for potential problems in RooFit workspaces to be used with combine
# (see https://twiki.cern.ch/twiki/bin/viewauth/CMS/HiggsWG/HiggsPAGPreapprovalChecks)

# import ROOT with a fix to get batch mode (http://root.cern.ch/phpBB3/viewtopic.php?t=3198)
hasHelp = False
for X in ("-h", "-?", "--help"):
    if X in argv:
        hasHelp = True
        argv.remove(X)
argv.append( '-b-' )
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat("")
argv.remove( '-b-' )
if hasHelp: argv.append("-h")

ARXIV = "XXXX.XXXXX"

SUPP = ""

parser = OptionParser(usage="usage: %prog [options] in.root  \nrun with --help to get list of options")
parser.add_option("--approved",      dest="approved",    default=False,  action="store_true", help="Plot is approved, no preliminary")

(options, args) = parser.parse_args()
if len(args) == 0:
    parser.print_usage()
    exit(1)

setUpString = "diffNuisances run on %s, at %s with the following options ... "%(args[0],datetime.datetime.utcnow())+str(options)

file = ROOT.TFile(args[0])
if file == None: raise RuntimeError, "Cannot open file %s" % args[0]
fit_s  = file.Get("fit_s")
fit_b  = file.Get("fit_b")
prefit = file.Get("nuisances_prefit")
if fit_s == None or fit_s.ClassName()   != "RooFitResult": raise RuntimeError, "File %s does not contain the output of the signal fit 'fit_s'"     % args[0]
if fit_b == None or fit_b.ClassName()   != "RooFitResult": raise RuntimeError, "File %s does not contain the output of the background fit 'fit_b'" % args[0]
if prefit == None or prefit.ClassName() != "RooArgSet":    raise RuntimeError, "File %s does not contain the prefit nuisances 'nuisances_prefit'"  % args[0]

# get the fitted parameters
fpf_b = fit_b.floatParsFinal()
fpf_s = fit_s.floatParsFinal()

nuis_p_i=0
title = "pull"

# Also make histograms for pull distributions:
hist_fit_b  = ROOT.TH1F("fit_b"   ,"B-only fit Nuisances;;%s "%title,prefit.getSize(),0,prefit.getSize())
hist_fit_s  = ROOT.TH1F("fit_s"   ,"S+B fit Nuisances   ;;%s "%title,prefit.getSize(),0,prefit.getSize())
hist_prefit = ROOT.TH1F("prefit_nuisancs","Prefit Nuisances    ;;%s "%title,prefit.getSize(),0,prefit.getSize())
# Store also the *asymmetric* uncertainties
gr_fit_b    = ROOT.TGraphAsymmErrors(); gr_fit_b.SetTitle("fit_b_g")
gr_fit_s    = ROOT.TGraphAsymmErrors(); gr_fit_s.SetTitle("fit_b_s")

# loop over all fitted parameters
nuis_list = []
for i in range(fpf_s.getSize()):

    nuis_s = fpf_s.at(i)
    name   = nuis_s.GetName();
    nuis_b = fpf_b.find(name)
    nuis_p = prefit.find(name)

    mean_p, sigma_p, sigma_pu, sigma_pd = 0,0,0,0

    if nuis_p != None:
        if "d_" == name[0:2]: continue
        b = nuis_b.getVal(); bErrUp = nuis_b.getErrorHi(); bErrDown = nuis_b.getErrorLo()
        s = nuis_s.getVal(); sErrUp = nuis_s.getErrorHi(); sErrDown = nuis_s.getErrorLo()

        bErr = 0.0
        if b < 0: bErr = bErrUp
        else:     bErr = bErrDown

        sErr = 0.0
        if s < 0: sErr = sErrUp
        else:     sErr = sErrDown

        bChi2 = (b / bErr)**2.0; sChi2 = (s / sErr)**2.0

        nuis_list.append({"name" : name, "bobj" : nuis_b, "sobj" : nuis_s, "bval" : nuis_b.getVal(), "sval" : nuis_s.getVal(), "bchi2" : bChi2, "schi2" : sChi2, "dchi2" : sChi2-bChi2, "diff" : abs(nuis_s.getVal())-abs(nuis_b.getVal())})

        # get best-fit value and uncertainty at prefit for this 
        # nuisance parameter
        if nuis_p.getErrorLo()==0: nuis_p.setError(nuis_p.getErrorHi())
        mean_p, sigma_p, sigma_pu,sigma_pd = (nuis_p.getVal(), nuis_p.getError(),nuis_p.getErrorHi(),nuis_p.getErrorLo())

        if not sigma_p > 0: sigma_p = (nuis_p.getMax()-nuis_p.getMin())/2
        nuisIsSymm = abs(abs(nuis_p.getErrorLo())-abs(nuis_p.getErrorHi()))<0.01 or nuis_p.getErrorLo() == 0

nuis_list = sorted(nuis_list, key=lambda i: abs(i["dchi2"]), reverse=True)

niceNames = {
    "noHT" : "H_{T} primary",
    "mpTScaled" : "Jet p_{T} / mass",
    "qcdCR" : "N_{jets} shape invariance",
    "htnjet" : "H_{T} N_{jets}-parameterization",
    "hdampUp" : "ME-PS (+)",
    "hdampDown" : "ME-PS (-)",
    "underlyingEvtUp" : "UE tune (+)",
    "underlyingEvtDown" : "UE tune (-)",
    "nom" : "Residual",
    "erdOn" : "Color reconnection",
    "JECDown" : "JES (-)",
    "JERDown" : "JER (-)",
    "JECUp" : "JES (+)",
    "JERUp" : "JER (+)",
    "scl" : "#mu_{R}/#mu_{f} scales",
    "JEC" : "JES",
    "JER" : "JER"
}

fuchsia = ROOT.TColor.GetColor("#88258C")
cornblue = ROOT.TColor.GetColor("#5CB4E8")

dChi2Histo = ROOT.TH1F("dChi2", "dChi2", 800, -20, 20)
dChi2Histo.SetLineWidth(2)
dChi2Histo.SetLineColor(ROOT.kRed)
dChi2Histo.SetFillColorAlpha(ROOT.kRed, 0.35)
dChi2Histo.GetXaxis().SetTitle("Nuisance Parameter #chi^{2}(s+b) - #chi^{2}(b)")
dChi2Histo.GetYaxis().SetTitle("NPs / bin")

bChi2Histo = ROOT.TH1F("bChi2", "bChi2", 800, 0, 20)
bChi2Histo.SetLineWidth(2)
bChi2Histo.SetLineColor(fuchsia)
bChi2Histo.SetFillColorAlpha(fuchsia, 0.35)
bChi2Histo.GetXaxis().SetTitle("Nuisance Parameter #chi^{2}")
bChi2Histo.GetYaxis().SetTitle("NPs / bin")

sbChi2Histo = ROOT.TH1F("sbChi2", "sbChi2", 800, 0, 20)
sbChi2Histo.SetLineWidth(2)
sbChi2Histo.SetLineColor(cornblue)
sbChi2Histo.SetFillColorAlpha(cornblue, 0.35)
sbChi2Histo.GetXaxis().SetTitle("Nuisance Parameter #chi^{2}")
sbChi2Histo.GetYaxis().SetTitle("NPs / bin")

bchi2 = 0.0; sbchi2 = 0.0
for d in nuis_list:
    name = d["name"]; 
    nuis_b = d["bobj"]; nuis_s = d["sobj"]

    for fit_name, nuis_x in [('b', nuis_b), ('s',nuis_s)]:
        if nuis_x == None: continue
        else: 
            nuisIsSymm = abs(abs(nuis_x.getErrorLo())-abs(nuis_x.getErrorHi()))<0.01 or nuis_x.getErrorLo() == 0
    
            if nuisIsSymm : nuis_x.setError(nuis_x.getErrorHi())
            nuiselo = abs(nuis_x.getErrorLo()) if nuis_x.getErrorLo()>0 else nuis_x.getError()
            nuisehi = nuis_x.getErrorHi()
            nx,ned,neu = nuis_x.getVal(), nuiselo, nuisehi
    
            print name, d["schi2"], d["bchi2"], d["dchi2"]
            if nuis_p != None:
                if fit_name=='b':
                    nuis_p_i+=1
                    if "d_" != name[0:2]:
                        if nuis_x.getVal() > 0:
                            bchi2 += (nuis_x.getVal() / nuis_x.getErrorLo())**2.0
                        else:
                            bchi2 += (nuis_x.getVal() / nuis_x.getErrorHi())**2.0
                    gr_fit_b.SetPoint(nuis_p_i-1,nuis_p_i-0.5+0.1,nuis_x.getVal())
                    gr_fit_b.SetPointError(nuis_p_i-1,0,0,abs(nuis_x.getErrorLo()),nuis_x.getErrorHi())
                    hist_fit_b.SetBinContent(nuis_p_i,nuis_x.getVal())
                    hist_fit_b.SetBinError(nuis_p_i,nuis_x.getError())
                    hist_fit_b.GetXaxis().SetBinLabel(nuis_p_i,name)
                    gr_fit_b.GetXaxis().SetBinLabel(nuis_p_i,name)
                if fit_name=='s':
                    if "d_" != name[0:2]:
                        if nuis_x.getVal() > 0:
                            sbchi2 += (nuis_x.getVal() / nuis_x.getErrorLo())**2.0
                        else:
                            sbchi2 += (nuis_x.getVal() / nuis_x.getErrorHi())**2.0

                    gr_fit_s.SetPoint(nuis_p_i-1,nuis_p_i-0.5-0.1,nuis_x.getVal())
                    gr_fit_s.SetPointError(nuis_p_i-1,0,0,abs(nuis_x.getErrorLo()),nuis_x.getErrorHi())
                    hist_fit_s.SetBinContent(nuis_p_i,nuis_x.getVal())
                    hist_fit_s.SetBinError(nuis_p_i,nuis_x.getError())
                    hist_fit_s.GetXaxis().SetBinLabel(nuis_p_i,name)
                    gr_fit_s.GetXaxis().SetBinLabel(nuis_p_i,name)
    
                hist_prefit.SetBinContent(nuis_p_i,mean_p)
                hist_prefit.SetBinError(nuis_p_i,sigma_p)

                newName = name
                nameParts = name.split("_")

                if len(nameParts) > 2:
                    badName = nameParts[2]; process = nameParts[1]; year = nameParts[-1]; year2 = nameParts[-2]
                    if "d_" != newName[0:2]:
                        if process == "tt": newName = ""

                        if badName in niceNames: newName += " %s"%(niceNames[badName])
                        else:                    newName += " %s"%(badName)

                        if "20" in year:
                            if "17" in year2:
                                newName += " (%s)"%(year.replace("pre", "A").replace("post", "B").replace("20", "").replace("18", "17-18"))
                            else:
                                newName += " (%s)"%(year.replace("pre", "A").replace("post", "B").replace("20", ""))
                            
                elif len(nameParts) == 2:

                    badName = nameParts[0]; year = nameParts[1]
                    newName = "non-t#bar{t}"
                    if badName in niceNames: newName += " %s"%(niceNames[badName])
                    else:                    newName += " %s"%(badName)

                    if "17" in year2:
                        newName += " (%s)"%(year.replace("pre", "A").replace("post", "B").replace("20", "").replace("18", "17-18"))
                    else:
                        newName += " (%s)"%(year.replace("pre", "A").replace("post", "B").replace("20", ""))


                hist_prefit.GetXaxis().SetBinLabel(nuis_p_i,newName)
                hist_prefit.GetXaxis().SetBinLabel(nuis_p_i,newName)

                if "Combo" not in file.GetName():
                    hist_prefit.GetXaxis().SetBinLabel(nuis_p_i,newName.replace("_2016", "").replace("_2017", "").replace("_2018pre", "").replace("_2018post", "").replace("_2018A", "").replace("_2018B", "").replace("_2018", "").replace("np_", ""))
                    hist_prefit.GetXaxis().SetBinLabel(nuis_p_i,newName.replace("_2016", "").replace("_2017", "").replace("_2018pre", "").replace("_2018post", "").replace("_2018A", "").replace("_2018B", "").replace("_2018", "").replace("np_", ""))

    # end of loop over s and b
#end of loop over all fitted parameters

parser.add_option("-f", "--format",   dest="format", default="text", type="string",  help="Output format ('text', 'latex', 'twiki'")
import ROOT
ROOT.gROOT.SetStyle("Plain")
ROOT.gStyle.SetOptFit(1)

year = ""; tag = ""; data = True
if "pseudo" in file.GetName():
    data = False
if   "2016"     in file.GetName():
    year = "2016 (13 TeV)"
    tag = "2016"
elif "2017"     in file.GetName():
    year = "2017 (13 TeV)"
    tag = "2017"
elif "2018pre"  in file.GetName():
    year = "2018A (13 TeV)"
    tag = "2018A"
elif "2018post" in file.GetName():
    year = "2018B (13 TeV)"
    tag = "2018B"
elif "Combo"    in file.GetName():
    year = "137 fb^{-1} (13 TeV)"
    tag = "Combo"

canvas_nuis = ROOT.TCanvas("nuisances", "nuisances", 1800, 800)
canvas_nuis.Divide(1,2); canvas_nuis.cd(1)
XMin = 0;    XMax = 1; RatioXMin = 0; RatioXMax = 1 
YMin = 0.529; YMax = 1; RatioYMin = 0; RatioYMax = 0.529
PadFactor = (YMax-YMin) / (RatioYMax-RatioYMin)
ROOT.gPad.SetPad(XMin, YMin, XMax, YMax)

deltaChi2 = ROOT.TGraph(); runningdChi2h = ROOT.TH1F("runningdChi2", "runningdChi2", gr_fit_b.GetN(), 0, gr_fit_b.GetN())
x1 = ROOT.Double(0.0); y1 = ROOT.Double(0.0)
x2 = ROOT.Double(0.0); y2 = ROOT.Double(0.0)

y1up = ROOT.Double(0.0); y1down = ROOT.Double(0.0)
y2up = ROOT.Double(0.0); y2down = ROOT.Double(0.0)

lastBin = 14; incldChi2 = 0.0; runningdChi2 = 0.0
for i in xrange(0, gr_fit_b.GetN()):
    gr_fit_b.GetPoint(i, x1, y1)
    gr_fit_s.GetPoint(i, x2, y2) 

    y1up = gr_fit_b.GetErrorYhigh(i); y1down = gr_fit_b.GetErrorYlow(i)
    y2up = gr_fit_s.GetErrorYhigh(i); y2down = gr_fit_s.GetErrorYlow(i)

    y1err = 0.0
    if y1 < 0: y1err = y1up
    else:      y1err = y1down

    y2err = 0.0
    if y2 < 0: y2err = y2up
    else:      y2err = y2down

    chi2s = (y2/y2err)**2.0; chi2b = (y1/y1err)**2.0; dChi2 = chi2s-chi2b

    runningdChi2 += dChi2

    print "(%d) NP: %s, dChi2: %f"%(i+1,hist_prefit.GetXaxis().GetBinLabel(i+1), dChi2)
    if i < lastBin:
        deltaChi2.SetPoint(i, (x1+x2)/2.0, chi2s-chi2b)
        runningdChi2h.SetBinContent(i+1, runningdChi2)
    else:
        incldChi2 += dChi2 
    name = hist_prefit.GetXaxis().GetBinLabel(i+1)
    if "d_" != name[0:2]:
        dChi2Histo.Fill(chi2s-chi2b)
        bChi2Histo.Fill(chi2b)
        sbChi2Histo.Fill(chi2s)
        
runningdChi2h.SetBinContent(lastBin+1, runningdChi2)
deltaChi2.SetPoint(lastBin, lastBin+0.5, incldChi2)
gr_fit_b.GetPoint(lastBin, x1, y1); gr_fit_s.GetPoint(lastBin, x2, y2)
gr_fit_b.SetPoint(lastBin, x1, -10.0); gr_fit_s.SetPoint(lastBin, x2, -10.0)

dChi2Histo.SetTitle("")
dChi2Histo.GetYaxis().SetTitleSize(0.06)
dChi2Histo.GetYaxis().SetTitleOffset(1.25)
dChi2Histo.GetYaxis().SetLabelSize(0.055)
dChi2Histo.GetXaxis().SetLabelSize(0.055)
dChi2Histo.GetYaxis().SetTitleSize(0.06)
dChi2Histo.GetXaxis().SetTitleSize(0.06)
dChi2Histo.GetXaxis().SetTitleOffset(1.1)

bChi2Histo.SetTitle("")
bChi2Histo.GetYaxis().SetTitleSize(0.06)
bChi2Histo.GetYaxis().SetTitleOffset(1.25)
bChi2Histo.GetYaxis().SetLabelSize(0.055)
bChi2Histo.GetXaxis().SetLabelSize(0.055)
bChi2Histo.GetYaxis().SetTitleSize(0.06)
bChi2Histo.GetXaxis().SetTitleSize(0.06)
bChi2Histo.GetXaxis().SetTitleOffset(1.1)

sbChi2Histo.SetTitle("")
sbChi2Histo.GetYaxis().SetTitleSize(0.06)
sbChi2Histo.GetYaxis().SetTitleOffset(1.25)
sbChi2Histo.GetYaxis().SetLabelSize(0.055)
sbChi2Histo.GetXaxis().SetLabelSize(0.055)
sbChi2Histo.GetYaxis().SetTitleSize(0.06)
sbChi2Histo.GetXaxis().SetTitleSize(0.06)
sbChi2Histo.GetXaxis().SetTitleOffset(1.1)

hist_fit_e_s = hist_fit_s.Clone("errors_s")
hist_fit_e_b = hist_fit_b.Clone("errors_b")
gr_fit_s.SetLineColor(cornblue)
gr_fit_s.SetMarkerColor(cornblue)
gr_fit_b.SetLineColor(fuchsia)
gr_fit_b.SetMarkerColor(fuchsia)
deltaChi2.SetLineColor(ROOT.kRed)
deltaChi2.SetMarkerColor(ROOT.kRed)
gr_fit_b.SetMarkerStyle(20)
gr_fit_s.SetMarkerStyle(20)
deltaChi2.SetMarkerStyle(20)
gr_fit_b.SetMarkerSize(2.0)
gr_fit_s.SetMarkerSize(2.0)
deltaChi2.SetMarkerSize(2.0)
gr_fit_b.SetLineWidth(2)
gr_fit_s.SetLineWidth(2)
deltaChi2.SetLineWidth(2)
hist_prefit.SetLineWidth(2)
hist_prefit.GetYaxis().SetTitleSize(0.13)
hist_prefit.GetYaxis().SetTitleOffset(0.225)
hist_prefit.GetYaxis().SetLabelSize(0.1)
hist_prefit.GetXaxis().SetLabelSize(0.075)
hist_prefit.GetXaxis().SetLabelOffset(0.012)
hist_prefit.GetYaxis().SetTitle("#theta")
hist_prefit.SetTitle("")
hist_prefit.SetLineColor(ROOT.kBlack)
hist_prefit.SetFillColor(ROOT.kGray)
hist_prefit.SetMaximum(3.5)
hist_prefit.SetMinimum(-3.5)
hist_prefit.GetXaxis().SetRangeUser(0.0,lastBin+1)
if "Combo" in file.GetName(): hist_prefit.GetXaxis().SetRangeUser(0.0, lastBin+1)
dummyChi2 = hist_prefit.Clone("dummyChi2")
dummyChi2.Reset("ICESM")
dummyChi2.GetYaxis().SetRangeUser(-3.5,3.5)
dummyChi2.GetXaxis().SetBinLabel(lastBin+1, "Remainder")

l = ROOT.TLine(lastBin, -3.7, lastBin, 3.5)
l.SetLineWidth(2)
l.SetLineColor(ROOT.kBlack)
l.SetLineStyle(1)

hist_prefit.Draw("E2")
hist_prefit.Draw("histsame")
gr_fit_b.Draw("EPsame")
gr_fit_s.Draw("EPsame")
l.Draw("SAME")
ROOT.gPad.SetGridx()
ROOT.gPad.RedrawAxis()
ROOT.gPad.RedrawAxis('g')

cmstext = ROOT.TLatex()
cmstext.SetNDC(True)

cmstext.SetTextAlign(31)
cmstext.SetTextSize(0.13)
cmstext.SetTextFont(42)
cmstext.DrawLatex(1 - ROOT.gPad.GetRightMargin() + 0.07, 1 - (ROOT.gPad.GetTopMargin() + 0.015), year)

mark = ROOT.TLatex()
mark.SetNDC(True)

mark.SetTextAlign(11);
mark.SetTextSize(0.15);
mark.SetTextFont(61);
mark.DrawLatex(-0.04 + ROOT.gPad.GetLeftMargin(), 1 - (ROOT.gPad.GetTopMargin() + 0.005), "CMS")
mark.SetTextFont(52);
if data:
    mark.DrawLatex(-0.04 + ROOT.gPad.GetLeftMargin() + 0.07, 1 - (ROOT.gPad.GetTopMargin() + 0.005), SUPP)
else:
    if not options.approved: 
        mark.DrawLatex(-0.04 + ROOT.gPad.GetLeftMargin() + 0.03, 1 - (ROOT.gPad.GetTopMargin() - 0.02), "Simulation")
    else:
        mark.DrawLatex(-0.04 + ROOT.gPad.GetLeftMargin() + 0.03, 1 - (ROOT.gPad.GetTopMargin() - 0.02), "Simulation")

mark.SetTextSize(0.11)
mark.SetTextFont(42)
if "Combo" not in year: mark.DrawLatex(-0.04 + ROOT.gPad.GetLeftMargin() + 0.30, 1 - (ROOT.gPad.GetTopMargin() + 0.005), "arXiv:%s"%(ARXIV))

leg=ROOT.TLegend(0.68,0.56,0.78,0.85)
leg.SetFillColor(0)
leg.SetTextFont(42)
leg.AddEntry(hist_prefit,"prefit","FL")
leg.AddEntry(gr_fit_b,"b-only fit","EPL")
leg.AddEntry(gr_fit_s,"s+b fit"   ,"EPL")
leg.Draw()
ROOT.gPad.SetTopMargin(0.15)
ROOT.gPad.SetBottomMargin(0.00)
ROOT.gPad.SetRightMargin(0.03)
ROOT.gPad.SetLeftMargin(0.06)

canvas_nuis.cd(2)
ROOT.gPad.SetPad(RatioXMin, RatioYMin, RatioXMax, RatioYMax)
ROOT.gPad.SetTopMargin(0.0)
ROOT.gPad.SetBottomMargin(0.32)
ROOT.gPad.SetRightMargin(0.03)
ROOT.gPad.SetLeftMargin(0.06)


dummyChi2.GetYaxis().SetTitleSize(0.13*PadFactor)
dummyChi2.GetYaxis().SetTitleOffset(0.225/PadFactor)
dummyChi2.GetYaxis().SetLabelSize(0.1*PadFactor)
dummyChi2.GetXaxis().SetLabelSize(0.1*PadFactor)
dummyChi2.GetXaxis().SetLabelOffset(0.012/PadFactor)

if data: dummyChi2.GetYaxis().SetRangeUser(-3.7,2.7)
else:    dummyChi2.GetYaxis().SetRangeUser(-16.2,1.2)

dummyChi2.GetYaxis().SetNdivisions(5,5,0)
dummyChi2.SetLineStyle(2)
dummyChi2.SetLineColor(ROOT.kBlack)
dummyChi2.GetYaxis().SetTitle("#chi^{2}(s+b) - #chi^{2}(b)")

runningdChi2h.SetFillColorAlpha(ROOT.kBlue, 0.15)
runningdChi2h.SetLineColor(ROOT.kBlue)
runningdChi2h.SetLineWidth(0)

leg2=ROOT.TLegend(0.68,0.72,0.83,1.0)
leg2.SetFillColor(0)
leg2.SetTextFont(42)
leg2.AddEntry(deltaChi2,"#chi^{2}(s+b) - #chi^{2}(b)","P")
leg2.AddEntry(runningdChi2h,"Cumulative #Delta#chi^{2} " ,"F")

dummyChi2.Draw()
runningdChi2h.Draw("HIST SAME")
deltaChi2.Draw("EPsame")
leg2.Draw("SAME")
l.Draw("SAME")
ROOT.gPad.SetGridx()

if not options.approved:
    canvas_nuis.SaveAs("Nuisance_Pulls_%s_prelim.pdf"%(tag))
    canvas_nuis.SaveAs("Nuisance_Pulls_%s_prelim.png"%(tag))
else:
    canvas_nuis.SaveAs("Nuisance_Pulls_%s.pdf"%(tag))
    canvas_nuis.SaveAs("Nuisance_Pulls_%s.png"%(tag))

# Make a delta chi2 1D histo
canvas_dchi2 = ROOT.TCanvas("dchi2_c", "dchi2_c", 1200, 1200)
canvas_dchi2.cd()

ROOT.gPad.SetTopMargin(0.06)
ROOT.gPad.SetLeftMargin(0.15)
ROOT.gPad.SetBottomMargin(0.15)
ROOT.gPad.SetRightMargin(0.05)

dChi2Histo.Draw("HIST")

cmstext = ROOT.TLatex()
cmstext.SetNDC(True)

cmstext.SetTextAlign(31)
cmstext.SetTextSize(0.040)
cmstext.SetTextFont(42)
cmstext.DrawLatex(1 - ROOT.gPad.GetRightMargin(), 1 - (ROOT.gPad.GetTopMargin() - 0.017), year)

mark = ROOT.TLatex()
mark.SetNDC(True)

mark.SetTextAlign(11);
mark.SetTextSize(0.045);
mark.SetTextFont(61);
mark.DrawLatex(ROOT.gPad.GetLeftMargin(), 1 - (ROOT.gPad.GetTopMargin() - 0.02), "CMS")
mark.SetTextFont(52);
if data:
    mark.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.10, 1 - (ROOT.gPad.GetTopMargin() - 0.02), SUPP)
else:
    if not options.approved: 
        mark.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.10, 1 - (ROOT.gPad.GetTopMargin() - 0.02), "Simulation Supplementary")
    else:
        mark.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.10, 1 - (ROOT.gPad.GetTopMargin() - 0.02), "Simulation")

mark.SetTextSize(0.035)
mark.SetTextFont(42)
if "Combo" not in year: mark.DrawLatex(0.65, 0.90, "arXiv:%s"%(ARXIV))

nentries = dChi2Histo.GetEntries()
mean = dChi2Histo.GetMean()
dchi2 = mean * nentries

if data: dChi2Histo.GetXaxis().SetRangeUser(-3.1,3.1)
else:    dChi2Histo.GetXaxis().SetRangeUser(-13.75,0.75)

canvas_dchi2.SetLogy()

meta = ROOT.TLatex()
meta.SetNDC(True)

meta.SetTextAlign(11);
meta.SetTextSize(0.04);
meta.SetTextFont(62);
meta.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.05, 1 - ROOT.gPad.GetTopMargin() - 0.07, "NPs = %d"%(nentries))
meta.SetTextColor(ROOT.kRed)
meta.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.05, 1 - ROOT.gPad.GetTopMargin() - 0.12, "#LT#Delta#chi^{2}#GT = %3.3f"%(mean))
meta.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.05, 1 - ROOT.gPad.GetTopMargin() - 0.18, "#sum#Delta#chi^{2} = %3.2f"%(dchi2))

if not options.approved:
    canvas_dchi2.SaveAs("dChi2_Dist_%s_prelim.pdf"%(tag))
    canvas_dchi2.SaveAs("dChi2_Dist_%s_prelim.png"%(tag))
else:
    canvas_dchi2.SaveAs("dChi2_Dist_%s.pdf"%(tag))
    canvas_dchi2.SaveAs("dChi2_Dist_%s.png"%(tag))

# Make a chi2 1D histo for b and s+b fits
canvas_chi2 = ROOT.TCanvas("chi2_c", "chi2_c", 1200, 1200)
canvas_chi2.cd()

ROOT.gPad.SetTopMargin(0.06)
ROOT.gPad.SetLeftMargin(0.15)
ROOT.gPad.SetBottomMargin(0.15)
ROOT.gPad.SetRightMargin(0.05)

bChi2Histo.Draw("HIST")
sbChi2Histo.Draw("HIST SAME")

cmstext = ROOT.TLatex()
cmstext.SetNDC(True)

cmstext.SetTextAlign(31)
cmstext.SetTextSize(0.040)
cmstext.SetTextFont(42)
cmstext.DrawLatex(1 - ROOT.gPad.GetRightMargin(), 1 - (ROOT.gPad.GetTopMargin() - 0.017), year)

mark = ROOT.TLatex()
mark.SetNDC(True)

mark.SetTextAlign(11);
mark.SetTextSize(0.045);
mark.SetTextFont(61);
mark.DrawLatex(ROOT.gPad.GetLeftMargin(), 1 - (ROOT.gPad.GetTopMargin() - 0.02), "CMS")
mark.SetTextFont(52);
if data:
    mark.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.10, 1 - (ROOT.gPad.GetTopMargin() - 0.02), SUPP)
else:
    if not options.approved: 
        mark.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.10, 1 - (ROOT.gPad.GetTopMargin() - 0.02), "Simulation Supplementary")
    else:
        mark.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.10, 1 - (ROOT.gPad.GetTopMargin() - 0.02), "Simulation")

mark.SetTextSize(0.035)
mark.SetTextFont(42)
if "Combo" not in year: mark.DrawLatex(0.65, 0.90, "arXiv:%s"%(ARXIV))

bnentries = bChi2Histo.GetEntries()
bmean = bChi2Histo.GetMean()
bchi2 = bmean * nentries

sbnentries = sbChi2Histo.GetEntries()
sbmean = sbChi2Histo.GetMean()
sbchi2 = sbmean * nentries

if data: bChi2Histo.GetXaxis().SetRangeUser(0,3.1)
else:    bChi2Histo.GetXaxis().SetRangeUser(0,13.75)

canvas_chi2.SetLogy()

meta = ROOT.TLatex()
meta.SetNDC(True)

meta.SetTextAlign(11);
meta.SetTextSize(0.04);
meta.SetTextFont(62);
meta.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.05, 1 - ROOT.gPad.GetTopMargin() - 0.07, "NPs = %d"%(nentries))
meta.SetTextColor(fuchsia);
meta.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.05, 1 - ROOT.gPad.GetTopMargin() - 0.12, "#LT#chi^{2}(b)#GT = %3.3f"%(bmean))
meta.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.05, 1 - ROOT.gPad.GetTopMargin() - 0.18, "#sum#chi^{2} = %3.2f"%(bchi2))
meta.SetTextColor(cornblue);
meta.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.05, 1 - ROOT.gPad.GetTopMargin() - 0.26, "#LT#chi^{2}(s+b)#GT = %3.3f"%(sbmean))
meta.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.05, 1 - ROOT.gPad.GetTopMargin() - 0.32, "#sum#chi^{2} = %3.2f"%(sbchi2))

if not options.approved:
    canvas_chi2.SaveAs("Chi2_Dist_%s_prelim.pdf"%(tag))
    canvas_chi2.SaveAs("Chi2_Dist_%s_prelim.png"%(tag))
else:
    canvas_chi2.SaveAs("Chi2_Dist_%s.pdf"%(tag))
    canvas_chi2.SaveAs("Chi2_Dist_%s.png"%(tag))
