import argparse
import sys 
import ROOT
from array import array

parser = argparse.ArgumentParser()
parser.add_argument("--model", help="One of our three models, RPV, SYY, or SHH", default="RPV")
parser.add_argument("--masses", nargs='+', help="Masses to make plots for")
parser.add_argument("--year", nargs='+', help="2016, 2017, or Combo", default=["2016"])
parser.add_argument("--data", type=int, default=0, help="Data (0), pseudo-data (1), or pseudo-data with signal (2)")
parser.add_argument("--poi", type=str, default="r", help="Default is r: can pass in a parameter that the profile was performed for")
parser.add_argument("--inFile", nargs='+', type=str, default=[""])
parser.add_argument("--basedir", help="Directory that contains the output Fit_data_year directories", default="OutputForFreezing")
parser.add_argument("--setXRange", nargs='+', default=["-0.2", "1.0"], help="Set Range of x-axis")
parser.add_argument("--setYRange", nargs='+', default=["0.0", "20.0"], help="Set Range of y-axis")
args=parser.parse_args()
sys.argv.append( '-b' ) #setting batch mode for ROOT
model = args.model
data = "Data"
if args.data == 1:
    data = "pseudoData"
elif args.data == 2:
    data = "pseudoDataS"
poi = args.poi
inFile = args.inFile
basedir = args.basedir
xMin = float(args.setXRange[0])
xMax = float(args.setXRange[1])
yMin = float(args.setYRange[0])
yMax = float(args.setYRange[1]) 
color = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen+2, ROOT.kOrange, ROOT.kMagenta]

for mass in args.masses:
    model_mass = "%s_%s" % (model, mass)

    canvas = ROOT.TCanvas("c","c", 600, 600)
    canvas.cd()
    canvas.SetBottomMargin(0.12)
    ROOT.gPad.SetTicks(1,1)
    h = ROOT.TH1F("dummy","dummy",10000, -100.0, 100.0)
    h.Draw()
    h.GetXaxis().SetTitleSize(0.05)
    h.GetXaxis().SetLabelSize(0.04)
    h.GetXaxis().SetTitle("parameter "+poi)
    h.GetYaxis().SetTitle("-2#Delta lnL")
    h.GetYaxis().SetTitleSize(0.05)
    h.GetYaxis().SetLabelSize(0.04)
    h.GetXaxis().SetRangeUser(xMin, xMax)
    h.GetYaxis().SetRangeUser(yMin, yMax)
    h.SetStats(0)
    h.SetTitle("Profile scan for %s in %s" % (model_mass, data))

    legend = ROOT.TLegend(0.6, 0.75, 0.9, 0.9)

    y = ""
    histos = []
    i = 0
    for year in args.year:    
        inputfilename = "%s/Fit_%s_%s/output-files/%s_%s/higgsCombineSCAN_r_wSig.MultiDimFit.mH%s.MODEL%s.root" % (basedir, data, year, model_mass, year, mass, model)
        if inFile[0] != "": inputfilename = inFile[i]         
        inputfile = ROOT.TFile.Open(inputfilename)
    
        poiArray = array( 'd' )
        tDLArray = array( 'd' )
        limit = inputfile.Get("limit")
        for entry in limit:
            poiArray.append( entry.GetLeaf(poi).GetValue() )
            tDLArray.append( 2*(entry.deltaNLL) )
    
        graph = ROOT.TGraph(len(poiArray), poiArray, tDLArray)
        graph.Sort()
        graph.SetLineColor( color[i] )
        graph.SetLineWidth( 2 )
        graph.SetMarkerColor( ROOT.kBlack )
        graph.SetMarkerStyle( ROOT.kFullSquare )
        graph.SetMarkerSize( 0.5 )
        graph.Draw("same PL")
        legend.AddEntry(graph, year, "l")

        y += year
        histos.append(graph)
        i += 1
    
    l1 = ROOT.TLine(xMin,1,xMax,1)
    l1.Draw()
    l2 = ROOT.TLine(0,yMin,0,yMax)
    l2.Draw()

    legend.Draw()
        
    outputdir = "%s/Fit_%s_%s/output-files/%s_%s" % (basedir, data, y, model_mass, year)
    if inFile[0] != "": outputdir = "."         
    canvas.SaveAs(outputdir + "/profilescan_%s_%s_%s_%s.pdf" % (model_mass, y, data, poi))
