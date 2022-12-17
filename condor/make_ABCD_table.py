from optparse import OptionParser
import ROOT
import glob
import os
from math import sqrt

class Table:
    
    #Dict with all table information
    def __init__(self, pre_nps, post_nps, pre_A_bins, post_A_bins, prebkg, postbkg, data, base_dir):
        self.pre_nps = pre_nps
        self.post_nps = post_nps
        self.pre_A_bins = pre_A_bins
        self.post_A_bins = post_A_bins
        self.prebkg = prebkg
        self.postbkg = postbkg
        self.data = data

        self.name = pre_nps['name']
        self.suf = self.name[-2:]
        self.base_dir = base_dir[:-1]

        print(self.pre_nps['name'])
        print(self.post_nps['name'])
        print(self.pre_A_bins['name'])
        print(self.post_A_bins['name'])
        print(self.prebkg['name'])
        print(self.postbkg['name'])
        print(self.data['name'])

    def get_closure_est(self,i):
        closure_est = round(self.pre_nps["vals"]["beta{}_{}".format(i, self.suf)] * self.pre_nps["vals"]["gamma{}_{}".format(i, self.suf)] / self.pre_nps["vals"]["delta{}_{}".format(i, self.suf)],2)
        return closure_est

    def make_table_cols(self):
        cols = {'name': self.pre_A_bins['name'], 'nA_Act': [], 'nA_Pred':[], 'fitTT':[], 'ccPerf':[], 'ccPre':[], 'ccPost':[]}
        for i in range(7,12):
            cols["nA_Act"].append(self.get_unc_str("A{}".format(i), self.pre_A_bins))
            cols["nA_Pred"].append(self.get_closure_est(i))
            cols["fitTT"].append(self.get_unc_str("A{}".format(i), self.post_A_bins))
            cols["ccPerf"].append(round(self.pre_A_bins["vals"][("A{}".format(i))]/self.get_closure_est(i), 2))
            cols["ccPre"].append(self.get_unc_str("np_ClosureNj{}_{}".format(i, self.suf), self.pre_nps))
            cols["ccPost"].append(self.get_unc_str("np_ClosureNj{}_{}".format(i, self.suf), self.post_nps))
            
        return cols

    def make_table2_cols(self):
        cols = {'name': self.pre_A_bins['name'], 'nA_pre':[], 'nA_post':[], 'nA_data':[], 'nB_pre':[], 'nB_post':[], 'nB_data':[], 'nC_pre':[], 'nC_post':[], 'nC_data':[], 'nD_pre':[], 'nD_post':[], 'nD_data':[]}
        for reg in ['A', 'B', 'C', 'D']:
            for i in range(7,12):
                cols["n{}_pre".format(reg)].append(self.get_unc_str("{}{}".format(reg, i), self.prebkg))
                cols["n{}_post".format(reg)].append(self.get_unc_str("{}{}".format(reg, i), self.postbkg))
                cols["n{}_data".format(reg)].append(self.get_unc_str("{}{}".format(reg, i), self.data))
            
        return cols
        

    # Write Latex table to file
    def write_table(self, landing_dir):

        cols = self.make_table_cols()

        f_out = open("{}/ABCD_table_{}_{}.tex".format(landing_dir, cols['name'], self.base_dir), 'w')

        f_out.write('''\documentclass[11pt,a4paper,english]{article} % document type and language

\usepackage{lscape}
\usepackage{babel}   % multi-language support
\usepackage{float}   % floats
\usepackage{url}     % urls \n\n''')

        f_out.write("\\begin{document} \n\n")
        f_out.write("% {} \n \n".format(cols['name']))
        f_out.write("\\resizebox{\\textwidth}{!}{\\begin{tabular}{ l | l | l | l | l | l | l } \n")
        f_out.write("{} & {} & {} & {} & {} & {} & {} \\\\ \n".format('$N_J$', '$TT_{A,Actual}$', '$TT_{A,Expected}$', '$TT_{A,Post}$', 'Closure Correction Perfect', 'Closure Correction Pre', 'Closure Correction Post'))
        f_out.write("\hline \n")
        for i in range(len(cols["nA_Act"])):
            f_out.write("${}$ & ${}$ & ${}$ & ${}$ & ${}$ & ${}$ & ${}$ \\\\ \n".format(i+7, cols["nA_Act"][i], cols["nA_Pred"][i], cols["fitTT"][i], cols["ccPerf"][i], cols["ccPre"][i], cols["ccPost"][i]))
        f_out.write("\\end{tabular}}\n \n")

        f_out.write("\\vspace{3em}\n \n")

        cols = self.make_table2_cols()

        f_out.write("\\resizebox{\\textwidth}{!}{\\begin{tabular}{ l | l | l | l | l | l | l | l | l | l | l | l | l } \n")
        f_out.write("{} & {} & {} & {} & {} & {} & {} & {} & {} & {} & {} & {} & {} \\\\ \n".format('$N_J$', 'A Pre', 'A Post', 'A Data', 'B Pre', 'B Post', 'B Data', 'C Pre', 'C Post', 'C Data', 'D Pre', 'D Post', 'D Data'))
        f_out.write("\hline \n")
        for i in range(len(cols["nA_pre"])):
            f_out.write("${}$ & ${}$ & ${}$ & ${}$ & ${}$ & ${}$ & ${}$ & ${}$ & ${}$ & ${}$ & ${}$ & ${}$ & ${}$ \\\\ \n".format(i+7, cols["nA_pre"][i], cols["nA_post"][i], cols["nA_data"][i], cols["nB_pre"][i], cols["nB_post"][i], cols["nB_data"][i], cols["nC_pre"][i], cols["nC_post"][i], cols["nC_data"][i], cols["nD_pre"][i], cols["nD_post"][i], cols["nD_data"][i]))
        f_out.write("\\end{tabular}}\n \n")
        f_out.write("\\end{document} \n\n")

        f_out.close()

        here = os.getcwd()
        
        os.chdir(landing_dir)
        os.system("pdflatex {}".format("ABCD_table_{}_{}.tex".format(cols['name'],self.base_dir)))

        os.chdir(here)

        print("New table created: {}".format("{}/ABCD_table_{}_{}.tex".format(landing_dir, cols['name'], self.base_dir)))

        return

    def get_unc_str(self, name, vals):
        unc_str = str(round(vals["vals"][name],2)) + " \pm " + str(round(vals["unc"][name],2))
        return unc_str

    def printTable(self):
        print(self.pre_nps)
        print(self.post_nps)
        print(self.pre_A_bins)
        print(self.post_A_bins)

