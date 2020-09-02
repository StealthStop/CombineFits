#!/bin/python
import sys
import copy
import ROOT
import argparse 

ROOT.gStyle.SetOptTitle( 0 )
ROOT.gStyle.SetOptStat( 0 )
ROOT.gROOT.SetBatch( ROOT.kTRUE )

parser = argparse.ArgumentParser()
parser.add_argument( '--plotbkg', action = 'store_true', dest = 'bkgdfit', default = False, help = 'Plot the background component to the fit' )
parser.add_argument( '--twosigfit', action = 'store_true', dest = 'twosigfit', default = False, help = 'Plot SYY 850 signal in the fit' )
parser.add_argument( '--bkgonlyfit', action = 'store_true', dest = 'bkgonlyfit', default = False, help = 'Plot background only fit results' )
parser.add_argument( '--compshapes', action = 'store_true', dest = 'compshapes', default = False, help = 'Plot individual shapes of bkgds' )
parser.add_argument( '--mass1', dest = 'mass1', default = "450", help = 'Set mass for first reference signal' )
parser.add_argument( '--mass2', dest = 'mass2', default = "600", help = 'Set mass for second reference signal' )
parser.add_argument( '--model1', dest = 'model1', default = "RPV", help = 'Set model for first reference signal' )
parser.add_argument( '--model2', dest = 'model2', default = "SYY", help = 'Set model for second reference signal' )

parser.add_argument( '--path', dest = 'path', default=".", help = 'Input path' )

args = parser.parse_args()

#Define some global arrays that will be used later in the plotting script
mvaBinList                  = [ "D1", "D2", "D3", "D4" ]
textArray                   = [ "NN bin D1", "NN bin D2", "NN bin D3", "NN bin D4" ]
borderSize                  = 0.20
yearList                    = [ ("Combo16","Y16_")]
#yearList                    = [ ("2016",""), ("2017",""), ("2018pre",""), ("2018post",""), ("Combo16","Y16_"), ("Combo17","Y17_"), ("Combo18pre","Y18pre_"), ("Combo18post","Y18post_") ]
lumi                        = 0.0

#Variables for pads that are derived from the border size
pad1and4Size                = 1.0+borderSize
pad2and3Size                = 1.0
totalPadSize                = 2*pad1and4Size + 2*pad2and3Size

