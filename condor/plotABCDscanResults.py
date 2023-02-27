import os
import glob
import argparse

import ROOT
ROOT.gROOT.SetBatch(True)

# Put matplotlib in batch mode
# to avoid asinine runtime errors
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
plt.rc('font', family='Nimbus Sans')

import numpy as np

# Class to hold---for a given model, year, channel
# interesting Combine results for multiple choices
# of ABCD edges. In this case, interesting quantities
# include significance and observed limit
class FitResults():

    def __init__(self, year, model, channel):

        self.data    = {}
        self.year    = year
        self.model   = model
        self.channel = channel

        self.paramValues = {
            "discs"     : [],
        }

    # All combine results are stored uniquely inside a dictionary
    def makeKey(self, variable = None, **kwargs):

        theKey = ""

        if "disc" in kwargs:
            theKey += kwargs["disc"]
            if kwargs["disc"] not in self.paramValues["discs"]: self.paramValues["discs"].append(kwargs["disc"])

        if variable != None: theKey += variable
        
        return theKey

    # Upon specifying mass point, year, model, channel, and disc values for a particular fit
    # open up the corresponding higgsCombine SignifExp (Asimov) ROOT file and read the significance value
    # from the "limit" TTree
    def scrapePvalue(self, path, mass, disc):
        
        tagName    = "%s%s%spseudoData_%s_%s"%(self.year, self.model, mass, self.channel, disc)

        # -------------------------------------------------------------
        # Get sigma and p-value from fit output significance ROOT files
        # -------------------------------------------------------------
        sigma        = -1; pvalue = 10; file_sig = -1
        filename_sig = "%s/higgsCombine%s_SignifExp_Asimov.Significance.mH%s.MODEL%s.root" %(path, tagName, mass, self.model)

        try:
            file_sig = ROOT.TFile.Open(filename_sig, "READ")

            tree_sig = file_sig.Get("limit")
            tree_sig.GetEntry(0)
            sigma = tree_sig.limit
            pvalue = 0.5 - ROOT.TMath.Erf(float(sigma)/ROOT.TMath.Sqrt(2.0))/2.0

        except Exception as e:
            print("Could not retrieve significance for fit \"%s\":"%(tagName))
            print(e)
            return
        
        self.data[self.makeKey(variable = "sign",   mass = mass, disc = disc)] = float(sigma)
        self.data[self.makeKey(variable = "pvalue", mass = mass, disc = disc)] = float(pvalue)

    # Upon specifying mass point, year, model, channel, and disc values for a particular fit
    # open up the corresponding higgsCombine AsymptoticLimits ROOT file and read the limits
    # from the "limit" TTree
    def scrapeLimit(self, path, mass, disc):

        # path for input root files   
        label    = self.year + self.model + mass + "pseudoData_" + self.channel + "_" + disc + "_AsymLimit" 
        fitInput = path + "/higgsCombine%s.AsymptoticLimits.mH%s.MODEL%s.root"%(label, mass, self.model)
        
        try:
            # load input root files 
            rootFile = ROOT.TFile.Open(fitInput, "READ")

            # read tree and leaves from each root file
            tree = rootFile.Get("limit")
        except Exception as e:
            print("Could not retrieve limits for fit \"%s\":"%(label))
            print(e)
            return

        iEntry = 0
        try:
            tree.GetEntry(iEntry)
        except Exception as e:
            print("limit not present in root file")
            return
        
        # Limits and band values are just all in a row in the TTree...
        limits_95expected_below = tree.limit
        iEntry += 1
        tree.GetEntry(iEntry)
        
        limits_68expected_below = tree.limit
        iEntry += 1
        tree.GetEntry(iEntry)

        limits_mean = tree.limit

        iEntry += 1
        tree.GetEntry(iEntry)
        
        limits_68expected_above = tree.limit
        iEntry += 1
        tree.GetEntry(iEntry)
        
        limits_95expected_above = tree.limit
        iEntry += 1
        tree.GetEntry(iEntry)
        
        limits_obs              = tree.limit
        limits_obsErr           = tree.limitErr

        rootFile.Close()

        self.data[self.makeKey(variable = "obsLimit", mass = mass, disc = disc)] = limits_obs
        self.data[self.makeKey(variable = "expLimit", mass = mass, disc = disc)] = limits_mean

    # Retrieve a certain variable of interested e.g. significance for all possible paramNames
    def getByParam(self, paramName, var, **kwargs):

        params = []; variables = []
        for p in self.paramValues[paramName]:
            theKey = ""
            if paramName == "names":    theKey = self.makeKey(variable = var, name    = p, **kwargs)
            if paramName == "models":   theKey = self.makeKey(variable = var, model   = p, **kwargs)
            if paramName == "masses":   theKey = self.makeKey(variable = var, mass    = p, **kwargs)
            if paramName == "channels": theKey = self.makeKey(variable = var, channel = p, **kwargs)
            if paramName == "discs":    theKey = self.makeKey(variable = var, disc    = p, **kwargs)
            else: return [], []

            params.append(p)
            variables.append(self.data[theKey])

        return params, variables

