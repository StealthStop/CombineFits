# make a systematics table
import ROOT

def getHisto(f, name):
    h = f.Get(name)
    if not h:
        print "-----------------------------------------"
        print "Histo not found", name, "in file", f
        print "-----------------------------------------"
    return h

def getlist(histos):
    mylist = []
    for i in range(len(histos)):
        for bin in range(1,histos[i].GetNbinsX()+1):
            mylist.append(histos[i].GetBinContent(bin))
    return mylist

def getMin(l):
    num=99999999.9
    for i in l: 
        if i < num and i < 100: 
            num = i
    return round(num)

def getMax(l):
    num=-1.0
    for i in l:
        if i > num and i < 100:
            num = i
    if round(num) == 0: num = 1
    return round(num)

def loopNonttbar(year, sources, f, mvas, name):
    for key in sources.keys():
        histos_     = [getHisto(f,"%s_%s_h_njets_pt30_1l" % (mva,name)) for mva in mvas]
        histos_Up   = [getHisto(f,"%s_%s_h_njets_pt30_1l_%sUp" % (mva,name,key)) for mva in mvas]
        histos_Down = [getHisto(f,"%s_%s_h_njets_pt30_1l_%sDown" % (mva,name,key)) for mva in mvas]
    
        # get nominal, and  minimum and maximum variation
        nom_  = getlist(histos_)
        up_   = getlist(histos_Up)
        down_ = getlist(histos_Down)
    
        # get relative differences
        rel_up_ = [abs(100*(up_[i]/nom_[i]-1)) for i in range(len(nom_))]
        rel_down_ = [abs(100*(down_[i]/nom_[i]-1)) for i in range(len(nom_))]
        #if (key == "JEC" or key == "JER") and name == "OTHER":
        #    print "-----------------"+year+"-------------------------"        
        #    print key, rel_up_+rel_down_
        rel__min = getMin(rel_up_+rel_down_)
        rel__max = getMax(rel_up_+rel_down_)
        sources[key] = [rel__min, rel__max]

def loopttbar(year, sources, f, mvas):
    for key in sources.keys():
        histos_ttbar = [getHisto(f,"%s_%s" % (mva,key)) for mva in mvas]
        list_ttbar = getlist(histos_ttbar)
    
        rel_ttbar = [abs(100*(list_ttbar[i]-1)) for i in range(len(list_ttbar))]
        rel_ttbar_min = getMin(rel_ttbar)
        rel_ttbar_max = getMax(rel_ttbar)
        sources[key] = [rel_ttbar_min, rel_ttbar_max]

class AllSources:
    def __init__(self):
        self.sources_nonttbar          = None
        self.sources_nonttbar_2017     = None 
        self.sources_nonttbar_2018pre  = None 
        self.sources_nonttbar_2018post = None 
        self.sources_signal            = None 
        self.sources_signal_2017       = None 
        self.sources_signal_2018pre    = None 
        self.sources_signal_2018post   = None 
        self.sources_ttbar             = None 
        self.sources_ttbar_2017        = None 
        self.sources_ttbar_2018pre     = None 
        self.sources_ttbar_2018post    = None 

    def getS(self,s, name):
        return "%d--%d" % (s[name][0],s[name][1]) if name else "-"

    def makeLine(self,title, tt16,tt17,tt18,tt19, non16,non17,non18,non19, sig16,sig17,sig18,sig19):
        line = "%s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s & %s \\\\  " % (
            title, 
            self.getS(self.sources_ttbar,tt16),     self.getS(self.sources_ttbar_2017,tt17),     self.getS(self.sources_ttbar_2018pre,tt18),     self.getS(self.sources_ttbar_2018post,tt19), 
            self.getS(self.sources_nonttbar,non16), self.getS(self.sources_nonttbar_2017,non17), self.getS(self.sources_nonttbar_2018pre,non18), self.getS(self.sources_nonttbar_2018post,non19), 
            self.getS(self.sources_signal,sig16),   self.getS(self.sources_signal_2017,sig17),   self.getS(self.sources_signal_2018pre,sig18),   self.getS(self.sources_signal_2018post,sig19))
        return line

table = open("table_systematics.tex", 'w')