def main() :

    for year, prefix in yearList :
        #Name of root file that takes Owen's output code and makes the histogram
        fitType = "b" if args.bkgonlyfit else "s"
        inputRootFileName           = args.path+"/KELVIN_RPV"+args.mass1+year+fitType+".root"
        inputRootFile               = ROOT.TFile.Open( inputRootFileName )
    
        if year == "2016" or year == "Combo16" :
            lumi                    = "35.9"
        elif year == "2017" or year == "Combo17" :
            lumi                    = "41.5"
        elif year == "2018pre" or year == "Combo18pre" :
            lumi                    = "21.1"
        elif year == "2018post" or year == "Combo18post" :
            lumi                    = "38.7"
    
        c1, topPadArray, ratioPadArray = makeCanvasAndPads(year, prefix)
        c1, topPadArray, ratioPadArray = formatCanvasAndPads( c1, topPadArray, ratioPadArray )
    
        #Arrays needed for easy plotting (save a copy of all legends and fit histograms derived
        #    from the graphs)
        legendArray1                = []
        legendArray2                = []
        fitHistArray                = []
        lineArray                   = []
       
        dummyPullHist, dummyPullHist_D4 = makeDummyPullHistograms()
    
        for itBin in xrange( 0, len(mvaBinList) ):    
    
            #Define the name of the bin, which is used in the naming convention of the root file
            mvaBin                      = prefix+mvaBinList[ itBin ]
    
            sigRefHist1                  = inputRootFile.Get( "sigRefHist1_"+mvaBin )
            sigRefHist2                  = inputRootFile.Get( "sigRefHist2_"+mvaBin )
            sigHist                     = inputRootFile.Get( "sigHist_"+mvaBin )
            ttHist                     = inputRootFile.Get( "ttHist_"+mvaBin )
            qcdHist                     = inputRootFile.Get( "qcdHist_"+mvaBin )
            ttxHist                     = inputRootFile.Get( "ttxHist_"+mvaBin )
            otherHist                   = inputRootFile.Get( "otherHist_"+mvaBin )
            bkgdHist                    = inputRootFile.Get( "bkgdHist_"+mvaBin )
            fitGraph                    = inputRootFile.Get( "Fit_"+mvaBin )
            dataGraph                   = inputRootFile.Get( "Nobs_"+mvaBin )
            fitHist                     = ROOT.TH1D( "fitHist_"+mvaBinList[itBin], "fitHist_"+mvaBinList[itBin], 6, 0, 6 )
    
            #Make the fit graph (TGraphAsymmErrors object) into a histogram object so that axes can be changed accordingly (can also use dummy histogram here).
            #Bands will be drawn using the TGraphAsymmErrors, so the bin error here is just for some consistency ( but is not really used ).
            for itHistBin in xrange( 0, fitGraph.GetN() ) :
                fitHist.SetBinContent( itHistBin + 1, fitGraph.GetY()[itHistBin] )
                fitHist.SetBinError( itHistBin + 1, fitGraph.GetEYhigh()[itHistBin] )
            
            #Fit colors determined by previous iteration of the code.
            fitHist.SetLineColor( 4 )
            fitHist.SetLineWidth( 2 )
            
            #Special care has to be done to the first bit since it defines the y-axis
            #TO DO: Parameters have not been fully made a function of the border size yet (or the aspect ratio)
            if itBin == 0 :
                fitHist.SetYTitle( "Events" )
                fitHist.SetTitleSize( 0.075, "y" )
                fitHist.SetTitleOffset( 1.3, "y" )
                fitHist.SetLabelSize( 0.065, "y" )
           
            #Save a verstion of the fitHist for plotting later
            fitHistArray.append( copy.deepcopy( fitHist ) )
            

            if( args.compshapes ): 
                #Range has been set by previous analysis plots to be between 0.05 and 1e5
                fitHistArray[itBin].GetYaxis().SetRangeUser( 0.05, 1e7 )
            else:
                fitHistArray[itBin].GetYaxis().SetRangeUser( 0.05, 1e6 )
   
            #This is the graphs for where the pulls are calculated
            pullsGraph                  = inputRootFile.Get( "pulls_"+mvaBin )
            pullsErrGraph               = inputRootFile.Get( "pullsErr_"+mvaBin )
            
            pullsGraph.SetLineWidth( 1 )
            pullsErrGraph.SetLineWidth( 1 )
    
            #Begin plotting for the top pad for each NN bin.
            topPadArray[itBin].cd()
    
            fitHistArray[itBin].Draw( "HIST" ) #Hist plot necessary to get the right borders
            fitGraph.Draw( "2 SAME" ) #Need to be drawn next to get any asymmetric errors (though they seem symmetric in spot checks)
            ROOT.gPad.RedrawAxis()
    
            #Draw the TText for the naming of the NN bin. Size and location is dependent on border size
            ttext                       = ROOT.TText()
    
            if itBin == 0:
                ttext.SetTextSize( 0.06*pad2and3Size/pad1and4Size )
                ttext.DrawTextNDC( ROOT.gPad.GetLeftMargin() + 0.03, 1 - (ROOT.gPad.GetTopMargin() + 0.097 ), textArray[itBin] )
            
            elif itBin == len(mvaBinList) - 1 :
                ttext.SetTextSize( 0.06*pad2and3Size/pad1and4Size )
                ttext.DrawTextNDC( ROOT.gPad.GetLeftMargin() + 0.03, 1 - (ROOT.gPad.GetTopMargin() + 0.097 ), textArray[itBin] )
            
            else:
                ttext.SetTextSize( 0.06 )
                ttext.DrawTextNDC( ROOT.gPad.GetLeftMargin() + 0.03, 1 - (ROOT.gPad.GetTopMargin() + 0.097 ), textArray[itBin] )
    
            #Add CMS Preliminary (work in progress)
            mark                        = ROOT.TLatex()
            mark.SetNDC( ROOT.kTRUE )
            mark.SetTextAlign( 11 )
            if itBin == 0 :
                mark.SetTextSize( 0.055*pad1and4Size/pad2and3Size )
                mark.SetTextFont( 60 )
                mark.DrawLatex( ROOT.gPad.GetLeftMargin() + 0.015, 0.91, "CMS")
                mark.SetTextSize( 0.044*pad1and4Size/pad2and3Size )
                mark.SetTextFont( 52 )
                mark.DrawLatex( ROOT.gPad.GetLeftMargin() + 0.165, 0.91, "Preliminary")
            if itBin == len(mvaBinList) - 1:
                mark.SetTextFont( 42 )
                mark.SetTextAlign( 31 )
                mark.DrawLatex( 1 - ROOT.gPad.GetRightMargin(), 0.91, lumi+" fb^{-1} (13 TeV)" )
    
            #Draw and save the legends in an array so that the previous legend isn't wiped when switching to a new NN bin.
            #    Location of legend also depends on NN bin
            l1                          = ROOT.TLegend()
            l2                          = ROOT.TLegend()
            l1_yStart                   = 0.70
            l2_yStart                   = 0.55
            if( args.bkgdfit ):
                l1_yStart               = l1_yStart - 0.05
            if( args.twosigfit ) :
                l1_yStart               = l1_yStart - 0.05
    
            if itBin == 0 :
                l1                          = ROOT.TLegend( 0.45+(borderSize)/2, l1_yStart, 0.87+(borderSize)/2, 0.85 )
                l2                          = ROOT.TLegend( 0.45+(borderSize)/2, l2_yStart, 0.87+(borderSize)/2, l1_yStart-0.01 )

                l1.SetTextSize(0.05*pad2and3Size/pad1and4Size)
                l2.SetTextSize(0.05*pad2and3Size/pad1and4Size)
            elif itBin == len(mvaBinList) - 1:
                l1                          = ROOT.TLegend( 0.45-(borderSize)/2, l1_yStart, 0.87-(borderSize)/2, 0.85 )
                l2                          = ROOT.TLegend( 0.45-(borderSize)/2, l2_yStart, 0.87-(borderSize)/2, l1_yStart-0.01 )

                l1.SetTextSize(0.05*pad2and3Size/pad1and4Size)
                l2.SetTextSize(0.05*pad2and3Size/pad1and4Size)

            else :
                l1                          = ROOT.TLegend( 0.45, l1_yStart, 0.87, 0.85 )
                l2                          = ROOT.TLegend( 0.45, l2_yStart, 0.87, l1_yStart-0.01 )

                l1.SetTextSize(0.05)
                l2.SetTextSize(0.05)
           
            l1.AddEntry( fitHist, "Fit" )
            l1.AddEntry( dataGraph, "N observed", "pl" )
            if( args.bkgonlyfit ) :
                l1.AddEntry( sigRefHist1, args.model1+" m_{#tilde t} = "+args.mass1+" GeV" )
            else :
                l1.AddEntry( sigHist, "Fit Signal" )
            if( args.twosigfit ) :
                l1.AddEntry( sigRefHist2, args.model2+" m_{#tilde t} = "+args.mass2+" GeV" )
            if( args.bkgdfit ) :
                l1.AddEntry( bkgdHist, "Fit Background" )
            if( args.compshapes ):
                l2.SetNColumns(2)
                l2.AddEntry(ttHist, "TT")
                l2.AddEntry(qcdHist, "QCD")
                l2.AddEntry(ttxHist, "TTX")
                l2.AddEntry(otherHist, "OTHER")

            l1.SetBorderSize(0)
            l2.SetBorderSize(0)
            legendArray1.append( copy.deepcopy( l1 ) ) #Need to save legend as to not be erased
            legendArray1[itBin].Draw()
    
            if( args.compshapes ):
                legendArray2.append( copy.deepcopy( l2 ) ) #Need to save legend as to not be erased
                legendArray2[itBin].Draw()

            if( args.bkgdfit ) :
                fitHistArray[itBin].Draw( "HIST SAME" )
                bkgdHist.Draw( "HIST SAME" )
            if( args.bkgonlyfit ) :
                sigRefHist1.Draw( "HIST SAME" )
            else :
                sigHist.Draw( "HIST SAME" )
            if( args.twosigfit ) :
                sigRefHist2.Draw( "HIST SAME" )
            if( args.compshapes ):
                ttHist.Draw("HIST SAME")
                qcdHist.Draw("HIST SAME")
                ttxHist.Draw("HIST SAME")
                otherHist.Draw("HIST SAME")
            dataGraph.Draw( "P SAME" )
           
            #Draw pulls here
            ratioPadArray[itBin].cd()
              
            myline = ROOT.TLine( 0.0, 0.0, 6.0, 0.0 ) 
            myline.SetLineWidth( 1 )
            lineArray.append( copy.deepcopy( myline ) )
            
            if itBin == len(mvaBinList) - 1:
                dummyPullHist_D4.Draw()
            else:
                dummyPullHist.Draw()
            
            pullsErrGraph.Draw("2 SAME")
            ROOT.gPad.RedrawAxis()
            lineArray[-1].Draw("SAME")
            dummyPullHist.Draw("AL SAME")
            pullsGraph.Draw("P SAME")
            
            c1.Update()
    
        c1.SaveAs("RPV"+args.mass1+year+fitType+"_fitPlots.pdf")

