import ROOT
import optparse

def makeDataHisto(histRef, name, l, sys=[], norm=False):
    scale = 1.0
    if norm:
        for h in l:
            if h[0].find("_TT_h_njets_pt30_1l") != -1:
                scale = h[1].Integral()
                htemp = h[1].Clone("temp")
                for hs in sys:
                    htemp.Multiply(hs)
                scale = h[1].Integral()/htemp.Integral()
                    
    pseudoData = ROOT.TH1D(name, name, histRef.GetNbinsX(), histRef.GetBinLowEdge(1), histRef.GetBinLowEdge(1)+histRef.GetNbinsX())
    for bin in range(histRef.GetNbinsX()):
        sumdata = 0
        for h in l:
            d = h[1].GetBinContent(bin+1)
            if h[0].find("_TT_h_njets_pt30_1l") != -1 and len(sys)>0:
                for hs in sys:
                    d *= scale*hs.GetBinContent(bin+1)
            sumdata += d
        pseudoData.SetBinContent(bin+1, int(round(sumdata)))
    return pseudoData    

def line(L, H, x):
    m = (1.0/5.0)*(H-L)
    b = L - m
    return m*x + b

def makeLineHisto(histRef, name, L, H):
    lHisto = histRef.Clone(name)
    for bin in range(lHisto.GetNbinsX()):
        lHisto.SetBinContent(bin+1, line(L, H, bin+1) )
    return lHisto

def main():
    parser = optparse.OptionParser("usage: %prog [options]\n")
    parser.add_option('-d', dest='basedir', type='string', default='Keras_V1.2.8_Approval_SepOther_StatErrPlusFullDev', help="Path to input rootfiles")
    parser.add_option('--rootFile', dest='rootFile', type='string', default='pseudoData.root', help="Output root file")
    options, args = parser.parse_args()
    path = options.basedir
    outfile = path+"/"+options.rootFile

    bgNames = ["_TT_h_njets_pt30_1l", "_TTX_h_njets_pt30_1l", "_OTHER_h_njets_pt30_1l", "_QCD_h_njets_pt30_1l"]
    mvaBins = ["D1", "D2", "D3", "D4"]
    
    njets_for_Aron = ROOT.TFile.Open(path+"/njets_for_Aron.root")
    ttbar_sys = ROOT.TFile.Open(path+"/ttbar_systematics.root")
    newfile = ROOT.TFile.Open(outfile,"RECREATE")
    histRef = njets_for_Aron.Get("D1_TT_h_njets_pt30_1l")

    lHisto = makeLineHisto(histRef, "line", 0.8, 1.2)

    lDic = {}
    lDic["D1"] = makeLineHisto(histRef, "line_D1", 0.95, 1.05)
    lDic["D2"] = makeLineHisto(histRef, "line_D2", 0.90, 1.10)
    lDic["D3"] = makeLineHisto(histRef, "line_D3", 0.85, 1.15)
    lDic["D4"] = makeLineHisto(histRef, "line_D4", 0.80, 1.20)

    lDicOp = {}
    lDicOp["D1"] = makeLineHisto(histRef, "lineOp_D1", 0.80, 1.20)
    lDicOp["D2"] = makeLineHisto(histRef, "lineOp_D2", 0.85, 1.15)
    lDicOp["D3"] = makeLineHisto(histRef, "lineOp_D3", 0.90, 1.10)
    lDicOp["D4"] = makeLineHisto(histRef, "lineOp_D4", 0.95, 1.05)
    
    bgHistoListofList = []
    for mvaBin in mvaBins:
        bgHistoList = []
        for bgName in bgNames:
            bgHistoList.append( (mvaBin+bgName, njets_for_Aron.Get(mvaBin+bgName)) )
        bgHistoListofList.append( (mvaBin, bgHistoList) )
    
    newfile.cd()            
    for lMVA in bgHistoListofList:
        #makeDataHisto(histRef, lMVA[0]+"_pseudodata_h_njets_pt30_1l", lMVA[1]).Write()  
        makeDataHisto(histRef, lMVA[0]+"_pseudodata_qcdCR_h_njets_pt30_1l", lMVA[1], [ ttbar_sys.Get(lMVA[0]+"_qcdCR") ]).Write()
        makeDataHisto(histRef, lMVA[0]+"_pseudodata_2xqcdCR_h_njets_pt30_1l", lMVA[1], [ ttbar_sys.Get(lMVA[0]+"_qcdCR"), ttbar_sys.Get(lMVA[0]+"_qcdCR") ]).Write()
        makeDataHisto(histRef, lMVA[0]+"_pseudodata_JECUp_JERDown_FSR_h_njets_pt30_1l", lMVA[1], [ ttbar_sys.Get(lMVA[0]+"_JECUp"), ttbar_sys.Get(lMVA[0]+"_JERDown"), ttbar_sys.Get(lMVA[0]+"_FSR") ]).Write()
        makeDataHisto(histRef, lMVA[0]+"_pseudodata_0.2xLine_h_njets_pt30_1l", lMVA[1], [ lHisto ]).Write()        
        makeDataHisto(histRef, lMVA[0]+"_pseudodata_0.05-0.2xLine_h_njets_pt30_1l", lMVA[1], [ lDic[lMVA[0]] ]).Write()
        makeDataHisto(histRef, lMVA[0]+"_pseudodata_0.05-0.2xLineNorm_h_njets_pt30_1l", lMVA[1], [ lDic[lMVA[0]] ], True).Write()
        makeDataHisto(histRef, lMVA[0]+"_pseudodata_0.2-0.05xLine_h_njets_pt30_1l", lMVA[1], [ lDicOp[lMVA[0]] ]).Write()
        makeDataHisto(histRef, lMVA[0]+"_pseudodata_qcdCR_0.05-0.2xLine_h_njets_pt30_1l", lMVA[1], [ lDic[lMVA[0]], ttbar_sys.Get(lMVA[0]+"_qcdCR") ]).Write()
        makeDataHisto(histRef, lMVA[0]+"_pseudodata_qcdCR_0.2xLine_h_njets_pt30_1l", lMVA[1], [ lHisto, ttbar_sys.Get(lMVA[0]+"_qcdCR") ]).Write()
        
        sRPV350 = njets_for_Aron.Get(lMVA[0]+"_RPV_350_h_njets_pt30_1l")
        sRPV350.Scale(0.3)
        makeDataHisto(histRef, lMVA[0]+"_pseudodataS_0.3xRPV_350_h_njets_pt30_1l", lMVA[1]+[("RPV_350", sRPV350)]).Write()  
    
    newfile.Close()
    njets_for_Aron.Close()
    ttbar_sys.Close()

if __name__ == "__main__":
    main()
