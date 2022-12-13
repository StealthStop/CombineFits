import os
import numpy as np
import ROOT
import argparse
from array import array

ROOT.gROOT.SetBatch(True)

class LimitPlots():

    def __init__(self, inputDir, year, model, channel, dataType, limitType):

        self.inputDir      = inputDir
        self.year          = year
        self.model         = model
        self.channel       = channel
        self.dataType      = dataType
        self.limitType     = limitType
        self.canvas        = None
        self.tdrStyle      = None
        self.outputDir     = inputDir + "/" + "output-files/" + "plots_dataCards_TT_allTTvar/" + "limit_plots/"
        self.textXposition = None
        self.textYposition = None

        # create output directory to save the plots
        if not os.path.isdir(self.outputDir):
            os.makedirs(self.outputDir)

    # -----------
    # make canvas
    # -----------
    def make_Canvas(self):

        self.canvas = ROOT.TCanvas("canvas", "", 800, 600 )
        self.canvas.SetTopMargin(0.09)
        self.canvas.SetBottomMargin(0.13)
        self.canvas.SetLeftMargin(0.16)
        self.canvas.SetRightMargin(0.03)
        self.canvas.SetTicks(1) 

    # --------------------
    # set limit plot style
    # --------------------
    def set_tdrStyle(self):

        self.tdrStyle = ROOT.TStyle("tdrStyle","Style for P-TDR")

        # for canvas
        self.tdrStyle.SetCanvasBorderMode(0)
        self.tdrStyle.SetCanvasColor(ROOT.kWhite)
        self.tdrStyle.SetCanvasDefH(600) # Height of canvas
        self.tdrStyle.SetCanvasDefW(600) # Width of canvas
        self.tdrStyle.SetCanvasDefX(0)   # POsition on screen
        self.tdrStyle.SetCanvasDefY(0)

        # for pad
        self.tdrStyle.SetPadBorderMode(0)
        self.tdrStyle.SetPadColor(ROOT.kWhite)
        self.tdrStyle.SetPadGridX(False)
        self.tdrStyle.SetPadGridY(False)
        self.tdrStyle.SetGridColor(0)
        self.tdrStyle.SetGridStyle(3)
        self.tdrStyle.SetGridWidth(1)

        # for frame
        self.tdrStyle.SetFrameBorderMode(0)
        self.tdrStyle.SetFrameBorderSize(1)
        self.tdrStyle.SetFrameFillColor(0)
        self.tdrStyle.SetFrameFillStyle(0)
        self.tdrStyle.SetFrameLineColor(1)
        self.tdrStyle.SetFrameLineStyle(1)
        self.tdrStyle.SetFrameLineWidth(1)

        # for histogram
        self.tdrStyle.SetHistLineColor(1)
        self.tdrStyle.SetHistLineStyle(0)
        self.tdrStyle.SetHistLineWidth(1)
        self.tdrStyle.SetEndErrorSize(2)
        self.tdrStyle.SetMarkerStyle(20)
        self.tdrStyle.SetFitFormat("5.4g")
        self.tdrStyle.SetFuncColor(2)
        self.tdrStyle.SetFuncStyle(1)
        self.tdrStyle.SetFuncWidth(1)

        # for date
        self.tdrStyle.SetOptDate(0)

        # for stat box
        self.tdrStyle.SetOptFile(0)
        self.tdrStyle.SetOptStat(0) # To display the mean and RMS:   SetOptStat("mr");
        self.tdrStyle.SetStatColor(ROOT.kWhite)
        self.tdrStyle.SetStatFont(42)
        self.tdrStyle.SetStatFontSize(0.025)
        self.tdrStyle.SetStatTextColor(1)
        self.tdrStyle.SetStatFormat("6.4g")
        self.tdrStyle.SetStatBorderSize(1)
        self.tdrStyle.SetStatH(0.1)
        self.tdrStyle.SetStatW(0.15)

        # margins
        self.tdrStyle.SetPadTopMargin(0.05)
        self.tdrStyle.SetPadBottomMargin(0.13)
        self.tdrStyle.SetPadLeftMargin(0.16)
        self.tdrStyle.SetPadRightMargin(0.03)

        # for global titles & axes titles & axes labels
        self.tdrStyle.SetOptTitle(0)
        self.tdrStyle.SetTitleFont(42)
        self.tdrStyle.SetTitleColor(1)
        self.tdrStyle.SetTitleTextColor(1)
        self.tdrStyle.SetTitleFillColor(10)
        self.tdrStyle.SetTitleFontSize(0.05)

        self.tdrStyle.SetTitleColor(1, "XYZ")
        self.tdrStyle.SetTitleFont(42, "XYZ")
        self.tdrStyle.SetTitleSize(0.06, "XYZ")
        self.tdrStyle.SetTitleXOffset(0.9)
        self.tdrStyle.SetTitleYOffset(1.25)

        self.tdrStyle.SetLabelColor(1, "XYZ")
        self.tdrStyle.SetLabelFont(42, "XYZ")
        self.tdrStyle.SetLabelOffset(0.007, "XYZ")
        self.tdrStyle.SetLabelSize(0.05, "XYZ")

        self.tdrStyle.SetAxisColor(1, "XYZ")
        self.tdrStyle.SetStripDecimals(True)
        self.tdrStyle.SetTickLength(0.03, "XYZ")
        self.tdrStyle.SetNdivisions(510, "XYZ")
        self.tdrStyle.SetPadTickX(1) # To get tick marks on the opposite side of the frame
        self.tdrStyle.SetPadTickY(1)

        self.tdrStyle.SetOptLogx(0)
        self.tdrStyle.SetOptLogy(0)
        self.tdrStyle.SetOptLogz(0)

        self.tdrStyle.SetPaperSize(20.,20.)
        self.tdrStyle.SetHatchesLineWidth(5)
        self.tdrStyle.SetHatchesSpacing(0.05)

        self.tdrStyle.cd()

    # -----------------
    # draw lumi and CMS
    # -----------------
    def draw_LumiCMS(self, approved = False, wip = True):

        self.canvas.cd()

        lumiText = ""
        if   self.year == "2016preVFP":
            lumiText = "19.5 fb^{-1}"
        elif self.year == "2016postVFP":
            lumiText = "16.8 fb^{-1}"
        elif self.year == "2016":
            lumiText = "36.3 fb^{-1}"
        elif self.year == "2017":
            lumiText = "41.5 fb^{-1}"
        elif self.year == "2018":
            lumiText = "59.8 fb^{-1}"
        elif self.year == "Run2UL":
            lumiText = "138 fb^{-1}"

        lumiText += " (13 TeV)"

        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextAngle(0)
        latex.SetTextColor(ROOT.kBlack)

        # Text sizes and text offsets with respect to the top frame
        # in unit of the top margin size
        leftMargin   = self.canvas.GetLeftMargin()
        topMargin    = self.canvas.GetTopMargin()
        rightMargin  = self.canvas.GetRightMargin()
        bottomMargin = self.canvas.GetBottomMargin()

        # Text font/style in ROOT
        # https://root.cern.ch/doc/master/classTAttText.html#ATTTEXT5
        latex.SetTextFont(42)
        latex.SetTextAlign(31)
        latex.SetTextSize(0.65 * topMargin)
        latex.DrawLatex(1.0 - rightMargin, 1.0 - topMargin + 0.2 * topMargin, lumiText)

        self.textXposition = leftMargin + 0.045 * (1.0 - leftMargin - rightMargin)
        self.textYposition = 1.0 - topMargin - 0.045 * (1 - topMargin - bottomMargin)

        # Text alignment in ROOT
        # https://root.cern.ch/doc/master/classTAttText.html#ATTTEXT1
        textAlignment = 13
        cmsTextSize = 0.8

        latex.SetTextFont(61)
        latex.SetTextSize(cmsTextSize * topMargin)
        latex.SetTextAlign(textAlignment)
        latex.DrawLatex(self.textXposition, self.textYposition, "CMS")

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

            latex.DrawLatex(self.textXposition, self.textYposition - 1.2 * cmsTextSize * topMargin, extraText) 

    # -----------------------
    # draw signal information
    # -----------------------
    def draw_SignalInfo(self):

        self.canvas.cd()

        textSize = 0.04

        latex = ROOT.TLatex()
        latex.SetNDC()
        latex.SetTextAngle(0)
        latex.SetTextColor(ROOT.kBlack)
        #latex.SetBorderSize(0)
        #latex.SetFillStyle(0)
        latex.SetTextAlign(12)
        latex.SetTextFont(42)
        latex.SetTextSize(textSize)

        if (self.model=="RPV"):
            latex.DrawLatex(self.textXposition, (self.textYposition - 0.55),                  "#bf{#it{#Beta}}(#tilde{t} #rightarrow t #tilde{#chi}^{0}_{1}) = 1.0")
            latex.DrawLatex(self.textXposition, (self.textYposition - 1.8 * textSize) - 0.55, "#bf{#it{#Beta}}(#tilde{#chi}^{0}_{1} #rightarrow jjj) = 1.0")
            latex.DrawLatex(self.textXposition, (self.textYposition - 3.5 * textSize) - 0.55, "m_{#tilde{#chi}^{0}_{1}} = 100 GeV")
      
        elif (self.model=="SYY"):
            latex.DrawLatex(self.textXposition, (self.textYposition - 0.55),                  "#bf{#it{#Beta}}(#tilde{t} #rightarrow t#tilde{S}g) = 1.0")
            latex.DrawLatex(self.textXposition, (self.textYposition - 1.2 * textSize) - 0.55, "#bf{#it{#Beta}}(#tilde{S} #rightarrow S#tilde{G}) = 1.0, #bf{#it{#Beta}}(S #rightarrow gg) = 1.0")
            latex.DrawLatex(self.textXposition, (self.textYposition - 2.4 * textSize) - 0.55, "m_{#tilde{S}} = 100 GeV, m_{#tilde{G}} = 1 GeV, m_{S} = 90 GeV")
        
    # ----------------
    # make limit plots
    # ----------------
    def make_LimitPlots(self, approved = False, wip = True, limitType = "AsymptoticLimits"):

        # -----------
        # make canvas
        # -----------
        self.make_Canvas()
    
        # --------------------
        # set limit plot style
        # --------------------
        self.set_tdrStyle()

        # ---------------------------------------------------------------------------
        # extract limit results from set of root files produced by Higgs Combine tool
        # --------------------------------------------------------------------------- 
        mass_points     = list(range(300, 1450, 50))
        num_mass_points = len(mass_points)

        # ------------------------------------------------------
        # initialize lists to store expected and observed limits
        # ------------------------------------------------------ 
        limits_68expected_below = [0] * num_mass_points # 68% expected below 
        limits_68expected_above = [0] * num_mass_points # # 68% expected above
        limits_95expected_below = [0] * num_mass_points # 95% expected below
        limits_95expected_above = [0] * num_mass_points # 95% expected above
        limits_mean             = [0] * num_mass_points # blue dashed line on the limit plot
        limits_obs              = [0] * num_mass_points # dot black point line on the limit plot
        limits_obsErr           = [0] * num_mass_points # unc. on dot black point line

        # ---------------------------
        # labels for input root files
        # ---------------------------
        extra = ""
    
        if (self.limitType == "AsymptoticLimits"):
            extra = "_AsymLimit"

        elif (self.limitType == "Significance"):
            extra = "_SignifExp"

        # -------------------------------------------------
        # loop over mass points to open and read root files
        # -------------------------------------------------   
        for n in range(0, num_mass_points):

            mass = str(mass_points[n])

            # path for input root files   
            label    = self.year + self.model + mass + self.dataType + "_" + self.channel + "_AsymLimit" 
            fitInput = self.inputDir + "/output-files" + "/" + self.model + "_" + mass + "_" + self.year + "/higgsCombine" + label + "." + self.limitType + ".mH" + mass + ".MODEL" + self.model + ".root"

            # load input root files 
            rootFile = ROOT.TFile.Open(fitInput, "READ")

            # read tree and leaves from each root file
            tree = rootFile.Get("limit")

            iEntry = 0
            tree.GetEntry(iEntry)
            
            limits_95expected_below[n] = tree.limit
            iEntry += 1
            tree.GetEntry(iEntry)
            
            limits_68expected_below[n] = tree.limit
            iEntry += 1
            tree.GetEntry(iEntry)

            limits_mean[n] = tree.limit
            iEntry += 1
            tree.GetEntry(iEntry)
            
            limits_68expected_above[n] = tree.limit
            iEntry += 1
            tree.GetEntry(iEntry)
            
            limits_95expected_above[n] = tree.limit
            iEntry += 1
            tree.GetEntry(iEntry)
            
            limits_obs[n]              = tree.limit
            limits_obsErr[n]           = tree.limitErr

            rootFile.Close()

        # ----------------------------------------------------------------
        # define the cross section times branching fraction (called sigBr)
        # ----------------------------------------------------------------
        sigBr = []; sigBr1SPpercent = []; sigBr1SMpercent = []
        
        # cross sections and uncertainties from
        # https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SUSYCrossSections13TeVstopsbottom
        stopPair_Br = [ 10.00, 4.43, 2.15, 1.11,  0.609, 0.347, 0.205, 0.125, 0.0783, 0.0500, 0.0326, 0.0216, 0.0145, 
                         0.00991, 0.00683, 0.00476, 0.00335, 0.00238, 0.00170, 0.00122, 0.000887, 0.000646, 0.000473 ]
        
        stopPair_Br1SPpercent = [ 6.65, 6.79, 6.99, 7.25,  7.530, 7.810, 8.120, 8.450, 8.8000, 9.1600, 9.5300, 9.9300, 10.3300,
                                   10.76, 11.2, 11.65, 12.12, 12.62, 13.13, 13.66, 14.21, 14.78, 15.37 ]
        
        stopPair_Br1SMpercent = stopPair_Br1SPpercent

        # for stop pair production
        sigBr           = stopPair_Br
        sigBr1SPpercent = stopPair_Br1SPpercent
        sigBr1SMpercent = stopPair_Br1SMpercent
    
        sigBr1SP = [0] * num_mass_points
        xErr     = [0] * num_mass_points
        sigBr1SM = [0] * num_mass_points

        for n in range(0, num_mass_points):
            sigBr1SP[n] = sigBr[n] * sigBr1SPpercent[n] / 100.0
            sigBr1SM[n] = sigBr[n] * sigBr1SMpercent[n] / 100.0

        # x-y ranges & y-axis label in the limit plot
        projectingRLimitLogY     = True;
        projectingXmin           = mass_points[0]  - 50 
        projectingXmax           = mass_points[-1] + 50
        projectingRLimitYmin     = 0.0005
        projectingRLimitYmax     = 100
        projectingRLimitXYtitles = ";m_{#tilde{t}} [GeV]; 95% CL upper limit on #sigma#bf{#it{#Beta}} [pb]"
        plotLabel                = self.outputDir + "_CLs"

        # ----------------------------------
        # store expected and observed limits
        # ----------------------------------
        limits_exp = [0] * num_mass_points
        for n in range(0, num_mass_points):
            limits_68expected_below[n] = limits_68expected_below[n] * sigBr[n]
            limits_68expected_above[n] = limits_68expected_above[n] * sigBr[n]
            limits_95expected_below[n] = limits_95expected_below[n] * sigBr[n]
            limits_95expected_above[n] = limits_95expected_above[n] * sigBr[n]
            limits_mean[n]             = limits_mean[n] * sigBr[n]
            limits_exp[n]              = limits_mean[n]
            limits_obs[n]              = limits_obs[n]  * sigBr[n]

        # ---------------
        # dummy histogram
        # ---------------
        stmp   = "hframe"
        stmp  += plotLabel
        hframe = ROOT.TH1F(stmp, projectingRLimitXYtitles, 1000, projectingXmin, projectingXmax)
        hframe.SetMinimum(projectingRLimitYmin)
        hframe.SetMaximum(projectingRLimitYmax)
        hframe.SetStats(0)
        hframe.SetFillStyle(1)
        hframe.Draw(" ")
        self.canvas.SetLogy(projectingRLimitLogY)
        
        # -------------------------------------------------------------------
        # make bands and lines for limits
        #   -- blue dashed line - expected limit
        #   -- yellow band - 95% expected
        #   -- green band - 68% expected
        #   -- black line - observed
        #   -- red solid line - theory cross section for stop pair production
        # -------------------------------------------------------------------
        grMean      = ROOT.TGraph(num_mass_points, np.array(mass_points,dtype="d"), np.array(limits_exp,dtype="d")) # blue dahed line
        grYellow    = ROOT.TGraph(2 * num_mass_points)                                                              # yellow band 
        grGreen     = ROOT.TGraph(2 * num_mass_points)                                                              # green band 
        grObs       = ROOT.TGraph(num_mass_points, np.array(mass_points,dtype="d"), np.array(limits_obs,dtype="d")) # black line 
        grTheory    = ROOT.TGraph(num_mass_points, np.array(mass_points,dtype="d"), np.array(sigBr, dtype="d"))     # red solid line 
        grTheoryErr = ROOT.TGraphAsymmErrors(num_mass_points, np.array(mass_points,dtype="d"), np.array(sigBr, dtype="d"), np.array(xErr,dtype="d"), np.array(xErr,dtype="d"), np.array(sigBr1SM,dtype="d"), np.array(sigBr1SP,dtype="d")) 

        for n in range(0,num_mass_points):
            grYellow.SetPoint(n, mass_points[n], limits_95expected_above[n])
            grYellow.SetPoint(num_mass_points + n, mass_points[num_mass_points - n - 1], limits_95expected_below[num_mass_points - n - 1])
            grGreen.SetPoint(n, mass_points[n], limits_68expected_above[n])
            grGreen.SetPoint(num_mass_points + n, mass_points[num_mass_points - n - 1], limits_68expected_below[num_mass_points - n - 1])

        grYellow.SetFillColor(ROOT.kOrange)
        grYellow.SetLineColor(ROOT.kOrange)
        grYellow.Draw("f")
        grGreen.SetFillColor(ROOT.kGreen+1)
        grGreen.SetLineColor(ROOT.kGreen+1)
        grGreen.Draw("f, same")
        grMean.SetMarkerSize(0)
        grMean.SetLineWidth(2)
        grMean.SetLineStyle(2)
        grMean.SetLineColor(ROOT.kBlue)
        grMean.Draw("lp")
        grObs.SetLineWidth(2)
        grObs.SetMarkerStyle(20)
        grObs.SetLineColor(ROOT.kBlack)
        grObs.SetMarkerColor(ROOT.kBlack)
        grObs.Draw("lp")
        grTheory.SetLineColor(2)
        grTheory.SetLineWidth(2)
        grTheoryErr.SetLineColor(2)
        grTheoryErr.SetLineWidth(2)
        grTheoryErr.SetFillColor(42)

        # add them to legend
        legend = ROOT.TLegend(0.65, 0.62, 0.845, 0.88)
        legend.SetFillColor(0)
        legend.SetFillStyle(0)
        legend.SetTextFont(42)
        legend.SetBorderSize(0)
        legend.SetTextAlign(12)
        legend.SetTextSize(0.035)

        header = ""
        if (self.model=="RPV"):
            header = "pp #rightarrow #tilde{t} #bar{#tilde{t}}, #tilde{t} #rightarrow t #tilde{#chi}^{0}_{1},  #tilde{#chi}^{0}_{1} #rightarrow jjj"
            legend.SetHeader(header)
        elif (self.model=="SYY"):
            header = "pp #rightarrow #tilde{t} #bar{#tilde{t}}, #tilde{t} #rightarrow t#tilde{S}g, #tilde{S} #rightarrow S#tilde{G}, S #rightarrow gg"
            legend.SetHeader(header)

        legend.AddEntry(grGreen,  "68% expected",   "f" )
        legend.AddEntry(grYellow, "95% expected",   "f" )
        legend.AddEntry(grObs,    "Observed limit", "lp")

        if (self.model=="RPV"):
            legend.AddEntry(grTheoryErr,"#sigma_{#tilde{t}#bar{#tilde{t}}} (NNLO+NNLL)", "lf")
        elif (self.model=="SYY"):
            legend.AddEntry(grTheoryErr,"#sigma_{#tilde{t}#bar{#tilde{t}}} (NNLO+NNLL)", "lf")

        legend.Draw()

        grTheoryErr.Draw("3, same")       
        grTheory.Draw("   l, same") 

        # redraw
        grMean.Draw("lp")
        grObs.Draw("lp")

        # -----------------------
        # draw signal information
        # -----------------------
        self.canvas.cd()
        self.draw_LumiCMS()
        self.draw_SignalInfo()
        self.canvas.SaveAs(self.outputDir + "sigBrLim" + "_" + self.inputDir + "_" + self.year + "_" + self.model + "_" + self.channel + "_" + self.dataType + ".pdf")