def makeDummyPullHistograms():
    
    dummyPullHist                   = ROOT.TH1D( "dummyPullHist", "dummyPullHist", 6, 0, 6 )
    dummyPullHist.GetYaxis().SetRangeUser( -3.5, 3.5 )
    dummyPullHist.SetMinimum( -3.5 )
    dummyPullHist.SetMaximum( 3.5 )
    dummyPullHist.SetYTitle( "(val - fit) / #sigma" )
    dummyPullHist.SetTitleSize( 0.175, "y" )
    dummyPullHist.SetTitleOffset( 0.5, "y" )
    dummyPullHist.SetLabelOffset( 0.025, "x" )
    dummyPullHist.SetLabelOffset( 0.025, "y" )
    dummyPullHist.SetLabelSize( 0.24, "x" )
    dummyPullHist.SetLabelSize( 0.145, "y" )
    dummyPullHist.SetNdivisions( 404, "y" )
    dummyPullHist.SetStats( 0 )
    
    dummyPullHist_D4                   = ROOT.TH1D( "dummyPullHist_D4", "dummyPullHist_D4", 6, 0, 6 )
    dummyPullHist_D4.GetYaxis().SetRangeUser( -3.5, 3.5 )
    dummyPullHist.SetMinimum( -3.5 )
    dummyPullHist.SetMaximum( 3.5 )
    dummyPullHist_D4.SetXTitle( "Number of jets" )
    dummyPullHist_D4.SetTitleSize( 0.175, "x" )
    dummyPullHist_D4.SetLabelOffset( 0.025, "x" )
    dummyPullHist_D4.SetLabelSize( 0.24, "x" )
    dummyPullHist_D4.SetNdivisions( 404, "y" )
    dummyPullHist_D4.SetStats( 0 )
    
    for itDummyBin in xrange( 1, dummyPullHist.GetNbinsX()+1 ):
        if itDummyBin == 6 :
            dummyPullHist.GetXaxis().SetBinLabel( itDummyBin, "#geq"+"12" )
            dummyPullHist_D4.GetXaxis().SetBinLabel( itDummyBin, "#geq"+"12" )
        else :
            dummyPullHist.GetXaxis().SetBinLabel( itDummyBin, str( itDummyBin + 6 ) )
            dummyPullHist_D4.GetXaxis().SetBinLabel( itDummyBin, str( itDummyBin + 6 ) )

    return dummyPullHist, dummyPullHist_D4

