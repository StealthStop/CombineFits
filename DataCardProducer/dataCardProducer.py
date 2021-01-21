import ROOT

RUN2SF = 3.82

class dataCardMaker:

    def __init__(self, path, signal, observed, histos, lumi, outpath, othersys, doABCD, dataType):
        self.path = path
        self.signal = signal
        self.observed = observed
        self.histos = histos
        self.outpath = outpath
        self.othersys = othersys
        self.lumi = lumi
        self.dataType = dataType
        self.doABCD = doABCD
        self.fillBinValues()
        self.writeCards()

    def calcBinValues(self, tfile):
        binValues = []; binNames = []
        for hist in sorted(self.histos.keys()):
            h = tfile.Get(self.histos[hist]["name"])
            if isinstance(h, ROOT.TH2D) or isinstance(h, ROOT.TH2F):
                if self.histos[hist]["disco"]:
                    val = RUN2SF*round(h.Integral())
                    if self.histos[hist]["region"] == "A" and "mStop" in tfile.GetName():
                        binValues.append(val)
                        binNames.append(self.histos[hist]["region"]+str(self.histos[hist]["Njets"]))
                    elif "mStop" not in tfile.GetName():
                        binValues.append(val)
                        binNames.append(self.histos[hist]["region"]+str(self.histos[hist]["Njets"]))
                    else:
                        binValues.append(val)
                        binNames.append(self.histos[hist]["region"]+str(self.histos[hist]["Njets"]))
                else:
                    if self.histos[hist]["end"][0] == "last":
                        lastbinx = h.GetNbinsX()
                    else:
                        lastbinx = self.histos[hist]["end"][0]
                        
                    histbinsx = lastbinx - self.histos[hist]["start"][0]
                    skipx = histbinsx/self.histos[hist]["nbins"][0]
                    if self.histos[hist]["end"][1] == "last":
                        lastbiny = h.GetNbinsY()
                    else:
                        lastbiny = self.histos[hist]["end"][1]
                        
                    histbinsy = lastbiny - self.histos[hist]["start"][1]
                    skipy = histbinsy/self.histos[hist]["nbins"][1]
                    for binx in range(self.histos[hist]["start"][0], lastbinx, skipx):
                        for biny in range(self.histos[hist]["start"][1], lastbiny, skipy):
                            val = round(h.Integral(binx, binx + skipx, biny, biny + skipy), 1)
                            if val < 0.1: val = 0.1
                            binValues.append(val)
                            binNames.append(self.histos[hist]["region"]+str(self.histos[hist]["Njets"]))

            else:
                if self.histos[hist]["end"] == "last":
                    lastbin = h.GetNbinsX()
                else:
                    lastbin = self.histos[hist]["end"]
                    
                histbins = lastbin - self.histos[hist]["start"]
                skip = histbins/self.histos[hist]["nbins"]
                for bin in range(self.histos[hist]["start"], lastbin, skip):
                    val = round(h.Integral(bin, bin + skip), 1)
                    if val < 0.1: val = 0.1
                    binValues.append(val)
                    binNames.append(self.histos[hist]["region"]+str(self.histos[hist]["Njets"]))

        return binValues, binNames
                    

    def fillBinValues(self):
        self.nbins = 0
        for sg in self.signal.keys():
            tfile = ROOT.TFile.Open(self.path+self.signal[sg]["path"])            
            self.signal[sg]["binValues"], self.signal[sg]["binNames"] = self.calcBinValues(tfile)
        for ob in self.observed.keys():
            tfile = ROOT.TFile.Open(self.path+self.observed[ob]["path"])
            self.observed[ob]["binValues"], self.observed[ob]["binNames"] = self.calcBinValues(tfile)
        self.nbins = 0
        for h in self.histos.keys():
            if self.histos[h]["disco"]:
                self.nbins += 1
            elif isinstance(self.histos[h]["nbins"], list) and len(self.histos[h]["nbins"]) == 2:
                self.nbins += self.histos[h]["nbins"][0]*self.histos[h]["nbins"][1]
            else:
                self.nbins += self.histos[h]["nbins"]
        self.observedPerBin = []        

        if self.dataType == "pseudoData":
            for n in range(self.nbins):
                obs = 0
                for ob in self.observed.keys():
                    obs += self.observed[ob]["binValues"][n]
                self.observedPerBin.append(obs)
        elif self.dataType == "pseudoDataS":
            for n in range(self.nbins):
                obs = 0
                for sg in self.signal.keys():
                    obs += self.signal[sg]["binValues"][n]
                for ob in self.observed.keys():
                    obs += self.observed[ob]["binValues"][n]
                self.observedPerBin.append(obs)
        elif self.dataType == "Data":
            for n in range(self.nbins):
                self.observedPerBin.append(self.observed["Data"]["binValues"][n])

    def writeCards(self):

        with open(self.outpath, "w") as file:
            file.write("imax {}  \n".format(self.nbins))
            file.write("jmax {}  \n".format(len(self.observed.keys())))
            file.write("kmax * \n")
            file.write("\n------------------------")
            bin_str = "{} ".format("\nbin")
            tempproc = self.observed.keys()[0]
            for bin in range(self.nbins):
                temp_str = "{} ".format(self.observed[tempproc]["binNames"][bin])
                bin_str += "{} ".format(temp_str)
            file.write(bin_str)
            obs_str = "{} ".format("\nobservation")
            for obs in range(self.nbins):
                if obs % 4 == 0: 
                    obs_str += "{} ".format(self.observedPerBin[obs])
                else:
                    obs_str += "{} ".format(self.observedPerBin[obs])
            file.write(obs_str)
            file.write("\n--------------------------")
            pbin_str = "{} ".format("\nbin")
            process1_str = "{} ".format("\nprocess")
            process2_str = "{} ".format("\nprocess")
            rate_str = "{} ".format("\nrate")
            for bin in range(self.nbins):
                for proc in self.signal.keys():
                    temp_str = "{} ".format(self.observed[tempproc]["binNames"][bin])
                    pbin_str += "{} ".format(temp_str)
                    process1_str += "{} ".format(proc)
                    process2_str += "{} ".format(0)
                    rate_str += "{} ".format(self.signal[proc]["binValues"][bin])
                cnt = 0
                for proc in self.observed.keys():
                    cnt += 1
                    temp_str = "{} ".format(self.observed[tempproc]["binNames"][bin])
                    pbin_str += "{} ".format(temp_str)
                    process1_str += "{} ".format(proc)
                    process2_str += "{} ".format(cnt)
                    if not self.doABCD:
                        rate_str += "{} ".format(self.observed[proc]["binValues"][bin])
                    elif self.doABCD and (proc == "Data" or proc == "TT"):
                        rate_str += "{} ".format(1)
                    else:
                        rate_str += "{} ".format(self.observed[proc]["binValues"][bin])

            file.write(pbin_str)
            file.write(process1_str)
            file.write(process2_str)
            file.write(rate_str)
            process2_str = "{} ".format("\nprocess")
            file.write("\n--------------------------")
            lumi_str = "{0:<8}".format("\nlumi")
            lumi_str += "{0:<7}".format("lnN")
            for bin in range(self.nbins):
                for proc in range(len(self.signal.keys()) + len(self.observed.keys())):
                    lumi_str += "{} ".format(1.02)
            file.write(lumi_str)
            for signal1 in self.signal.keys():
                sig_str = "{} ".format("\n"+signal1)
                sig_str += "{0:<7}".format("lnN")
                for bin in range(self.nbins):
                    for signal2 in self.signal.keys():
                        if signal1 == signal2:
                            sig_str += "{} ".format(self.signal[signal1]["sys"])
                        else:
                            sig_str += "{} ".format("--")
                    sig_str += "{} ".format("--")*len(self.observed.keys())
                file.write(sig_str)
            for observed1 in self.observed.keys():
                bg_str = "{0:<8}".format("\n"+observed1)
                bg_str += "{0:<7}".format("lnN")
                for bin in range(self.nbins):
                    bg_str += "{} ".format("--")*len(self.signal.keys())                
                    for observed2 in self.observed.keys():
                        if observed1 == observed2 and bin % 4 == 0:
                            bg_str += "{} ".format(self.observed[observed1]["sys"])
                        else:
                            bg_str += "{} ".format("--")
                file.write(bg_str)
            if self.othersys:
                for sys in self.othersys.keys():
                    sys_str = "{0:<8}".format("\n"+sys)
                    sys_str += "{0:<7}".format(self.othersys[sys]["distr"])
                    for bin in range(self.nbins):
                        for sg in self.signal.keys():
                            if sg in self.othersys[sys]["apply"]:
                                sys_str += "{} ".format(self.othersys[sys]["sys"])
                            else:
                                sys_str += "{} ".format("--")
                        for bg in self.observed.keys():
                            if bg in self.othersys[sys]["apply"]:
                                sys_str += "{} ".format(self.othersys[sys]["sys"])
                            else:
                                sys_str += "{} ".format("--")
                    file.write(sys_str)
                    
            if self.doABCD:
                params = ["alpha", "beta", "gamma", "delta"]
                file.write("\n")
                bkgd = None
                if self.dataType == "Data":
                    bkgd = "Data"
                elif "pseudo" in self.dataType:
                    bkgd = "TT"

                jbin = 0
                for abin in range(0, len(self.observedPerBin), 4):
                    jbin += 1
                    file.write("\n")
                    for ibin in range(0, 4):
                        rate = self.observedPerBin[abin+ibin]
                        for proc in self.observed.keys():
                            if proc != bkgd:
                                rate -= self.observed[proc]["binValues"][abin+ibin]
                        if self.dataType != "pseudoDataS":
                            for proc in self.signal.keys():
                                rate -= self.signal[proc]["binValues"][abin+ibin]

                        if ibin == 0:
                            file.write("{0}{1} rateParam {2:<12} {3} (@0*@1/@2) beta{1},gamma{1},delta{1}\n".format(params[ibin],jbin,self.observed[bkgd]["binNames"][ibin+abin],bkgd))
                        else: 
                            file.write("{0}{1} rateParam {2:<12} {3} {4:<12}\n".format(params[ibin],jbin,self.observed[bkgd]["binNames"][ibin+abin],bkgd,rate))
