import os
import time
import numpy as np
import ROOT
import argparse
import copy
import math
from array import array

ROOT.gROOT.SetBatch(True)

class LimitPlots():

    def __init__(self, inputDirs, outputDir, year, model, channel, dataType, limitType, graft, noRatio):

        self.inputDirs     = inputDirs
        self.year          = year
        self.model         = model
        self.channel       = channel
        self.dataType      = dataType
        self.limitType     = limitType
        self.graft         = graft
        self.canvas        = None
        self.tdrStyle      = None
        self.outputDir     = outputDir 
        self.textXposition = None
        self.textYposition = None
        self.noRatio = noRatio

        # create output directory to save the plots
        if not os.path.isdir(self.outputDir):
            os.makedirs(self.outputDir)

    # -----------
    # make canvas
    # -----------
    def make_Canvas(self):

        if self.noRatio:
            self.canvas = ROOT.TCanvas("canvas", "", 800, 600 )
            self.canvas.SetTopMargin(0.09)
            self.canvas.SetBottomMargin(0.13)
            self.canvas.SetLeftMargin(0.16)
            self.canvas.SetRightMargin(0.03)
        else:
            self.TopMargin    = 0.09
            self.BottomMargin = 0.13
            self.RightMargin  = 0.03
            self.LeftMargin   = 0.16

            self.canvas = ROOT.TCanvas("canvas", "", 1200, 1200 )
            
            self.split = 0.3
            self.upperSplit = 1.0 - self.split
            self.lowerSplit = self.split
            self.scale = self.upperSplit / self.lowerSplit

            self.pad1 = ROOT.TPad("pad1", "", 0.0, self.split, 1.0, 1.0)
            self.pad1.SetTopMargin(self.TopMargin / self.upperSplit)
            self.pad1.SetBottomMargin(0)
            self.pad1.SetLeftMargin(self.LeftMargin)
            self.pad1.SetRightMargin(self.RightMargin)
            self.pad1.Draw()
            self.pad2 = ROOT.TPad("pad2", "", 0.0, 0.0, 1.0, 0.3)
            self.pad2.SetTopMargin(0)
            self.pad2.SetBottomMargin(self.BottomMargin / self.lowerSplit)
            self.pad2.SetLeftMargin(self.LeftMargin)
            self.pad2.SetRightMargin(self.RightMargin)
            self.pad2.Draw()
            

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
        if self.noRatio:
            self.canvas.cd()
        else:
            self.pad1.cd()

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
        latex.SetTextSize(0.55 * topMargin)
        if self.noRatio:
            latex.DrawLatex(1.0 - rightMargin, 1.0 - topMargin + 0.2 * topMargin, lumiText)
        else:
            latex.DrawLatex(1.0 + 0.07 - rightMargin, 1.0 - 0.02 - topMargin + 0.2 * topMargin, lumiText)

        if self.noRatio:
            self.textXposition = leftMargin + 0.045 * (1.0 - leftMargin - rightMargin)
            self.textYposition = 1.0 - topMargin - 0.045 * (1 - topMargin - bottomMargin)
        else:
            self.textXposition = leftMargin + 0.06 + 0.045 * (1.0 - leftMargin - rightMargin)
            self.textYposition = 1.0 - topMargin - 0.045 * (1 - topMargin - bottomMargin) - 0.02

        # Text alignment in ROOT
        # https://root.cern.ch/doc/master/classTAttText.html#ATTTEXT1
        textAlignment = 13
        cmsTextSize = 0.6

        latex.SetTextFont(61)
        latex.SetTextSize(cmsTextSize * topMargin)
        latex.SetTextAlign(textAlignment)
        latex.DrawLatex(self.textXposition, self.textYposition, "CMS")
        #latex.DrawLatex(self.textXposition, self.textYposition, "Private Work")

        # Label with "Prelimiary" if not approved and "work in progress" is WIP
        if not approved:

            latex.SetTextFont(52)
            latex.SetTextAlign(textAlignment)
            latex.SetTextSize(0.35 * cmsTextSize * topMargin)

            extraText = ""
            if not wip:
                extraText = "Preliminary"
            else:
                extraText = "Work in Progress"
                #extraText = "(CMS Simulation)"

            latex.DrawLatex(self.textXposition, self.textYposition - 1.1 * cmsTextSize * topMargin, extraText) 

    # -----------------------
    # draw signal information
    # -----------------------
    def draw_SignalInfo(self):
        if self.noRatio:
            self.canvas.cd()
        else:
            self.pad1.cd(1)

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
        
        if not self.noRatio:
            self.textYposition -= 0.1

        if (self.model=="RPV"):
            latex.DrawLatex(self.textXposition, (self.textYposition - 0.55),                  "#bf{#it{#Beta}}(#tilde{t} #rightarrow t #tilde{#chi}^{0}_{1}) = 1.0")
            latex.DrawLatex(self.textXposition, (self.textYposition - 1.9 * textSize) - 0.55, "#bf{#it{#Beta}}(#tilde{#chi}^{0}_{1} #rightarrow jjj) = 1.0")
            latex.DrawLatex(self.textXposition, (self.textYposition - 3.6 * textSize) - 0.55, "m_{#tilde{#chi}^{0}_{1}} = 100 GeV")
      
        elif (self.model=="StealthSYY"):
            latex.DrawLatex(self.textXposition, (self.textYposition - 0.55),                  "#bf{#it{#Beta}}(#tilde{t} #rightarrow t#tilde{S}g) = 1.0")
            latex.DrawLatex(self.textXposition, (self.textYposition - 1.6 * textSize) - 0.55, "#bf{#it{#Beta}}(#tilde{S} #rightarrow S#tilde{G}) = 1.0, #bf{#it{#Beta}}(S #rightarrow gg) = 1.0")
            latex.DrawLatex(self.textXposition, (self.textYposition - 3.3 * textSize) - 0.55, "m_{#tilde{S}} = 100 GeV, m_{#tilde{G}} = 1 GeV, m_{S} = 90 GeV")
        
    # ----------------
    # make limit plots
    # ----------------
    def make_LimitPlots(self, approved = False, wip = True, limitType = "AsymptoticLimits", asimov=False, combo=False):

        # -----------
        # make canvas
        # -----------
        self.make_Canvas()
   
        # --------------------
        # set limit plot style
        # --------------------
        self.set_tdrStyle()

        # NEED TO WRITE RATIO HERE 
        if not self.noRatio:
            self.pad2.cd()
            ROOT.gPad.Update()
            stmp   = "hframe2"
            hframe2 = ROOT.TH1F(stmp, "title", 1000, 250, 1250)
            hframe2.SetMinimum(0)
            hframe2.SetMaximum(4.2)
            hframe2.SetStats(0)
            hframe2.SetFillStyle(1)
            hframe2.GetYaxis().SetTitle("#frac{SUS-19-004 Expected}{Combo Expected}")
            hframe2.GetXaxis().SetTitle("m_{ #tilde{t}} [GeV]")
            hframe2.Draw(" ")

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
        
        if combo:
            limits_mean_0l = [0] * num_mass_points
            limits_mean_1l = [0] * num_mass_points
            limits_mean_2l = [0] * num_mass_points

        # ---------------------------
        # labels for input root files
        # ---------------------------
        extra = ""
    
        if (self.limitType == "AsymptoticLimits"):
            extra = "_AsymLimit"

        elif (self.limitType == "Significance"):
            extra = "_SignifExp"

        if asimov:
            extra += "_Asimov"

        # -------------------------------------------------
        # loop over mass points to open and read root files
        # -------------------------------------------------   
        for n in range(0, num_mass_points):

            mass = str(mass_points[n])

            if self.graft >= int(mass) or self.graft == 0:
                self.inputDir = self.inputDirs[0]
            else:
                self.inputDir = self.inputDirs[1]

            # path for input root files   
            label    = self.year + self.model + mass + self.dataType + "_" + self.channel + "_AsymLimit" 
            fitInput = self.inputDir + "/output-files" + "/" + self.model + "_" + mass + "_" + self.year + "/higgsCombine" + label + "." + self.limitType + ".mH" + mass + ".MODEL" + self.model + ".root"
            
            extra_inputs = []
            if combo:
                for ch in ["0l", "1l", "2l"]:
                    extra_label    = self.year + self.model + mass + self.dataType + "_" + ch + "_AsymLimit" 
                    extra_inputs.append(self.inputDir + "/output-files" + "/" + self.model + "_" + mass + "_" + self.year + "/higgsCombine" + extra_label + "." + self.limitType + ".mH" + mass + ".MODEL" + self.model + ".root")

            try:
                # load input root files 
                rootFile = ROOT.TFile.Open(fitInput, "READ")

                if combo:
                    extra_rootFiles = []
                    extraTrees = []
                    for i,ext in enumerate(extra_inputs):
                        extra_rootFiles.append(ROOT.TFile.Open(ext, "READ"))

                        extraTrees.append(extra_rootFiles[i].Get("limit"))


                # read tree and leaves from each root file
                tree = rootFile.Get("limit")
            except Exception as e:
                print("Something went wrong while {} {} fit, continuing...".format(mass, self.model))
                print(e)
                continue

            iEntry = 0
            try:
                tree.GetEntry(iEntry)
            except Exception as e:
                print("limit not present in root file")
                continue
            
            limits_95expected_below[n] = tree.limit
            iEntry += 1
            tree.GetEntry(iEntry)
            
            limits_68expected_below[n] = tree.limit
            iEntry += 1
            tree.GetEntry(iEntry)

            limits_mean[n] = tree.limit

            # ------------------------------------------------------------------
            # Overlay mean for three channels independently for combo limit plot
            # ------------------------------------------------------------------
            if combo:
                try:
                    extraTrees[0].GetEntry(iEntry)
                except Exception as e:
                    print("limit not present in root file")
                    continue
                limits_mean_0l[n] = extraTrees[0].limit

                try:
                    extraTrees[1].GetEntry(iEntry)
                except Exception as e:
                    print("limit not present in root file")
                    continue
                limits_mean_1l[n] = extraTrees[1].limit
                
                try:
                    extraTrees[2].GetEntry(iEntry)
                except Exception as e:
                    print("limit not present in root file")
                    continue
                limits_mean_2l[n] = extraTrees[2].limit

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
        projectingXmax           = 1200 + 50
        #projectingXmax           = mass_points[-1] + 50
        projectingRLimitYmin     = 0.002
        projectingRLimitYmax     = 40
        projectingRLimitXYtitles = ";m_{ #tilde{t}} [GeV]; 95% CL upper limit on #sigma#bf{#it{#Beta}} [pb]"
        plotLabel                = self.outputDir + "_CLs"

        # ----------------------------------
        # store expected and observed limits
        # ----------------------------------
        limits_exp = [0] * num_mass_points
        if combo:
            limits_exp_0l = [0] * num_mass_points
            limits_exp_1l = [0] * num_mass_points
            limits_exp_2l = [0] * num_mass_points
            
        for n in range(0, num_mass_points):
            limits_68expected_below[n] = limits_68expected_below[n] * sigBr[n]
            limits_68expected_above[n] = limits_68expected_above[n] * sigBr[n]
            limits_95expected_below[n] = limits_95expected_below[n] * sigBr[n]
            limits_95expected_above[n] = limits_95expected_above[n] * sigBr[n]
            limits_mean[n]             = limits_mean[n] * sigBr[n]

            if combo:
                limits_mean_0l[n]             = limits_mean_0l[n] * sigBr[n]
                limits_mean_1l[n]             = limits_mean_1l[n] * sigBr[n]
                limits_mean_2l[n]             = limits_mean_2l[n] * sigBr[n]

                limits_exp_0l[n]              = limits_mean_0l[n]
                limits_exp_1l[n]              = limits_mean_1l[n]
                limits_exp_2l[n]              = limits_mean_2l[n]
                
            limits_exp[n]              = limits_mean[n]
            limits_obs[n]              = limits_obs[n]  * sigBr[n]

        # ---------------
        # dummy histogram
        # ---------------
        if self.noRatio:
            self.canvas.cd()
        else:
            self.pad1.cd()
        stmp   = "hframe"
        stmp  += plotLabel
        hframe = ROOT.TH1F(stmp, projectingRLimitXYtitles, 1000, projectingXmin, projectingXmax)
        hframe.SetMinimum(projectingRLimitYmin)
        hframe.SetMaximum(projectingRLimitYmax)
        hframe.SetStats(0)
        hframe.SetFillStyle(1)
        hframe.Draw(" ")
        if self.noRatio:
            self.canvas.SetLogy(projectingRLimitLogY)
        else:
            self.pad1.SetLogy(projectingRLimitLogY)
        
        # -------------------------------------------------------------------
        # make bands and lines for limits
        #   -- blue dashed line - expected limit
        #   -- yellow band - 95% expected
        #   -- green band - 68% expected
        #   -- black line - observed
        #   -- red solid line - theory cross section for stop pair production
        # -------------------------------------------------------------------
        grMean      = ROOT.TGraph(num_mass_points, np.array(mass_points,dtype="d"), np.array(limits_exp,dtype="d")) # blue dahed line
        if combo:
            grMean_0l      = ROOT.TGraph(num_mass_points, np.array(mass_points,dtype="d"), np.array(limits_exp_0l,dtype="d")) # red dahed line
            grMean_1l      = ROOT.TGraph(num_mass_points, np.array(mass_points,dtype="d"), np.array(limits_exp_1l,dtype="d")) # cyan dahed line
            grMean_2l      = ROOT.TGraph(num_mass_points, np.array(mass_points,dtype="d"), np.array(limits_exp_2l,dtype="d")) # magenta dahed line
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
        grGreen.SetLineColor(ROOT.kGreen)
        grGreen.Draw("f, same")
        grMean.SetMarkerSize(0)
        grMean.SetLineWidth(2)
        grMean.SetLineStyle(2)
        grMean.SetLineColor(ROOT.kBlue)
        grMean.Draw("lp")

        if combo:
            grMean_0l.SetMarkerSize(0)
            grMean_0l.SetLineWidth(2)
            grMean_0l.SetLineStyle(2)
            grMean_0l.SetLineColor(ROOT.TColor.GetColor("#2ca25f"))
            grMean_0l.Draw("l")

            grMean_1l.SetMarkerSize(0)
            grMean_1l.SetLineWidth(2)
            grMean_1l.SetLineStyle(2)
            grMean_1l.SetLineColor(ROOT.kCyan)
            grMean_1l.Draw("l")

            grMean_2l.SetMarkerSize(0)
            grMean_2l.SetLineWidth(2)
            grMean_2l.SetLineStyle(2)
            grMean_2l.SetLineColor(ROOT.TColor.GetColor("#CE1256"))
            grMean_2l.Draw("l")

        grObs.SetLineWidth(2)
        grObs.SetMarkerStyle(20)
        grObs.SetLineColor(ROOT.kBlack)
        grObs.SetMarkerColor(ROOT.kBlack)
        if not asimov: grObs.Draw("lp")
        grTheory.SetLineColor(2)
        grTheory.SetLineWidth(2)
        grTheoryErr.SetLineColor(2)
        grTheoryErr.SetLineWidth(2)
        grTheoryErr.SetFillColor(42)

        # add them to legend
        legend = None
        if self.noRatio:
            if combo:
                legend = ROOT.TLegend(0.325, 0.65, 0.90, 0.90)
            else:
                legend = ROOT.TLegend(0.325, 0.65, 0.90, 0.90)
            legend.SetNColumns(2)
            legend.SetFillColor(0)
            legend.SetFillStyle(0)
            legend.SetTextFont(42)
            legend.SetBorderSize(0)
            legend.SetTextAlign(12)
            legend.SetTextSize(0.035)
        else: 
            legend = ROOT.TLegend(0.325, 0.60, 0.975, 0.85)
            legend.SetNColumns(2)
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
        elif (self.model=="StealthSYY"):
            header = "pp #rightarrow #tilde{t} #bar{#tilde{t}}, #tilde{t} #rightarrow t#tilde{S}g, #tilde{S} #rightarrow S#tilde{G}, S #rightarrow gg"
            legend.SetHeader(header)


        legend.Draw()

        grTheoryErr.Draw("3, same")       
        grTheory.Draw("   l, same") 

        # redraw
        grMean.Draw("lp")

        ratio = grMean.Clone()
        if combo:
            grMean_0l.Draw("lp")
            grMean_1l.Draw("lp")
            grMean_2l.Draw("lp")
            legend.AddEntry(grGreen,  "68% expected",   "f" )
            legend.AddEntry(grMean_0l,  "Mean expected limit (0l)",   "l" )
            legend.AddEntry(grYellow, "95% expected",   "f" )
            legend.AddEntry(grMean_1l,  "Mean expected limit (1l)",   "l" )
            if (self.model=="RPV"):
                legend.AddEntry(grTheoryErr,"#sigma_{#tilde{t} #bar{#tilde{t}}} (NNLO+NNLL)", "lf")
            elif (self.model=="StealthSYY"):
                legend.AddEntry(grTheoryErr,"#sigma_{#tilde{t} #bar{#tilde{t}}} (NNLO+NNLL)", "lf")
            legend.AddEntry(grMean_2l,  "Mean expected limit (2l)",   "l" )
            #if "SYY" in self.model:
            #    f = ROOT.TFile.Open("HEPData-ins1846679-v1-Figure_6b.root", "read")

            #    old = f.Get("Figure 6b").Get("Graph1D_y3")
            #    if not self.noRatio:
            #        legend.AddEntry(old, "SUS-19-004 Limit", "l")
            #        old.Draw("lp")
            #elif "RPV" in self.model:
            #    f = ROOT.TFile.Open("HEPData-ins1846679-v1-Figure_6a.root", "read")

            #    old = f.Get("Figure 6a").Get("Graph1D_y3")

            #    if not self.noRatio:
            #        legend.AddEntry(old, "SUS-19-004 Limit", "l")
            #        old.Draw("lp")
            legend.AddEntry(grMean,  "Mean expected limit (Combo)",   "l" )
            if not asimov: legend.AddEntry(grObs,    "Observed limit", "lp")

        #grMean.Draw("lp")

        if self.noRatio:
            self.canvas.cd()
        else:
            self.pad1.cd()
        self.draw_LumiCMS()
        self.draw_SignalInfo()

        if not self.noRatio:
            self.pad2.cd()
            ROOT.gPad.Update()

            line = ROOT.TLine(250, 1, 1250, 1)
            line.SetLineColor(ROOT.kRed)
            line.SetLineWidth(2)
            line.SetLineStyle(2)
            line.Draw("SAME")

            RatioHist = ROOT.TH1F("Ratio", "Ratio", 20, 225, 1225)
            for i in range(old.GetN()):
                tempYval = old.GetY()[i]/ratio.GetY()[i]
                tempXval = old.GetX()[i]

                temp2sig = (abs(grGreen.GetY()[i] - ratio.GetY()[i]) + abs(ratio.GetY()[i] - grGreen.GetY()[45-i])) / 2.

                # estimating the one sigma error here
                old_rel_err = ((0.68/0.95)*old.GetErrorY(i))/old.GetY()[i]
                current_rel_err = temp2sig/ratio.GetY()[i]

                err_tot = tempYval * math.sqrt(old_rel_err**2 + current_rel_err**2)

                RatioHist.SetBinContent(i+2, tempYval)
                RatioHist.SetBinError(i+2, err_tot)

            RatioHist.Draw("APE SAME")
            RatioHist.GetXaxis().SetRangeUser(250., 1250.)
            RatioHist.GetYaxis().SetRangeUser(0., 4.2)
            RatioHist.SetMinimum(0.0)
            RatioHist.SetMaximum(4.2)
            RatioHist.SetStats(0)
            RatioHist.SetFillStyle(1)
            RatioHist.SetLineColor(ROOT.kBlack)
            RatioHist.SetMarkerStyle(20)
            RatioHist.SetMarkerColor(ROOT.kBlack)

        #grObs.Draw("lp")

        # -----------------------
        # draw signal information
        # -----------------------
        if asimov:
            self.asimov = "_Asimov"
        else:
            self.asimov = ""
        if self.graft == 0:
            self.canvas.SaveAs(self.outputDir + "/sigBrLim" + "_" + self.inputDir + "_" + self.year + "_" + self.model + "_" + self.channel + "_" + self.dataType + self.asimov + ".pdf")
            self.canvas.SaveAs(self.outputDir + "/sigBrLim" + "_" + self.inputDir + "_" + self.year + "_" + self.model + "_" + self.channel + "_" + self.dataType + self.asimov + ".png")
        else:
            self.canvas.SaveAs(self.outputDir + "/sigBrLim" + "_" + "Grafted" + "_" + self.year + "_" + self.model + "_" + self.channel + "_" + self.dataType + self.asimov + ".pdf")
            self.canvas.SaveAs(self.outputDir + "/sigBrLim" + "_" + "Grafted" + "_" + self.year + "_" + self.model + "_" + self.channel + "_" + self.dataType + self.asimov + ".png")

