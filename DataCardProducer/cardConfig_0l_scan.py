from collections import OrderedDict
# ---------------------------------
# Systematics for minor backgrounds
# ---------------------------------
# all backgrounds are entries in the dictionary. the path to the root file (starting from base path) and the systematic uncertainty are specified
# "NAME OF PROCESS" : {
#     "path"      : "Name of ROOT file containing Njets histograms (Run2UL_TT.root)",
#     "sys"       : "Flat normalization systematic to apply to all bins (1.2)",
#     "hist"      : "Name of Njets histogram to load event counts from (h_njets_12incl_1l_ABCD)",
#     "type"      : "bkg" or "sig" or "obs" for real data,
#     "fit"       : Include specific bkg or sig component in the fit (boolean),
#     "inj"       : Include specific bkg or sig component into total composite pseudoData(S) (boolean),
#     "processID" : Number for "process" line in datacard signal must be 0 and TT should be 1
#     "start"     : Starting Njets bin in histogram (7),
#     "end"       : Ending Njets bin in histogram (12),
# }

obs_hist  = "h_njets_13incl_$MODELS_$CHANNEL_ABCD_$DISC1_$DISC2"
obs_start = 8
obs_end   = 13

observed = OrderedDict()
observed["$MODEL_$MASS"] = {
        "path"      : "$YEAR_$MODELS_$MASS.root",
        "sys"       : 1.05,
        "hist"      : obs_hist, 
        "type"      : "sig", 
        "fit"       : True,
        "inj"       : False, # Choice of signal injection into pseudoDataS is handled by command line option
        "mcStat"    : True,
        "processID" : 0,
        "start"     : obs_start,
        "end"       : obs_end,
    }
observed["TT"] = {
        "path"      : "$YEAR_TT.root",
        "sys"       : 1.0, # 1.2
        "hist"      : obs_hist, 
        "type"      : "bkg", 
        "fit"       : True,
        "inj"       : False, # Don't inject data
        "mcStat"    : False, # Handled in general systematics because it has a different form
        "processID" : 1,
        "start"     : obs_start,
        "end"       : obs_end,
    }
observed["QCD"] = {
        "path"      : "$YEAR_$MODELS_$CHANNEL_QCDCR_Prediction.root",
        "sys"       : 1.0, 
        "hist"      : "$YEAR_Data_only_QCD_$MODELS_$CHANNEL_QCDCR_$DISC1_$DISC2", 
        "type"      : "bkg", 
        "fit"       : True,
        "inj"       : True,
        "mcStat"    : True,
        "processID" : 2,
        "start"     : obs_start,
        "end"       : obs_end,
    }
observed["TTX"] = {
        "path"      : "$YEAR_TTX.root",
        "sys"       : 1.2,
        "hist"      : obs_hist, 
        "type"      : "bkg", 
        "fit"       : True,
        "inj"       : True,
        "mcStat"    : True,
        "processID" : 3,
        "start"     : obs_start,
        "end"       : obs_end,
    }
observed["Other"] = {
        "path"      : "$YEAR_BG_OTHER.root",
        "sys"       : 1.2,
        "hist"      : obs_hist,
        "type"      : "bkg",
        "fit"       : True,
        "inj"       : True,
        "mcStat"    : True,
        "processID" : 4,
        "start"     : obs_start, # starting njet bin
        "end"       : obs_end,
    }
observed["TT_MC"] = {
        "path"      : "$YEAR_TT.root",
        "sys"       : 1.0, # 1.2
        "hist"      : obs_hist, 
        "type"      : "bkg", 
        "fit"       : False,
        "inj"       : True,
        "mcStat"    : False,
        "processID" : -999,
        "start"     : obs_start,
        "end"       : obs_end,
    }

# ---------------------------------
# Systematics for TT, TTvar and QCD
# ---------------------------------

# other systematics. list the name of background/signal the systematic applies to under the "apply" key
# "NAME OF SYSTEMATIC" : {
#     "path"  : "Name of ROOT file containing Njets histograms (Run2UL_TT_TTvar_Syst_1l.root)",
#     "hist"  : "Name of Njets histogram to load syst values from (MCcorr_Ratio_MC_$SYST)",
#     "distr" : "Type of distribution for systematic - see Combine documentation (lnN),
#     "proc"  : "Which bkg or sig process to apply systematic to (TT)",
#     "type"  : "sys" for pure systematic or "corr" for MC correction factor in ABCD calculation,
#     "start" : Starting Njets bin in histogram (7),
#     "end"   : Ending Njets bin in histogram (12),
#     "njets" : Total number of Njets bins for each A, B, C, D region (6)
# }

sys_path_tt     = "$YEAR_TT.root" # including TT and QCD
sys_path_qcd    = "$YEAR_$MODELS_$CHANNEL_QCDCR_Prediction.root"
sys_type        = "sys"
sys_start       = 8
sys_end         = 13

