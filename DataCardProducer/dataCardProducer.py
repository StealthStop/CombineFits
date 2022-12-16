import ROOT
import math
import copy

# path          : Full path to the input ROOT files containing Njets histograms for event counts and systematic values
# observed      : Dictionary loaded from cardConfig containing info about ROOT files, histograms etc.
# outpath       : Location to save datacards to
# systematics   : Dictionary loaded from cardConfig to specify info about ROOT files and histograms
# lumiSyst      : Flat systematic uncertainty applied to all bins in datacard
# dataType      : Either pseudoData, pseudoDataS, or Data
# channel       : Either "0l", "1l", "2l" or "combo"
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

    def __init__(self, path, observed, outpath, systematics, dataType, channel, year, NoMCcorr, min_nj, max_nj, model, mass, injectedModel, injectedMass):
     
        self.path           = path
        self.observed       = observed
        self.outpath        = outpath
        self.systematics    = systematics
        self.lumiSyst       = 1.016
        self.dataType       = dataType
        self.channel        = channel
        self.year           = year
        self.model          = model
        self.models         = "SYY" if "SYY" in model else "RPV"
        self.mass           = mass
        self.injectedModel  = injectedModel
        self.injectedModels = "SYY" if "SYY" in model else "RPV"
        self.injectedMass   = injectedMass
        self.NoMCcorr       = NoMCcorr
        self.min_nj         = min_nj
        self.max_nj         = max_nj

        self.RUN2SF = 1.0
        
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
        binValues = []; binErrors =[]; binNames = []; binWeights = [];

        # The histogram name will most likely contain the $CHANNEL keyword
        # and should be replaced with respective channel string e.g. 1l or 0l
        histName = hdict["hist"].replace("$CHANNEL", self.channel) \
                                .replace("$YEAR",    self.year) \
                                .replace("$MODELS",   self.models)
        
        # If loading a systematic, replace $SYST keyword with actual name e.g. TT_JECup
        # that is passed in the kwargs
        if "extra" in kwargs:
            histName = histName.replace("$SYST", kwargs["extra"])

        h = tfile.Get(histName)

        nbins          = h.GetNbinsX()
        self.njetStart = hdict["start"] 
        self.njetEnd   = hdict["end"]
        self.njets     = self.njetEnd - self.njetStart + 1

        # Region labels e.g. "ABCD" are taken from last four characters of histogram name
        # See cardConfig for format of histogram name
        regions = "ABCD"
        mask    = self.getBinMask()

        # Scale factor only applies to event counts, not systematic values or corrections
        SF = 1.0
        if hdict["type"] != "sys" and hdict["type"] != "corr":
            SF = self.RUN2SF

        for bin in range(0, nbins):
            val = SF * h.GetBinContent(bin+1)
            err = SF * h.GetBinError(bin+1)
            wgt = SF * (h.GetSumOfWeights() / h.GetEntries())
            reg = regions[int(bin/self.njets)]

            # Round all event count values to whole number (do not round systematic values of course)
            if hdict["type"] != "sys" and hdict["type"] != "corr":
               
                # Apply a floor to weighted event counts for any bkg or sig process 
                roundedVal = round(val)
                if roundedVal < 0.1:
                    binValues.append(0.1)
                else:
                    binValues.append(roundedVal)
            else:
                binValues.append(val)
           
            binErrors.append(err)
            binNames.append(reg+str(self.njetStart + bin % self.njets))
            binWeights.append(wgt)

        return binValues, binErrors, binNames, nbins, binWeights

    # --------------------------------------
    # Determine systematic variations ratios
    # --------------------------------------
    def calcVarValues(self, tfile, hdict):
        binValues = []; binErrors =[]; binNames = []

        # The histogram name will most likely contain the $CHANNEL keyword
        # and should be replaced with respective channel string e.g. 1l or 0l
        upHistName = hdict["upHist"].replace("$CHANNEL", self.channel) \
                                    .replace("$YEAR",    self.year) \
                                    .replace("$MODELS",   self.models)

        downHistName = hdict["downHist"].replace("$CHANNEL", self.channel) \
                                        .replace("$YEAR",    self.year) \
                                        .replace("$MODELS",   self.models)


        # Also need to collect the nominal histogram for computing the 
        # systematic ratio 
        nomName = hdict["nomHist"].replace("$CHANNEL", self.channel) \
                                  .replace("$YEAR",    self.year) \
                                  .replace("$MODELS",   self.models)

        upRatio = copy.copy(tfile.Get(upHistName))
        downRatio = copy.copy(tfile.Get(downHistName))
        h_nom = copy.copy(tfile.Get(nomName))

        # Divide variation by nominal to compute the systematic variation
        upRatio.Divide(h_nom)
        downRatio.Divide(h_nom)

        nbins          = upRatio.GetNbinsX()
        self.njetStart = hdict["start"] 
        self.njetEnd   = hdict["end"]
        self.njets     = self.njetEnd - self.njetStart + 1

        # Region labels e.g. "ABCD" are taken from last four characters of histogram name
        # See cardConfig for format of histogram name
        regions = "ABCD"
        mask    = self.getBinMask()

        for bin in range(0, nbins):
            valUp = upRatio.GetBinContent(bin+1)
            errUp = upRatio.GetBinError(bin+1)
            valDown = downRatio.GetBinContent(bin+1)
            errDown = downRatio.GetBinError(bin+1)

            valUp = 1.0 if math.isnan(valUp) else valUp
            valDown = 1.0 if math.isnan(valDown) else valDown

            valUp = 10.0 if valUp > 10 else valUp
            valDown = 10.0 if valDown > 10 else valDown

            valUp = 0.1 if valUp < 0.1 else valUp
            valDown = 0.1 if valDown < 0.1 else valDown

            val = "{:.3f}/{:.3f}".format(valDown, valUp)
            err = "{}/{}".format(errDown, errUp)

            reg = regions[int(bin/self.njets)]

            binValues.append(val)
            binErrors.append(err)
            binNames.append(reg+str(self.njetStart + bin % self.njets))

        return binValues, binErrors, binNames, nbins

    # --------------------------------------------------------------------
    # Read bin values (transfer factor) from a histogram
    # --------------------------------------------------------------------
    def calcBinValuesTF(self, tfile, hdict, **kwargs):
        binValues = []; binErrors =[]; binNames = []

        # The histogram name will most likely contain the $CHANNEL keyword
        # and should be replaced with respective channel string e.g. 1l or 0l
        histName = hdict["hist"].replace("$CHANNEL", self.channel) \
                                .replace("$MODELS",  self.models) \
                                .replace("$YEAR",    self.year)
        
        h = tfile.Get(histName)

        nbins          = h.GetNbinsX()

        # Region labels e.g. "ABCD" are taken from last four characters of histogram name
        # See cardConfig for format of histogram name
        regions = "ABCD"
        mask    = self.getBinMask()

        for bin in range(0, nbins):
            val = h.GetBinContent(bin+1)
            err = h.GetBinError(bin+1)
            reg = regions[int(bin)]

            binValues.append(val)
            binErrors.append(err)
            binNames.append(reg)

        return binValues, binErrors, binNames, nbins

    # --------------------------------------------------------------------------------------
    # Extract events counts for background and signal processes as well as systematic values
    # --------------------------------------------------------------------------------------
    def fillBinValues(self):

        # Loop over processes in the observed dictionary
        # and read their corresponding histogram bin entries
        # into a dictionary. Do this also for loading the systematics.
        for proc in self.observed.keys():

            # Several keywords for $CHANNEL, $YEAR, etc. can be present in the 
            # ROOT file name and need to be replaced with actual values "1l", "2016", etc. 
            # For the special case of loading signal, _two_ files are loaded:
            # One file for signal component used in fit and other injected into pseudoData
            path    = self.observed[proc]["path"].replace("$MASS",    self.mass         ) \
                                                 .replace("$MODELS",  self.models       ) \
                                                 .replace("$MODEL",   self.model        ) \
                                                 .replace("$CHANNEL", self.channel      ) \
                                                 .replace("$YEAR",    self.year         )
            pathInj = self.observed[proc]["path"].replace("$MASS",    self.injectedMass ) \
                                                 .replace("$MODELS",  self.injectedModels) \
                                                 .replace("$MODEL",   self.injectedModel) \
                                                 .replace("$CHANNEL", self.channel      ) \
                                                 .replace("$YEAR",    self.year         )

            tfile    = ROOT.TFile.Open(self.path+"/"+path   )
            tfileInj = ROOT.TFile.Open(self.path+"/"+pathInj)

            newproc    = proc.replace("$MODEL", self.model) \
                             .replace("$MASS",  self.mass )
            newprocInj = "INJECT_" + proc.replace("$MODEL", self.injectedModel) \
                                         .replace("$MASS",  self.injectedMass )

            # Replace the "$MODEL_$MASS" key with actual model and mass key
            # Add "INJECT" prefix for key pointing to signal being injected
            if newproc != proc:
                self.observed[newproc]    = copy.copy(self.observed[proc])
                #self.observed[newprocInj] = copy.copy(self.observed[proc])

                # Specify that _this_ "inj" signal is being injected
                # But, we do not fit with this signal
                self.observed[newproc]["inj"] = True
                self.observed[newproc]["fit"] = True

                #self.observed[newprocInj]["binValues"], self.observed[newprocInj]["binErrors"], self.observed[newprocInj]["binNames"], self.obsNbins, self.observed[newprocInj]["binWeights"] = self.calcBinValues(tfileInj, self.observed[newprocInj])

                # Remove template "$MODEL_$MASS" key and subdictionary from observed
                # as they have been replaced e.g. "RPV_550" and "INJECTED_RPV_400"
                del self.observed[proc]

            self.observed[newproc]["binValues"], self.observed[newproc]["binErrors"], self.observed[newproc]["binNames"], self.obsNbins, self.observed[newproc]["binWeights"] = self.calcBinValues(tfile, self.observed[newproc])

        # Loop over the systematics dictionary and load in Njets histograms for systs and MC correction factor
        for sy in self.systematics.keys():
            tfile = ROOT.TFile.Open(self.path+"/"+ self.systematics[sy]["path"].replace("$CHANNEL", self.channel) \
                                                                               .replace("$YEAR", self.year) \
                                                                               .replace("$MODELS", self.models)\
                                                                               .replace("$MASS", self.mass)\
                                                                               .replace("$MODEL", self.model))

            self.systematics[sy]["proc"] = self.systematics[sy]["proc"].replace("$MODEL", self.model) \
                                                                       .replace("$MASS", self.mass)

            if "nomHist" in self.systematics[sy].keys():
                self.systematics[sy]["binValues"], self.systematics[sy]["binErrors"], self.systematics[sy]["binNames"], self.varNbins = self.calcVarValues(tfile, self.systematics[sy])
            elif self.systematics[sy]["type"] != "TF":
                self.systematics[sy]["binValues"], self.systematics[sy]["binErrors"], self.systematics[sy]["binNames"], self.sysNbins, _ = self.calcBinValues(tfile, self.systematics[sy], extra=sy)
            else:
                self.systematics["QCD_TF"]["binValues"], self.systematics["QCD_TF"]["binErrors"], self.systematics["QCD_TF"]["binNames"], self.tfNbins = self.calcBinValuesTF(tfile, self.systematics["QCD_TF"])

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
                        if "QCD" in ob and "2l" not in self.channel:
                            tf_idx = self.systematics["QCD_TF"]["binNames"].index(self.observed[ob]["binNames"][n][:1])
                            obs += self.observed[ob]["binValues"][n] * self.systematics["QCD_TF"]["binValues"][tf_idx]
                        else:
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
                        if "QCD" in proc and "2l" not in self.channel:
                            tf_idx = self.systematics["QCD_TF"]["binNames"].index(self.observed[proc]["binNames"][n][:1])
                            obs += self.observed[proc]["binValues"][n] * self.systematics["QCD_TF"]["binValues"][tf_idx]
                        else:
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

        # ------------------------------------------------------------
        # Get a mask for determining which bins to include in datacard
        # (based on minNjet and maxNjet specified on command line)
        # ------------------------------------------------------------
        mask  = self.getBinMask()
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

            # -----------------------------------------------------------------------
            # Write datacard header specifying number of processes, bins, systematics
            # -----------------------------------------------------------------------
            file.write("imax {}  \n".format(self.obsNbins - masks))
            file.write("jmax {}  \n".format(jmax))
            file.write("kmax * \n")
            file.write("\n------------------------")
            bin_str  = "{} ".format("\nbin")
            tempproc = self.observed.keys()[0]

            # ---------------------------
            # Write out FAKE shapes lines
            # ---------------------------
            shape_str = ""
            for reg in ["A", "B", "C", "D"]:
                for nj in range(self.njetStart, self.njetEnd+1):
                    ch = "Y{}_{}{}_{}".format(self.year[-2:],reg,nj,self.channel)
                    shape_str += "\nshapes * {} FAKE".format(ch)
            file.write(shape_str)
            file.write("\n------------------------")

            # -------------------------
            # Write line for bin labels
            # -------------------------
            for bin in range(self.obsNbins):
                if not mask[bin]:
                    continue
                temp_str = "Y{}_{}_{} ".format(self.year[-2:],self.observed[tempproc]["binNames"][bin],self.channel)
                bin_str += "{} ".format(temp_str)
            file.write(bin_str)

            # ------------------------------------------------------
            # Write line for total observed event counts in each bin
            # ------------------------------------------------------
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
                            rate_str += "{} ".format(1)
                        elif proc == "QCD" and "2l" not in self.channel:
                            tf_idx = self.systematics["QCD_TF"]["binNames"].index(self.observed[proc]["binNames"][bin][:1])
                            rate_str += "{} ".format(self.observed[proc]["binValues"][bin] * self.systematics["QCD_TF"]["binValues"][tf_idx])
                            
                        else:
                            rate_str += "{} ".format(self.observed[proc]["binValues"][bin])

            file.write(pbin_str)
            file.write(process1_str)
            file.write(process2_str)
            file.write(rate_str)
            process2_str = "{} ".format("\nprocess")
            file.write("\n--------------------------")

            # -------------------------------------------------------
            # Write out 5% lumi systematic for all processes and bins
            # -------------------------------------------------------
            lumi_str = "{0:<8}".format("\nlumi")
            lumi_str += "{0:<7}".format("lnN")
            for bin in range(self.obsNbins):
                if not mask[bin]:
                    continue
                for proc in self.observed.keys():
                    if not self.observed[proc]["fit"]:
                        continue
                    lumi_str += "{} ".format(self.lumiSyst)
            file.write(lumi_str)

            # -----------------------------------------------------------
            # Write 20% normalization systematic on signal and background
            # -----------------------------------------------------------
            #for process1 in self.observed.keys():

            #    # Only put systematic for component being used in the fit
            #    if (self.observed[process1]["type"] != "sig" and self.observed[process1]["type"] != "bkg") or not self.observed[process1]["fit"]:
            #        continue

            #    process_str = "{} ".format("\nnp_"+process1)
            #    process_str += "{0:<7}".format("lnN")
            #    for bin in range(self.obsNbins):
            #        if not mask[bin]:
            #            continue
            #        for process2 in self.observed.keys():

            #            # Again, skip any process that is not included in the fit
            #            if not self.observed[process2]["fit"]:
            #                continue
            #            if process1 == process2:
            #                process_str += "{} ".format(self.observed[process1]["sys"])
            #            else:
            #                process_str += "{} ".format("--")
            #    file.write(process_str)

            # --------------------------------------------------------
            # Write a line to datacard for each independent systematic
            # --------------------------------------------------------
            for sys in self.systematics.keys():
            
                # To skip MC correction factor (added in a different spot in datacard)
                if self.systematics[sys]["type"] != "sys":
                    continue

                doUncorr = "uncorr" in self.systematics[sys]

                if doUncorr:

                    for abin in range(self.njetStart - self.njetStart, self.njetEnd - self.njetStart + 1):
                        file.write("\n")
                        for ibin in range(0, len(self.observedPerBin), self.njets):
                            if ibin > 0:
                                continue

                            sys_str = "{0:<8}".format("\n"+"np_"+sys + self.systematics[sys]["binNames"][abin] + "_" + self.channel + '\t')
                            sys_str += "{0:<7}".format(self.systematics[sys]["distr"])

                            for ibin2 in range(0, len(self.observedPerBin), self.njets):
                                for abin2 in range(self.njetStart - self.njetStart, self.njetEnd - self.njetStart + 1):
                                    for proc in self.observed.keys():
                                        if not self.observed[proc]['fit']:
                                            continue

                                        if not mask[abin+ibin]:
                                            continue
                                        if self.systematics[sys]['proc'] == proc and abin == abin2 and ibin2 == 0:
                                            sys_str += "{:.3f} ".format(self.systematics[sys]["binValues"][abin])
                                        else:
                                            sys_str += "{} ".format("--")
                            file.write(sys_str)
                else:
                    sys_str = "{0:<8}".format("\n"+"np_"+sys + "_" + self.channel + '\t')
                    sys_str += "{0:<7}".format(self.systematics[sys]["distr"])

                    for bin in range(self.obsNbins):
                        if not mask[bin]:
                            continue

                        for proc in self.observed.keys():
                            
                            if not self.observed[proc]["fit"]:
                                continue
                            
                            if bin >= self.sysNbins and not "nomHist" in self.systematics[sys].keys():
                                sys_str += "{} ".format("--")
                                continue
                            elif bin >= self.varNbins:
                                sys_str += "{} ".format("--")
                                continue
                          
                            if proc == self.systematics[sys]["proc"]:
                                if type(self.systematics[sys]["binValues"][bin]) == str:
                                    sys_str += "{} ".format(self.systematics[sys]["binValues"][bin])
                                else:
                                    sys_str += "{:.3f} ".format(self.systematics[sys]["binValues"][bin])
                            else:
                                sys_str += "{} ".format("--")

                    file.write(sys_str)

            # Write lines for MC statistical uncertainty
            # Note: We could use autoMCStats if we were handing histograms into the datacard
            # However, our current implementation requires us to write a separate line for each process

            file.write('\n\n # MC Statistical uncertainties')
            
            for process1 in self.observed.keys():

                if (self.observed[process1]["type"] != "sig" and self.observed[process1]["type"] != "bkg") or not self.observed[process1]["mcStat"] or "INJECT" in process1:
                    continue

                for abin in range(self.njetStart - self.njetStart, self.njetEnd - self.njetStart + 1):
                    file.write("\n")
                    for ibin in range(0, len(self.observedPerBin), self.njets):
                        process_str = "{} ".format("\nCH" + self.channel + "_mcStat"+self.observed[process1]["binNames"][ibin+abin]+process1+"_"+self.year)
                        if "QCD" in process1 and "2l" not in self.channel:
                            process_str += "{0:<7}".format("gmN {:.0f} ".format(self.observed[process1]["binValues"][ibin+abin]))
                        else:
                            process_str += "{0:<7}".format("gmN {:.0f} ".format(self.observed[process1]["binValues"][ibin+abin] / self.observed[process1]["binWeights"][0]))
                        
                        for ibin2 in range(0, len(self.observedPerBin), self.njets):
                            for abin2 in range(self.njetStart - self.njetStart, self.njetEnd - self.njetStart + 1):
                                for process2 in self.observed.keys():

                                    if not mask[abin+ibin] or not self.observed[process2]["fit"]:
                                        continue
                                    if process2 == process1 and abin2 == abin and ibin2 == ibin:
                                        if "QCD" in process1 and "2l" not in self.channel:
                                            tf_idx = self.systematics["QCD_TF"]["binNames"].index(self.observed[process1]["binNames"][abin+ibin][:1])
                                            process_str += "{:.8f} ".format(self.systematics["QCD_TF"]["binValues"][tf_idx])
                                        else:
                                            process_str += "{:.8f} ".format(self.observed[process1]["binWeights"][0])
                                    else:
                                        process_str += "{} ".format("--")
                        file.write(process_str)
                
                    
            params     = ["alpha", "beta", "gamma", "delta"]
            moreparams = ["romeo", "sierra", "tango", "uniform", "qcdtf"]
            file.write("\n")
            bkgd = None
            if self.dataType == "Data":
                bkgd = "Data"
            elif "pseudo" in self.dataType:
                bkgd = "TT"

            for abin in range(self.njetStart - self.njetStart, self.njetEnd - self.njetStart + 1):
                file.write("\n")
                for ibin in range(0, len(self.observedPerBin), self.njets):
                    if not mask[abin+ibin]:
                        continue
                    rate = self.observed[bkgd]["binValues"][abin+ibin]
                    for proc in self.observed.keys():
                        if not self.observed[proc]["fit"]:
                            continue
                        if proc != bkgd and self.observed[proc]["type"] != "sig":
                            if "QCD" in proc and "2l" not in self.channel:
                                tf_idx = self.systematics["QCD_TF"]["binNames"].index(self.observed[proc]["binNames"][abin+ibin][:1])
                                rate -= self.observed[proc]["binValues"][abin+ibin] * self.systematics["QCD_TF"]["binValues"][tf_idx]
                            else:
                                rate -= self.observed[proc]["binValues"][abin+ibin]

                    # ----------------------------
                    # Write tt MC correction ratio
                    # ----------------------------
                    if ibin == 0:

                        # Hard-coded MC correction factor to 1.0 (turning off the correction in ABCD calculation)
                        if self.NoMCcorr:
                            file.write("{0}{1}_{4:<12} rateParam Y{5}_{2}_{4} {3} (@0*@1/@2*@3) beta{1}_{4},gamma{1}_{4},delta{1}_{4},CH{4}_mcStat{1}TT_{5}\n".format(params[int(ibin/self.njets)],self.observed[bkgd]["binNames"][ibin+abin][1:],self.observed[bkgd]["binNames"][ibin+abin],bkgd,self.channel,self.year[-2:], 1.0))

                        # Includes actual MC Correction Ratio
                        else:
                            file.write("{0}{1}_{4:<12} rateParam Y{5}_{2}_{4} {3} (@0*@1/@2*@3) beta{1}_{4},gamma{1}_{4},delta{1}_{4},CH{4}_mcStat{1}TT_{5}\n".format(params[int(ibin/self.njets)],self.observed[bkgd]["binNames"][ibin+abin][1:],self.observed[bkgd]["binNames"][ibin+abin],bkgd,self.channel,self.year[-2:], round(self.systematics["MCcorrectionRatio"]["binValues"][abin],4)))

                    else: 
                        file.write("{0}{1}_{6:<12} rateParam Y{7}_{2}_{6} {3} {4:<12} {5}\n".format(params[int(ibin/self.njets)],self.observed[bkgd]["binNames"][ibin+abin][1:],self.observed[bkgd]["binNames"][ibin+abin],bkgd,rate, "[0,{}]".format(10*rate),self.channel,self.year[-2:])) 

                # TTbar MC stat uncertainty applied to the alpha parameters
                for ibin in range(0, len(self.observedPerBin), self.njets):
                    if ibin == 0:
                        file.write("CH{0}_mcStat{1}TT_{2} param {4} {3}".format(self.channel, self.observed["TT"]["binNames"][ibin+abin][1:], self.year[-2:], self.systematics["TT_MCStat"]["binErrors"][abin],round(self.systematics["MCcorrectionRatio"]["binValues"][abin],4)))
                file.write("\n")

                

                ## Write in QCD prediction based on scaling data from CR
                #for ibin in range(0, len(self.observedPerBin), self.njets):

                #    rate  = self.observed["QCD"]["binValues"][abin+ibin]

                #    # ------------------------------
                #    # Write QCD estimate to the card 
                #    # ------------------------------
                #    if "2l" not in self.channel:
                #        file.write("{0}{8}_{3:<12} rateParam Y{4}_{1}{8}_{3} {2} (@0*{5}) {6}{7}_{3}\n".format(moreparams[int(ibin / self.njets)],self.systematics["QCD_TF"]["binNames"][int(ibin / self.njets)],"QCD",self.channel,self.year[-2:], round(rate,4), moreparams[4],self.systematics["QCD_TF"]["binNames"][int(ibin / self.njets)], abin+self.min_nj))

            #file.write("\n")
            #if "2l" not in self.channel:
            #    for ibin in range(0, self.tfNbins):
            #        tf    = self.systematics["QCD_TF"]["binValues"][ibin]
            #        tfUnc = self.systematics["QCD_TF"]["binErrors"][ibin]

            #        #file.write("{0}{1}_{5:<12} rateParam Y{6}_{1}_{5} {2} {3:<12} {4}\n".format(moreparams[4],self.systematics["QCD_TF"]["binNames"][ibin],"QCD",round(tf,4),"[{0},{1}]".format(round(tf-tfUnc, 4), round(tf+tfUnc,4)),self.channel,self.year[-2:])) 
            #        file.write("{0}{1}_{4:<12} param {2:<12} {3}\n".format(moreparams[4],self.systematics["QCD_TF"]["binNames"][ibin],round(tf,4),round(tfUnc, 4),self.channel,self.year[-2:])) 

    

    # ----------------------------------------------------------------
    # Make a bin mask based on Njets range specified on command line
    # and histogram absolute Njets bounds specified in the card config
    # ----------------------------------------------------------------
    def getBinMask(self):
        mask = []
        for k in range(4):
            for i in range(self.njetStart, self.njetEnd+1):
                if i < self.njetStart or i > self.njetEnd:
                    mask.append(0)
                else:
                    mask.append(1)

        return mask