class Plotter():

    def __init__(self, outPath, cmsLabel, year, model, channel):
    
        self.outputDir = outPath
        self.cmsLabel  = cmsLabel
        self.year      = year
        self.channel   = channel
        self.model     = model

    def addCMSlabel(self, ax):

        ax.text(0.0,  1.003, 'CMS',                     transform=ax.transAxes, fontsize=16, fontweight='bold',   va='bottom', ha='left')
        ax.text(0.15, 1.010, '%s'%(self.cmsLabel),      transform=ax.transAxes, fontsize=11, fontstyle='italic',  va='bottom', ha='left')
        ax.text(1.0,  1.010, '%s (13 TeV)'%(self.year), transform=ax.transAxes, fontsize=11, fontweight='normal', va='bottom', ha='right')
    
        return ax

    def plot_Var_vsDisc1Disc2(self, var, edges, bestVal, bestLoc, vmin, vmax, mass, doLog = False, variable = ""):

        fig = plt.figure(figsize=(6, 5)) 
    
        if doLog:
            plt.scatter(edges[:,0], edges[:,1], c=var, marker="o", cmap="viridis", norm=mpl.colors.LogNorm(), vmin=vmin, vmax=vmax)
        else:
            plt.scatter(edges[:,0], edges[:,1], c=var, marker="o", cmap="viridis", vmin=vmin, vmax=vmax)
            
        plt.colorbar()
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        ax = plt.gca()
        ax.set_xlabel("Disc. 1 Bin Edge", fontsize=14)
        ax.set_ylabel("Disc. 2 Bin Edge", fontsize=14)

        ax = self.addCMSlabel(ax)

        # put model, channel, njet labels
        md = ""
        if self.model == "SYY":
            md = "Stealth SYY"
        else:
            md = self.model

        ch = ""
        if self.channel == "0l":
            ch = "Fully-Hadronic"
        elif self.channel == "1l":
            ch = "Semi-Leptonic"
        elif self.channel == "2l":
            ch = "Fully-Leptonic"

        textLabel = "%s"%(variable) + " | %s"%(md) + r" ($m_{\tilde{t}} = %s$ GeV)"%(mass) + " | %s"%(ch)
        ax.text(0.02, 0.97, textLabel, transform=ax.transAxes, color="cadetblue",  fontsize=10,  fontweight='normal', va='center', ha='left')

        ax.text(bestLoc[0], bestLoc[1]+0.03, "(%.2f, %.2f)"%(bestLoc[0], bestLoc[1]), transform=ax.transAxes, color="black", fontsize=8, fontweight='normal', va='center', ha='center')
        ax.text(bestLoc[0], bestLoc[1]-0.03, "%.2f"%(bestVal),                        transform=ax.transAxes, color="black", fontsize=8, fontweight='normal', va='center', ha='center')

        fig.tight_layout()
        fig.subplots_adjust(top=0.95, right=0.99)

        fig.savefig(self.outputDir+"/%s_%s_vs_Disc1Disc2_%s_%s.pdf"%(self.year, variable, self.model, self.channel), dpi=fig.dpi)

        plt.close(fig)