systematics = {

    # Closure Correction 
    "ClosureCorrection" : {
        "path"  : sys_path_tt,
        "hist"  : "$YEAR_MCcorr_TT_TT_$MODELS_$CHANNEL_$DISC1_$DISC2",
        "distr" : "lnN",
        "proc"  : "TT",
        "type"  : "corr",
        "start" : sys_start, 
        "end"   : sys_end, 
    },

    # MC-based TT systematics: Statistical uncertainty on Closure Correction 
    "ClosureCorrection_StatUnc" : {
        "path"  : sys_path_tt,
        "hist"  : "$YEAR_MCcorr_TT_TT_$MODELS_$CHANNEL_$DISC1_$DISC2",
        "distr" : "param",
        "proc"  : "TT",
        "type"  : "mcStat",
        "start" : sys_start,
        "end"   : sys_end,
    },

    # Data-based TT systematics: Corrected Data Closure
    "CorrectedDataClosure" : {
        "path"  : sys_path_tt,
        "hist"  : "$YEAR_maximum_MCcorrectedData_Syst_All_$MODELS_$CHANNEL_$DISC1_$DISC2",
        "distr" : "lnN",
        "proc"  : "TT",
        "uncorr": True,
        "type"  : sys_type,
        "start" : sys_start,
        "end"   : sys_end,
    },

    # QCD TF (transfer factor)
    "QCD_TF" : {
        "path"  : sys_path_qcd,
        "hist"  : "$YEAR_TF_$MODELS_$CHANNEL_$DISC1_$DISC2Over$MODELS_$CHANNEL_QCDCR_$DISC1_$DISC2ABCD",
        "distr" : "lnN",
        "proc"  : "QCD",
        "type"  : "TF",
        "start" : sys_start, 
        "end"   : sys_end, 
    },

    ## QCD syst.
    #"QCD_Syst" : {
    #    "path"  : sys_path,
    #    "hist"  : "Run2UL_QCDCR_syst_0l", # need to put correct histo here
    #    "distr" : "lnN",
    #    "proc"  : "QCD",
    #    "type"  : sys_type,
    #    "start" : sys_start,
    #    "end"   : sys_end,
    #},
}

# Up/Down Variations on minor background
var_list  = ["JEC", "JER", "btg", "jet", "pdf", "prf", "pu", "scl", "ttg"] 
#var_list  = ["JEC", "JER", "btg", "fsr", "isr", "jet", "pdf", "prf", "pu", "scl", "ttg"] 
var_proc  = ["TTX", "Other"]

for var in var_list:
    for proc in var_proc:
        name = "BG_OTHER" if proc == "Other" else proc
        up = "up" if var in ["JEC", "JER"] else "Up"
        down = "down" if var in ["JEC", "JER"] else "Down"

        systematics["{}_{}".format(proc, var)] = {
            "path"      : "$YEAR_{}.root".format(name),
            "upHist"    : "h_njets_13incl_$MODELS_$CHANNEL_ABCD_{}{}_$DISC1_$DISC2".format(var, up),
            "downHist"  : "h_njets_13incl_$MODELS_$CHANNEL_ABCD_{}{}_$DISC1_$DISC2".format(var, down),
            "nomHist"   : "h_njets_13incl_$MODELS_$CHANNEL_ABCD_$DISC1_$DISC2".format(var),
            "distr"     : "lnN",
            "proc"      : proc,
            "type"      : "sys",
            "start"     : sys_start, 
            "end"       : sys_end, 
        }

# Up/Down Variations on signal
for var in var_list:
    if var is "scl" or var is "isr" or var is "fsr":
        continue
    
    up = "up" if var in ["JEC", "JER"] else "Up"
    down = "down" if var in ["JEC", "JER"] else "Down"

    systematics["SIG_{}".format(var)] = {
            "path"      : "$YEAR_$MODELS_$MASS.root",
            "upHist"    : "h_njets_13incl_$MODELS_$CHANNEL_ABCD_{}{}_$DISC1_$DISC2".format(var, up),
            "downHist"  : "h_njets_13incl_$MODELS_$CHANNEL_ABCD_{}{}_$DISC1_$DISC2".format(var, down),
            "nomHist"   : "h_njets_13incl_$MODELS_$CHANNEL_ABCD_$DISC1_$DISC2".format(var),
            "distr"     : "lnN",
            "proc"      : "SIG",
            "type"      : "sys",
            "start"     : sys_start, 
            "end"       : sys_end, 
        }

# MC-based TT syst. come from the uncertainty on the each Closure Correction Factor Ratio (TTvar / TT)
# Divided into detector-based and modeling-based categories (at the moment)
#MCcorr_Systs_Det = [
#                    "JECup", "JECdown", 
#                    "JERup", "JERdown"
#]
#MCcorr_Systs_Mod = [
#                    "fsrUp", "fsrDown",
#                    "isrUp", "isrDown", 
#                    "erdON", 
#                    "hdampUP", "hdampDOWN", 
#                    "TuneCP5up", "TuneCP5down"
#]
#
#for syst in MCcorr_Systs_Det + MCcorr_Systs_Mod:
#    systName = "TT_%s"%(syst)
#    systematics[systName] = {
#        "path"  : sys_path,
#        "hist"  : sys_hist,
#        "distr" : "lnN",
#        "proc"  : "TT",
#        "type"  : sys_type,
#        "start" : sys_start, 
#        "end"   : sys_end,
#    }

special = {
    "NoSigBCD": False
}
