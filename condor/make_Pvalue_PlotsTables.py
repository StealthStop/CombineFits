# make a table of the signal strength and associated signifances. 
# Do this for every signal point

import os
import argparse
import ROOT
from array import array

class DataSet():

    def __init__(self, runtype, model, channel, year):

        self.runtype = runtype
        self.model   = model
        self.channel = channel
        self.data    = None
        self.year    = year

    def setData(self, payload):
        self.data = payload

    def getData(self):
        return self.data
    def getYear(self):
        return self.year
    def getRuntype(self):
        return self.runtype
    def getChannel(self):
        return self.channel
    def getModel(self):
        return self.model

class Plotter():

    def __init__(self, pdfName, path, outPath, asimov):
    
        self.pdfName  = pdfName
        self.path     = path
        self.outPath  = outPath
        self.asimov   = asimov

        self.labels = {"2016"        : "2016", 
                       "2016preVFP"  : "2016preVFP", 
                       "2016postVFP" : "2016postVFP", 
                       "2017"        : "2017", 
                       "2018"        : "2018",
                       "Run2UL"      : "Run2UL", 
                       "0l"          : "fully-hadronic", 
                       "1l"          : "semi-leptonic",
                       "2l"          : "fully-leptonic", 
                       "combo"       : "Combo", 
        }

        self.colors = {"2016"        : ROOT.kBlack,
                       "2016preVFP"  : ROOT.kRed+1,
                       "2016postVFP" : ROOT.kBlue+1,
                       "2017"        : ROOT.kGreen+1,
                       "2018"        : ROOT.kOrange+1,
                       "Run2UL"      : ROOT.kBlack,
                       "0l"          : ROOT.TColor.GetColor("#2ca25f"),
                       "1l"          : ROOT.TColor.GetColor("#5cb4e8"),
                       "2l"          : ROOT.TColor.GetColor("#CE1256"),
                       "combo"       : ROOT.kBlack,
        }

        self.lstyles = {"2016"        : 0,
                        "2016preVFP"  : 4,
                        "2016postVFP" : 3,
                        "2017"        : 2,
                        "2018"        : 7,
                        "Run2UL"      : 1,
                        "0l"          : 7,
                        "1l"          : 7,
                        "2l"          : 7,
                        "combo"       : 1,
        }

        self.lwidths = {"2016"        : 3,
                        "2016preVFP"  : 3,
                        "2016postVFP" : 3,
                        "2017"        : 3,
                        "2018"        : 3,
                        "Run2UL"      : 3,
                        "0l"          : 4,
                        "1l"          : 4,
                        "2l"          : 4,
                        "combo"       : 4,
        }

    # ---------------------------------------
    # Draw significance lines to pvalue plots
    # ---------------------------------------
    def drawSignificanceLines(self, canvas, Xmin, Xmax, numSigma):

        canvas.cd(1)

        entries = []

        color = ROOT.TColor.GetColor("#8B2D8F")
        # Draw the 1sigma, 2sigma, and 3sigma lines
        # For 1 sigma: s = 0.68
        #   1 - (0.5 + s/2) = 0.5 - s/2
        for s in range(1, numSigma+1):

            sigma = 0.5 - ROOT.TMath.Erf(float(s)/ROOT.TMath.Sqrt(2.0))/2.0
            L = ROOT.TLine(Xmin, sigma, Xmax, sigma)
            L.SetLineColor(color)
            L.SetLineWidth(2)
            L.Draw("same")
    
            S = ROOT.TPaveText(Xmax+16,sigma-0.25*sigma,Xmax+30,sigma+0.5*sigma,"")
            S.SetBorderSize(0)
            S.SetFillStyle(0)
            S.SetTextColor(color)
            S.SetTextSize(0.045)
            S.AddText( str(s)+"#sigma" )
            S.Draw("same")
            entries.append((L,S))

        return canvas, entries


    # -----------------
    # Make pvalue plots
    # -----------------
    def makePValuePlot(self, path, dataSets, runType, approved, wip, years = ["2016"], channels = ["0l", "1l", "2l", "combo"], models = ["RPV"]):

        # Use any of the DataSet objects to get range of mass points
        tempDataSet = dataSets["%s_%s_%s"%(years[0], models[0], channels[0])]
        xpoints = tempDataSet.getData()["mList"]
        npoints = len(xpoints)

        Xmin = xpoints[0]
        Xmax = xpoints[-1]
        Ymin = 5.0e-10 # 5.0e-37 

        #if runType != "pseudoDataS":
        #Ymin = 5.0e-37 # 5.0e-10 
        Ymax = 1
    
        numSigma = 4
        if "pseudoData" in runType: numSigma = 8
    
        c1 = ROOT.TCanvas("c1","PValues",1000,1000)
        c1.Divide(1, 2)    
        c1.SetFillColor(0)
        c1.cd(1)
        ROOT.gPad.SetPad("p1", "p1", 0, 2.5 / 9.0, 1, 1, ROOT.kWhite, 0, 0)
        #ROOT.gPad.SetPad("p1", "p1", 0, 2.0 / 9.0, 1, 1, ROOT.kWhite, 0, 0)
        #ROOT.gPad.SetBottomMargin(0.01)
        ROOT.gPad.SetLeftMargin(0.11)
        ROOT.gPad.SetRightMargin(0.04)
        #ROOT.gPad.SetTopMargin(0.06 * (8.0 / 6.5))
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

        #legend = ROOT.TLegend(0.30, 0.03, 0.93, 0.29,"")
        legend = ROOT.TLegend(0.30, 0.13, 0.93, 0.29,"")
        legend.SetNColumns(2)
        legend.SetTextSize(0.05)
        legend.SetBorderSize(0)
        legend.SetFillStyle(0)

        graphs = []
        for model in models:

            if  model == "RPV": 
                legend.SetHeader("pp #rightarrow #tilde{t} #bar{#tilde{t}}, #tilde{t} #rightarrow t #tilde{#chi}^{0}_{1},  #tilde{#chi}^{0}_{1} #rightarrow jjj");
            
            elif model == "StealthSYY": 
                legend.SetHeader("pp #rightarrow #tilde{t} #bar{#tilde{t}}, #tilde{t} #rightarrow t#tilde{S}g, #tilde{S} #rightarrow S#tilde{G}, S #rightarrow gg");
            
            elif model == "SHH": 
                legend.SetHeader("pp #rightarrow #tilde{t} #bar{#tilde{t}}, SHH coupling");
            
            for year in years:

                for channel in channels:

                    coption = None
                    soption = None
                    loption = None
                    lwidth  = None
                    tag     = None

                    if len(years) == 1 and len(channels) > 1:
                        coption = self.colors[channel]
                        soption = self.lstyles[channel]
                        loption = self.labels[channel]
                        lwidth  = self.lwidths[channel]
                        tag     = year

                    elif len(years) > 1 and len(channels) == 1:
                        coption = self.colors[year]
                        soption = self.lstyles[year]
                        loption = self.labels[year]
                        lwidth  = self.lwidths[year]
                        tag     = channel

                    elif len(years) > 1 and len(channels) > 1:
                        coption = self.colors[year]
                        soption = self.lstyles[channel]
                        loption = "%s, %s"%(year, channel)
                        lwidth  = self.lwidths[channel]
                        tag = "Multiple"

                    elif len(years) == 1 and len(channels) == 1:
                        coption = self.colors[year]
                        soption = self.lstyles[year]
                        loption = "%s, %s"%(year, channel)
                        lwidth  = self.lwidths[year]
                        tag = "%s_%s"%(year, channel)

                    data = dataSets["%s_%s_%s"%(year, model, channel)].getData()

                    gr = ROOT.TGraph(npoints, array('d', xpoints), array('d', data["pList"]))
                    gr.SetLineColor(coption)
                    gr.SetLineWidth(lwidth)
                    gr.SetLineStyle(soption) 
                    gr.Draw("L SAME")
                    legend.AddEntry(gr, loption, "l")
                    graphs.append(gr)
    
        legend.Draw("same")
   
        # CMS logo 
        cmstext = ROOT.TLatex()
        cmstext.SetNDC(True)
        cmstext.SetTextAlign(11)
        cmstext.SetTextSize(0.060)
        cmstext.SetTextFont(61)
        cmstext.DrawLatex(ROOT.gPad.GetLeftMargin(), 1 - (ROOT.gPad.GetTopMargin() - 0.017), "CMS")
        cmstext.SetTextSize(0.045)
        cmstext.SetTextFont(52)

        if not approved:
            if wip:
                cmstext.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.095, 1 - (ROOT.gPad.GetTopMargin() - 0.017), "Work in Progress")
            else:
                cmstext.DrawLatex(ROOT.gPad.GetLeftMargin() + 0.095, 1 - (ROOT.gPad.GetTopMargin() - 0.017), "Preliminary")
   
        cmstext.SetTextFont(42)
        cmstext.SetTextAlign(31)
        cmstext.SetTextSize(0.045)
        cmstext.DrawLatex(1 - ROOT.gPad.GetRightMargin(), 1 - (ROOT.gPad.GetTopMargin() - 0.017), "138 fb^{-1} (13 TeV)")
    
        c1, aux = self.drawSignificanceLines(c1, Xmin, Xmax, numSigma)

        c1.cd(2)
        #ROOT.gPad.SetPad("p2", "p2", 0, 0, 1, 2.5 / 9.0, ROOT.kWhite, 0, 0)
        ROOT.gPad.SetPad("p2", "p2", 0, 0, 1, 0.1 / 9.0, ROOT.kWhite, 0, 0)
        ROOT.gPad.SetLeftMargin(0.11)
        ROOT.gPad.SetRightMargin(0.04)
        ROOT.gPad.SetTopMargin(0.01)
        ROOT.gPad.SetBottomMargin(0.37)
        ROOT.gPad.SetTicks(1,1)
    
        # Make ratio (signal strength)
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
        #hr.Draw()

        channel = "1l"
        diagnostics = dataSets["%s_%s_%s"%(year, model, channel)].getData()
        
        rvalue  = array('d', diagnostics["rList"])
        rpvalue = array('d', diagnostics["rpList"])
        rmvalue = array('d', diagnostics["rmList"])
        zero    = array('d', diagnostics["zero"])

        rband = ROOT.TGraphAsymmErrors(npoints, array('d', xpoints), rvalue, zero, zero, rmvalue, rpvalue)
        rband.SetFillColor(ROOT.TColor.GetColor("#99D8C9"))
        rband.Draw("3 same")

        r = ROOT.TGraph(npoints, array('d', xpoints), rvalue)
        r.SetLineColor(ROOT.kBlack)
        r.SetLineStyle(ROOT.kDashed)
        r.SetLineWidth(3)
        #r.Draw("PL same")
        c1.Update()
        
        line = ROOT.TF1("line", "1", Xmin, Xmax)
        line.SetLineColor(ROOT.kRed)
        #line.Draw("same")
        
        line2 = ROOT.TF1("line", "1", Xmin, Xmax)
        line2.SetLineColor(ROOT.kBlack)
        #line2.Draw("same")
   
        if approved:
            c1.Print(self.outPath + "/" + runType + "_" + model + "_" + tag + self.pdfName + "%s.pdf"%(self.asimov))
        else:
            c1.Print(self.outPath + "/" + runType + "_" + model + "_"+ tag + self.pdfName + "%s_prelim.pdf"%(self.asimov))
        del c1


