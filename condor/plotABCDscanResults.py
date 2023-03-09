import os
import glob
import argparse

import ROOT
ROOT.gROOT.SetBatch(True)

# Put matplotlib in batch mode
# to avoid asinine runtime errors
import matplotlib as mpl
mpl.use('Agg')

# Looks very similar to Arial/Helvetica
import matplotlib.pyplot as plt
plt.rc('font', family='Nimbus Sans')

import numpy as np

# Class to hold---for a given model, year, channel
# interesting Combine results for multiple choices
# of ABCD edges. In this case, interesting quantities
# include significance and observed limit
class FitResults():

    def __init__(self, xsecs, channel):

        # A list of tuples, which can be converted
        # to np.ndarray by calling numpyFriendly()
        self.data    = []

        self.channel = channel

        self.stopPair_xsec = xsecs

        # Holds effective column headers and types for self.data
        # to make referencing and getting data easy
        self.paramNames = None
        self.paramTypes = None

        # For converting operation in selection string to literal function
        self.ops = [(">=", np.greater_equal), (">", np.greater), ("<=", np.less_equal), ("<", np.less)]

    # Get pointer to "limit" TTree in Combine output ROOT file
    def getTree(self, filename):

        tfile = None; ttree = None 
        try:
            tfile = ROOT.TFile.Open(filename, "READ")
        except:
            print("Could not open TFile \"%s\""%(filename))
            return

        ttree = tfile.Get("limit")
        if ttree == None:
            print("No TTree \"limit\" found in file \"%s\""%(filename))

        return tfile, ttree

    # Upon specifying mass point, year, model, channel, and disc values for a particular fit
    # open up the corresponding higgsCombine SignifExp (Asimov) ROOT file and read the significance value
    # Also open the corresponding higgsCombine AsymptoticLimits ROOT file and read the limits
    def scrapeValues(self, path, year, model, mass, disc):
        
        # Go for the pvalues first
        tagName  = "%s%s%spseudoDataS_%s_%s"%(year, model, mass, self.channel, disc)
        filename = "%s/higgsCombine%s_SignifExp_Asimov.Significance.mH%s.MODEL%s.root"%(path, tagName, mass, model)

        tfile, ttree = self.getTree(filename)
        pvalue = -999.0; sigma = -999.0
        if tfile != None and ttree != None:
        
            ttree.GetEntry(0)
            sigma  = ttree.limit
            pvalue = 0.5 - ROOT.TMath.Erf(float(sigma)/ROOT.TMath.Sqrt(2.0))/2.0

            tfile.Close()

        # Now go for the limits
        tagName  = "%s%s%spseudoData_%s_%s_AsymLimit"%(year, model, mass, self.channel, disc)
        filename = "%s/higgsCombine%s.AsymptoticLimits.mH%s.MODEL%s.root"%(path, tagName, mass, model)
        
        tfile, ttree = self.getTree(filename)
        limits_mean = -999.0; limits_obs = -999.0
        if tfile != None and ttree != None:

            # Limits and band values are just all in a row in the TTree...
            ttree.GetEntry(2)
            limits_mean = ttree.limit

            ttree.GetEntry(5)
            limits_obs    = ttree.limit
            limits_obsErr = ttree.limitErr

            tfile.Close()

        if limits_mean != None:
            limits_mean *= self.stopPair_xsec[mass]
        if limits_obs != None:
            limits_obs *= self.stopPair_xsec[mass]

        self.save(sign = sigma, pvalue = pvalue, obsLimit = limits_obs, year = year, model = model, mass = mass, disc1 = float("0.%s"%(disc.split("_")[0])), disc2 = float("0.%s"%(disc.split("_")[1])))

    def save(self, **kwargs):

        sortedKeys = sorted(kwargs.keys())

        self.data.append([kwargs[kw] for kw in sortedKeys])

        if self.paramNames == None:
            self.paramNames = sortedKeys 
    
        if self.paramTypes == None:
            self.paramTypes = [type(kwargs[kw]) for kw in sortedKeys]

    def get(self, var, afilter = None):

        iVar = self.paramNames.index(var)
        if "array" in afilter.__class__.__name__:
            return self.data[:, iVar][afilter].astype(self.paramTypes[iVar])
        else:
            return self.data[:, iVar].astype(self.paramTypes[iVar])

    # If the user defines a simple selection e.g. sign>5.27
    # Make numpy array filter for selecting values out of self.data
    def getSelectionFilter(self, selection):

        selVar = None; selVal = None
        for op in self.ops:
            if op[0] in selection:
                chunks = selection.split(op[0])
                selVar = chunks[0]
                selVal = float(chunks[-1])

                return op[1](self.get(selVar), selVal)

    # Retrieve a certain variable of interested e.g. significance for all possible paramNames
    # Based on use cases, the kwargs dictionary will either have a single key "mass"
    # or a single key "disc", with their respective, appropriate values
    def getByParam(self, paramName, var, selection = None, removeOutliers = False, **kwargs):

        paramName1 = None; paramName2 = None
        # For special case of requesting "disc"
        # We need to package disc1 and disc2
        if paramName == "disc":
            paramName1 = paramName + "1"
            paramName2 = paramName + "2"

        allVarVals = self.get(var)

        baseFilter = allVarVals!=-999.0

        # Build up a filter based on all keywords passed
        afilter = baseFilter
        for kw in kwargs.keys():
            afilter &= self.get(kw)==kwargs[kw]

        if selection != None:
            afilter &= self.getSelectionFilter(selection)

        if removeOutliers:
            mean   = np.mean(allVarVals[baseFilter])
            stdd   = np.std(allVarVals[baseFilter])
            afilter &= abs(allVarVals-mean)/stdd<2.0

        # If requested "disc" param, returning two param lists (disc1 and disc2)
        if paramName1 == None:
            return self.get(paramName, afilter), self.get(var, afilter) 
        else:
            return self.get(paramName1, afilter), self.get(paramName2, afilter), self.get(var, afilter)

    # Turn list of tuples in numpy ndarray on request
    def numpyFriendly(self):
        self.data = np.array(self.data)

    def getParamList(self, paramName):
        return np.unique(self.get(paramName))

