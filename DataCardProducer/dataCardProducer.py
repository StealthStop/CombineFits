import ROOT
import math

sigScale = 1

class dataCardMaker:

    def __init__(self, path, signal, observed, histos, lumi, outpath, othersys, doABCD, dataType, suffix, year, setClosure, closureUp, closureDown, closureUpConst, closureDownConst, closureUnc, closureUncUncorr, closureReal, Run2, NoSigBCD, min_nj, max_nj):
        
        self.path = path
        self.signal = signal
        self.observed = observed
        self.histos = histos
        self.outpath = outpath
        self.othersys = othersys
        self.lumi = lumi
        self.dataType = dataType
        self.doABCD = doABCD
        self.suffix = suffix
        self.year = str(year)
        self.setClosure = setClosure
        self.closureUp = closureUp
        self.closureDown = closureDown
        self.closureUpConst = closureUpConst
        self.closureDownConst = closureDownConst
        self.closureUnc = closureUnc
        self.closureUncUncorr = closureUncUncorr
        self.closureReal = closureReal
        self.closureManip = self.closureUp or self.closureDown or self.closureUpConst or self.closureDownConst or self.closureUnc or self.closureUncUncorr or self.closureReal
        self.RUN2SF = 1
        if Run2:
            self.RUN2SF = 137.0 / 35.9 
        self.NoSigBCD = NoSigBCD
        self.min_nj = min_nj
        self.max_nj = max_nj
        self.fillBinValues()
        self.writeCards()

    def calcBinValues(self, tfile):
        binValues = []; binNames = []
        for hist in sorted(self.histos.keys()):
            if len(self.histos.keys()) == 1:
                h = tfile.Get(self.histos[hist]["name"][:14] + self.suffix + self.histos[hist]["name"][14:])
            else:
                h = tfile.Get(self.histos[hist]["name"][:25] + self.suffix + self.histos[hist]["name"][25:])
            if isinstance(h, ROOT.TH2D) or isinstance(h, ROOT.TH2F):
                if self.histos[hist]["disco"]:
                    val = abs(self.RUN2SF*round(h.Integral()))
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
                regions = self.histos[hist]["name"][-4::]
                mask = self.getBinMask()
                for bin in range(self.histos[hist]["start"], lastbin, skip):
                    val = round(self.RUN2SF * h.Integral(bin+1, bin+1), 1)
                    reg = regions[int(bin/5)]
                    if val < 0.1: val = 0.1
                    binValues.append(val)
                    binNames.append(reg+str(7 + bin % 5))

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
        self.closureUncertainties = []
        self.closureUncertaintiesUnc = []
        if self.dataType == "pseudoData":
            for n in range(self.nbins):
                obs = 0
                closure_unc = "--"
                for ob in self.observed.keys():
                    temp = 0
                    obs_ac = 0
                    if n <= 4 and ob == "TT" and self.closureManip:
                        temp = (self.observed[ob]["binValues"][n + 5] * self.observed[ob]["binValues"][n + 10] / self.observed[ob]["binValues"][n + 15])
                        if self.closureUnc or self.closureReal or self.closureUncUncorr:
                            obs += self.observed[ob]["binValues"][n]
                        if self.setClosure:
                            obs += temp
                        if self.closureUp:
                            obs += math.sqrt(temp)
                        if self.closureDown:
                            obs -= math.sqrt(temp)
                        if self.closureUpConst:
                            obs += temp * self.closureUpConst / 100
                        if self.closureDownConst:
                            obs -= temp * self.closureDownConst / 100
                        obs_ac = self.observed[ob]["binValues"][n]
                        closure_unc = str(round(pow(obs_ac/temp,1), 2))
                        closure_unc_unc = str(round(pow(obs_ac/temp,1) * math.sqrt(pow(math.sqrt(obs_ac)/obs_ac,2) + pow(math.sqrt(temp)/temp,2)), 2))
                        if closure_unc == "1.0":
                            closure_unc = "1.01"
                        self.closureUncertainties.append(closure_unc)
                        self.closureUncertaintiesUnc.append(closure_unc_unc)
                    else:
                        obs += self.observed[ob]["binValues"][n]
                self.observedPerBin.append(obs)
        elif self.dataType == "pseudoDataS":
            for n in range(self.nbins):
                obs = 0
                closure_unc = "--"
                for sg in self.signal.keys():
                    if n > 4 and self.NoSigBCD:
                        continue
                    obs += self.signal[sg]["binValues"][n]/sigScale
                for ob in self.observed.keys():
                    temp = 0
                    obs_ac = 0
                    if n <= 4 and ob == "TT" and self.closureManip:
                        temp = (self.observed[ob]["binValues"][n + 5] * self.observed[ob]["binValues"][n + 10] / self.observed[ob]["binValues"][n + 15])
                        if self.closureUnc or self.closureReal or self.closureUncUncorr:
                            obs += self.observed[ob]["binValues"][n]
                        if self.setClosure: 
                            obs += temp 
                        if self.closureUp:
                            obs += math.sqrt(temp)
                        if self.closureDown:
                            obs -= math.sqrt(temp)
                        if self.closureUpConst:
                            obs += temp * self.closureUpConst / 100
                        if self.closureDownConst:
                            obs -= temp * self.closureDownConst / 100
                        obs_ac = self.observed[ob]["binValues"][n]
                        closure_unc = str(round(pow(obs_ac/temp,1), 2))
                        closure_unc_unc = str(pow(obs_ac/temp,1) * math.sqrt(pow((math.sqrt(obs_ac)/obs_ac),2) + pow((math.sqrt(temp)/temp),2)))
                        if closure_unc == "1.0":
                            closure_unc = "1.01"
                        self.closureUncertainties.append(closure_unc)
                        self.closureUncertaintiesUnc.append(closure_unc_unc)
                    else:
                        obs += self.observed[ob]["binValues"][n]
                self.observedPerBin.append(obs)
        elif self.dataType == "Data":
            for n in range(self.nbins):
                self.observedPerBin.append(self.observed["Data"]["binValues"][n])

    def writeCards(self):
        mask = self.getBinMask()
        masks = 0
        for i in mask:
            masks -= i - 1
        with open(self.outpath, "w") as file:
            file.write("imax {}  \n".format(self.nbins - masks))
            file.write("jmax {}  \n".format(len(self.observed.keys())))
            file.write("kmax * \n")
            file.write("\n------------------------")
            bin_str = "{} ".format("\nbin")
            tempproc = self.observed.keys()[0]
            shape_str = ""
            for reg in ["A", "B", "C", "D"]:
                for nj in range(self.min_nj, self.max_nj+1):
                    ch = "Y{}_{}{}{}".format(self.year[-2:],reg,nj,self.suffix)
                    shape_str += "\nshapes * {} FAKE".format(ch)
            file.write(shape_str)
            file.write("\n------------------------")
            for bin in range(self.nbins):
                if not mask[bin]:
                    continue
                temp_str = "Y{}_{}{} ".format(self.year[-2:],self.observed[tempproc]["binNames"][bin],self.suffix)
                bin_str += "{} ".format(temp_str)
            file.write(bin_str)
            obs_str = "{} ".format("\nobservation")
            for obs in range(self.nbins):
                if not mask[obs]:
                    continue
                obs_str += "{} ".format(round(self.observedPerBin[obs]))
            file.write(obs_str)
            file.write("\n--------------------------")
            pbin_str = "{} ".format("\nbin")
            process1_str = "{} ".format("\nprocess")
            process2_str = "{} ".format("\nprocess")
            rate_str = "{} ".format("\nrate")
            for bin in range(self.nbins):
                if not mask[bin]:
                    continue
                for proc in self.signal.keys():
                    temp_str = "Y{}_{}{} ".format(self.year[-2:],self.observed[tempproc]["binNames"][bin],self.suffix)
                    pbin_str += "{} ".format(temp_str)
                    process1_str += "{} ".format(proc)
                    process2_str += "{} ".format(0)
                    if (proc.find("RPV") != -1 or proc.find("SYY") != -1) and self.NoSigBCD and bin > self.max_nj - self.min_nj:
                        rate_str += "{} ".format(0.1)
                    elif float(self.signal[proc]["binValues"][bin]) > 0.1:
                        rate_str += "{} ".format(self.signal[proc]["binValues"][bin]/sigScale)
                    else:
                        rate_str += "{} ".format(0.1)
                cnt = 0
                for proc in self.observed.keys():
                    cnt += 1
                    temp_str = "Y{}_{}{} ".format(self.year[-2:],self.observed[tempproc]["binNames"][bin],self.suffix)
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
                if not mask[bin]:
                    continue
                for proc in range(len(self.signal.keys()) + len(self.observed.keys())):
                    lumi_str += "{} ".format(1.05)
            file.write(lumi_str)
            for signal1 in self.signal.keys():
                sig_str = "{} ".format("\nnp_"+signal1)
                sig_str += "{0:<7}".format("lnN")
                for bin in range(self.nbins):
                    if not mask[bin]:
                        continue
                    for signal2 in self.signal.keys():
                        if signal1 == signal2:
                            sig_str += "{} ".format(self.signal[signal1]["sys"])
                        else:
                            sig_str += "{} ".format("--")
                    sig_str += "{} ".format("--")*len(self.observed.keys())
                file.write(sig_str)
            for observed1 in self.observed.keys():
                bg_str = "{0:<14}".format("\nnp_"+observed1)
                bg_str += "{0:<7}".format("lnN")
                for bin in range(self.nbins):
                    if not mask[bin]:
                        continue
                    bg_str += "{} ".format("--")*len(self.signal.keys())                
                    for observed2 in self.observed.keys():
                        if observed1 == observed2:
                            bg_str += "{} ".format(self.observed[observed1]["sys"])
                        else:
                            bg_str += "{} ".format("--")
                file.write(bg_str)
            if self.closureUnc:
                sys_str = "{0:<8}".format("\nnp_Closure" + self.suffix + '\t')
                sys_str += "{0:<7}".format("lnN")
                for i, unc in enumerate(self.closureUncertainties):
                    if not mask[i]:
                        continue
                    for sg in self.signal.keys():
                        sys_str += "{} ".format("--")
                    for bg in self.observed.keys():
                        if bg == "TT":
                            sys_str += "{} ".format(unc)
                        else:
                            sys_str += "{} ".format("--")
                file.write(sys_str)
            if self.closureUncUncorr:
                for nj in range(self.min_nj, self.max_nj + 1):
                    sys_str = "{0:<8}".format("\nnp_ClosureNj" + str(nj) + self.suffix + '\t')
                    sys_str += "{0:<7}".format("lnN")
                    for i, unc in enumerate(self.closureUncertainties):
                        if not mask[i]:
                            continue
                        for sg in self.signal.keys():
                            sys_str += "{} ".format("--")
                        for bg in self.observed.keys():
                            if bg == "TT" and nj - 7 == i:
                                sys_str += "{} ".format(unc)
                            else:
                                sys_str += "{} ".format("--")
                    file.write(sys_str)
            if self.closureReal:
                file.write("\n")
                for nj in range(self.min_nj, self.max_nj + 1):
                    
                    sys_str = "{0:<8}".format("\nnp_ClosureNj" + str(nj) + self.suffix + '\t')
                    sys_str += "{0:<7}".format("rateParam ")
                    for i, unc in enumerate(self.closureUncertainties):
                        if i + 7 == nj:
                            sys_str += "Y{2}_{0}{1} TT ".format(self.observed["TT"]["binNames"][nj-7],self.suffix,self.year[-2:])
                            sys_str += "{0}".format(unc, round((1-float(self.closureUncertaintiesUnc[i])*float(unc)),2), round((1.+float(self.closureUncertaintiesUnc[i]))*float(unc),2))
                    file.write(sys_str)
                    
                    sys_str = "{0:<8}".format("\nnp_ClosureNj" + str(nj) + self.suffix + '\t')
                    sys_str += "{0:<7}".format("param ")
                    for i, unc in enumerate(self.closureUncertainties):
                        if i + 7 == nj:
                            sys_str += "{0} {1}".format(unc, round((float(self.closureUncertaintiesUnc[i])*float(unc)),2))
                    file.write(sys_str)
                    
                '''
                for nj in range(self.min_nj, self.max_nj + 1):
                    sys_str = "{0:<8}".format("\nnp_ClosureNj" + str(nj) + self.suffix + 'Unc\t')
                    sys_str += "{0:<7}".format("lnN ")
                    for i, unc in enumerate(self.closureUncertaintiesUnc):
                        if not mask[i]:
                            continue
                        for sg in self.signal.keys():
                            sys_str += "{} ".format("--")
                        for bg in self.observed.keys():
                            if bg == "TT" and nj - 7 == i:
                                sys_str += "{} ".format(1 + float(unc))
                            else:
                                sys_str += "{} ".format("--")
                    file.write(sys_str)
                '''
            if self.othersys:
                for sys in self.othersys.keys():
                    sys_str = "{0:<8}".format("\n"+sys + self.suffix + '\t')
                    sys_str += "{0:<7}".format(self.othersys[sys]["distr"])
                    for bin in range(self.nbins):
                        if not mask[bin]:
                            continue
                        if type(self.othersys[sys]["sys"]) == type([]):
                            i = bin
                        else:
                            i = 0
                        for sg in self.signal.keys():
                            if sg in self.othersys[sys]["apply"]:
                                sys_str += "{} ".format(self.othersys[sys]["sys"][i] )
                            else:
                                sys_str += "{} ".format("--")
                        for bg in self.observed.keys():
                            if bg in self.othersys[sys]["apply"]:
                                sys_str += "{} ".format(self.othersys[sys]["sys"][i])
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

                for abin in range(self.min_nj - 7, self.max_nj - 6):
                    file.write("\n")
                    for ibin in range(0, len(self.observedPerBin), 5):
                        if not mask[abin+ibin]:
                            continue
                        rate = self.observedPerBin[abin+ibin]
                        for proc in self.observed.keys():
                            if proc != bkgd:
                                rate -= self.observed[proc]["binValues"][abin+ibin]
                        #if self.dataType == "pseudoDataS":
                        #    for proc in self.signal.keys():
                        #        rate -= self.signal[proc]["binValues"][abin+ibin]/sigScale

                        if ibin == 0:
                            file.write("{0}{1}{4:<12} rateParam Y{5}_{2}{4} {3} (@0*@1/@2) beta{1}{4},gamma{1}{4},delta{1}{4}\n".format(params[ibin%4],self.observed[bkgd]["binNames"][ibin+abin][1:],self.observed[bkgd]["binNames"][ibin+abin],bkgd,self.suffix,self.year[-2:]))
                        else: 
                            file.write("{0}{1}{6:<12} rateParam Y{7}_{2}{6} {3} {4:<12} {5}\n".format(params[ibin%4],self.observed[bkgd]["binNames"][ibin+abin][1:],self.observed[bkgd]["binNames"][ibin+abin],bkgd,rate, "[0,{}]".format(3*rate),self.suffix,self.year[-2:])) 
            if self.closureReal:
                file.write("\n")
                sys_str = "closure group = "
                for nj in range(self.min_nj, self.max_nj + 1):
                    sys_str += "{0} ".format("np_ClosureNj" + str(nj) + self.suffix)
                file.write(sys_str)
            
            #sys_str = "\n\n* autoMCStats 0"
            #file.write(sys_str)               
 
    def getBinMask(self):
        mask = []
        for k in range(4):
            for i in range(7, self.max_nj + 1):
                if i < self.min_nj:
                    mask.append(0)
                else:
                    mask.append(1)

        return mask