def formatCanvasAndPads( c1, topPadArray, ratioPadArray ) :

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

def makeCanvasAndPads(year, prefix) :
    tag = year + "_" + prefix

    c1                          = ROOT.TCanvas( "c1_%s"%(tag), "c1_%s"%(tag), 0, 0, 1200, 480 )
    
    p1_D1                       = ROOT.TPad( "p1_D1_%s"%(tag), "p1_D1_%s"%(tag), 0, 0.30, pad1and4Size/totalPadSize, 1.0 )
    p2_D1                       = ROOT.TPad( "p2_D1_%s"%(tag), "p2_D1_%s"%(tag), 0, 0, pad1and4Size/totalPadSize, 0.30 )
    
    p1_D2                       = ROOT.TPad( "p1_D2_%s"%(tag), "p1_D2_%s"%(tag), pad1and4Size/totalPadSize, 0.30, (pad1and4Size + pad2and3Size)/totalPadSize, 1.0 )
    p2_D2                       = ROOT.TPad( "p2_D2_%s"%(tag), "p2_D2_%s"%(tag), pad1and4Size/totalPadSize, 0, (pad1and4Size + pad2and3Size)/totalPadSize, 0.30 )
    
    p1_D3                       = ROOT.TPad( "p1_D3_%s"%(tag), "p1_D3_%s"%(tag), (pad1and4Size + pad2and3Size)/totalPadSize, 0.30, (pad1and4Size + 2*pad2and3Size)/totalPadSize, 1.0 )
    p2_D3                       = ROOT.TPad( "p2_D3_%s"%(tag), "p2_D3_%s"%(tag), (pad1and4Size + pad2and3Size)/totalPadSize, 0, (pad1and4Size + 2*pad2and3Size)/totalPadSize, 0.30 )
    
    p1_D4                       = ROOT.TPad( "p1_D4_%s"%(tag), "p1_D4_%s"%(tag), (pad1and4Size + 2*pad2and3Size)/totalPadSize, 0.30, 1.0, 1.0 )
    p2_D4                       = ROOT.TPad( "p2_D4_%s"%(tag), "p2_D4_%s"%(tag), (pad1and4Size + 2*pad2and3Size)/totalPadSize, 0, 1.0, 0.30 )

    return c1, [p1_D1, p1_D2, p1_D3, p1_D4], [p2_D1, p2_D2, p2_D3, p2_D4]


if __name__ == "__main__" :
    main()