def getPreFitVals(fname, signal, mass, year):

    # Open root file and collect all the necessary values
    f = ROOT.TFile.Open(fname)

    suf = fname[-7:-5]

    w = f.w

    params = {}
    unc = {}

    np_list = []
    for i in range(7, 12):
        np_list += ['beta{}_{}'.format(i,suf), 'gamma{}_{}'.format(i,suf), 'delta{}_{}'.format(i,suf), 'np_ClosureNj{}_{}'.format(i,suf)]

    for par in np_list:
        params[w.var(par).GetName()] = w.var(par).getVal()
        unc[w.var(par).GetName()] = w.var(par).getError()

    f.Close()

    return {'name':'{}_{}_{}_{}'.format(signal, mass, year, suf), 'vals':params, 'unc':unc}

def getPostFitVals(fname, signal, mass, year):
    
    # Open root file and collect all the necessary values
    f = ROOT.TFile.Open(fname)

    suf = fname[-7:-5]

    argList = f.fit_b.floatParsFinal()

    params = {}
    unc = {}

    np_list = ['alpha', 'beta', 'gamma', 'delta', 'np_Closure']

    for par in range(0, len(argList)):
        if any(x in argList[par].GetName() for x in np_list):
            params[argList[par].GetName()] = argList[par].getVal()
            unc[argList[par].GetName()] = argList[par].getError()

    f.Close()
    
    return {'name':'{}_{}_{}_{}'.format(signal, mass, year, suf), 'vals':params, 'unc':unc}