# -------------
# Main function
# -------------
def main():
    parser = argparse.ArgumentParser("usage: %prog [options]\n")
    parser.add_argument("--inputDir",  dest="inputDir",  type=str, required=True,                                      help = "path to get the input root files")
    parser.add_argument("--year",      dest="year",      type=str, default = "Run2UL" ,                                help = "which year to plot"              )
    parser.add_argument("--model",     dest="model",     type=str, default = "RPV" ,                                   help = "which model to plot"             )
    parser.add_argument("--channel",   dest="channel",   type=str, default = "1l" ,                                    help = "which channel to plot"           )
    parser.add_argument("--dataType",  dest="dataType",  type=str, default = "pseudoData",                             help = "which dataType to plot"          )
    parser.add_argument("--limitType", dest="limitType", type=str, default = "AsymptoticLimits",                       help = "which limitType to plot"         )
    parser.add_argument("--approved",  dest="approved",            default = False,              action="store_true",  help = "is plot approved"                )
    parser.add_argument("--wip",       dest="wip",                 default = False,              action="store_true",  help = "is plot a work in progress"      )


    args = parser.parse_args()

    limitPlots_Objects = LimitPlots(args.inputDir, args.year, args.model, args.channel, args.dataType, args.limitType) 
    limitPlots_Objects.make_LimitPlots(args.approved, args.wip, args.limitType)



if __name__ == '__main__':
    main()