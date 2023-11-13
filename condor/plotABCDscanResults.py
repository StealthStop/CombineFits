import os
import re
import glob
import math
import argparse
import subprocess

# Put matplotlib in batch mode to avoid asinine runtime errors
import matplotlib as mpl
mpl.use("Agg")

# Looks very similar to Arial/Helvetica
import matplotlib.pyplot as plt
plt.rc("font", family="Nimbus Sans")

import numpy as np

# Avoid pyROOT intercepting -h from commandline
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)

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
                tfile.Close()

        return tfile, ttree

    # Upon specifying mass point, year, model, channel, and disc values for a particular fit
    # open up the corresponding higgsCombine SignifExp (Asimov) ROOT file and read the significance value
    # Also open the corresponding higgsCombine AsymptoticLimits ROOT file and read the limit
    # Likewise, parse the corresponding data card to get systematics and rates
    def scrapeValues(self, combineResultPath, dataCardPath, year, model, mass, disc1, disc2, disc):
        
        # Try the datacard first, if not there, then do not worry about anything else
        dataCardFile = None
        usefulInfo = {}
        try:
            dataCardFile  = open(dataCardPath, "r")
            dataCardLines = dataCardFile.readlines()
            dataCardFile.close()
        except:
            print("Could not open data card textfile: \"%s\""%(dataCardPath))
            return

        if dataCardFile != None:
            obsCheckpoint = False
            savedLines = {}
            for line in dataCardLines:
    
                # Any empty lines or mcStat lines are not used
                if "mcStat" in line or line[0] == " ":
                    continue 

                # The first "bin" line corresponds to total obs counts in each analysis bin
                # One unique name for each bin
                if "bin" in line and not obsCheckpoint: 
                    savedLines["obsbin"] = list(filter(None, line.rstrip("\n").split(" ")))[1:]
                    continue

                # One obs counts for each analysis bin
                if "observation" in line:
                    savedLines["obs"] = list(filter(None, line.rstrip("\n").split(" ")))[1:]
                    obsCheckpoint = True
                    continue

                # Second "bin" line pertains to each process in each analysis bin
                # Bin names from first "bin" line used here, but repeated for each process
                if "bin" in line and obsCheckpoint: 
                    savedLines["bin"] = list(filter(None, line.rstrip("\n").split(" ")))[1:]
                    continue

                # Get "process" line with process names, not process IDs
                if "process" in line and "TT" in line:
                    savedLines["process"] = list(filter(None, line.rstrip("\n").split(" ")))[1:]
                    continue

                # Rate line will give individual counts for a process in a particular analysis bin
                if "rate " in line:
                    savedLines["rate"] = list(filter(None, line.rstrip("\n").split(" ")))[1:]
                    continue

                # Each systematic is on own line an includes "np_" in its name
                # Location of values aligns where systematic is applicable for process + analysis bin
                if "np_" in line:
                    savedLines[line.replace("\t", " ").split(" ")[0]] = list(filter(None, line.replace("--", "-999.0").replace("\t", " ").rstrip("\n").split(" ")))[2:]
                    continue
            
                # Finally, get the rate for TT in special section at end of datacard
                if "rateParam" in line:
                    chunks = list(filter(None, line.rstrip("\n").split(" ")))
                    binName = chunks[2]
                    ttRate  = chunks[4]
                    savedLines["rate"][savedLines["bin"].index(binName)] = ttRate
                    continue

            # Now processing useful information extracted from the data card lines
            # For the observation line, only one entry for each Njets-ABCD analysis bin
            for iBin in range(0, len(savedLines["obsbin"])):
    
                obs     = savedLines["obs"][iBin]
                binName = savedLines["obsbin"][iBin]

                # Bin name example: "YUL_B9_1l"
                region = binName.split("_")[1][0]
                njets  = binName.split("_")[1][1:]

                usefulInfo["Nobs_" + region + "_Njets" + njets] = float(obs)

            nps = [np for np in savedLines.keys() if "np_" in np]
            for iBin in range(0, len(savedLines["bin"])):

                process = savedLines["process"][iBin].replace("_2t6j_", "")
                binName = savedLines["bin"][iBin]
                region  = binName.split("_")[1][0]
                njets   = binName.split("_")[1][1:]
                rate    = savedLines["rate"][iBin]

                # No unique rate information for TT in region A as it is calculated via ABCD method
                if not (process == "TT" and region == "A"):
                    usefulInfo[process + "_rate_" + region + "_Njets" + njets] = float(rate)

                for np in nps:

                    # Blindly looping over all Njet ABCD process combinations
                    # So move on in loop if certain combination is meaningless
                    if   "Corr"     in np and (region+njets not in np or process != "TT"):
                        continue
                    elif "Corr" not in np and process == "QCD": #(process == "TT"  or process == "QCD"):
                        continue

                    # Naming things in a certain way for later on
                    processStub = None
                    regionStub  = None
                    if "Corr" not in np:
                        processStub = process + "_"
                        regionStub  = "_" + region
                    else:
                        processStub = ""
                        regionStub  = ""

                    npNameStub = np.split("_")[1].replace(region + njets, "")
                    npName     = processStub + npNameStub + regionStub + "_Njets" + njets

                    # For all systematics, convert to a percent from 1 e.g. 1.1 or 0.9 ==> 10%
                    # And for any up/down systematic that is reported with "/", take the largest
                    # E.g. 1.02/0.8 ==> 20%, rather than 2%
                    #npVals = [100.0 * abs(1.0-eval(val)) for val in savedLines[np][iBin].split("/")]
                    #usefulInfo[npName] = max(npVals)
                    usefulInfo[npName] = 10.0

        # Go for the significance first
        tagName  = "%s%s%dpseudoDataS_%s_%s"%(year, model, mass, self.channel, disc)
        filename = "%s/higgsCombine%s_SignifExp_Asimov.Significance.mH%d.MODEL%s.root"%(combineResultPath, tagName, mass, model)

        tfile, ttree = self.getTree(filename)
        sigma = -999.0
        if tfile != None and ttree != None:
        
            ttree.GetEntry(0)
            sigma = ttree.limit

            tfile.Close()

        filename = "%s/higgsCombine%s_SignifExp.Significance.mH%d.MODEL%s.root"%(combineResultPath, tagName, mass, model)

        # Go for non-Asimov style significance (should match closely to Asimov style)
        tfile, ttree = self.getTree(filename)
        sigma_nonasimov = -999.0
        if tfile != None and ttree != None:
        
            ttree.GetEntry(0)
            sigma_nonasimov = ttree.limit

            tfile.Close()

        # Define difference between the two sigmas
        # For a reliable result, they should very close i.e. ~< 2.0
        sigmaDiff = -999.0
        if sigma > 0.0 and sigma_nonasimov > 0.0:
            sigmaDiff = abs(sigma - sigma_nonasimov)

        # Now go for the limit
        filename = "%s/higgsCombine%s_AsymLimit_Asimov.AsymptoticLimits.mH%d.MODEL%s.root"%(combineResultPath, tagName.replace("DataS", "Data"), mass, model)
        logName  = "%s/log_%s_Asymp.txt"%(combineResultPath, tagName.replace("DataS", "Data"))

        # If we are dumping many lines into the log file, something is going wrong---do not trust...
        healthyLimit = 1
        try:
            healthyLimit = int(int(subprocess.check_output("wc -l %s"%(os.path.abspath(logName)), shell=True).split()[0]) < 25)
        except:
            pass
        
        tfile, ttree = self.getTree(filename)
        limit_mean = -999.0; limit_obs = -999.0
        if tfile != None and ttree != None:

            # Limits, 2.5%, 16%, 50%, 84%, and 97.5% values are just all in a sequence in the TTree
            ttree.GetEntry(2)
            limit_mean = ttree.limit

            ttree.GetEntry(5)
            limit_obs  = ttree.limit

            tfile.Close()
        
        # Multiply bare limit by cross section for top squark pair
        if limit_mean != None:
            limit_mean *= self.stopPair_xsec[mass]
        if limit_obs  != None:
            limit_obs  *= self.stopPair_xsec[mass]

        self.save(sign = sigma, sign_nonasimov = sigma_nonasimov, signDiff = sigmaDiff, healthyLimit = healthyLimit, expLimit = limit_mean, obsLimit = limit_obs, year = year, model = model, mass = int(mass), disc1 = float(disc1)/100., disc2 = float(disc2)/100., dataCardInfo = usefulInfo)

    # Pass everything to be saved in numpy array for extraction later
    # A specific order of parameters is retained along with names and types
    # for easy backend access
    def save(self, **kwargs):

        sortedKeys = sorted(kwargs.keys())

        # Treat "dataCardInfo" dictionary separately
        self.data.append([kwargs[key] for key in sortedKeys if key != "dataCardInfo"])

        dcSortedKeys = sorted(kwargs["dataCardInfo"].keys())
        for key in dcSortedKeys:
            self.data[-1].append(kwargs["dataCardInfo"][key])

        if self.paramNames == None:
            self.paramNames = [key               for key in sortedKeys if key != "dataCardInfo"]
            self.paramTypes = [type(kwargs[key]) for key in sortedKeys if key != "dataCardInfo"]

            for key in dcSortedKeys:
                self.paramNames.append(key)
                self.paramTypes.append(type(kwargs["dataCardInfo"][key]))

    # Retrieve for a variable from self.data (a column in an numpy ndarray)
    # Also allow for a column filter to be applied
    def get(self, var, afilter = None):

        iVar = self.paramNames.index(var)
        if "array" in afilter.__class__.__name__:
            return self.data[:, iVar][afilter].astype(self.paramTypes[iVar])
        else:
            return self.data[:, iVar].astype(self.paramTypes[iVar])

    # If the user defines a simple selection e.g. sign>5.27&&obsLimit<0.1
    # Make numpy array filter for selecting values out of self.data
    def getSelectionFilter(self, selection):

        # From a selection like "(disc1>0.1)&(disc2>0.1)&(obsLimit>0.012935)"
        # Obtain the variable names "disc1", "disc2", and "obsLimit"
        pattern  = r"\b(?![0-9]+\b)[a-zA-Z0-9_]+\b" 
        varNames = list(set(re.findall(pattern, selection)))
        varNames.sort(key = lambda x : len(x), reverse = True)

        # The needed variables to evaluate the selection, paired with their literal column of values
        nameVarPairs = [(varName, self.get(varName)) for varName in varNames]

        # Replace the unique names in the selectionsStr with the variable created above "nameVarPairs"
        # so that eval() can successfully evaluate
        selectionExp = selection
        iPair = 0
        for nameVarPair in nameVarPairs:
            selectionExp = selectionExp.replace(nameVarPair[0], "nameVarPairs[%d][1]"%(iPair))
            iPair += 1

        afilter = eval(selectionExp)

        return afilter

    # Retrieve a certain variable of interest e.g. significance for all possible values of "paramName"
    # Based on use cases, the kwargs dictionary will either have a single key "mass"
    # or a single key "disc", with their respective, appropriate values
    def getByParam(self, paramName, var, selection = None, **kwargs):
        
        allVarVals = self.get(var)

        # Initialize perfectly transparent filter to element-wise AND with
        baseFilter = allVarVals!=-999.0

        # Build up a filter based on all keywords passed
        afilter = baseFilter
        for key in kwargs.keys():
            afilter &= self.get(key)==kwargs[key]

        if selection != None:
            afilter &= self.getSelectionFilter(selection)

        # If requested "disc" param, returning two param lists (disc1 and disc2)
        if paramName == "disc":
            return self.get("disc1", afilter), self.get("disc2", afilter), self.get(var, afilter)
        else:
            return self.get(paramName, afilter), self.get(var, afilter) 

    # Turn list of lists into numpy ndarray on request
    # Done at the conclusion of appending to self.data
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


        # Expected limits for full Run2 setup
        self.SUS19004limitsRPV = np.array([[300.0,  1.4307],   [350.0,  0.61432],  [400.0,  0.32229],  [450.0,  0.20813],  [500.0,  0.1469],
                                           [550.0,  0.11149],  [600.0,  0.089687], [650.0,  0.07251],  [700.0,  0.066983], [750.0,  0.060742],
                                           [800.0,  0.055267], [850.0,  0.05805],  [900.0,  0.056414], [950.0,  0.058221], [1000.0, 0.059549],
                                           [1050.0, 0.062773], [1100.0, 0.06365],  [1150.0, 0.069615], [1200.0, 0.071612]])

        self.SUS19004limitsSYY = np.array([[300.0,  2.4316],    [350.0,  0.71166],   [400.0,  0.2887],    [450.0,  0.14796],  [500.0,  0.087127],
                                           [550.0,  0.057607],  [600.0,  0.039038],  [650.0,  0.031006],  [700.0,  0.024239], [750.0,  0.019092],
                                           [800.0,  0.016618],  [850.0,  0.014428],  [900.0,  0.012744],  [950.0,  0.01142],  [1000.0, 0.010512],
                                           [1050.0, 0.0096316], [1100.0, 0.0095004], [1150.0, 0.0088134], [1200.0, 0.0088188]])

        # Expected sensitivity for full Run2 setup
        self.SUS19004signsRPV = np.array([[300.0,  8.02], [350.0,  9.29], [400.0,  9.58], [450.0,  8.46], [500.0,  7.07],
                                          [550.0,  5.69], [600.0,  4.36], [650.0,  3.41], [700.0,  2.42], [750.0,  1.74],
                                          [800.0,  1.10], [850.0,  0.46], [900.0,  0.25], [950.0,  0.20], [1000.0, 0.18],
                                          [1050.0, 0.04], [1100.0, 0.00], [1150.0, 0.00], [1200.0, 0.00]])

        self.SUS19004signsSYY = np.array([[300.0,  5.37], [350.0,  8.13], [400.0,  9.87], [450.0, 10.37], [500.0,  9.89],
                                          [550.0,  9.14], [600.0,  7.39], [650.0,  6.91], [700.0,  5.71], [750.0,  4.91],
                                          [800.0,  3.99], [850.0,  3.29], [900.0,  2.48], [950.0,  2.05], [1000.0, 1.68],
                                          [1050.0, 0.80], [1100.0, 0.67], [1150.0, 0.51], [1200.0, 0.13]])

    # Option for putting CMS along top of frame
    # or the preferred standard of within the frame
    def addCMSlabel(self, ax, location = "inframe", **kwargs):

        if location == "top":
            ax.text(0.00, 0.996, "CMS",         transform = ax.transAxes, fontsize = 22, fontweight = "bold",   va = "bottom", ha = "left")
            ax.text(0.18, 1.004, self.cmsLabel, transform = ax.transAxes, fontsize = 14, fontstyle  = "italic", va = "bottom", ha = "left")
        else:
            ax.text(0.02, 0.980, "CMS",         transform = ax.transAxes, fontsize = 22, fontweight = "bold",   va = "top",    ha = "left")
            ax.text(0.02, 0.910, self.cmsLabel, transform = ax.transAxes, fontsize = 14, fontstyle  = "italic", va = "top",    ha = "left")

        if "year" in kwargs:
            ax.text(1.00, 1.007, "%s (13 TeV)"%(kwargs["year"]), transform = ax.transAxes, fontsize = 13, fontweight = "normal", va = "bottom", ha = "right")
    
        return ax

    # Add custom text label to the plot (within top of frame)
    # To display information about variable being plotted, SUSY model (mass), and channel
    def addAuxLabel(self, ax, atBottom = False, **kwargs):

        # Text label of the form "NN model signal (mass) | channel | njets"
        # Variable label drawn separately if specified
        textLabel = []; varLabel = ""
        if "var" in kwargs and kwargs["var"] != None:
            if "_" in kwargs["var"] and "$" not in kwargs["var"]:
                varLabel = kwargs["var"].rpartition("_")[0]
            else:
                varLabel = kwargs["var"]

            if "Significance" in kwargs["var"]:
                varLabel += r" [$\sigma$]"

            ax.text(0.5, 0.97, varLabel, transform = ax.transAxes, color = "cadetblue", fontsize = 12, fontweight = "normal", va = "center", ha = "center")

        model = None 
        if "model" in kwargs and kwargs["model"] != None:
            if kwargs["model"] == "StealthSYY":
                model = r"Stealth (SYY)"
            else:
                model = "RPV"
        if model != None:
            textLabel.append(model)
            if "mass" in kwargs and kwargs["mass"] != None:
                textLabel[-1] += r" ($m_{\tilde{t}} = %d$ GeV)"%(kwargs["mass"])

        channel = ""
        if self.channel == "0l":
            channel = r"Fully-Hadronic"
        elif self.channel == "1l":
            channel = r"Semi-Leptonic"
        elif self.channel == "2l":
            channel = r"Fully-Leptonic"
        elif self.channel == "combo":
            channel = r"0L + 1L + 2L"
        textLabel.append(channel)

        if "njets" in kwargs and kwargs["njets"] != None:
            op = "="
            if (kwargs["njets"] == "11" and self.channel == "2l") or \
               (kwargs["njets"] == "12" and self.channel == "1l") or \
               (kwargs["njets"] == "13" and self.channel == "0l"):
                op = r"\geq" 
            textLabel.append(r"$N_{\rm{jets}}%s%s$"%(op,kwargs["njets"]))

        if atBottom:
            ax.text(0.50, 0.03, " | ".join(textLabel), transform = ax.transAxes, color = "cadetblue", fontsize = 12, fontweight = "normal", va = "center", ha = "center")
        else:
            ax.text(0.98, 0.97, " | ".join(textLabel), transform = ax.transAxes, color = "cadetblue", fontsize = 12, fontweight = "normal", va = "center", ha = "right")

        return ax

    def plot_Var_vsDisc1Disc2(self, var, disc1s, disc2s, vmin, vmax, binWidth = 0.1, xMin = 0.36, xMax = 0.92, yMin = 0.36, yMax = 0.92, mass = None, labelVals = False, labelBest = False, doLog = False, variable = "", **kwargs):
    
        massIsList = any(t in mass.__class__.__name__ for t in ["list", "array"])

        # For most part, limit plots use divergent color scheme and black text
        # Significance plots use plasma color scheme with turquoise text
        # Plots of process rates and NPs use sequential colors
        colMap        = "plasma"
        labelSuffix   = ""
        labelPrefix   = ""
        globalTextCol = "darkturquoise"
        plottingLimit = False; plottingRate = False; plottingSign = False; plottingNP = False; njets = None
        if "Limit" in variable:
            plottingLimit = True

            if massIsList:
                colMap = "plasma_r"
            else:
                colMap = "bwr"
                globalTextCol = "black"

            labelPrefix = "Expected "
            labelSuffix = r" on $\sigma_{\tilde{t}\bar{\tilde{t}}}$ [pb]"

        elif "Sign" in variable:
            plottingSign = True

        elif "rate" in variable or "_" in variable:
            njets = variable.split("_Njets")[-1]

            if "rate" not in variable:
                plottingNP = True
            elif "rate" in variable:
                plottingRate = True
                if   "TT_"   in variable:
                    colMap = "Purples"
                elif "QCD"   in variable:
                    colMap = "Greens"
                elif "TTX"   in variable:
                    colMap = "Blues"
                elif "Other" in variable:
                    colMap = "Oranges"
                else:
                    colMap = "PuRd"

        # Based on margins and space for colorbar and predetermined figure height
        # Optimize figure width so that plot _frame_ is square
        lmargin = 0.12; rmargin = 1.0; bmargin = 0.12; tmargin = 0.94
        cpad = 0.0; cfraction = 0.14

        hfraction = 1.0 - (1.0 - tmargin) - bmargin
        wfraction = 1.0 - (1.0 - lmargin) * (cpad + cfraction) - (1.0 - rmargin) - lmargin

        figheight = 5.0
        figwidth  = figheight * hfraction / wfraction

        fig = plt.figure(figsize = (figwidth, figheight)) 
        fig.subplots_adjust(left = lmargin, bottom = bmargin, top = tmargin, right = rmargin)

        ax   = plt.gca()

        # Based on spacing of points, axis range, calculate the size of a colored
        # square in point units so that the squares are always flush with one another 
        pixel2PointSF  = fig.dpi / 72.0
        axPointSize    = fig.dpi * figwidth * wfraction / pixel2PointSF
        axRange        = xMax - xMin
        axBoxes        = axRange / binWidth
        axBoxPointSize = axPointSize / axBoxes

        if doLog:
            plt.scatter(disc1s, disc2s, s = axBoxPointSize**2.0, c = var, marker = "s", edgecolors = "none", cmap = colMap, norm = mpl.colors.LogNorm())#, vmin = vmin, vmax = vmax)
        else:
            plt.scatter(disc1s, disc2s, s = axBoxPointSize**2.0, c = var, marker = "s", edgecolors = "none", cmap = colMap,                            )#vmin = vmin, vmax = vmax)

        cbar = plt.colorbar(pad = cpad, fraction = cfraction)
        plt.xlim(xMin, xMax)
        plt.ylim(yMin, yMax)

        ax.set_xlabel("Disc. 1 Bin Edge", fontsize = 16)
        ax.set_ylabel("Disc. 2 Bin Edge", fontsize = 16)

        ax.tick_params(axis = "both",     labelsize = 12)
        cbar.ax.tick_params(labelsize = 12)

        ax = self.addCMSlabel(ax, location = "top", **kwargs)

        # If the input "mass" is a list, then we are plotting the specified var
        # only for the best bin edge choice for each mass point
        # Otherwise, we are plotting all choices for a given mass point
        if massIsList:
            ax = self.addAuxLabel(ax, var = labelPrefix + variable + labelSuffix, atBottom = True, **kwargs)

            # On-the-fly determining which mass points" best bin edge choice are common
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
                    massVarText += "%s:%.1f"%(str(int(mvp[0])), float(mvp[1]))
                    massVarText += "\n"
                ax.text(edge[0]+axRange/1e3, edge[1]-axRange/2e3, "%s"%(massVarText[:-1]), color = "midnightblue", fontsize = 7, fontweight = "normal", va = "center", ha = "center")
                ax.text(edge[0],             edge[1],             "%s"%(massVarText[:-1]), color = globalTextCol,  fontsize = 7, fontweight = "normal", va = "center", ha = "center")

            fig.savefig(self.outputDir+"/%s_%s_vs_Disc1Disc2_%s_%s.pdf"%(kwargs["year"], variable, kwargs["model"], self.channel), dpi = fig.dpi)


        else:
            ax = self.addAuxLabel(ax, var = labelPrefix + variable + labelSuffix, mass = mass, njets = njets, atBottom = True, **kwargs)

            if labelVals:
                sortForMax = True 
                if plottingLimit:
                    sortForMax = False
                top5index = sorted(range(len(var)), key=lambda i: var[i], reverse=sortForMax)[:5]

                # When labeling each bin, swap to special text colors
                # depending on if plotting best choice or worst choice
                textCol    = globalTextCol
                fontWeight = "normal"
                fontSize   = None
                for iVar in range(0, len(var)):
                    if iVar in top5index and labelBest:
                        if plottingLimit:
                            textCol = "limegreen"
                        else:
                            textCol = "lime"

                        fontWeight  = "black"
                        fontSize    = axBoxPointSize * 0.4 * 1.2
                    else:
                        textCol = globalTextCol
                        fontWeight = "normal"
                        fontSize   = axBoxPointSize * 0.4

                    payloadStr = ""
                    if plottingNP:
                        payloadStr = "%2.0f%%"%(var[iVar]) 
                    elif plottingSign or plottingRate:
                        payloadStr = "%.1f"%(var[iVar]) 
                    elif plottingLimit:
                        payloadStr = "%.2f"%(var[iVar])
                    else:
                        payloadStr = "%d"%(var[iVar])
                    ax.text(disc1s[iVar]+axRange/2e3, disc2s[iVar]-axRange/2e3, payloadStr, color = "midnightblue", fontsize = fontSize, fontweight = fontWeight, va = "center", ha = "center")
                    ax.text(disc1s[iVar],             disc2s[iVar],             payloadStr, color = textCol,        fontsize = fontSize, fontweight = fontWeight, va = "center", ha = "center")

            if not plottingRate and not plottingNP:
                fig.savefig(self.outputDir+"/%s_%s_vs_Disc1Disc2_%s%d_%s.pdf"%(kwargs["year"], variable, kwargs["model"], mass, self.channel), dpi = fig.dpi)
            else:
                fig.savefig(self.outputDir+"/%s_%s_vs_Disc1Disc2_%s_%s.pdf"%(kwargs["year"], variable, kwargs["model"], self.channel), dpi = fig.dpi)

        plt.close(fig)

    def plot_Var_vsMass(self, var, mass, colScales, vmin, vmax, doLog = False, variable = "", **kwargs):

        colMap = "plasma"
        labelPrefix = ""
        labelSuffix = ""
        if "Limit" in variable:
            colMap = "bwr"
            labelPrefix = "Expected "
            labelSuffix = r" on $\sigma_{\tilde{t}\bar{\tilde{t}}}$ [pb]"

        fig = plt.figure(figsize = (6, 5)) 
        fig.subplots_adjust(left = 0.13, bottom = 0.12, top = 0.95, right = 0.97)

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
        ax.set_ylabel(labelPrefix + variable + labelSuffix, fontsize = 16)
        ax.set_xlabel("Top Squark Mass [GeV]",              fontsize = 16)

        ax.tick_params(axis = "both", labelsize = 12)

        ax = self.addCMSlabel(ax, **kwargs)
        ax = self.addAuxLabel(ax, **kwargs)

        fig.savefig(self.outputDir+"/%s_%s_vs_Mass_%s_%s.pdf"%(kwargs["year"], variable, kwargs["model"], self.channel), dpi = fig.dpi)

        plt.close(fig)

    def plot_bestVar_vsMass(self, vares, colors, linestyles, linewidths, labels, vmin, vmax, doLog = False, variable = "", auxText = "", **kwargs):

        fig = plt.figure(figsize = (6, 5)) 
        fig.subplots_adjust(left = 0.13, bottom = 0.12, top = 0.95, right = 0.97)

        labelPrefix = ""
        labelSuffix = ""
        if   "Limit" in variable:
            labelPrefix = "Expected "
            labelSuffix = r" on $\sigma_{\tilde{t}\bar{\tilde{t}}}$ [pb]"
        elif "Significance" in variable:
            labelSuffix = r" [$\sigma$]"

        iMass = 0
        for iVar in range(0, len(vares)):
            if iVar == len(vares)-1:
                plt.plot(vares[iVar][:,0], vares[iVar][:,1], c = colors[iVar], marker = "o", linestyle = linestyles[iVar], linewidth = linewidths[iVar], label = labels[iVar])
            iMass += 1

        if   "Limit" in variable:
            if   "SYY" in kwargs["model"]:
                plt.plot(self.SUS19004limitsSYY[:,0], self.SUS19004limitsSYY[:,1], c = "silver", marker = "o", linestyle = ":", label = "SUS-19-004 Expected Limit (Semi-leptonic)")
            elif "RPV" in kwargs["model"]:
                plt.plot(self.SUS19004limitsRPV[:,0], self.SUS19004limitsRPV[:,1], c = "silver", marker = "o", linestyle = ":", label = "SUS-19-004 Expected Limit (Semi-leptonic)")
        elif "Sign" in variable:
            if   "SYY" in kwargs["model"]:
                plt.plot(self.SUS19004signsSYY[:,0], self.SUS19004signsSYY[:,1], c = "silver", marker = "o", linestyle = ":", label = "SUS-19-004 Expected Sensitivity (Semi-leptonic)")
            elif "RPV" in kwargs["model"]:
                plt.plot(self.SUS19004signsRPV[:,0], self.SUS19004signsRPV[:,1], c = "silver", marker = "o", linestyle = ":", label = "SUS-19-004 Expected Sensitivity (Semi-leptonic)")
           
        ax = plt.gca()
        ax.set_xlim(250, 1300)

        legendLoc = "upper right"
        if "Limit" in variable:
            if   "SYY" in kwargs["model"]:
                plt.ylim(0.5*np.min(self.SUS19004limitsSYY[:,1]), 2.0*vmax)
            elif "RPV" in kwargs["model"]:
                plt.ylim(0.5*np.min(self.SUS19004limitsRPV[:,1]), 1.5*vmax)
        else:
            ax.set_ylim(vmin, vmax)
            ax.set_yticks([i*2 for i in range(vmin, vmax/2 + 1) if i >= 0])
            ax.invert_yaxis()
            ax.axhline(y = 0.0, color = "black", linestyle = "-", linewidth = 1.0)
            legendLoc = "lower right"

        if doLog:
            ax.set_yscale("log")
        ax.set_ylabel(labelPrefix + variable + labelSuffix, fontsize = 16)
        ax.set_xlabel("Top Squark Mass [GeV]",              fontsize = 16)

        ax.tick_params(axis = "both", labelsize = 12)

        ax = self.addCMSlabel(ax, **kwargs)
        ax = self.addAuxLabel(ax, **kwargs)

        ax.legend(loc = legendLoc, bbox_to_anchor = (0, 0, 1, 0.95), numpoints = 1, frameon = False, fontsize = 10)

        fig.savefig(self.outputDir+"/%s_%s%s_vs_Mass_%s_%s.pdf"%(kwargs["year"], variable, auxText, kwargs["model"], self.channel), dpi = fig.dpi)

        plt.close(fig)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("usage: %prog [options]\n")
    parser.add_argument("--basedir",    dest="basedir",    required = True,                       help = "Path to output files"    )
    parser.add_argument("--outdir",     dest="outdir",     required = True,                       help = "Path to put output files")
    parser.add_argument("--approved",   dest="approved",   default  = False, action="store_true", help = "Is plot approved"        )
    parser.add_argument("--plotInputs", dest="plotInputs", default  = False, action="store_true", help = "Plot all inputs in card" )
    parser.add_argument("--channel",    dest="channel",    default  = "0l",                       help = "Which channels to plot"  )
    parser.add_argument("--datacards",  dest="datacards",  default  = "cards_scan",               help = "Folder with data cards"  )
    args = parser.parse_args()

    combineResults = args.basedir
    dataCardsPath  = args.basedir + "/" + args.datacards
    outPath        = args.outdir
    channel        = args.channel
    plotFitInputs  = args.plotInputs

    njets   = [str(iNjet) for iNjet in range(7, 13)]
    regions = ["A", "B", "C", "D"]
    if   channel == "0l":
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

        if "_90" in combineFitResultPath:
            continue

        # Split up each individual job folder to get edge vals, mass, etc
        chunks = combineFitResultPath.split("/")[-1].split("_")

        #if chunks[-1] != "MassExclusion" and chunks[-1] != "MaxSig":
        #    continue
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
        #else:
        #    if chunks[-1] == "MassExclusion":
        #        disc1 = "0.4"
        #        disc2 = "0.4"
        #    else:
        #        disc1 = "0.5"
        #        disc2 = "0.5"

        #    disc = chunks[-1]

        mass  = int(chunks[1])
        model = chunks[0]
        year  = chunks[2]

        dataCardPath = "%s/%s_%s_%d_pseudoDataS_%s_%s.txt"%(dataCardsPath, year, model, mass, channel, disc)

        theScraper.scrapeValues(combineFitResultPath, dataCardPath, year, model, mass, disc1, disc2, disc)

    theScraper.numpyFriendly()

    masses = theScraper.getParamVals(paramName = "mass")
    years  = theScraper.getParamVals(paramName = "year")
    models = theScraper.getParamVals(paramName = "model")

    # Determine granularity of grid scan for plotting purposes
    disc1s  = theScraper.getParamVals(paramName = "disc1")
    disc2s  = theScraper.getParamVals(paramName = "disc2")
    #spacing = min(disc1s[i+1]-disc1s[i] for i in range(len(disc1s)-1))
    spacing = 0.02

    xInnerMargin = 0.09 * ((max(disc1s) + spacing/2.0) - (min(disc1s) - spacing/2.0))
    xMin = min(disc1s) - xInnerMargin
    xMax = max(disc1s) + xInnerMargin

    yInnerMargin = 0.09 * ((max(disc2s) + spacing/2.0) - (min(disc2s) - spacing/2.0))
    yMin = min(disc2s) - yInnerMargin
    yMax = max(disc2s) + yInnerMargin

    params = theScraper.getParamNames()

    thePlotter = Plotter(outPath, args.approved, channel)

    # Adjust log and linear scales for axis ranges
    # depending on the channel
    limitScale = 1.3
    signScaleMax = 20 
    if channel != "1l":
        limitScale = 0.9 
        signScaleMax = 7

    obsSelection = []
    for region in regions:
        if region == "A":
            continue
        for njet in njets:
            obsSelection.append("(Nobs_%s_Njets%s>=3.0)"%(region,njet))
    obsSelection = "&".join(obsSelection)
    obsSelection = "(mass!=2)"

    # Best choices at 100% xsection
    bestLimitFullXS = {"RPV"        : {"0l" : (0.74,0.80),
                                       "1l" : (0.80,0.72),
                                       "2l" : (0.50,0.50)},
                       "StealthSYY" : {"0l" : (0.54,0.56),
                                       "1l" : (0.68,0.82),
                                       "2l" : (0.70,0.84)}
    }

    bestSignFullXS = {"RPV"        : {"0l": (0.52,0.54),
                                      "1l": (0.84,0.42),
                                      "2l": (0.70,0.50)},
                      "StealthSYY" : {"0l": (0.76,0.70),
                                      "1l": (0.44,0.42),
                                      "2l": (0.64,0.42)}
    }
    
    for year in years:
        for model in models:

            # Plot all fit inputs from data card (takes a bit longer to run...)
            if plotFitInputs:
                for param in params:

                    # By construction, inputs all have "_" in their names
                    if any(x in param for x in var_list):
                        pass
                    elif "_" not in param or "Corr" not in param:
                        continue

                    disc1s, disc2s, paramVals = theScraper.getByParam(paramName = "disc", var = param, selection = obsSelection, mass = masses[0], model = model, year = year)

                    thePlotter.plot_Var_vsDisc1Disc2(paramVals, disc1s, disc2s, binWidth = spacing, xMin = xMin, xMax = xMax, yMin = yMin, yMax = yMax, vmin = 0.0, vmax = 30.0, labelVals = True, variable = param, model = model, year = year)

            colScales = []

            # Storing all choices of bin edges for all mass points for summary plot
            allMasses_sign = []; allMasses_lim = []
            allSigns       = []; allExpLims    = []

            # Retain absolute best limits and significances for a given mass point
            bestSigns      = []; bestLimits    = []

            # Store limit and significance for particular choice 
            # of bin edges for all mass points
            signsByBestMassSign  = []; signsByBestMassLimit  = []
            limitsByBestMassSign = []; limitsByBestMassLimit = []
            labelsByBestMassSign = []; labelsByBestMassLimit = []
            for mass in masses:

                #disc1s, disc2s, signDiffs = theScraper.getByParam(paramName = "disc", var = "signDiff", selection = "(disc1>0.1)&(disc2>0.1)&(signDiff<100000000000.0)", mass = mass, model = model, year = year)
                #thePlotter.plot_Var_vsDisc1Disc2(signDiffs, disc1s, disc2s, binWidth = spacing, vmin = 0.0, vmax = max(signDiffs), mass = mass, labelVals = True, labelBest = False, variable = "SignificanceDiff", model = model, year = year)

                # Plot significances as function of bin edges
                disc1s, disc2s, signs = theScraper.getByParam(paramName = "disc", var = "sign_nonasimov", selection = "(disc1>-0.1)&(disc2>-0.1)&(sign>0.0)&(signDiff<10000000.0)&%s"%(obsSelection), mass = mass, model = model, year = year)

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
                maxDisc1 = 0.5
                maxDisc2 = 0.5

                massesByBestSign, signsByBestSign  = theScraper.getByParam(paramName = "mass", var = "sign_nonasimov",     selection = "(disc1==%f)&(disc2==%f)"%(maxDisc1, maxDisc2), model = model, year = year)
                signsByBestMassSign.append(np.vstack((massesByBestSign, signsByBestSign)).T)

                massesByBestSign, limitsByBestSign = theScraper.getByParam(paramName = "mass", var = "expLimit", selection = "(disc1==%f)&(disc2==%f)"%(maxDisc1, maxDisc2), model = model, year = year)
                limitsByBestMassSign.append(np.vstack((massesByBestSign, limitsByBestSign)).T)

                labelsByBestMassSign.append(r"Sensitivity Optimized")
                #labelsByBestMassSign.append(r"Sign. Opt. for $m_{\tilde{t}}=%d$ GeV | (%.2f, %.2f)"%(mass, maxDisc1, maxDisc2))

                thePlotter.plot_Var_vsDisc1Disc2(signs, disc1s, disc2s, binWidth = spacing, xMin = xMin, xMax = xMax, yMin = yMin, yMax = yMax, vmin = 0.0, vmax = 18, mass = mass, labelVals = True, labelBest = True, variable = "Significance", model = model, year = year)

                # Plot limits as function of bin edges
                disc1s, disc2s, expLims = theScraper.getByParam(paramName = "disc", var = "expLimit", selection = "(disc1>-0.1)&(disc2>-0.1)&(expLimit>0.0)&(healthyLimit!=3)&%s"%(obsSelection), mass = mass, model = model, year = year)

                allMasses_lim.append([mass]*len(disc1s))
                allExpLims.append(expLims)

                minLimit = -999.0; minDisc1 = -999.0; minDisc2 = -999.0
                try:
                    minLimit = np.min(expLims)
                    minDisc1 = disc1s[np.argmin(expLims)]
                    minDisc2 = disc2s[np.argmin(expLims)]
                except:
                    pass
                bestLimits.append([mass, minDisc1, minDisc2, minLimit])
                maxDisc1 = 0.4
                maxDisc2 = 0.4

                massesByBestLimit, signsByBestLimit  = theScraper.getByParam(paramName = "mass", var = "sign_nonasimov",     selection = "(disc1==%f)&(disc2==%f)"%(minDisc1, minDisc2), model = model, year = year)
                signsByBestMassLimit.append(np.vstack((massesByBestLimit, signsByBestLimit)).T)

                massesByBestLimit, limitsByBestLimit = theScraper.getByParam(paramName = "mass", var = "expLimit", selection = "(disc1==%f)&(disc2==%f)"%(minDisc1, minDisc2), model = model, year = year)
                limitsByBestMassLimit.append(np.vstack((massesByBestLimit, limitsByBestLimit)).T)

                labelsByBestMassLimit.append(r"Limit Optimized")
                #labelsByBestMassLimit.append(r"Limit Opt. for $m_{\tilde{t}}=%d$ GeV | (%.2f, %.2f)"%(mass, minDisc1, minDisc2))

                colScales.append(stopPair_xsec[mass])

                thePlotter.plot_Var_vsDisc1Disc2(expLims, disc1s, disc2s, binWidth = spacing, xMin = xMin, xMax = xMax, yMin = yMin, yMax = yMax, vmin = stopPair_xsec[mass]*10**(-limitScale), vmax = stopPair_xsec[mass]*10**limitScale, mass = mass, labelVals = True, labelBest = True, doLog = True, variable = "Limit", model = model, year = year)

                # Plot "boolean" if limit fit had problems or not
                disc1s, disc2s, healthy = theScraper.getByParam(paramName = "disc", var = "healthyLimit", selection = "(disc1>0.1)&(disc2>0.1)", mass = mass, model = model, year = year)
                thePlotter.plot_Var_vsDisc1Disc2(healthy, disc1s, disc2s, binWidth = spacing, xMin = xMin, xMax = xMax, yMin = yMin, yMax = yMax, vmin = 0.0, vmax = max(healthy), mass = mass, labelVals = True, labelBest = False, variable = "HealthyLim", model = model, year = year)

            bestSigns  = np.array(bestSigns)
            bestLimits = np.array(bestLimits)

            bestOfTheBestBlues  = ["#c6dbef", "#6baed6", "#2171b5", "#253494"]
            bestOfTheBestGreens = ["#c7e9c0", "#74c476", "#238b45", "#006837"]
            bestOfTheBestLines  = ["-", "-", "-", "-"]
            bestOfTheBestWidths = [0.75, 1.5, 2.25, 2.75]
            thePlotter.plot_bestVar_vsMass(signsByBestMassSign,   colors = bestOfTheBestBlues,  linestyles = bestOfTheBestLines, linewidths = bestOfTheBestWidths, labels = labelsByBestMassSign,  vmin = -3,              vmax = 18,                         variable = "Significance", auxText = "ByBestSign",  model = model, year = year)
            thePlotter.plot_bestVar_vsMass(limitsByBestMassSign,  colors = bestOfTheBestGreens, linestyles = bestOfTheBestLines, linewidths = bestOfTheBestWidths, labels = labelsByBestMassSign,  vmin = 10**(-limitScale), vmax = 10**limitScale, doLog = True, variable = "Limit",        auxText = "ByBestSign",  model = model, year = year)
            thePlotter.plot_bestVar_vsMass(signsByBestMassLimit,  colors = bestOfTheBestBlues,  linestyles = bestOfTheBestLines, linewidths = bestOfTheBestWidths, labels = labelsByBestMassLimit, vmin = -3,              vmax = 18,                         variable = "Significance", auxText = "ByBestLimit", model = model, year = year)
            thePlotter.plot_bestVar_vsMass(limitsByBestMassLimit, colors = bestOfTheBestGreens, linestyles = bestOfTheBestLines, linewidths = bestOfTheBestWidths, labels = labelsByBestMassLimit, vmin = 10**(-limitScale), vmax = 10**limitScale, doLog = True, variable = "Limit",        auxText = "ByBestLimit", model = model, year = year)

            # Plot all bin edge choices for all mass points together for significance and limits
            thePlotter.plot_Var_vsMass(allSigns,   allMasses_sign, colScales = [1.0]*len(allSigns), vmin = -0.25,             vmax = signScaleMax,                 variable = "Significances", model = model, year = year)
            thePlotter.plot_Var_vsMass(allExpLims, allMasses_lim,  colScales = colScales,           vmin = 10**(-limitScale), vmax = 10**limitScale, doLog = True, variable = "Limits",        model = model, year = year)

            thePlotter.plot_Var_vsDisc1Disc2(bestSigns[:,-1],  bestSigns[:,1],  bestSigns[:,2],  binWidth = spacing, vmin = 0.0,    vmax = signScaleMax, mass = bestSigns[:,0],                variable = "Significance", model = model, year = year)
            thePlotter.plot_Var_vsDisc1Disc2(bestLimits[:,-1], bestLimits[:,1], bestLimits[:,2], binWidth = spacing, vmin = 0.5e-2, vmax = 0.5e1,        mass = bestLimits[:,0], doLog = True, variable = "Limit",        model = model, year = year)
