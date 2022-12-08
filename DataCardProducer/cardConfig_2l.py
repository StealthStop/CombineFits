# ---------------------------------
# Systematics for minpr backgrounds
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

obs_hist  = "h_njets_11incl_$MODELS_$CHANNEL_ABCD"
obs_start = 6
obs_end   = 11

observed = {
    "$MODEL_$MASS" : {
        "path"      : "$YEAR_$MODEL_mStop-$MASS.root",
        "sys"       : 1.05,
        "hist"      : obs_hist, 
        "type"      : "sig", 
        "fit"       : True,
        "inj"       : False, # Choice of signal injection into pseudoDataS is handled by command line option
        "processID" : 0,
        "start"     : obs_start,
        "end"       : obs_end,
    },
    "TT" : {
        "path"      : "$YEAR_TT.root",
        "sys"       : 1.0, 
        "hist"      : obs_hist, 
        "type"      : "bkg", 
        "fit"       : True,
        "inj"       : True,
        "processID" : 1,
        "start"     : obs_start,
        "end"       : obs_end,
    },
    "QCD" : {
        "path"      : "$YEAR_QCD.root",
        "sys"       : 1.0,
        "hist"      : obs_hist,
        "type"      : "bkg", 
        "fit"       : True,
        "inj"       : True,
        "processID" : 2,
        "start"     : obs_start,
        "end"       : obs_end,
    },
    "TTX" : {
        "path"      : "$YEAR_TTX.root",
        "sys"       : 1.2,
        "hist"      : obs_hist, 
        "type"      : "bkg", 
        "fit"       : True,
        "inj"       : True,
        "processID" : 3,
        "start"     : obs_start,
        "end"       : obs_end,
    },
    "Other" : {
        "path"      : "$YEAR_BG_OTHER.root",
        "sys"       : 1.2,
        "hist"      : obs_hist,
        "type"      : "bkg",
        "fit"       : True,
        "inj"       : True,
        "processID" : 4,
        "start"     : obs_start, # starting njet bin
        "end"       : obs_end,
    }
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

sys_path  = "$YEAR_TT_TTvar_Syst_$MODELS_550_$CHANNEL_0.6_0.6.root" # including TT and QCD
sys_hist  = "$YEAR_MCcorr_Ratio_MC_$SYST"
sys_type  = "sys"
sys_start = 6
sys_end   = 11

systematics = {
    # Data-based TT systematics: Corrected Data Closure
    "CorrectedDataClosure" : {
        "path"  : sys_path,
        "hist"  : "$YEAR_maximum_MCcorrectedData_Syst_All",
        "distr" : "lnN",
        "proc"  : "TT",
        "type"  : sys_type,
        "start" : sys_start, 
        "end"   : sys_end, 
    },
    # MC-based TT systematics: Closure Correction Factor Ratio (TTvar/TT) in signal region (at boundary value 1.0)
    "MCcorrectionRatio" : {
        "path"  : sys_path,
        "hist"  : "$YEAR_MCcorr_TT_TT",
        "distr" : "lnN",
        "proc"  : "TT",
        "type"  : "corr",
        "start" : sys_start, 
        "end"   : sys_end, 
    },

    # There is QCD estimation for 2l
    # So, derive from MC - inside observed dictionary above
}

# MC-based TT syst. come from the uncertainty on the each Closure Correction Factor Ratio (TTvar / TT)
# Divided into detector-based and modeling-based categories (at the moment)
MCcorr_Systs_Det = [
                    "JECup", "JECdown", 
                    "JERup", "JERdown"
]
MCcorr_Systs_Mod = [
                    "fsrUp", "fsrDown",
                    "isrUp", "isrDown", 
                    "erdON", 
                    "hdampUP", "hdampDOWN", 
                    "TuneCP5up", "TuneCP5down"
]

for syst in MCcorr_Systs_Det + MCcorr_Systs_Mod:
    systName = "TT_%s"%(syst)
    systematics[systName] = {
        "path"  : sys_path,
        "hist"  : sys_hist,
        "distr" : "lnN",
        "proc"  : "TT",
        "type"  : sys_type,
        "start" : sys_start, 
        "end"   : sys_end,
    }
