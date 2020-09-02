import ROOT
import optparse
import sys 

def makePostFitPlot(preFitHisto, year, bin, paramDic, postFitNP):
    h1 = preFitHisto.Clone("PreFit")
    h2 = preFitHisto.Clone("PostFit")
    for i in range(1, h1.GetNbinsX()+1):
        coef = paramDic[year,bin,i]
        val = coef[0] + coef[1]*postFitNP[0] + coef[2]*postFitNP[1] + coef[3]*postFitNP[2]
        h1.SetBinContent(i,coef[0])
        h2.SetBinContent(i,val)
    return h1, h2

def drawPull(postFitNP):
    mark = ROOT.TLatex()
    mark.SetNDC(True)
    mark.SetTextAlign(11);
    mark.SetTextSize(0.050);
    mark.DrawLatex(0.2,0.30,"#beta = %0.4f" % postFitNP[3])
    mark.DrawLatex(0.2,0.25,"#theta_{1} = %0.4f" % postFitNP[0])
    mark.DrawLatex(0.2,0.20,"#theta_{2} = %0.4f" % postFitNP[1])
    mark.DrawLatex(0.2,0.15,"#theta_{3} = %0.4f" % postFitNP[2])

def getMap(inFile, l):
    m = {}
    for bin in l: 
        h = inFile.Get(bin+"_qcdCR")
        hErr = inFile.Get(bin+"_qcdCRErr")
        for i in range(1, h.GetNbinsX()+1):
            r = h.GetBinContent(i)
            rPrime = hErr.GetBinContent(i)
            h.SetBinError(i, r*(rPrime-1))
        m[bin] = (h, hErr)
    return m

def getNPList(entry, bin, year):
    l = []
    if(year=="2016"):
        if  (bin=="D1"): l = [entry.np_tt_qcdCRD1Coef1_2016, entry.np_tt_qcdCRD1Coef2_2016, entry.np_tt_qcdCRD1Coef3_2016, entry.np_tt_qcdCR_2016]
        elif(bin=="D2"): l = [entry.np_tt_qcdCRD2Coef1_2016, entry.np_tt_qcdCRD2Coef2_2016, entry.np_tt_qcdCRD2Coef3_2016, entry.np_tt_qcdCR_2016]
        elif(bin=="D3"): l = [entry.np_tt_qcdCRD3Coef1_2016, entry.np_tt_qcdCRD3Coef2_2016, entry.np_tt_qcdCRD3Coef3_2016, entry.np_tt_qcdCR_2016]
        elif(bin=="D4"): l = [entry.np_tt_qcdCRD4Coef1_2016, entry.np_tt_qcdCRD4Coef2_2016, entry.np_tt_qcdCRD4Coef3_2016, entry.np_tt_qcdCR_2016]
    elif(year=="2017"):
        if  (bin=="D1"): l = [entry.np_tt_qcdCRD1Coef1_2017, entry.np_tt_qcdCRD1Coef2_2017, entry.np_tt_qcdCRD1Coef3_2017, entry.np_tt_qcdCR_2017]
        elif(bin=="D2"): l = [entry.np_tt_qcdCRD2Coef1_2017, entry.np_tt_qcdCRD2Coef2_2017, entry.np_tt_qcdCRD2Coef3_2017, entry.np_tt_qcdCR_2017]
        elif(bin=="D3"): l = [entry.np_tt_qcdCRD3Coef1_2017, entry.np_tt_qcdCRD3Coef2_2017, entry.np_tt_qcdCRD3Coef3_2017, entry.np_tt_qcdCR_2017]
        elif(bin=="D4"): l = [entry.np_tt_qcdCRD4Coef1_2017, entry.np_tt_qcdCRD4Coef2_2017, entry.np_tt_qcdCRD4Coef3_2017, entry.np_tt_qcdCR_2017]
    return l

