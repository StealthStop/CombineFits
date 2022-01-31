import sys

lumi = 1.05

year = 2016

#all backgrounds are entries in the dictionary. the path to the root file (starting from base path) and the systematic uncertainty are specified
observed = {
    "Other" : {
        "path" : "2016_BG_OTHER.root",
        "sys"  : 1.2
    },
    "QCD" : {
        "path" : "2016_QCD.root",
        "sys"  : 1.2
    },
    "TT" : {
        "path" : "2016_TT.root",
        "sys"  : 1.2
    },
    "TTX" : {
        "path" : "2016_TTX.root",
        "sys"  : 1.2
    },
    #"Test" : {
    #    "path" : "TestFile_NewNjets.root",
    #    "sys"  : 1.0
    #},
}

#the names of the histograms to use along with number of bins to divide it into, which bin to start from, and which to end. use "last" to use the last bin
histos = {
    "h_njets_11incl_1l_ABCD" : {
        "name"   : "h_njets_11incl_ABCD",
        "nbins"  : 20, #if histogram is 2d, input as list [nbins x, nbins y]
        "start"  : 0, #if histogram is 2d, input as list [start x, start y]
        "end"    : "last", #if histogram is 2d, input as list [end x, end y]
        "disco"  : False #option to bypass info above for double disco cards, bypass if True
    },
}
#other systematics. list the name of background/signal the systematic applies to under the "apply" key
othersys = {
}
