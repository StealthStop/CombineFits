import ROOT
import math
import copy

# path          : Full path to the input ROOT files containing Njets histograms for event counts and systematic values
# observed      : Dictionary loaded from cardConfig containing info about ROOT files, histograms etc.
# outpath       : Location to save datacards to
# systematics   : Dictionary loaded from cardConfig to specify info about ROOT files and histograms
# lumiSyst      : Flat systematic uncertainty applied to all bins in datacard
# dataType      : Either pseudoData, pseudoDataS, or Data
# channel       : Either "0l", "1l", or "combo"
# year          : Which year to run on
# model         : Which signal model "RPV" or "SYY" to use in the fit
# mass          : Which signal mass point to use in the fit
# injectedModel : Which signal model "RPV" or "SYY" to inject into "pseudoDataS"
# injectedMass  : Which signal mass point to inject into "pseudoDataS" 
# RUN2SF        : To scale a single year to full Run2 luminosity in terms of number of events 
# NoMCcorr      : Disable MC closure correction from being applied to ABCD calculation (setting factor to 1.0)
# min_nj        : Lowest Njet bin to use in datacard 
# max_nj        : Highest Njet bin to use in datacard
# njetStart     : Starting Njet bin for Njets histograms
# njetEnd       : Ending Njet bin for Njets histograms
# njets         : Number of Njet bins in each A, B, C, D region