# --------------
# Make tex files
# -------------- 
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


# -------------
# Main function
# -------------
def main():
    parser = argparse.ArgumentParser("usage: %prog [options]\n")
    parser.add_argument('--basedirs',  dest='basedirs',  type=str, nargs="+", default = ['.'],                       help = "Paths to output files"            )
    parser.add_argument('--outdir',    dest='outdir',    type=str,            default = '.',                         help = "Path to put output files"        )
    parser.add_argument('--pdfName',   dest='pdfName',   type=str,            default = '',                          help = "name to add at the end of pdf"   )
    parser.add_argument('--approved',  dest='approved',                       default = False, action='store_true',  help = 'Is plot approved'                )
    parser.add_argument('--wip',       dest='wip',                            default = False, action='store_true',  help = 'Is plot a work in progress'      )
    parser.add_argument('--asimov',    dest='asimov',                         default = False, action='store_true',  help = 'Is plot w/wo asimov style'       )
    parser.add_argument('--models',    dest='models',    type=str, nargs="+", default = ["RPV"] ,                    help = 'Which models to plot for'        )
    parser.add_argument('--dataTypes', dest='dataTypes', type=str, nargs="+", default = ["pseudoDataS"] ,            help = 'Which dataTypes to plot'         )
    parser.add_argument('--years',     dest='years',     type=str, nargs="+", default = ["Run2UL"] ,                 help = 'Which years to plot'             )
    parser.add_argument('--channels',  dest='channels',  type=str, nargs="+", default = ["0l", "1l", "2l", "combo"], help = 'Which channels to plot'          )
    parser.add_argument('--massRange', dest='massRange', type=str, nargs="+", default = ["300", "1400"] ,            help = 'End points of mass range to plot')
    parser.add_argument('--graft',     dest='graft',     type=int,            default = 0,                           help = 'All masses below (inclusive) the graft value will use the first basedir, anything above will use second')
    parser.add_argument('--p2',     dest='p2',                                default = False, action='store_true',  help = 'Make plots with r=0.2 (must run specific fits)')

    args    = parser.parse_args()
    pdfName = "_"+args.pdfName if args.pdfName != '' else args.pdfName

    ROOT.gROOT.SetBatch(True)

    pre_tabular = """\\begin{tabular}{l l l l}
    Mass & Best fit signal strength & Observed Significance & p-value\\\\ \hline
    """    
    path      = args.basedirs[0]
    if len(args.basedirs) == 1:
        outPath   = args.basedirs[0] + "/" + "output-files/" + "plots_dataCards_TT_allTTvar/" + args.outdir
    else:
        outPath   = "./" + args.outdir
    models    = args.models
    dataTypes = args.dataTypes
    years     = args.years
    graft     = args.graft

    if not os.path.exists(outPath):
        os.makedirs(outPath)

    masses = []
    for mass in range(int(args.massRange[0]), int(args.massRange[1])+50, 50):
        masses.append(str(mass))
    channels = args.channels

    # -----------------------------------------
    # Loop over all jobs in get the info needed
    # -----------------------------------------
    l = []; dataSets = {}; fNumber  = 0

    for runtype in dataTypes:

        # Use Asimov data set for p-values
        # Except for when running on data !
        asimovStr = ""
        if args.asimov:
            asimovStr = "_Asimov"
        if args.p2:
            asimovStr += "_0p2"

        for model in models:
     
           for channel in channels:

                outFileName = "%s/table_signal_strength_%s_%s_%i%s.tex" % (outPath, model, runtype, fNumber, asimovStr)
                fNumber += 1
                file_table = open(outFileName,'w')
                file_table.write(pre_tabular)

                for year in years:

                    aDataSet = DataSet(runtype, model, channel, year)
                    data     = {"mList":[],"rList":[],"rmList":[],"rpList":[],"sList":[],"pList":[],"zero":[]}
                    file_table.write("\\multicolumn{4}{c}{$%s$} \\\\ \\hline \n"%year)

                    for mass in masses:

                        print "Year %s, Model %s, Mass %s, Channel %s"%(year, model, mass, channel)
                        
                        tagName    = "%s%s%s%s_%s"%(year, model, mass, runtype, channel)
                        
                        if int(mass) > graft and graft != 0:
                            path = args.basedirs[1]
                            print(mass, channel)
                        else:
                            path = args.basedirs[0]

                        filename_r = "%s/output-files/%s_%s_%s/fitDiagnostics%s%s.root" % (path, model, mass, year, tagName, asimovStr)
       
                        # ------------------------------------------------------ 
                        # Get signal strength (r) from fit diagnostic ROOT files
                        # ------------------------------------------------------ 
                        r       = -1; file_r   = -1; rLowErr = 0;  rHighErr = 0

                        try:
                            file_r = ROOT.TFile.Open(filename_r, "READ")
                            tree_r = file_r.Get("tree_fit_sb")

                            tree_r.GetEntry(0)
                            fitStatus = tree_r.fit_status

                            # Assuming any non-negative status is OK...
                            if fitStatus >= 0:
                                r        = tree_r.r
                                rLowErr  = tree_r.rLoErr
                                rHighErr = tree_r.rHiErr

                        except Exception as e:
                            print(e)

                        # -------------------------------------------------------------
                        # Get sigma and p-value from fit output significance ROOT files
                        # -------------------------------------------------------------
                        sigma        = -1; pvalue = 10; file_sig = -1
                        filename_sig = "%s/output-files/%s_%s_%s/higgsCombine%s_SignifExp%s.Significance.mH%s.MODEL%s.root" % (path, model, mass, year, tagName, asimovStr, mass, model)

                        try:
                            file_sig = ROOT.TFile.Open(filename_sig, "READ")

                            tree_sig = file_sig.Get("limit")
                            tree_sig.GetEntry(0)
                            sigma = tree_sig.limit
                            pvalue = 0.5 - ROOT.TMath.Erf(float(sigma)/ROOT.TMath.Sqrt(2.0))/2.0

                        except Exception as e:
                            print(e)
        
                        # Fill lists of data
                        data["mList"].append(abs(float(mass)))
                        data["rList"].append(r)
                        data["rmList"].append(abs(rLowErr))
                        data["rpList"].append(abs(rHighErr))
                        data["sList"].append(abs(float(sigma)))
                        data["pList"].append(abs(float(pvalue)))
                        data["zero"].append(0.0)

                        aDataSet.setData(data)
        
                        # Write out r, sigma, and p-value to file
                        file_table.write("%s & %.3f_{%.2f}^{%.2f} & %.3f & %.3f\\\\ \n" % (mass, r, rLowErr, rHighErr, sigma, pvalue))

                    file_table.write("\\hline \n")
                    dataSets["%s_%s_%s"%(year, model, channel)] = aDataSet

                file_table.write("\\end{tabular}\n")
                file_table.close()
                l.append({"model":model, "runtype":runtype, "outFileName":outFileName})

    # ---------------------------------------    
    # Make tex file with all signal strengths
    # --------------------------------------- 
    makeSigTex("%s/table_signal_strength.tex"%(outPath), l)

    thePlotter = Plotter(pdfName, path, outPath, asimovStr)
    thePlotter.makePValuePlot(path, dataSets, runtype, args.approved, args.wip, args.years, args.channels, args.models)



if __name__ == '__main__':
    main()