pretex = """\\begin{tabular}{l | c c c c | c c c c | c c c c }
Source     & \\multicolumn{4}{c}{ttbar}        & \\multicolumn{4}{c}{non-ttbar}    & \\multicolumn{4}{c}{signal}      \\\\ \\hline
           & 2016 & 2017 & 2018pre & 2018post  & 2016 & 2017 & 2018pre & 2018post  & 2016 & 2017 & 2018pre & 2018post \\\\ \\hline
Luminosity & -    & -    & -       & -         & 2.5  & 2.3  & 2.5     & 2.5       & 2.5  & 2.3  & 2.5     & 2.5      \\\\
"""
table.write(pretex)

# extract numbers
nonttbar_file_2016     = ROOT.TFile.Open("../Keras_2016_v1.2/njets_for_Aron.root")
ttbar_file_2016        = ROOT.TFile.Open("../Keras_2016_v1.2/ttbar_systematics.root")
nonttbar_file_2017     = ROOT.TFile.Open("../Keras_2017_v1.2/njets_for_Aron.root")
ttbar_file_2017        = ROOT.TFile.Open("../Keras_2017_v1.2/ttbar_systematics.root")
nonttbar_file_2018pre  = ROOT.TFile.Open("../Keras_2018pre_v1.2/njets_for_Aron.root")
ttbar_file_2018pre     = ROOT.TFile.Open("../Keras_2018pre_v1.2/ttbar_systematics.root")
nonttbar_file_2018post = ROOT.TFile.Open("../Keras_2018post_v1.2/njets_for_Aron.root")
ttbar_file_2018post    = ROOT.TFile.Open("../Keras_2018post_v1.2/ttbar_systematics.root")

s = AllSources()
s.sources_nonttbar          = dict([(n,[]) for n in ["JEC","JER","btg","lep","pdf","pu","scl", "ht"]])
s.sources_nonttbar_2017     = dict([(n,[]) for n in ["JEC","JER","btg","lep","pdf","prf","pu","scl", "ht"]])
s.sources_nonttbar_2018pre  = dict([(n,[]) for n in ["JEC","JER","btg","lep","pdf","pu","scl", "ht"]])
s.sources_nonttbar_2018post = dict([(n,[]) for n in ["JEC","JER","btg","lep","pdf","pu","scl", "ht"]])
s.sources_signal            = dict([(n,[]) for n in ["JEC","JER","btg","lep","pdf","pu","scl"]])
s.sources_signal_2017       = dict([(n,[]) for n in ["JEC","JER","btg","lep","pdf","prf","pu","scl"]])
s.sources_signal_2018pre    = dict([(n,[]) for n in ["JEC","JER","btg","lep","pdf","pu","scl"]])
s.sources_signal_2018post   = dict([(n,[]) for n in ["JEC","JER","btg","lep","pdf","pu","scl"]])
s.sources_ttbar             = dict([(n,[]) for n in ["JECUp","JERUp","btg","lep","pdf","pu","ht","httail", "htnjet","scl","ISR","FSR","nom","qcdCR","hdampUp","underlyingEvtUp","erdOn","mpTScaled","noHT"]])
s.sources_ttbar_2017        = dict([(n,[]) for n in ["JECUp","JERUp","btg","lep","pdf","prf","pu","ht","httail", "htnjet","scl","ISR","FSR","nom","qcdCR","hdampUp","underlyingEvtUp","erdOn","mpTScaled","noHT"]])
s.sources_ttbar_2018pre     = dict([(n,[]) for n in ["JECUp","JERUp","btg","lep","pdf","pu","ht","httail", "htnjet","scl","ISR","FSR","nom","qcdCR","hdampUp","underlyingEvtUp","erdOn","mpTScaled","noHT"]])
s.sources_ttbar_2018post    = dict([(n,[]) for n in ["JECUp","JERUp","btg","lep","pdf","pu","ht","httail", "htnjet","scl","ISR","FSR","nom","qcdCR","hdampUp","underlyingEvtUp","erdOn","mpTScaled","noHT"]])

mvas = ["D1","D2","D3","D4"]