class dataCardMaker:

    def __init__(self, path, observed, outpath, systematics, dataType, channel, year, Run2, NoMCcorr, min_nj, max_nj, model, mass, injectedModel, injectedMass):
     
        self.path          = path
        self.observed      = observed
        self.outpath       = outpath
        self.systematics   = systematics
        self.lumiSyst      = 1.05
        self.dataType      = dataType
        self.channel        = channel
        self.year          = year
        self.model         = model
        self.mass          = mass
        self.injectedModel = injectedModel
        self.injectedMass  = injectedMass

        self.RUN2SF = 1.0
        if Run2:
            self.RUN2SF = 138.0 / 35.9 

        self.NoMCcorr = NoMCcorr

        self.min_nj    = min_nj
        self.max_nj    = max_nj
        self.njetStart = None
        self.njetEnd   = None
        self.njets     = None

        self.fillBinValues()
        self.writeCards()

    # --------------------------------------------------------------------
    # Read bin values (event counts or systematic values) from a histogram
    # in the corresponding histogram
    # --------------------------------------------------------------------
    def calcBinValues(self, tfile, hdict, **kwargs):
        binValues = []; binErrors =[]; binNames = []

        # The histogram name will most likely contain the $CHANNEL keyword
        # and should be replaced with respective channel string e.g. 1l or 0l
        histName = hdict["hist"].replace("$CHANNEL", self.channel)
        
        # If loading a systematic, replace $SYST keyword with actual name e.g. TT_JECup
        # that is passed in the kwargs
        if "extra" in kwargs:
            histName = histName.replace("$SYST", kwargs["extra"])

        h = tfile.Get(histName)

        nbins = h.GetNbinsX()
        self.njetStart = hdict["start"] 
        self.njetEnd = hdict["end"]
        self.njets = self.njetEnd - self.njetStart + 1

        # Region labels e.g. "ABCD" are taken from last four characters of histogram name
        # See cardConfig for format of histogram name
        regions = hdict["hist"][-4::]
        mask = self.getBinMask()

        # Scale factor only applies to event counts, not systematic values or corrections
        SF = 1.0
        if hdict["type"] != "sys" and hdict["type"] != "corr":
            SF = self.RUN2SF

        for bin in range(0, nbins):
            val = SF * h.GetBinContent(bin+1)
            err = SF * h.GetBinError(bin+1)
            reg = regions[int(bin/self.njets)]

            # Round all event count values to whole number (do not round systematic values of course)
            if hdict["type"] != "sys" and hdict["type"] != "corr":
                roundedVal = round(val)
                # Apply a floor to weighted event counts for any bkg or sig process
                if roundedVal < 0.1:
                    binValues.append(0.1)
                else:
                    binValues.append(roundedVal)
            else:
                binValues.append(val)
           
            binErrors.append(err)
            binNames.append(reg+str(self.njetStart + bin % self.njets))

        return binValues, binErrors, binNames, nbins

    # --------------------------------------------------------------------------------------
    # Extract events counts for background and signal processes as well as systematic values
    # --------------------------------------------------------------------------------------
    def fillBinValues(self):

        # ------------------------------------------------------------
        # Loop over processes in the observed dictionary
        # and read their corresponding histogram bin entries
        # into a dictionary. Do this also for loading the systematics.
        # ------------------------------------------------------------
        for proc in self.observed.keys():

            # Several keywords for $CHANNEL, $YEAR, etc. can be present in the 
            # ROOT file name and need to be replaced with actual values "1l", "2016", etc. 
            # For the special case of loading signal, _two_ files are loaded:
            # One file for signal component used in fit and other injected into pseudoData
            path    = self.observed[proc]["path"].replace("$MASS", self.mass) \
                                                 .replace("$MODEL", self.model) \
                                                 .replace("$CHANNEL", self.channel) \
                                                 .replace("$YEAR", self.year)
            pathInj = self.observed[proc]["path"].replace("$MASS", self.injectedMass) \
                                                 .replace("$MODEL", self.injectedModel) \
                                                 .replace("$CHANNEL", self.channel) \
                                                 .replace("$YEAR", self.year)

            tfile    = ROOT.TFile.Open(self.path+"/"+path)
            tfileInj = ROOT.TFile.Open(self.path+"/"+pathInj)

            newproc    = proc.replace("$MODEL", self.model) \
                             .replace("$MASS", self.mass)
            newprocInj = "INJECT_" + proc.replace("$MODEL", self.injectedModel) \
                                         .replace("$MASS", self.injectedMass)

            # Replace the "$MODEL_$MASS" key with actual model and mass key
            # Add "INJECT" prefix for key pointing to signal being injected
            if newproc != proc:
                self.observed[newproc]    = copy.copy(self.observed[proc])
                self.observed[newprocInj] = copy.copy(self.observed[proc])

                # Specify that _this_ "inj" signal is being injected
                # But, we do not fit with this signal
                self.observed[newprocInj]["inj"] = True
                self.observed[newprocInj]["fit"] = False

                self.observed[newprocInj]["binValues"], self.observed[newprocInj]["binErrors"], self.observed[newprocInj]["binNames"], self.obsNbins = self.calcBinValues(tfileInj, self.observed[newprocInj])

                # Remove template "$MODEL_$MASS" key and subdictionary from observed
                # as they have been replaced e.g. "RPV_550" and "INJECTED_RPV_400"
                del self.observed[proc]

            self.observed[newproc]["binValues"], self.observed[newproc]["binErrors"], self.observed[newproc]["binNames"], self.obsNbins = self.calcBinValues(tfile, self.observed[newproc])

        # Loop over the systematics dictionary and load in Njets histograms for systs and MC correction factor
        for sy in self.systematics.keys():
            tfile = ROOT.TFile.Open(self.path+"/"+ self.systematics[sy]["path"].replace("$CHANNEL", self.channel) \
                                                                               .replace("$YEAR", self.year))

            self.systematics[sy]["binValues"], self.systematics[sy]["binErrors"], self.systematics[sy]["binNames"], self.sysNbins = self.calcBinValues(tfile, self.systematics[sy], extra=sy)

        # Depending on if running for pseudoData(S) or Data
        # make the values for the "observed" line in the datacard
        # i.e. add all bkgd processes for "pseudoData" or just take
        # the actual data for "Data"
        self.observedPerBin = []
        self.closureUncertainties = []
        self.closureUncertaintiesUnc = []

        # PSEUDODATA
        if self.dataType == "pseudoData":
            for n in range(self.obsNbins):
                obs = 0

                # Check the type to _not_ inject signal into the pseudoData (no S !)
                for ob in self.observed.keys():
                    if self.observed[ob]["type"] == "bkg" and self.observed[ob]["inj"]:
                        obs += self.observed[ob]["binValues"][n]
                self.observedPerBin.append(obs)

        # PSEUDODATAS
        elif self.dataType == "pseudoDataS":
            for n in range(self.obsNbins):
                obs = 0
                for proc in self.observed.keys():
                    if self.observed[proc]["type"] == "sig" and self.observed[proc]["inj"]:
                        obs += self.observed[proc]["binValues"][n]
                    elif self.observed[proc]["type"] == "bkg" and self.observed[proc]["inj"]:
                        obs += self.observed[proc]["binValues"][n]
                self.observedPerBin.append(obs)

        # DATA
        elif self.dataType == "Data":
            for n in range(self.obsNbins):
                self.observedPerBin.append(self.observed["Data"]["binValues"][n])

    # ---------------------------------
    # For writing out txt file datacard
    # ---------------------------------
    def writeCards(self):
        # Get a mask for determining which bins to include in datacard
        # (based on minNjet and maxNjet specified on command line)
        mask = self.getBinMask()
        masks = 0
        for i in mask:
            masks -= i - 1
        with open(self.outpath, "w") as file:

            jmax = 0
            for proc, info in self.observed.items():
                if info["fit"] and info["type"] == "bkg":
                    jmax += 1

            if self.dataType == "pseudoDataS": 
                file.write("# INJECTING SIGNAL : {0}_{1}\n".format(self.injectedModel, self.injectedMass))
                file.write("# FITTING SIGNAL   : {0}_{1}\n\n\n".format(self.model, self.mass))

            # Write datacard header specifying number of processes, bins, systematics
            file.write("imax {}  \n".format(self.obsNbins - masks))
            file.write("jmax {}  \n".format(jmax))
            file.write("kmax * \n")
            file.write("\n------------------------")
            bin_str = "{} ".format("\nbin")
            tempproc = self.observed.keys()[0]

            # Write out FAKE shapes lines
            shape_str = ""
            for reg in ["A", "B", "C", "D"]:
                for nj in range(self.min_nj, self.max_nj+1):
                    ch = "Y{}_{}{}_{}".format(self.year[-2:],reg,nj,self.channel)
                    shape_str += "\nshapes * {} FAKE".format(ch)
            file.write(shape_str)
            file.write("\n------------------------")

            # Write line for bin labels
            for bin in range(self.obsNbins):
                if not mask[bin]:
                    continue
                temp_str = "Y{}_{}_{} ".format(self.year[-2:],self.observed[tempproc]["binNames"][bin],self.channel)
                bin_str += "{} ".format(temp_str)
            file.write(bin_str)

            # Write line for total observed event counts in each bin
            obs_str = "{} ".format("\nobservation")
            for obs in range(self.obsNbins):
                if not mask[obs]:
                    continue
                obs_str += "{} ".format(round(self.observedPerBin[obs]))
            file.write(obs_str)
            file.write("\n--------------------------")

            pbin_str = "{} ".format("\nbin")
            process1_str = "{} ".format("\nprocess")
            process2_str = "{} ".format("\nprocess")
            rate_str = "{} ".format("\nrate")
            for bin in range(self.obsNbins):
                if not mask[bin]:
                    continue

                for proc in self.observed.keys():

                    # Exclude any processes not designated for fit
                    if not self.observed[proc]["fit"]:
                        continue

                    temp_str = "Y{}_{}_{} ".format(self.year[-2:],self.observed[tempproc]["binNames"][bin],self.channel)
                    pbin_str += "{} ".format(temp_str)
                    process1_str += "{} ".format(proc)

                    if self.observed[proc]["type"] == "sig":
                        process2_str += "{} ".format(self.observed[proc]["processID"])
                        if float(self.observed[proc]["binValues"][bin]) > 0.1:
                            rate_str += "{} ".format(self.observed[proc]["binValues"][bin])
                        else:
                            rate_str += "{} ".format(0.1)

                    else:
                        process2_str += "{} ".format(self.observed[proc]["processID"])

                        # For TT process, put the processID instead of the actual event counts
                        # as TT is calculated via the ABCD method
                        if proc == "Data" or proc == "TT":
                            rate_str += "{} ".format(self.observed[proc]["processID"])
                        else:
                            rate_str += "{} ".format(self.observed[proc]["binValues"][bin])

            file.write(pbin_str)
            file.write(process1_str)
            file.write(process2_str)
            file.write(rate_str)
            process2_str = "{} ".format("\nprocess")
            file.write("\n--------------------------")

            # Write out 5% lumi systematic for all processes and bins
            lumi_str = "{0:<8}".format("\nlumi")
            lumi_str += "{0:<7}".format("lnN")
            for bin in range(self.obsNbins):
                if not mask[bin]:
                    continue
                for proc in range(len(self.observed.keys())):
                    lumi_str += "{} ".format(self.lumiSyst)
            file.write(lumi_str)

            # ---------------------------------------------------------
            # Add 20% normalization systematic on signal and background
            # ---------------------------------------------------------
            for process1 in self.observed.keys():

                # Only put systematic for component being used in the fit
                if (self.observed[process1]["type"] != "sig" and self.observed[process1]["type"] != "bkg") or not self.observed[process1]["fit"]:
                    continue

                process_str = "{} ".format("\nnp_"+process1)
                process_str += "{0:<7}".format("lnN")
                for bin in range(self.obsNbins):
                    if not mask[bin]:
                        continue
                    for process2 in self.observed.keys():

                        # Again, skip any process that is not included in the fit
                        if not self.observed[process2]["fit"]:
                            continue
                        if process1 == process2:
                            process_str += "{} ".format(self.observed[process1]["sys"])
                        else:
                            process_str += "{} ".format("--")
                file.write(process_str)

            # ---------------------------------------------------------
            # Add in a line to datacard for each independent systematic
            # ---------------------------------------------------------
            for sys in self.systematics.keys():
            
                # To skip MC correction factor (added in a different spot in datacard)
                if self.systematics[sys]["type"] != "sys":
                    continue

                sys_str = "{0:<8}".format("\n"+"np_"+sys + "_" + self.channel + '\t')
                sys_str += "{0:<7}".format(self.systematics[sys]["distr"])
                for bin in range(self.obsNbins):
                    if not mask[bin]:
                        continue

                    for proc in self.observed.keys():
                        if not self.observed[proc]["fit"]:
                            continue
                        if bin >= self.sysNbins:
                            sys_str += "{} ".format("--")
                            continue
                       
                        if proc == self.systematics[sys]["proc"]:
                            sys_str += "{:.3f} ".format(self.systematics[sys]["binValues"][bin])
                        else:
                            sys_str += "{} ".format("--")
                file.write(sys_str)
                    
            params = ["alpha", "beta", "gamma", "delta"]
            file.write("\n")
            bkgd = None
            if self.dataType == "Data":
                bkgd = "Data"
            elif "pseudo" in self.dataType:
                bkgd = "TT"

            for abin in range(self.min_nj - self.njetStart, self.max_nj - self.njets):
                file.write("\n")
                for ibin in range(0, len(self.observedPerBin), self.njets):
                    if not mask[abin+ibin]:
                        continue
                    rate = self.observedPerBin[abin+ibin]
                    for proc in self.observed.keys():
                        if proc != bkgd and self.observed[proc]["type"] != "sig":
                            rate -= self.observed[proc]["binValues"][abin+ibin]
                    if ibin == 0:

                        if self.NoMCcorr:
                            # Hard-coded MC correction factor to 1.0 (turning off the correction in ABCD calculation)
                            file.write("{0}{1}_{4:<12} rateParam Y{5}_{2}_{4} {3} (@0*@1/@2*{6}) beta{1}_{4},gamma{1}_{4},delta{1}_{4}\n".format(params[int(ibin/self.njets)],self.observed[bkgd]["binNames"][ibin+abin][1:],self.observed[bkgd]["binNames"][ibin+abin],bkgd,self.channel,self.year[-2:], 1.0))
                        else:
                            # Includes actual MC Correction
                            file.write("{0}{1}_{4:<12} rateParam Y{5}_{2}_{4} {3} (@0*@1/@2*{6}) beta{1}_{4},gamma{1}_{4},delta{1}_{4}\n".format(params[int(ibin/self.njets)],self.observed[bkgd]["binNames"][ibin+abin][1:],self.observed[bkgd]["binNames"][ibin+abin],bkgd,self.channel,self.year[-2:], round(self.systematics["MCcorrection"]["binValues"][abin],4)))

                    else: 
                        file.write("{0}{1}_{6:<12} rateParam Y{7}_{2}_{6} {3} {4:<12} {5}\n".format(params[int(ibin/self.njets)],self.observed[bkgd]["binNames"][ibin+abin][1:],self.observed[bkgd]["binNames"][ibin+abin],bkgd,rate, "[0,{}]".format(10*rate),self.channel,self.year[-2:])) 

    # ----------------------------------------------------------------
    # Make a bin mask based on Njets range specified on command line
    # and histogram absolute Njets bounds specified in the card config
    # ----------------------------------------------------------------
    def getBinMask(self):
        mask = []
        for k in range(4):
            for i in range(self.njetStart, self.njetEnd+1):
                if i < self.min_nj or i > self.max_nj:
                    mask.append(0)
                else:
                    mask.append(1)

        return mask