class Plotter():

    def __init__(self, outPath, approved, channel):
    
        self.outputDir = outPath

        self.cmsLabel = "Work in Progress"
        if approved:
            self.cmsLabel = ""

        self.channel   = channel

    def addCMSlabel(self, ax, location = "inframe", **kwargs):

        # Option for putting CMS along top of frame
        # or the preferred standard of within the frame
        if location == "top":
            ax.text(0.0,  0.998, 'CMS',                transform=ax.transAxes, fontsize=18, fontweight='bold',  va='bottom', ha='left')
            ax.text(0.14, 1.005, '%s'%(self.cmsLabel), transform=ax.transAxes, fontsize=11, fontstyle='italic', va='bottom', ha='left')
        else:
            ax.text(0.02, 0.980, 'CMS',                transform=ax.transAxes, fontsize=18, fontweight='bold',  va='top',    ha='left')
            ax.text(0.02, 0.92,  '%s'%(self.cmsLabel), transform=ax.transAxes, fontsize=11, fontstyle='italic', va='top',    ha='left')

        if "year" in kwargs:
            ax.text(1.0,  1.007, '%s (13 TeV)'%(kwargs["year"]), transform=ax.transAxes, fontsize=11, fontweight='normal', va='bottom', ha='right')
    
        return ax

    # Add custom text label to the plot (within top of frame)
    # To display information about variable being plotted, SUSY model (mass), and channel
    def addAuxLabel(self, ax, **kwargs):

        md = None 
        if "model" in kwargs:
            if kwargs["model"] == "StealthSYY":
                md = "Stealth SYY"
            else:
                md = "RPV"

        ch = ""
        if self.channel == "0l":
            ch = "Fully-Hadronic"
        elif self.channel == "1l":
            ch = "Semi-Leptonic"
        elif self.channel == "2l":
            ch = "Fully-Leptonic"

        textLabel = ""
        if "var" in  kwargs: textLabel += "%s"%(kwargs["var"])
        if md != None: textLabel += " | %s"%(md)
        if "mass" in kwargs: textLabel += r" ($m_{\tilde{t}} = %s$ GeV)"%(kwargs["mass"])
        textLabel += " | %s"%(ch)
        ax.text(0.98, 0.97, textLabel, transform=ax.transAxes, color="cadetblue", fontsize=10, fontweight='normal', va='center', ha='right')

        return ax

    def plot_Var_vsDisc1Disc2(self, var, disc1s, disc2s, vmin, vmax, mass, labelVals = False, doLog = False, variable = "", **kwargs):

        plottingLimit = False
        if "Limit" in variable:
            plottingLimit = True

        fig = plt.figure(figsize=(6, 5)) 
        fig.subplots_adjust(top=0.95, right=0.99)
        fig.tight_layout()

        # Depending on number of points in scatter i.e. coarseness of grid search
        # adjust the size of the markers accordingly to maintain same border separation
        sf = 1.0
        if len(var) > 81:
            sf = (float(len(var)) / 81.0)**2.0

        # For most part, limit plots use divergent color scheme and black text
        # Significance plots use plasma color scheme with turquoise text
        colMap = "plasma"
        globalTextCol = "paleturquoise"
        extraYlab = ""
        if plottingLimit:
            if any(t in mass.__class__.__name__ for t in ["list", "array"]):
                colMap = "plasma_r"
            else:
                colMap = "bwr"
                globalTextCol = "black"

            extraYlab = r" on $\sigma B$ [pb]"

        if doLog:
            plt.scatter(disc1s, disc2s, s=750*sf, c=var, marker="s", cmap=colMap, norm=mpl.colors.LogNorm(), vmin=vmin, vmax=vmax)
        else:
            plt.scatter(disc1s, disc2s, s=750*sf, c=var, marker="s", cmap=colMap, vmin=vmin, vmax=vmax)
            
        plt.colorbar()
        plt.xlim(0, 1)
        plt.ylim(0, 1)

        ax = plt.gca()
        ax.set_xlabel("Disc. 1 Bin Edge", fontsize=14)
        ax.set_ylabel("Disc. 2 Bin Edge", fontsize=14)

        ax = self.addCMSlabel(ax, location = "top", **kwargs)

        extraLabel = ""
        if not plottingLimit:
            extraLabel = r"$\sigma$"

        # If the input "mass" is a list, then we are plotting the specified var
        # only for the best bin edge choice for each mass point
        # Otherwise, we are plotting all choices for a given mass point
        if any(t in mass.__class__.__name__ for t in ["list", "array"]):
            ax = self.addAuxLabel(ax, var = variable + extraYlab, **kwargs)

            # On-the-fly determining which mass points' best bin edge choice are common
            # To label in the same bin on the plot
            edges2mass = {}
            for iMass in range(0, len(mass)):
                edgesPair = (disc1s[iMass], disc2s[iMass])
                if edgesPair in edges2mass:
                    edges2mass[edgesPair].append((mass[iMass], var[iMass]))
                else:
                    edges2mass[edgesPair] = [(mass[iMass], var[iMass])]

            for edge, massVarPair in edges2mass.items():
    
                massVarText = ""
                for mvp in massVarPair:
                    massVarText += "%s:%.2f%s"%(str(int(mvp[0])), float(mvp[1]), extraLabel)
                    massVarText += "\n"
                ax.text(edge[0]+0.001, edge[1]-0.001, "%s"%(massVarText[:-1]), transform=ax.transAxes, color="midnightblue", fontsize=6, fontweight='normal', va='center', ha='center')
                ax.text(edge[0],       edge[1],       "%s"%(massVarText[:-1]), transform=ax.transAxes, color=globalTextCol,  fontsize=6, fontweight='normal', va='center', ha='center')

            fig.savefig(self.outputDir+"/%s_%s_vs_Disc1Disc2_%s_%s.pdf"%(kwargs["year"], variable, kwargs["model"], self.channel), dpi=fig.dpi)

        else:
            ax = self.addAuxLabel(ax, var = variable + extraYlab, mass = str(mass), **kwargs)

            if labelVals:
                sortForMax = True 
                if plottingLimit:
                    sortForMax = False
                top5index = sorted(range(len(var)), key=lambda i: var[i], reverse=sortForMax)[:5]

                # When labeling each bin, swap to special text colors
                # depending on if plotting best choice or worst choice
                textCol    = globalTextCol
                fontWeight = "normal"
                fontSize   = 6
                for iVar in range(0, len(var)):
                    extraLabelNew = extraLabel
                    if iVar in top5index:
                        if plottingLimit:
                            textCol = "limegreen"
                        else:
                            textCol = "lime"

                        extraLabelNew = extraLabel.replace(r"\sigma", r"\mathbf{\sigma}")
                        fontWeight = "black"
                        fontSize   = 8
                    else:
                        textCol = globalTextCol
                        fontWeight = "normal"
                        fontSize   = 6

                    ax.text(disc1s[iVar]+0.001, disc2s[iVar]-0.001, "%.2f%s"%(var[iVar],extraLabelNew), transform=ax.transAxes, color="midnightblue", fontsize=fontSize, fontweight=fontWeight, va='center', ha='center')
                    ax.text(disc1s[iVar],       disc2s[iVar],       "%.2f%s"%(var[iVar],extraLabelNew), transform=ax.transAxes, color=textCol,        fontsize=fontSize, fontweight=fontWeight, va='center', ha='center')

            fig.savefig(self.outputDir+"/%s_%s_vs_Disc1Disc2_%s%s_%s.pdf"%(kwargs["year"], variable, kwargs["model"], mass, self.channel), dpi=fig.dpi)

        plt.close(fig)

    def plot_Var_vsMass(self, var, mass, colScales, vmin, vmax, doLog = False, variable = "", **kwargs):

        fig = plt.figure(figsize=(6, 5)) 
        fig.subplots_adjust(top=0.95, right=0.99)

        colMap = "plasma"
        extraYlab = ""
        if "Limit" in variable:
            colMap = "bwr"
            extraYlab = r" on $\sigma B$ [pb]"

        for iScatter in range(0, len(var)):
            if doLog:
                plt.scatter(mass[iScatter], var[iScatter], c=var[iScatter], marker="o", cmap=colMap, norm=mpl.colors.LogNorm(), vmin=vmin*colScales[iScatter], vmax=vmax*colScales[iScatter])
            else:
                plt.scatter(mass[iScatter], var[iScatter], c=var[iScatter], marker="o", cmap=colMap, vmin=vmin*colScales[iScatter], vmax=vmax*colScales[iScatter])
            
        plt.xlim(250, 1450)
        plt.ylim(vmin*colScales[-1], vmax*colScales[0])

        ax = plt.gca()
        if doLog:
            ax.set_yscale("log")
        ax.set_ylabel(variable + extraYlab,    fontsize=14)
        ax.set_xlabel("Top Squark Mass [GeV]", fontsize=14)

        ax = self.addCMSlabel(ax, **kwargs)
        ax = self.addAuxLabel(ax, var = variable + extraYlab, **kwargs)

        fig.tight_layout()
        fig.savefig(self.outputDir+"/%s_%s_vs_Mass_%s_%s.pdf"%(kwargs["year"], variable, kwargs["model"], self.channel), dpi=fig.dpi)

        plt.close(fig)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("usage: %prog [options]\n")
    parser.add_argument('--basedir',  dest='basedir',  type=str, required = True,                       help = "Path to output files"    )
    parser.add_argument('--outdir',   dest='outdir',   type=str, required = True,                       help = "Path to put output files")
    parser.add_argument('--approved', dest='approved',           default  = False, action='store_true', help = 'Is plot approved'        )
    parser.add_argument('--channel',  dest='channel',  type=str, default  = "0l",                       help = 'Which channels to plot'  )
    args = parser.parse_args()

    path    = args.basedir
    outPath = args.outdir
    channel = args.channel

    # Top squark pair production xsections [pb]
    stopPair_xsec = {"300"  : 10.00,    "350"  : 4.43,     "400"  : 2.15,    "450"  : 1.11,    "500"  : 0.609, 
                     "550"  : 0.347,    "600"  : 0.205,    "650"  : 0.125,   "700"  : 0.0783,  "750"  : 0.0500, 
                     "800"  : 0.0326,   "850"  : 0.0216,   "900"  : 0.0145,  "950"  : 0.00991, "1000" : 0.00683, 
                     "1050" : 0.00476,  "1100" : 0.00335,  "1150" : 0.00238, "1200" : 0.00170, "1250" : 0.00122, 
                     "1300" : 0.000887, "1350" : 0.000646, "1400" : 0.000473
    }

    if not os.path.exists(outPath):
        os.makedirs(outPath)

    # Get a listing of all job output
    # Each folder would correspond to different choice of bin edges
    fitResults = glob.glob("%s/*"%(path))

    # Loop over all jobs and get the info needed
    theScraper = FitResults(stopPair_xsec, channel)
    for result in fitResults:

        # Split up each individual job folder to get edge vals, mass, etc
        chunks = result.split("/")[-1].split("_")

        # Easier to ask for forgiveness than it is to ask for permission
        # Does the folder end in _XX_YY ? i.e. a legit job folder
        # A legit job folder has a name like: "RPV_550_Run2UL_80_90"
        try:
            trial = float(chunks[-1])
            trial = float(chunks[-2])
        except:
            print("Skipping non-Combine-result \"%s\""%(result))
            continue

        disc  = chunks[-2] + "_" + chunks[-1]
        mass  = chunks[1]
        model = chunks[0]
        year  = chunks[2]

        theScraper.scrapeValues(result, year, model, mass, disc)

    theScraper.numpyFriendly()

    masses = theScraper.getParamList(paramName = "mass")
    years  = theScraper.getParamList(paramName = "year")
    models = theScraper.getParamList(paramName = "model")

    thePlotter = Plotter(outPath, args.approved, channel)

    # Adjust log and linear scales for axis ranges
    # depending on the channel
    limitScale = 1.3
    signScale = 17 
    if channel != "1l":
        limitScale = 0.9 
        signScale = 10

    for year in years:
        for model in models:
            allMasses_sign = []; allMasses_lim = []; allSigns = []; allObsLims = []; colScales = []
            bestSigns = []; bestLimits = []
            for mass in masses:

                # Plot significances as function of bin edges
                disc1s, disc2s, signs = theScraper.getByParam(paramName = "disc", var = "sign", selection = "sign>0.0", mass = mass, model = model, year = year)

                allMasses_sign.append([int(mass)]*len(disc1s))
                allSigns.append(signs)

                maxSign  = np.max(signs)
                maxDisc1 = disc1s[np.argmax(signs)]
                maxDisc2 = disc2s[np.argmax(signs)]
                bestSigns.append([int(mass), maxDisc1, maxDisc2, maxSign])

                thePlotter.plot_Var_vsDisc1Disc2(signs, disc1s, disc2s, vmin = 0.0, vmax = signScale, mass = mass, labelVals = True, variable = "Significance", model = model, year = year)

                # Plot limits as function of bin edges
                disc1s, disc2s, obsLims = theScraper.getByParam(paramName = "disc", var = "obsLimit", selection = "obsLimit>0.0", mass = mass, model = model, year = year)

                allMasses_lim.append([int(mass)]*len(disc1s))
                allObsLims.append(obsLims)

                minLimit = np.min(obsLims)
                minDisc1 = disc1s[np.argmin(obsLims)]
                minDisc2 = disc2s[np.argmin(obsLims)]
                bestLimits.append([int(mass), minDisc1, minDisc2, minLimit])

                colScales.append(stopPair_xsec[mass])

                thePlotter.plot_Var_vsDisc1Disc2(obsLims, disc1s, disc2s, vmin = stopPair_xsec[mass]*10**(-limitScale), vmax = stopPair_xsec[mass]*10**limitScale, mass = mass, labelVals = True, doLog = True, variable = "Limit", model = model, year = year)

            bestSigns  = np.array(bestSigns)
            bestLimits = np.array(bestLimits)

            # Plot all bin edge choices for all mass points together for significance and limits
            thePlotter.plot_Var_vsMass(allSigns,   allMasses_sign, colScales = [1.0]*len(allSigns), vmin = -0.25,             vmax = signScale,                    variable = "Significances", model = model, year = year)
            thePlotter.plot_Var_vsMass(allObsLims, allMasses_lim,  colScales = colScales,           vmin = 10**(-limitScale), vmax = 10**limitScale, doLog = True, variable = "Limits",        model = model, year = year)

            thePlotter.plot_Var_vsDisc1Disc2(bestSigns[:,-1],  bestSigns[:,1],  bestSigns[:,2],  vmin = 0.0,    vmax = signScale, mass = bestSigns[:,0],                variable = "Significance", model = model, year = year)
            thePlotter.plot_Var_vsDisc1Disc2(bestLimits[:,-1], bestLimits[:,1], bestLimits[:,2], vmin = 0.5e-2, vmax = 0.5e1,     mass = bestLimits[:,0], doLog = True, variable = "Limit",        model = model, year = year)
