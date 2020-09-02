import ROOT
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import six
import os

def pull(nP):    
    return abs(float(nP[1]))

def findNP(strings):
    found = False
    for s in strings:
        if(nP[0].find(s) != -1):
            found = True
    return found

def render_mpl_table(data, col_width=4.0, row_height=0.625, font_size=20, header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w', bbox=[0, 0, 1, 1], header_columns=0, ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)
    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return fig, ax

def dumpResultsToTempFile(inFile):
    fullfile = ROOT.TFile.Open(inFile)
    fit_b = fullfile.Get("fit_b")
    fit_s = fullfile.Get("fit_s")
    code = '''
    std::ofstream outfile_b ("tmp_b.tmp", std::ofstream::binary); 
    std::ofstream outfile_s ("tmp_s.tmp", std::ofstream::binary);
    '''
    ROOT.gInterpreter.ProcessLine(code)
    fit_b.printStream(ROOT.outfile_b, fit_b.defaultPrintContents(''), fit_b.defaultPrintStyle(''))
    fit_s.printStream(ROOT.outfile_s, fit_s.defaultPrintContents(''), fit_s.defaultPrintStyle(''))
    return ("b","tmp_b.tmp"), ("s","tmp_s.tmp")

parser = argparse.ArgumentParser()
parser.add_argument("--model",   type=str, default="RPV",   help="One of our three models, RPV, SYY, or SHH")
parser.add_argument("--mass",    type=str, default='350',   help="Mass to make plots for")
parser.add_argument("--year",    type=str, default='2016',  help="2016, 2017, or Combo")
parser.add_argument("--data",    type=str, default='Data',  help="Data, pseudoData, or pseudoDataS")
parser.add_argument("--basedir", type=str, default="FullRun2_Unblinded_Jun15", help="Directory that contains the output Fit_data_year directories")
args=parser.parse_args()
model = args.model
mass = args.mass
year = args.year
data = args.data
basedir = args.basedir

inFile = "%s/Fit_%s_%s/output-files/%s_%s_%s/fitDiagnostics%s%s%s.root" % (basedir, data, year, model, mass, year, year, model, mass)
print inFile
tmpFile_b, tmpFile_s = dumpResultsToTempFile(inFile)

fitResults = {}
for tmpFile in [tmpFile_b, tmpFile_s]:    
    nPs = []
    with open(tmpFile[1], 'r') as f:
        for line in f:
            nP = tuple(line.split())    
            if len(nP) == 4 and nP[1] != ':':
                nPs.append((nP[0],float(nP[1]),float(nP[3])))

    nPs_parsed = []
    nPs.sort(key=pull,reverse=True)
    for nP in nPs:
        if(findNP(["N7_tt_","d_tt_","Stat","a0_tt_","a1_tt_","Coef"])): continue
        #print "{:<35} {:<12} +/- {}".format(nP[0],nP[1],nP[2])
        nPs_parsed.append(nP)
        t = (tmpFile[0], nP[0], nP[1], nP[2])
        if nP[0] in fitResults:
            fitResults[nP[0]].append(t)
        else:
            fitResults[nP[0]] = [t]

    df = pd.DataFrame(nPs_parsed, columns =['Name', 'Value', 'Unc.'])
    fig, ax = render_mpl_table(df, header_columns=0, col_width=5.0)
    fig.savefig(basedir+'/pullTable_%s_%s_%s_%s.pdf' % (model, mass, year, tmpFile[0]))
    print "Saved: ", basedir+'/pullTable_%s_%s_%s_%s.pdf' % (model, mass, year, tmpFile[0])
    os.remove(tmpFile[1])

bTotChi2 = 0.0
sTotChi2 = 0.0
for nP in fitResults:
    if nP == "r" : continue
    bPull = fitResults[nP][0][2]
    sPull = fitResults[nP][1][2]
    bChi2 = bPull**2
    sChi2 = sPull**2
    bTotChi2 += bChi2
    sTotChi2 += sChi2
    print "{0:<35} {1:<12.3f} {2:<12.3f} {0:<35} {3:<12.3f} {4:<12.3f}".format(nP, bPull, bChi2, sPull, sChi2)

print "{0:<12.3f} {1:<12.3f} {2:<12.3f}".format(bTotChi2, sTotChi2, abs(bTotChi2-sTotChi2))

