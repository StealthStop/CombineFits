import sys

#path = "./%s/"%(str(sys.argv[8]))

lumi = 1.05

year = 2016

#mass = int(sys.argv[6])

#model = str(sys.argv[7])

#all backgrounds are entries in the dictionary. the path to the root file (starting from base path) and the systematic uncertainty are specified
#observed = {
#    "Data" : {
#        "path" : "2016_Data.root",
#    },
#}

observed = {
    "Other" : {
        "path" : "2016_BG_OTHER.root",
        "sys"  : 1.0
    },
#   "DYJets" : {
#       "path" : "2016_DYJetsToLL_M-50.root",
#       "sys"  : 1.0
#   },
#   "Diboson" : {
#       "path" : "2016_Diboson.root",
#       "sys"  : 1.0
#   },
    "QCD" : {
        "path" : "2016_QCD.root",
        "sys"  : 1.0
    },
#   "ST" : {
#       "path" : "2016_ST.root",
#       "sys"  : 1.0
#   },
    "TT" : {
        "path" : "2016_TT.root",
        "sys"  : 1.2
    },
    "TTX" : {
        "path" : "2016_TTX.root",
        "sys"  : 1.0
    },
#   "Triboson" : {
#       "path" : "2016_Triboson.root",
#       "sys"  : 1.0
#   },
#   "WJets" : {
#       "path" : "2016_WJets.root",
#       "sys"  : 1.0
#   },
}

#background = {
#    "Bkgd" : {
#        "path" : "2016_Bkgd.root",
#        "sys"  : 1.2
#    },
#}

#all signals are entries in the dictionary. the path to the root file (starting from the base path) and the systematic uncertainty are specified 
#signal = {
#    "%s%d"%(model.split("_")[0],mass) : {
#        "path" : "2016_%s_mStop-%d.root"%(model,mass),
#        "sys"  : "--"
#
#    },
#    "RPV550" : {
#        "path" : "None",
#        "sys"  : 1.504
#    }
#}
#the names of the histograms to use along with number of bins to divide it into, which bin to start from, and which to end. use "last" to use the last bin
histos = {
    "ha" : {
        "region" : "A",
        "Njets"  : 7,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets7_A",
        "nbins"  : 7, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hb" : {
        "region" : "B",
        "Njets"  : 7,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets7_B",
        "nbins"  : 7, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hc" : {
        "region" : "C",
        "Njets"  : 7,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets7_C",
        "nbins"  : 7, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hd" : {
        "region" : "D",
        "Njets"  : 7,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets7_D",
        "nbins"  : 7, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "he" : {
        "region" : "A",
        "Njets"  : 8,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets8_A",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hf" : {
        "region" : "B",
        "Njets"  : 8,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets8_B",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hg" : {
        "region" : "C",
        "Njets"  : 8,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets8_C",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hh" : {
        "region" : "D",
        "Njets"  : 8,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets8_D",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hi" : {
        "region" : "A",
        "Njets"  : 9,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets9_A",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hj" : {
        "region" : "B",
        "Njets"  : 9,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets9_B",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hk" : {
        "region" : "C",
        "Njets"  : 9,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets9_C",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hl" : {
        "region" : "D",
        "Njets"  : 9,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets9_D",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hm" : {
        "region" : "A",
        "Njets"  : 10,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets10_A",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hn" : {
        "region" : "B",
        "Njets"  : 10,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets10_B",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "ho" : {
        "region" : "C",
        "Njets"  : 10,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets10_C",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hp" : {
        "region" : "D",
        "Njets"  : 10,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets10_D",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hq" : {
        "region" : "A",
        "Njets"  : 11,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets11_A",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hr" : {
        "region" : "B",
        "Njets"  : 11,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets11_B",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hs" : {
        "region" : "C",
        "Njets"  : 11,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets11_C",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "ht" : {
        "region" : "D",
        "Njets"  : 11,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets11_D",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hu" : {
        "region" : "A",
        "Njets"  : 12,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets12incl_A",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hv" : {
        "region" : "B",
        "Njets"  : 12,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets12incl_B",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hw" : {
        "region" : "C",
        "Njets"  : 12,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets12incl_C",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
    },
    "hx" : {
        "region" : "D",
        "Njets"  : 12,
        "name"   : "h_DoubleDisCo_disc1_disc2_Njets12incl_D",
        "nbins"  : 8, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 50, #if histogram is 2d, input as list [start x, start y]
        "end"    : 150, #if histogram is 2d, input as list [end x, end y]
        "disco"  : True #option to bypass info above for double disco cards, bypass if True
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