loopNonttbar("2016",    s.sources_nonttbar,          nonttbar_file_2016,     mvas, "OTHER")
loopNonttbar("2017",    s.sources_nonttbar_2017,     nonttbar_file_2017,     mvas, "OTHER")
loopNonttbar("2018pre", s.sources_nonttbar_2018pre,  nonttbar_file_2018pre,  mvas, "OTHER")
loopNonttbar("2018post",s.sources_nonttbar_2018post, nonttbar_file_2018post, mvas, "OTHER")
loopNonttbar("2016",    s.sources_signal,            nonttbar_file_2016,     mvas, "RPV_550")
loopNonttbar("2017",    s.sources_signal_2017,       nonttbar_file_2017,     mvas, "RPV_550")
loopNonttbar("2018pre", s.sources_signal_2018pre,    nonttbar_file_2018pre,  mvas, "RPV_550")
loopNonttbar("2018post",s.sources_signal_2018post,   nonttbar_file_2018post, mvas, "RPV_550")
loopttbar("2016",       s.sources_ttbar,             ttbar_file_2016,        mvas)
loopttbar("2017",       s.sources_ttbar_2017,        ttbar_file_2017,        mvas)
loopttbar("2018pre",    s.sources_ttbar_2018pre,     ttbar_file_2018pre,     mvas)
loopttbar("2018post",   s.sources_ttbar_2018post,    ttbar_file_2018post,    mvas)
    
line_JEC    = s.makeLine("Jet energy scale", "JECUp","JECUp","JECUp","JECUp", "JEC","JEC","JEC","JEC", "JEC","JEC","JEC","JEC")
line_JER    = s.makeLine("Jet energy resolution", "JERUp","JERUp","JERUp","JERUp", "JER","JER","JER","JER", "JER","JER","JER","JER")
line_btg    = s.makeLine("\\cPqb tagging", "btg","btg","btg","btg", "btg","btg","btg","btg", "btg","btg","btg","btg")
line_lep    = s.makeLine("Lepton id/iso/trigger", "lep","lep","lep","lep", "lep","lep","lep","lep", "lep","lep","lep","lep")
line_ht     = s.makeLine("\\HT (fit extrapolation)", "ht","ht","ht","ht", "ht","ht","ht","ht", None,None,None,None)
line_httail = s.makeLine("\\HT (high \\HT tail corr.)", "httail","httail","httail","httail", None, None, None, None, None,None,None,None)
line_htnjet = s.makeLine("\\HT (\\njets dependence)", "htnjet","htnjet","htnjet","htnjet", None, None, None, None, None,None,None,None)
line_pdf    = s.makeLine("PDF", "pdf","pdf","pdf","pdf", "pdf","pdf","pdf","pdf", "pdf","pdf","pdf","pdf")
line_pu     = s.makeLine("PU Reweighting", "pu","pu","pu","pu", "pu","pu","pu","pu", "pu","pu","pu","pu")
line_prf    = s.makeLine("Prefiring", None,"prf",None,None,None,"prf",None,None, None,"prf", None, None)
line_scl    = s.makeLine("Fact/Renorm scale", "scl","scl","scl","scl", "scl","scl","scl","scl", "scl","scl","scl","scl")
line_isr    = s.makeLine("ISR", "ISR","ISR","ISR","ISR", None,None,None,None, None,None,None,None)
line_fsr    = s.makeLine("FSR", "FSR","FSR","FSR","FSR", None,None,None,None, None,None,None,None)
line_nom    = s.makeLine("Nominal shape difference", "nom","nom","nom","nom", None,None,None,None, None,None,None,None)
line_shape  = s.makeLine("CR shape difference", "qcdCR","qcdCR","qcdCR","qcdCR", None,None,None,None, None,None,None,None)
line_jetmpt = s.makeLine("Jet mass-\\pt", "mpTScaled","mpTScaled","mpTScaled","mpTScaled", None,None,None,None, None,None,None,None)
line_noht   = s.makeLine("No \\HT reweight", "noHT","noHT","noHT","noHT", None,None,None,None, None,None,None,None)
line_hdamp  = s.makeLine("ME-PS Matching", "hdampUp","hdampUp","hdampUp","hdampUp", None,None,None,None, None,None,None,None)
line_erdOn  = s.makeLine("Color Reconnection", "erdOn","erdOn","erdOn","erdOn", None,None,None,None, None,None,None,None)
line_under  = s.makeLine("Underlying Event", "underlyingEvtUp","underlyingEvtUp","underlyingEvtUp","underlyingEvtUp", None,None,None,None, None,None,None,None)

table.write("\n".join([line_JEC,line_JER,line_btg,line_lep,line_ht,line_httail,line_htnjet,line_pdf,line_prf,line_pu,line_scl, line_isr, line_fsr, line_nom, line_shape, line_jetmpt, line_noht, line_hdamp, line_erdOn, line_under]))

posttex="""
\end{tabular}
"""
table.write(posttex)
table.close()
