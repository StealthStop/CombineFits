import os
import glob
import time
import argparse

import ROOT
ROOT.gROOT.SetBatch(True)

# Put matplotlib in batch mode to avoid asinine runtime errors
import matplotlib as mpl
mpl.use('Agg')

# Looks very similar to Arial/Helvetica
import matplotlib.pyplot as plt
plt.rc('font', family='Nimbus Sans')

import numpy as np

# Class to hold---for a given model, year, channel interesting Combine results for multiple choices of ABCD edges.
# In this case, interesting quantities include significance and observed limit
class FitResults():

    def __init__(self, xsecs, channel):

        # A list of tuples, which can be converted
        # to np.ndarray by calling numpyFriendly()
        self.data          = []
        self.channel       = channel
        self.stopPair_xsec = xsecs

        # Holds effective column headers and types for self.data
        # to make referencing and getting data easy
        self.paramNames = None
        self.paramTypes = None

        # For converting operation in selection string to literal function
        self.ops = [(">=", np.greater_equal),
                    (">",  np.greater), 
                    ("<=", np.less_equal),
                    ("<",  np.less)
        ]

    # Get pointer to "limit" TTree in Combine output ROOT file
    def getTree(self, filename):

        tfile = None; ttree = None 
        try:
            tfile = ROOT.TFile.Open(filename, "READ")
        except:
            print("Could not open TFile \"%s\""%(filename))
            return

        if tfile != None:
            ttree = tfile.Get("limit")
            if ttree == None:
                print("No TTree \"limit\" found in file \"%s\""%(filename))

        return tfile, ttree

    # Upon specifying mass point, year, model, channel, and disc values for a particular fit
    # open up the corresponding higgsCombine SignifExp (Asimov) ROOT file and read the significance value
    # Also open the corresponding higgsCombine AsymptoticLimits ROOT file and read the limits
    def scrapeValues(self, combineResultPath, dataCardPath, year, model, mass, disc):
        
        # Go for the pvalues first
        tagName  = "%s%s%dpseudoDataS_%s_%s"%(year, model, mass, self.channel, disc)
        filename = "%s/higgsCombine%s_SignifExp_Asimov.Significance.mH%d.MODEL%s.root"%(combineResultPath, tagName, mass, model)

        tfile, ttree = self.getTree(filename)
        pvalue = -999.0; sigma = -999.0
        if tfile != None and ttree != None:
        
            ttree.GetEntry(0)
            sigma  = ttree.limit
            pvalue = 0.5 - ROOT.TMath.Erf(float(sigma)/ROOT.TMath.Sqrt(2.0))/2.0

            tfile.Close()

        # Now go for the limits
        tagName  = "%s%s%dpseudoData_%s_%s_AsymLimit"%(year, model, mass, self.channel, disc)
        filename = "%s/higgsCombine%s.AsymptoticLimits.mH%d.MODEL%s.root"%(combineResultPath, tagName, mass, model)
        
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

        # Multiply bare limit by branching fraction
        # for apples-to-apples comparison with limit plots
        if limits_mean != None:
            limits_mean *= self.stopPair_xsec[mass]
        if limits_obs  != None:
            limits_obs  *= self.stopPair_xsec[mass]

        # And now finally parse the datacard
        dataCardFile = None
        try:
            dataCardFile = open(dataCardPath, "r")
        except:
            print("Could not open data card textfile: \"%s\""%(dataCardPath))

        usefulInfo = {}
        if dataCardFile != None:
            lines = dataCardFile.readlines()
            dataCardFile.close()

            obsCheckpoint = False
            savedLines = {}
            for line in lines:
                if "mcStat" in line or line[0] == " ":
                    continue 

                if "bin" in line and not obsCheckpoint: 
                    savedLines["obsbin"] = list(filter(None, line.rstrip("\n").split(" ")))[1:]
                    continue

                if "observation" in line:
                    savedLines["obs"] = list(filter(None, line.rstrip("\n").split(" ")))[1:]
                    obsCheckpoint = True
                    continue

                if "bin" in line and obsCheckpoint: 
                    savedLines["bin"] = list(filter(None, line.rstrip("\n").split(" ")))[1:]
                    continue

                if "process" in line and "TT" in line:
                    savedLines["process"] = list(filter(None, line.rstrip("\n").split(" ")))[1:]
                    continue

                if "rate " in line:
                    savedLines["rate"] = list(filter(None, line.rstrip("\n").split(" ")))[1:]
                    continue

                if "np_" in line:
                    savedLines[line.replace("\t", " ").split(" ")[0]] = list(filter(None, line.replace("--", "-999.0").replace("\t", " ").rstrip("\n").split(" ")))[2:]
                    continue
            
                if "rateParam" in line:
                    chunks = list(filter(None, line.rstrip("\n").split(" ")))
                    savedLines["rate"][savedLines["bin"].index(chunks[2])] = chunks[4]
                    continue

            # For the observation line, only one entry for each Njets ABCD bin
            for iBin in range(0, len(savedLines["obsbin"])):
    
                obs    = savedLines["obs"][iBin]
                obsBin = savedLines["obsbin"][iBin]
                region = obsBin.split("_")[1][0]
                njets  = obsBin.split("_")[1][1:]

                usefulInfo["Nobs_" + region + "_Njets" + njets] = float(obs)

            for iBin in range(0, len(savedLines["bin"])):

                process = savedLines["process"][iBin].replace("_2t6j_", "")
                binName = savedLines["bin"][iBin]
                region  = binName.split("_")[1][0]
                njets   = binName.split("_")[1][1:]
                rate    = savedLines["rate"][iBin]

                if not (process == "TT" and region == "A"):
                    usefulInfo[process + "_rate_" + region + "_Njets" + njets] = float(rate)

                for np in savedLines.keys():
                    processTemp = process
                    regionTemp  = region

                    # Only one key in savedLines actually is the np...
                    if "np_" not in np:
                        continue

                    # Blindly looping over all Njet ABCD process combinations
                    # So move on in loop if certain combination is meaningless
                    if   "Corr"     in np and (region+njets not in np or process != "TT"):
                        continue
                    elif "Corr" not in np and (process == "TT"  or process == "QCD"):
                        continue

                    # Naming things in a certain way for later on
                    if "Corr" not in np:
                        processTemp += "_"
                        regionTemp = "_" + regionTemp
                    else:
                        processTemp = ""
                        regionTemp = ""

                    npNameTemp = np.split("_")[1].replace(region + njets, "")
                    npName     = processTemp + npNameTemp + regionTemp + "_Njets" + njets

                    # For all systematics, convert to a percent from 1 e.g. 1.1 or 0.9 ==> 10%
                    # And for any up/down systematic that is reported with "/", take the largest
                    # E.g. 1.02/0.8 ==> 20%, rather than 2%
                    vals = savedLines[np][iBin].split("/")
                    if "/" in savedLines[np][iBin]:
                        tempUse = [float(100.0*abs(1.0-eval(vals[0]))), float(100.0*abs(1.0-eval(vals[1])))]
                        usefulInfo[npName] = max(tempUse)
                    else:
                        usefulInfo[npName] = float(100.0*abs(1.0-eval(vals[0])))

        self.save(sign = sigma, pvalue = pvalue, obsLimit = limits_obs, year = year, model = model, mass = int(mass), disc1 = float("0.%s"%(disc.split("_")[0])), disc2 = float("0.%s"%(disc.split("_")[1])), extra = usefulInfo)

    # Pass everything to be saved in numpy array for extraction later
    # A specific order of parameters is retained along with names and types
    # for easy backend access
    def save(self, **kwargs):

        sortedKeys = sorted(kwargs.keys())

        # Treat special "extra" dictionary separately
        self.data.append([kwargs[key] for key in sortedKeys if key != "extra"])

        extraSortedKeys = sorted(kwargs["extra"].keys())
        for key in extraSortedKeys:
            self.data[-1].append(kwargs["extra"][key])

        if self.paramNames == None:
            self.paramNames = [key               for key in sortedKeys if key != "extra"]
            self.paramTypes = [type(kwargs[key]) for key in sortedKeys if key != "extra"]

            for key in extraSortedKeys:
                self.paramNames.append(key)
                self.paramTypes.append(type(kwargs["extra"][key]))

    # Retrieve for a variable from self.data (a column in the numpy ndarray)
    # Also allow for a column filter to be applied
    def get(self, var, afilter = None):

        iVar = self.paramNames.index(var)
        if "array" in afilter.__class__.__name__:
            return self.data[:, iVar][afilter].astype(self.paramTypes[iVar])
        else:
            return self.data[:, iVar].astype(self.paramTypes[iVar])

    # If the user defines a simple selection e.g. sign>5.27
    # Make numpy array filter for selecting values out of self.data
    def getSelectionFilter(self, selectionStr):

        selVar = None; selVal = None; afilter = None
        selections = selectionStr.split("&&")
        for selection in selections:
            for op in self.ops:
                if op[0] in selection:
                    chunks = selection.split(op[0])
                    selVar = chunks[0]
                    selVal = float(chunks[-1])

                    if "array" not in afilter.__class__.__name__:
                        afilter = op[1](self.get(selVar), selVal)
                    else:
                        afilter &= op[1](self.get(selVar), selVal)
            
                    break

        return afilter

    # Retrieve a certain variable of interested e.g. significance for all possible paramNames
    # Based on use cases, the kwargs dictionary will either have a single key "mass"
    # or a single key "disc", with their respective, appropriate values
    def getByParam(self, paramName, var, selectionStr = None, removeOutliers = False, **kwargs):

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
        for key in kwargs.keys():
            afilter &= self.get(key)==kwargs[key]

        if selectionStr != None:
            afilter &= self.getSelectionFilter(selectionStr)

        if removeOutliers:
            mean     = np.mean(allVarVals[afilter])
            stdd     = np.std(allVarVals[afilter])
            afilter &= abs(allVarVals-mean)/stdd<2.0

        # If requested "disc" param, returning two param lists (disc1 and disc2)
        if paramName1 == None:
            return self.get(paramName, afilter), self.get(var, afilter) 
        else:
            return self.get(paramName1, afilter), self.get(paramName2, afilter), self.get(var, afilter)

    # Turn list of tuples in numpy ndarray on request
    def numpyFriendly(self):
        self.data = np.array(self.data)

    def getParamNames(self):
        return self.paramNames

    def getParamVals(self, paramName):
        return np.unique(self.get(paramName))

