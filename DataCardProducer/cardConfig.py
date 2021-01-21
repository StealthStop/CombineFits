path = "/uscms/home/jhiltb/nobackup/susy/ZeroAndTwoLep/CMSSW_10_2_9/src/Analyzer/Analyzer/test/condor/2016_DisCo_hadd/"

lumi = 1.05

#all backgrounds are entries in the dictionary. the path to the root file (starting from base path) and the systematic uncertainty are specified
background = {
    "TT" : {
        "path" : "2016_TT.root",
        "sys"  : 1.2
    },
    "QCD" : {
        "path" : "2016_QCD.root",
        "sys"  : 1.2
    },
    "DYJetsToLL" : {
        "path" : "2016_DYJetsToLL_M-50.root",
        "sys"  : 1.2
    },
    "Diboson" : {
        "path" : "2016_Diboson.root",
        "sys"  : 1.2
    },
    "Other" : {
        "path" : "2016_Other.root",
        "sys"  : 1.2
    },
    "ST" : {
        "path" : "2016_ST.root",
        "sys"  : 1.2
    },
    "TTX" : {
        "path" : "2016_TTX.root",
        "sys"  : 1.2
    },
    "Triboson" : {
        "path" : "2016_Triboson.root",
        "sys"  : 1.2
    },
    "WJets" : {
        "path" : "2016_WJets.root",
        "sys"  : 1.2
    },
    
}
#all signals are entries in the dictionary. the path to the root file (starting from the base path) and the systematic uncertainty are specified 
signal = {
    "RPV350" : {
        "path" : "2016_RPV_2t6j_mStop-350.root",
        "sys"  : "--"

    },
#    "RPV550" : {
#        "path" : "None",
#        "sys"  : 1.504
#    }
}
#the names of the histograms to use along with number of bins to divide it into, which bin to start from, and which to end. use "last" to use the last bin
histos = {
    "hA_7" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets7_A",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hA_8" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets8_A",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hA_9" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets9_A",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hA_10" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets10_A",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hA_11" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets11_A",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hB_7" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets7_B",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hB_8" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets8_B",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hB_9" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets9_B",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hB_10" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets10_B",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hB_11" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets11_B",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hC_7" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets7_C",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hC_8" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets8_C",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hC_9" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets9_C",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hC_10" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets10_C",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hC_11" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets11_C",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hD_7" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets7_D",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hD_8" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets8_D",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hD_9" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets9_D",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hD_10" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets10_D",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
    "hD_11" : {
        "name"  : "h_DoubleDisCo_disc1_disc2_Njets11_D",
        "nbins" : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start" : 50, #if histogram is 2d, input as list [start x, start y]
        "end"   : 150, #if histogram is 2d, input as list [end x, end y]
        "disco" : True #option to bypass info above for double disco cards, bypass if True
    },
}
#other systematics. list the name of background/signal the systematic applies to under the "apply" key
othersys = {

    #"s1" : {
    #    "sys" : 2.05,
    #    "distr" : "gmN 4",
    #    "apply" : ["TT"]
    #}
}