if __name__ == '__main__':
    parser = optparse.OptionParser("usage: %prog [options]\n")
    parser.add_option ('-t', dest='dataType', type='string', default = 'data',                           help="Specify if running over data or pseudo data")
    parser.add_option ('-s', dest='sysPath',  type='string', default = 'ttbar_systematics.root',         help="Specify if running over data or pseudo data")
    parser.add_option ('-f', dest='fitFile',  type='string', default = 'fitDiagnosticsComboRPV350.root', help="Specify if running over data or pseudo data")
    parser.add_option ('-y', dest='year',     type='string', default = '2016',                           help="year")
    parser.add_option ('-F', dest='fitType',  type='string', default = 'b',                              help="year")
    options, args = parser.parse_args()
    sys.argv.append( '-b' ) #setting batch mode for ROOT

    inFile = ROOT.TFile.Open(options.sysPath+"/ttbar_systematics.root")
    qcdParmFile = ROOT.TFile.Open(options.sysPath+"/qcdcr-syst-parameters.root")
    paramDic = {(str(e.year), "D{0}".format(e.MVAbin), e.Njets) : [e.coef0, e.coef1, e.coef2, e.coef3] for e in qcdParmFile.qcdCR_syst_parameters}
    qcdSysMap = getMap(inFile, ["D1","D2","D3","D4"])
    fitFileCombo = ROOT.TFile.Open(options.fitFile)
    treeIter = "default"
    if options.fitType == "b": treeIter = iter(fitFileCombo.tree_fit_b)
    elif options.fitType == "sb": treeIter = iter(fitFileCombo.tree_fit_sb)    
    entry = treeIter.next()

    c = ROOT.TCanvas( "c", "c", 0, 0, 1000, 1000)
    c.Divide(2,2)
    i=1
    objects = []
    for bin in ["D1","D2","D3","D4"]:
        c.cd(i)
        ROOT.gPad.SetLeftMargin(0.12)
        ROOT.gPad.SetRightMargin(0.15)
        ROOT.gPad.SetTopMargin(0.08)
        ROOT.gPad.SetBottomMargin(0.12)
        ROOT.gPad.SetTicks(1,1)
        ROOT.gStyle.SetOptStat(0); 
    
        leg = ROOT.TLegend(0.15, 0.65, 0.45, 0.88)
        objects.append(leg)
        leg.SetFillStyle(0)
        leg.SetBorderSize(0)
        leg.SetLineWidth(1)
        leg.SetNColumns(1)
        leg.SetTextFont(42)
    
        qcdSysHist = qcdSysMap[bin][0]
        objects.append(qcdSysHist)
        qcdSysHist.SetMaximum(1.5)
        qcdSysHist.SetMinimum(0.5)
        qcdSysHist.GetXaxis().SetTitle("N_{j} - 7")
        qcdSysHist.GetXaxis().SetTitleSize(0.055)
        qcdSysHist.GetXaxis().SetTitleOffset(0.85)
        qcdSysHist.GetYaxis().SetTitle("qcdCR NP R-Value")
        qcdSysHist.GetYaxis().SetTitleSize(0.055)
        qcdSysHist.GetYaxis().SetTitleOffset(0.85)
        qcdSysHist.SetLineColor(ROOT.kBlack)
        qcdSysHist.SetTitle("Pre and Post Fit qcdCR NP: "+bin+" "+options.dataType+" "+options.year+" "+options.fitType)
        qcdSysHist.Draw("E")
        leg.AddEntry(qcdSysHist, "R-Value", "l")
    
        postFitNP = getNPList(entry,bin,options.year)
        qcdSysHistPreFit, qcdSysHistPostFit = makePostFitPlot(qcdSysMap[bin][0], options.year, bin, paramDic, postFitNP)
        objects.append((qcdSysHistPreFit,qcdSysHistPostFit))
        qcdSysHistPreFit.SetLineColor(ROOT.kBlue)
        qcdSysHistPostFit.SetLineColor(ROOT.kRed)
        leg.AddEntry(qcdSysHistPreFit, "Pre-Fit", "l")
        leg.AddEntry(qcdSysHistPostFit, "Post-Fit", "l")
        qcdSysHistPreFit.Draw("hist same")
        qcdSysHistPostFit.Draw("hist same")
    
        line = ROOT.TF1("1" ,"1" ,-2000,20000)
        objects.append(line)
        line.SetLineColor(ROOT.kBlack)
        line.Draw("same")
        drawPull(postFitNP)

        leg.Draw()
        i+=1
    c.SaveAs("qcdCR_PlotCompare_"+options.dataType+"_"+options.year+"_"+options.fitType+".pdf")