def getPreABin(fname, signal, mass, year, suf, Run2):

    if Run2:
        sf = 137.0 / 35.9
    else:
        sf = 1

    f = ROOT.TFile.Open(fname)

    bins = {}
    unc = {}

    for bin in range(1,6):
        bins['A{}'.format(bin+6)] = sf * f.Get('h_njets_11incl_{}_ABCD'.format(suf)).GetBinContent(bin)
        unc['A{}'.format(bin+6)] = sqrt(sf) * f.Get('h_njets_11incl_{}_ABCD'.format(suf)).GetBinError(bin)

    f.Close()

    return {'name':'{}_{}_{}_{}'.format(signal, mass, year, suf), 'vals':bins, 'unc':unc}

def getPostABin(fname, signal, mass, year):

    f = ROOT.TFile.Open(fname)

    suf = fname[-7:-5]

    bins = {}
    unc = {}

    for bin in range(7,12):
        for l in ['0l', '1l']:
            if fname.find(l) != -1:
                bins['A{}'.format(bin)] = f.Get('shapes_fit_b/Y{}_A{}_{}/TT'.format(year[-2:], bin, l)).GetBinContent(1)
                unc['A{}'.format(bin)] = f.Get('shapes_fit_b/Y{}_A{}_{}/TT'.format(year[-2:], bin, l)).GetBinError(1)

    f.Close()

    return {'name':'{}_{}_{}_{}'.format(signal, mass, year, suf), 'vals':bins, 'unc':unc}

def getAllBkgPre(fname, signal, mass, year):
    
    f = ROOT.TFile.Open(fname)

    suf = fname[-7:-5]

    bins = {}
    unc = {}

    for reg in ['A', 'B', 'C', 'D']:
        for bin in range(7,12):
            for l in ['0l', '1l']:
                if fname.find(l) != -1:
                    bins['{}{}'.format(reg,bin)] = f.Get('shapes_prefit/Y{}_{}{}_{}/total'.format(year[-2:], reg, bin, l)).GetBinContent(1)
                    unc['{}{}'.format(reg,bin)] = f.Get('shapes_prefit/Y{}_{}{}_{}/total'.format(year[-2:], reg, bin, l)).GetBinError(1)

    f.Close()

    return {'name':'{}_{}_{}_{}'.format(signal, mass, year, suf), 'vals':bins, 'unc':unc}

def getAllBkgPost(fname, signal, mass, year):

    f = ROOT.TFile.Open(fname)

    suf = fname[-7:-5]

    bins = {}
    unc = {}

    for reg in ['A', 'B', 'C', 'D']:
        for bin in range(7,12):
            for l in ['0l', '1l']:
                if fname.find(l) != -1:
                    bins['{}{}'.format(reg,bin)] = f.Get('shapes_fit_b/Y{}_{}{}_{}/total'.format(year[-2:], reg, bin, l)).GetBinContent(1)
                    unc['{}{}'.format(reg,bin)] = f.Get('shapes_fit_b/Y{}_{}{}_{}/total'.format(year[-2:], reg, bin, l)).GetBinError(1)

    f.Close()

    return {'name':'{}_{}_{}_{}'.format(signal, mass, year, suf), 'vals':bins, 'unc':unc}

def getData(fname, signal, mass, year):

    f = ROOT.TFile.Open(fname)

    suf = fname[-7:-5]

    bins = {}
    unc = {}

    for reg in ['A', 'B', 'C', 'D']:
        for bin in range(7,12):
            for l in ['0l', '1l']:
                if fname.find(l) != -1:
                    bins['{}{}'.format(reg,bin)] = f.Get('shapes_prefit/Y{}_{}{}_{}/data'.format(year[-2:], reg, bin, l)).Eval(0.5)
                    unc['{}{}'.format(reg,bin)] = f.Get('shapes_prefit/Y{}_{}{}_{}/data'.format(year[-2:], reg, bin, l)).GetHistogram().GetBinError(1)

    f.Close()

    return {'name':'{}_{}_{}_{}'.format(signal, mass, year, suf), 'vals':bins, 'unc':unc}