def main():
    parser = argparse.ArgumentParser("usage: %prog [options]\n")
    parser.add_argument('--basedir',  dest='basedir',  type=str, required = True,                       help = "Path to output files"    )
    parser.add_argument('--outdir',   dest='outdir',   type=str, required = True,                       help = "Path to put output files")
    parser.add_argument('--approved', dest='approved',           default  = False, action='store_true', help = 'Is plot approved'        )
    parser.add_argument('--model',    dest='model',    type=str, default  = "RPV",                      help = 'Which models to plot for')
    parser.add_argument('--mass',     dest='mass',     type=str, default  = "550",                      help = 'Which mass to plot for'  )
    parser.add_argument('--year',     dest='year',     type=str, default  = "Run2UL",                   help = 'Which years to plot'     )
    parser.add_argument('--channel',  dest='channel',  type=str, default  = "0l",                       help = 'Which channels to plot'  )
    args = parser.parse_args()

    path    = args.basedir
    outPath = args.outdir
    model   = args.model
    mass    = args.mass
    year    = args.year
    channel = args.channel

    if not os.path.exists(outPath):
        os.makedirs(outPath)

    # Get a listing of all job output
    # Each folder would correspond to different choice of bin edges
    fitResults = glob.glob("%s/*"%(path))

    # Loop over all jobs and get the info needed
    theScraper = FitResults(year, model, channel)
    for result in fitResults:

        # Split up each individual job folder to get edge vals
        chunks = result.split("/")[-1].split("_")

        # Easier to ask for forgiveness
        # than it is to ask for permission
        # Does the folder end in _XX_YY ?
        # i.e. a legit job folder
        try:
            trial = float(chunks[-1])
            trial = float(chunks[-2])
        except:
            print("Skipping non-Combine-result \"%s\""%(result))
            continue

        disc = chunks[-2] + "_" + chunks[-1]

        theScraper.scrapePvalue(result, mass, disc)
        theScraper.scrapeLimit(result,  mass, disc)

    cmsLabel = "Work in Progress"
    if args.approved:
        cmsLabel = ""

    discs, signs   = theScraper.getByParam(paramName = "discs", var = "sign",     mass = mass)
    discs, obsLims = theScraper.getByParam(paramName = "discs", var = "obsLimit", mass = mass)

    # Get the best significance (max) and best limit (min) points for marking on plot
    maxSign = max(signs)
    minLim  = min(obsLims)

    iSign = signs.index(maxSign)
    iLim  = obsLims.index(minLim)

    signEdge = discs[iSign]
    limEdge  = discs[iLim]

    signEdge = (float("0.%s"%(signEdge.split("_")[0])), float("0.%s"%(signEdge.split("_")[1])))
    limEdge = (float("0.%s"%(limEdge.split("_")[0])), float("0.%s"%(limEdge.split("_")[1])))

    edges = np.array([(float("0.%s"%(disc.split("_")[0])), float("0.%s"%(disc.split("_")[-1]))) for disc in discs])

    thePlotter = Plotter(outPath, cmsLabel, year, model, channel)
    thePlotter.plot_Var_vsDisc1Disc2(signs,   edges, bestVal = maxSign, bestLoc = signEdge, vmin = 0.0,   vmax = 5.0,  mass = mass,               variable = "Significance")
    thePlotter.plot_Var_vsDisc1Disc2(obsLims, edges, bestVal = minLim,  bestLoc = limEdge,  vmin = 10e-2, vmax = 10.0, mass = mass, doLog = True, variable = "Limit")

if __name__ == '__main__':
    main()