# -------------
# Main function
# -------------
def main():
    parser = argparse.ArgumentParser("usage: %prog [options]\n")
    parser.add_argument("--inputDirs", dest="inputDirs", type=str, required=True, nargs='+',                           help = "path to get the input root files")
    parser.add_argument("--outputDir", dest="outputDir", type=str, required=True,                                      help = "path to write output files"      )
    parser.add_argument("--year",      dest="year",      type=str, default = "Run2UL" ,                                help = "which year to plot"              )
    parser.add_argument("--model",     dest="model",     type=str, default = "RPV" ,                                   help = "which model to plot"             )
    parser.add_argument("--channel",   dest="channel",   type=str, default = "1l" ,                                    help = "which channel to plot"           )
    parser.add_argument("--dataType",  dest="dataType",  type=str, default = "pseudoData",                             help = "which dataType to plot"          )
    parser.add_argument("--limitType", dest="limitType", type=str, default = "AsymptoticLimits",                       help = "which limitType to plot"         )
    parser.add_argument("--approved",  dest="approved",            default = False,              action="store_true",  help = "is plot approved"                )
    parser.add_argument("--asimov",    dest="asimov",              default = False,              action="store_true",  help = "use the Asimov data set"         )
    parser.add_argument("--wip",       dest="wip",                 default = False,              action="store_true",  help = "is plot a work in progress"      )
    parser.add_argument("--graft",     dest="graft",     type=int, default = 0,                                        help = "use input dir 1 up to (inclusive) this mass, then use input dir , then use input dir 2")
    parser.add_argument("--noRatio",     dest="noRatio",           default = False,              action='store_true',  help = "Do not plot ratio of SUS-19-004 to current expected")


    args = parser.parse_args()

    combo = args.channel == "combo"

    limitPlots_Objects = LimitPlots(args.inputDirs, args.outputDir, args.year, args.model, args.channel, args.dataType, args.limitType, args.graft, args.noRatio) 
    limitPlots_Objects.make_LimitPlots(args.approved, args.wip, args.limitType, args.asimov, combo)



if __name__ == '__main__':
    main()