def getOption(option, failMessage):
    if option:
        return option
    else:
        print failMessage
        exit(0)

def getOptionList(option, failMessage):
    l = []
    if option:
        if option.find("-") != -1:
            low, high = option.split("-")
            l = [str(x) for x in range(int(low), int(high) + 50, 50)]
        else:
            l = option.split(',')
        return l
    else:
        print failMessage
        exit(0)

def main():
    
    parser = OptionParser()
    parser.add_option("-s", "--signal", action="store", type="string", dest="signal", default="RPV", help="Signal process name")
    parser.add_option("-y", "--year", action="store", type="string", dest="year", default="2016", help="Year for data used")
    parser.add_option("-m", "--mass", action="store", type="string", dest="mass", default="400", help="Mass of stop in GeV")
    parser.add_option("-d", "--dataType", action="store", type="string", dest="dataType", default="pseudoData", help="Mass of stop in GeV")
    parser.add_option ('--basedir',         dest='basedir',  type='string', default = '.', help="Path to output files")
    parser.add_option ('--input',         dest='input',  type='string', default = '../DataCardProducer/2016_DisCo_0L_Cand1_1L/', help="Path to output files")
    parser.add_option ('--Run2',         dest='Run2',  action='store_true', default = False, help="Scale to Run 2 lumi")
    parser.add_option("--all", action="store_true", dest="all", default=False, help="Make all pre and post fit distributions (for 0l and 1l, pseudoData/S, RPV and SYY)")
    

    (options, args) = parser.parse_args()

    signal = getOption(options.signal, "No dataset specified")
    year = getOption(options.year, "No mass model specified")
    mass = getOption(options.mass, "No mass model specified")
    basedir = getOption(options.basedir, "No base directory specified")
    input = getOption(options.input, "No NN input directory specified")
    Run2 = options.Run2
    
    ROOT.TH1.AddDirectory(False)

    pre_file_names = glob.glob("./{0}/output-files/{1}_{2}_{3}/ws_{3}_{1}_{2}_pseudoData_?l.root".format(basedir, signal, mass, year))

    post_file_names = glob.glob("./{0}/output-files/{1}_{2}_{3}/fitDiagnostics{3}{1}{2}pseudoData?l.root".format(basedir, signal, mass, year))

    landing_dir = "./{}/output-files/tables".format(basedir)

    print(pre_file_names)
    print(post_file_names)

    if pre_file_names[0].find("1l") != -1:
        pre_file_names.reverse()

    if post_file_names[0].find("1l") != -1:
        post_file_names.reverse()

    if not os.path.exists(landing_dir):
        os.makedirs(landing_dir)    

    input_files = glob.glob("{}/2016_TT.root".format(input))
    pre_nps = [getPreFitVals(f, signal, mass, year) for f in pre_file_names]
    post_nps = [getPostFitVals(f, signal, mass, year) for f in post_file_names]
    pre_A_bins = [getPreABin(input_files[0], signal, mass, year, suf, Run2) for suf in ["0l", "1l"]]
    post_A_bins = [getPostABin(f, signal, mass, year) for f in post_file_names]

    prebkg = [getAllBkgPre(f, signal, mass, year) for f in post_file_names]
    postbkg = [getAllBkgPost(f, signal, mass, year) for f in post_file_names]
    data = [getData(f, signal, mass, year) for f in post_file_names]

    for (a,b,c,d,e,f,g) in zip(pre_nps, post_nps, pre_A_bins, post_A_bins, prebkg, postbkg, data):
        table = Table(a,b,c,d,e,f,g, basedir)
        table.write_table(landing_dir)


if __name__ == "__main__":
    main()
