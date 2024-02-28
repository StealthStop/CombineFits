import os
import argparse

import numpy as np

class SystTabulator():

    def __init__(self, dataCardPath, outPath, channel, model, mass, year):
    
        self.dataCardPath = dataCardPath
        self.outPath      = outPath
        self.model        = model
        self.mass         = mass
        self.year         = year
        self.channel      = channel

        self.processes = ["TT", "Minor", model]

        self.npEncoding = ["pdf", "scl", "fsr", "isr", "pu", "", "CorrectedDataClosure", "CC", "QCD_TF", "", "JEC", "JER", "btg", "ttg", "lep", "jet", "prf", "", "lumi", "TTX", "Other"]
        self.npDecoding = [ "PDF", "($\mu_\mathrm{R}$, $\mu_\mathrm{F}$) scales", "FSR", "ISR", "Pileup", "", "Non-Closure (Post-Corr.)", "Closure Corr. Stat. Unc.", "QCD TF", "", "JES", "JER", "b tagging", "Top tagging", "Lepton ID/trigger", "Jet trigger", "Prefiring", "", "Integrated Luminosity", "Theoretical Cross Section", "Theoretical Cross Section"]

    # Upon specifying mass point, year, model, channel, and disc values for a particular fit
    # Parse the corresponding data card to get systematics and rates
    def scrapeValues(self):
        
        # Try the datacard first, if not there, then do not worry about anything else
        dataCardFile = None
        self.dataCardInfo = {}
        try:
            dataCardFile  = open(self.dataCardPath, "r")
            dataCardLines = dataCardFile.readlines()
            dataCardFile.close()
        except:
            print("Could not open data card textfile: \"%s\""%(dataCardPath))
            return
    
        if dataCardFile != None:
            obsCheckpoint = False
            savedLines = {}
            for line in dataCardLines:
    
                # Any empty lines is not used
                if line[0] == " ":
                    continue 
    
                # One obs counts for each analysis bin
                if "observation" in line:
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
    
                # Each systematic is on own line an includes "np_" in its name
                # Location of values aligns where systematic is applicable for process + analysis bin
                if "np_" in line or "lumi" in line or ("TT_UL" in line and "param" in line):
                    auxStr = ""
                    if "lumi" in line or ("TT_UL" in line and "param" in line):
                        auxStr = "np_"
                    savedLines[auxStr + line.replace("\t", " ").split(" ")[0]] = list(filter(None, line.replace("--", "-999.0").replace("\t", " ").rstrip("\n").split(" ")))[2:]
                    continue
            
            nps = [np for np in savedLines.keys() if "np_" in np]
            for iBin in range(0, len(savedLines["bin"])):
    
                process = savedLines["process"][iBin].partition("_2t6j_")[0]
                binName = savedLines["bin"][iBin]
                region  = binName.split("_")[1][0]
                njets   = binName.split("_")[1][1:]
    
                for np in nps:

                    npName = np.split("np_")[1].replace(region + njets, "").partition("_%s"%(self.channel))[0]

                    npVals = None
                    if "TT_UL" in np and iBin == 0:
                        npName = "CC"
                        npVals = [100.0 * eval(savedLines[np][1])/eval(savedLines[np][0])]
                    elif "TT_UL" in np and iBin != 0:
                        continue
    
                    if savedLines[np][iBin] == "-999.0": continue

                    hardcodeProcess = process
                    if npName == "QCD_TF":
                        hardcodeProcess = "QCD"

                    # For all systematics, convert to a percent from 1 e.g. 1.1 or 0.9 ==> 10%
                    # And for any up/down systematic that is reported with "/", take the largest
                    # E.g. 1.02/0.8 ==> 20%, rather than 2%
                    npVals = [100.0 * round(abs(1.0-eval(val)),2) for val in savedLines[np][iBin].split("/") if val != "10.000"]
            
                    if npName not in self.dataCardInfo:
                        self.dataCardInfo[npName] = {}
                    if hardcodeProcess not in self.dataCardInfo[npName]:
                        self.dataCardInfo[npName][hardcodeProcess] = []

                    self.dataCardInfo[npName][hardcodeProcess] += npVals

                    if hardcodeProcess == "TTX" or hardcodeProcess == "Other" or hardcodeProcess == "QCD":
                        if "Minor" not in self.dataCardInfo[npName]:
                            self.dataCardInfo[npName]["Minor"] = []

                        self.dataCardInfo[npName]["Minor"] += npVals

    def writeHeader(self):

        header = []
        header.append("\\begin{scotch}{l r r r}\n")
        header.append("\multirow{2}{*}       & \\ttbar     & Minor      & %s    \\\\\n"%(self.model))
        header.append("Source of uncertainty & background & background & signal \\\\\n")
        header.append("\hline\n")

        return header

    def writeBody(self):

        body = []

        for npEncode, npDecode in zip(self.npEncoding, self.npDecoding):

            if npEncode == "":
                body.append("\n")
                continue

            if npEncode not in self.dataCardInfo:
                continue

            if npEncode == "Other": continue

            npDict = self.dataCardInfo[npEncode]
            line = "%s"%(npDecode).ljust(45)
            line += " & "

            procChunks = []
            for process in self.processes:

                if process not in npDict or npDict[process][0] == -999.0:
                    procChunks.append("\NA".ljust(12))
                else:
                    maximum = min(100, max(npDict[process]))
                    minimum = min(npDict[process])
                    percentiles = np.percentile(npDict[process], [16, 84])
    
                    if "lumi" in npEncode:
                        procChunks.append(("%.1f"%(maximum)).ljust(12))
                    elif  "TTX" in npEncode or "Other" in npEncode:
                        procChunks.append(("%d"%(maximum)).ljust(12))
                    elif "Closure" in npEncode:
                        procChunks.append(("%d--%d"%(minimum, maximum)).ljust(12))
                    else:
                        procChunks.append(("%d--%d (%d)"%(int(percentiles[0]), int(percentiles[1]), maximum)).ljust(12))
   
            line += " & ".join(procChunks)
            line += " \\\\ \n"

            body.append(line)

        return body

    def writeFooter(self):

        footer = []
        footer.append("\end{scotch}\n")
        footer.append("\label{tab:systematics_%s_%s}\n"%(self.model,self.channel))

        return footer

    def writeTable(self):
    
        table = open(self.outPath + "/%s_%s%s_%s.tex"%(self.year, self.model, self.mass, self.channel), "w")

        for line in self.writeHeader():
            table.write(line)

        for line in self.writeBody():
            table.write(line)

        for line in self.writeFooter():
            table.write(line)

        table.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser("usage: %prog [options]\n")
    parser.add_argument("--outPath",        dest="outPath",        required = True,     help = "Path to put output files")
    parser.add_argument("--dataCardsPath",  dest="dataCardsPath",  required = True,     help = "Plot all inputs in card" )
    parser.add_argument("--channel",        dest="channel",        default  = "0l",     help = "Which channels to plot"  )
    parser.add_argument("--model",          dest="model",          default  = "RPV",    help = "Which models to plot"  )
    parser.add_argument("--mass",           dest="mass",           default  = "550",    help = "Which mass to plot"  )
    parser.add_argument("--year",           dest="year",           default  = "Run2UL", help = "Which year to table"  )

    args = parser.parse_args()

    dataCardsPath  = args.dataCardsPath
    outPath        = args.outPath
    channel        = args.channel
    model          = args.model
    mass           = args.mass
    year           = args.year

    njets   = [str(iNjet) for iNjet in range(7, 13)]
    regions = ["A", "B", "C", "D"]
    if   channel == "0l":
        njets = [str(iNjet) for iNjet in range(8, 14)]
    elif channel == "2l":
        njets = [str(iNjet) for iNjet in range(6, 12)]

    if not os.path.exists(outPath):
        os.makedirs(outPath)

    dataCardPath = "%s/%s_%s_%s_Data_%s.txt"%(dataCardsPath, year, model, mass, channel)

    tabby = SystTabulator(dataCardPath, outPath, channel, model, mass, year)

    tabby.scrapeValues()

    tabby.writeTable()