class Plotter():

    def __init__(self, outPath, approved, channel):
    
        self.outputDir = outPath

        self.cmsLabel = "Work in Progress"
        if approved:
            self.cmsLabel = ""

        self.channel = channel

    def addCMSlabel(self, ax, location = "inframe", **kwargs):

        # Option for putting CMS along top of frame
        # or the preferred standard of within the frame
        if location == "top":
            ax.text(0.00, 0.998, "CMS",         transform = ax.transAxes, fontsize = 18, fontweight = "bold",   va = "bottom", ha = "left")
            ax.text(0.14, 1.005, self.cmsLabel, transform = ax.transAxes, fontsize = 11, fontstyle  = "italic", va = "bottom", ha = "left")
        else:
            ax.text(0.02, 0.980, "CMS",         transform = ax.transAxes, fontsize = 18, fontweight = "bold",   va = "top",    ha = "left")
            ax.text(0.02, 0.920, self.cmsLabel, transform = ax.transAxes, fontsize = 11, fontstyle  = "italic", va = "top",    ha = "left")

        if "year" in kwargs:
            ax.text(1.00, 1.007, "%s (13 TeV)"%(kwargs["year"]), transform = ax.transAxes, fontsize = 11, fontweight = "normal", va = "bottom", ha = "right")
    
        return ax

    # Add custom text label to the plot (within top of frame)
    # To display information about variable being plotted, SUSY model (mass), and channel
    def addAuxLabel(self, ax, **kwargs):

        # Text label of the form "variable | NN model signal (mass) | channel | njets"
        textLabel = ""
        if "var" in kwargs and kwargs["var"] != None:
            if "_" in kwargs["var"]:
                textLabel += kwargs["var"].rpartition("_")[0]
            else:
                textLabel += kwargs["var"]

        md = None 
        if "model" in kwargs and kwargs["model"] != None:
            if kwargs["model"] == "StealthSYY":
                md = "Stealth SYY"
            else:
                md = "RPV"
        if md != None:
            textLabel += " | %s"%(md)

        if "mass" in kwargs and kwargs["mass"] != None:
            textLabel += r" ($m_{\tilde{t}} = %d$ GeV)"%(kwargs["mass"])

        ch = ""
        if self.channel == "0l":
            ch = "Fully-Hadronic"
        elif self.channel == "1l":
            ch = "Semi-Leptonic"
        elif self.channel == "2l":
            ch = "Fully-Leptonic"
        textLabel += " | %s"%(ch)

        if "njets" in kwargs and kwargs["njets"] != None:
            op = "="
            if (kwargs["njets"] == "11" and self.channel == "2l") or \
               (kwargs["njets"] == "12" and self.channel == "1l") or \
               (kwargs["njets"] == "13" and self.channel == "0l"):
                op = r"\geq" 
            textLabel += r" | $N_{\rm{jets}}%s%s$"%(op,kwargs["njets"])

        ax.text(0.98, 0.97, textLabel, transform = ax.transAxes, color = "cadetblue", fontsize = 10, fontweight = 'normal', va = 'center', ha = 'right')

        return ax

    def plot_Var_vsDisc1Disc2(self, var, disc1s, disc2s, vmin, vmax, mass = None, labelVals = False, labelBest = False, doLog = False, variable = "", **kwargs):
    
        massIsList = any(t in mass.__class__.__name__ for t in ["list", "array"])

        # For most part, limit plots use divergent color scheme and black text
        # Significance plots use plasma color scheme with turquoise text
        # Plots of process rates use sequential colors and NPs use divergent scheme
        colMap        = "plasma"
        extraYlab     = ""
        globalTextCol = "darkturquoise"
        plottingLimit = False; plottingRate = False; plottingSign = False; plottingNP = False; njets = None
        if "Limit" in variable:
            plottingLimit = True

            if massIsList:
                colMap = "plasma_r"
            else:
                colMap = "bwr"
                globalTextCol = "black"

            extraYlab = r" on $\sigma B$ [pb]"

        elif "Sign" in variable:
            plottingSign = True

        elif "rate" in variable or "_" in variable:
            njets = variable.split("_Njets")[-1]

            if "rate" not in variable:
                plottingNP = True
            elif "rate" in variable:
                plottingRate = True
                if   "TT_" in variable:
                    colMap = "Purples"
                elif "QCD" in variable:
                    colMap = "Greens"
                elif "TTX" in variable:
                    colMap = "Blues"
                elif "Other" in variable:
                    colMap = "Oranges"
                else:
                    colMap = "PuRd"

        extraLabel = ""
        if not plottingLimit and not plottingRate and not plottingNP:
            extraLabel = r"$\sigma$"

        fig = plt.figure(figsize = (6, 5)) 
        fig.subplots_adjust(top = 0.95, right = 0.99)
        fig.tight_layout()

        # Depending on number of points in scatter i.e. coarseness of grid search
        # adjust the size of the markers accordingly to maintain same border separation
        sf = 1.0
        if len(var) > 81:
            sf = (float(len(var)) / 81.0)**2.0

        if doLog:
            plt.scatter(disc1s, disc2s, s = 750*sf, c = var, marker = "s", cmap = colMap, norm = mpl.colors.LogNorm(), vmin = vmin, vmax = vmax)
        else:
            plt.scatter(disc1s, disc2s, s = 750*sf, c = var, marker = "s", cmap = colMap,                              vmin = vmin, vmax = vmax)
            
        plt.colorbar()
        plt.xlim(0, 1)
        plt.ylim(0, 1)

        ax = plt.gca()
        ax.set_xlabel("Disc. 1 Bin Edge", fontsize = 14)
        ax.set_ylabel("Disc. 2 Bin Edge", fontsize = 14)

        ax = self.addCMSlabel(ax, location = "top", **kwargs)

        # If the input "mass" is a list, then we are plotting the specified var
        # only for the best bin edge choice for each mass point
        # Otherwise, we are plotting all choices for a given mass point
        if massIsList:
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
                    massVarText += "%s:%.1f%s"%(str(int(mvp[0])), float(mvp[1]), extraLabel)
                    massVarText += "\n"
                ax.text(edge[0]+0.001, edge[1]-0.001, "%s"%(massVarText[:-1]), transform=ax.transAxes, color="midnightblue", fontsize=7, fontweight='normal', va='center', ha='center')
                ax.text(edge[0],       edge[1],       "%s"%(massVarText[:-1]), transform=ax.transAxes, color=globalTextCol,  fontsize=7, fontweight='normal', va='center', ha='center')

            fig.savefig(self.outputDir+"/%s_%s_vs_Disc1Disc2_%s_%s.pdf"%(kwargs["year"], variable, kwargs["model"], self.channel), dpi=fig.dpi)


        else:
            ax = self.addAuxLabel(ax, var = variable + extraYlab, mass = mass, njets = njets, **kwargs)

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
                    if iVar in top5index and labelBest:
                        if plottingLimit:
                            textCol = "limegreen"
                        else:
                            textCol = "lime"

                        extraLabelNew = extraLabel.replace(r"\sigma", r"\mathbf{\sigma}")
                        fontWeight = "black"
                        fontSize   = 11 
                    else:
                        textCol = globalTextCol
                        fontWeight = "normal"
                        fontSize   = 9

                    payloadStr = ""
                    if plottingNP:
                       payloadStr = "%2.0f%%%s"%(var[iVar],extraLabelNew) 
                    elif plottingSign or plottingRate:
                       payloadStr = "%.1f%s"%(var[iVar],extraLabelNew) 
                    else:
                       payloadStr = "%.2f%s"%(var[iVar],extraLabelNew)
                    ax.text(disc1s[iVar]+0.001, disc2s[iVar]-0.001, payloadStr, transform = ax.transAxes, color = "midnightblue", fontsize = fontSize, fontweight = fontWeight, va = 'center', ha = 'center')
                    ax.text(disc1s[iVar],       disc2s[iVar],       payloadStr, transform = ax.transAxes, color = textCol,        fontsize = fontSize, fontweight = fontWeight, va = 'center', ha = 'center')

            if not plottingRate and not plottingNP:
                fig.savefig(self.outputDir+"/%s_%s_vs_Disc1Disc2_%s%d_%s.pdf"%(kwargs["year"], variable, kwargs["model"], mass, self.channel), dpi=fig.dpi)
            else:
                fig.savefig(self.outputDir+"/%s_%s_vs_Disc1Disc2_%s_%s.pdf"%(kwargs["year"], variable, kwargs["model"], self.channel), dpi=fig.dpi)

        plt.close(fig)

    def plot_Var_vsMass(self, var, mass, colScales, vmin, vmax, doLog = False, variable = "", **kwargs):

        colMap = "plasma"
        extraYlab = ""
        if "Limit" in variable:
            colMap = "bwr"
            extraYlab = r" on $\sigma B$ [pb]"

        fig = plt.figure(figsize = (6, 5)) 
        fig.subplots_adjust(top = 0.95, right = 0.99)

        for iScatter in range(0, len(var)):
            if doLog:
                plt.scatter(mass[iScatter], var[iScatter], c = var[iScatter], marker = "o", cmap = colMap, norm = mpl.colors.LogNorm(), vmin = vmin*colScales[iScatter], vmax = vmax*colScales[iScatter])
            else:
                plt.scatter(mass[iScatter], var[iScatter], c = var[iScatter], marker = "o", cmap = colMap,                              vmin = vmin*colScales[iScatter], vmax = vmax*colScales[iScatter])
            
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

    combineResults = args.basedir
    dataCardsPath  = args.basedir + "/cards_scan"
    outPath = args.outdir
    channel = args.channel

    njets = [str(iNjet) for iNjet in range(7, 13)]
    regions = ["A", "B", "C", "D"]
    if channel == "0l":
        njets = [str(iNjet) for iNjet in range(8, 14)]
    elif channel == "2l":
        njets = [str(iNjet) for iNjet in range(6, 12)]

    # Top squark pair production xsections [pb]
    stopPair_xsec = {300  : 10.00,    350  : 4.43,     400  : 2.15,    450  : 1.11,    500  : 0.609, 
                     550  : 0.347,    600  : 0.205,    650  : 0.125,   700  : 0.0783,  750  : 0.0500, 
                     800  : 0.0326,   850  : 0.0216,   900  : 0.0145,  950  : 0.00991, 1000 : 0.00683, 
                     1050 : 0.00476,  1100 : 0.00335,  1150 : 0.00238, 1200 : 0.00170, 1250 : 0.00122, 
                     1300 : 0.000887, 1350 : 0.000646, 1400 : 0.000473
    }

    if not os.path.exists(outPath):
        os.makedirs(outPath)

    # Get a listing of all job output
    # Each folder would correspond to different choice of bin edges
    combineFitResults = glob.glob("%s/*"%(combineResults))

    # Loop over all jobs and get the info needed
    theScraper = FitResults(stopPair_xsec, channel)
    for combineFitResultPath in combineFitResults:

        # Split up each individual job folder to get edge vals, mass, etc
        chunks = combineFitResultPath.split("/")[-1].split("_")

        # Easier to ask for forgiveness than it is to ask for permission
        # Does the folder end in _XX_YY ? i.e. a legit job folder
        # A legit job folder has a name like: "RPV_550_Run2UL_80_90"
        try:
            trial = float(chunks[-1])
            trial = float(chunks[-2])
        except:
            print("Skipping non-Combine-result \"%s\""%(combineFitResultPath))
            continue

        disc1 = chunks[-2]
        disc2 = chunks[-1]
        disc  = disc1 + "_" + disc2
        mass  = int(chunks[1])
        model = chunks[0]
        year  = chunks[2]

        dataCardPath = "%s/%s_%s_%d_pseudoData_%s_%s_%s.txt"%(dataCardsPath, year, model, mass, channel, disc1, disc2)

        theScraper.scrapeValues(combineFitResultPath, dataCardPath, year, model, mass, disc)

    theScraper.numpyFriendly()

    masses = theScraper.getParamVals(paramName = "mass")
    years  = theScraper.getParamVals(paramName = "year")
    models = theScraper.getParamVals(paramName = "model")

    params = theScraper.getParamNames()

    thePlotter = Plotter(outPath, args.approved, channel)

    # Adjust log and linear scales for axis ranges
    # depending on the channel
    limitScale = 1.3
    signScale  = 17 
    if channel != "1l":
        limitScale = 0.9 
        signScale  = 10

    minObsCut = []
    for njet in njets:
        for region in regions:
            minObsCut.append("Nobs_%s_Njets%s>3.0"%(region,njet))

    minObsCut = "&&".join(minObsCut)

    for year in years:
        for model in models:

            for param in params:

                if "_" not in param:
                    continue

                disc1s, disc2s, paramVals = theScraper.getByParam(paramName = "disc", var = param, mass = masses[0], model = model, year = year)

                vmin = 0.0
                vmax = max(paramVals)

                thePlotter.plot_Var_vsDisc1Disc2(paramVals, disc1s, disc2s, vmin = vmin, vmax = vmax, labelVals = True, variable = param, model = model, year = year)

            allMasses_sign = []; allMasses_lim = []; allSigns = []; allObsLims = []; colScales = []
            bestSigns = []; bestLimits = []
            for mass in masses:

                # Plot significances as function of bin edges
                disc1s, disc2s, signs = theScraper.getByParam(paramName = "disc", var = "sign", selectionStr = "sign>0.0&&sign<15.0&&%s"%(minObsCut), removeOutliers = False, mass = mass, model = model, year = year)

                allMasses_sign.append([mass]*len(disc1s))
                allSigns.append(signs)

                maxSign = -999.0; maxDisc1 = -999.0; maxDisc2 = -999.0
                try:
                    maxSign  = np.max(signs)
                    maxDisc1 = disc1s[np.argmax(signs)]
                    maxDisc2 = disc2s[np.argmax(signs)]
                except:
                    pass
                bestSigns.append([mass, maxDisc1, maxDisc2, maxSign])

                thePlotter.plot_Var_vsDisc1Disc2(signs, disc1s, disc2s, vmin = 0.0, vmax = maxSign*1.05, mass = mass, labelVals = True, labelBest = True, variable = "Significance", model = model, year = year)

                # Plot limits as function of bin edges
                disc1s, disc2s, obsLims = theScraper.getByParam(paramName = "disc", var = "obsLimit", selectionStr = "obsLimit>%f&&%s"%(stopPair_xsec[mass]*10**(-1.5),minObsCut), removeOutliers = False, mass = mass, model = model, year = year)

                allMasses_lim.append([mass]*len(disc1s))
                allObsLims.append(obsLims)

                minLimit = -999.0; minDisc1 = -999.0; minDisc2 = -999.0
                try:
                    minLimit = np.min(obsLims)
                    minDisc1 = disc1s[np.argmin(obsLims)]
                    minDisc2 = disc2s[np.argmin(obsLims)]
                except:
                    pass
                bestLimits.append([mass, minDisc1, minDisc2, minLimit])

                colScales.append(stopPair_xsec[mass])

                thePlotter.plot_Var_vsDisc1Disc2(obsLims, disc1s, disc2s, vmin = stopPair_xsec[mass]*10**(-limitScale), vmax = stopPair_xsec[mass]*10**limitScale, mass = mass, labelVals = True, labelBest = True, doLog = True, variable = "Limit", model = model, year = year)

            bestSigns  = np.array(bestSigns)
            bestLimits = np.array(bestLimits)

            # Plot all bin edge choices for all mass points together for significance and limits
            thePlotter.plot_Var_vsMass(allSigns,   allMasses_sign, colScales = [1.0]*len(allSigns), vmin = -0.25,             vmax = signScale,                    variable = "Significances", model = model, year = year)
            thePlotter.plot_Var_vsMass(allObsLims, allMasses_lim,  colScales = colScales,           vmin = 10**(-limitScale), vmax = 10**limitScale, doLog = True, variable = "Limits",        model = model, year = year)

            thePlotter.plot_Var_vsDisc1Disc2(bestSigns[:,-1],  bestSigns[:,1],  bestSigns[:,2],  vmin = 0.0,    vmax = signScale, mass = bestSigns[:,0],                variable = "Significance", model = model, year = year)
            thePlotter.plot_Var_vsDisc1Disc2(bestLimits[:,-1], bestLimits[:,1], bestLimits[:,2], vmin = 0.5e-2, vmax = 0.5e1,     mass = bestLimits[:,0], doLog = True, variable = "Limit",        model = model, year = year)
