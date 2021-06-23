import sys, os
from os import system, environ
import optparse 
import subprocess
import time

def makeExeAndFriendsTarball(filestoTransfer, fname, path):
    system("mkdir -p %s" % fname)
    for fn in filestoTransfer:
        system("cd %s; ln -s %s" % (fname, fn))
        
    tarallinputs = "tar czvf %s/%s.tar.gz %s --dereference"% (path, fname, fname)
    print tarallinputs
    system(tarallinputs)
    system("rm -r %s" % fname)

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
    repo = "HiggsAnalysis/CombinedLimit"
    seed = int(time.time())
    
    # Parse command line arguments
    parser = optparse.OptionParser("usage: %prog [options]\n")

    parser.add_option ('--inPut_2016',     dest='inputRoot2016',     type='string', default = 'DisCo_2016',     help="input root file directory: 2016")
    parser.add_option ('--inPut_2017',     dest='inputRoot2017',     type='string', default = 'DisCo_2017',     help="input root file directory: 2017")
    parser.add_option ('--inPut_2018pre',  dest='inputRoot2018pre',  type='string', default = 'DisCo_2018pre',  help="input root file directory: 2018pre")
    parser.add_option ('--inPut_2018post', dest='inputRoot2018post', type='string', default = 'DisCo_2018post', help="input root file directory: 2018post")
    parser.add_option ('-d',               dest='signalType',        type='string', default = '',                    help="List of signal model, comma separated")
    parser.add_option ('-t',               dest='dataType',          type='string', default = 'data',                help="Specify if running over data or pseudo data")
    parser.add_option ('--syst',           dest='syst',              type='string', default = 'None',                help="Specify what systimatic variation you want when picking a dataType")
    parser.add_option ('-s', '--suffix',           dest='suffix',              type='string', default = 'None',                help="Specify which final state (0l or 1l)")
    parser.add_option ('-m',               dest='masssets',          type='string', default = '',                    help="List of mass models, comma separated or range (e.g. 300-1400)")
    parser.add_option ('-y',               dest='year',              type='string', default = '2016',                help="year")
    parser.add_option ('-c',               dest='noSubmit',    action='store_true', default = False,                 help="Do not submit jobs.  Only create condor_submit.txt.")
    parser.add_option ('-A',               dest='doAsym',      action='store_true', default = False,                 help="Specify AsymptoticLimits and Significance fit command to run")
    parser.add_option ('-F',               dest='doFitDiag',   action='store_true', default = False,                 help="Specify FitDiagnostics fit command to run")
    parser.add_option ('-M',               dest='doMulti',     action='store_true', default = False,                 help="Specify MultiDimFit fit command to run")
    parser.add_option ('-I',               dest='doImpact',    action='store_true', default = False,                 help="Specify impact fit command to run")
    parser.add_option ('--setClosure',     dest='setClosure',  action='store_true', default = False,                 help="Specify whether to use nominal or perfect closure data cards")
    parser.add_option ('--output',         dest='outPath',           type='string', default = '.',                   help="Name of directory where output of each condor job goes")
    parser.add_option ('--inject',         dest='inject',            type='float' , default = 0,                     help="Inject signal at signal strength specified")
    parser.add_option ('--toy',            dest='toy',         action='store_true', default = False,                 help="Limits: Submit toy jobs instead of the normal set of fits")
    parser.add_option ('-T',               dest='numToys',           type='int',    default = 1000,                  help="Specify number of toys per job")
    parser.add_option ('--rMin',           dest='rMin',              type='float',  default = 0.05,                  help="Specify minimum r value")
    parser.add_option ('--rMax',           dest='rMax',              type='float',  default = 1.00,                  help="Specify maximum r value")
    parser.add_option ('--rStep',          dest='rStep',             type='float',  default = 0.05,                  help="Specify step size")
    parser.add_option ('--jPerR',          dest='jPerR',             type='int',    default = 5,                     help="Specify jobs per r setting")

    parser.add_option ('--toyS',           dest='toyS',        action='store_true', default = False,                 help="Sig.:   Submit toy jobs instead of the normal set of fits")
    parser.add_option ('--nJobs',          dest='numJobs',           type='int',    default = -1,                    help="Can specify the number of jobs for toyS")
    parser.add_option ('-i',               dest='iterations',        type='int',    default =  1,                    help="Can specify the number of iterations for toyS")

    options, args = parser.parse_args()
    signalType = getOptionList(options.signalType, "No dataset specified")
    masssets = getOptionList(options.masssets, "No mass model specified")

    doAsym = 1 if options.doAsym else 0
    doFitDiag = 1 if options.doFitDiag else 0
    doMulti = 1 if options.doMulti else 0
    doImpact = 1 if options.doImpact else 0
    doToyS = 1 if options.toyS else 0 
    setClosure = 1 if options.setClosure else 0
    if not doAsym and not doFitDiag and not doMulti and not doImpact:
        doAsym=1
        doFitDiag=1
        doMulti=1
        doImpact=1

    executable = "run_fits_disco.sh"
    if options.toy or options.toyS:
        executable = "run_toys.sh"

    fileParts = []
    fileParts.append("Universe   = vanilla\n")
    fileParts.append("Executable = %s\n" % executable)
    fileParts.append("Should_Transfer_Files = YES\n")
    fileParts.append("WhenToTransferOutput = ON_EXIT\n")
    #fileParts.append("request_disk = 1000000\n")
    #fileParts.append("request_memory = 5000\n")
    fileParts.append("x509userproxy = $ENV(X509_USER_PROXY)\n\n")
    fileParts.append("Transfer_Input_Files = {0}/CMSSW_10_2_13.tar.gz, {0}/exestuff.tar.gz\n".format(options.outPath))

    if options.suffix == "None":
        suffixes = ['0l', '1l', 'combo']
    else:
        suffixes = [options.suffix]
    close = ""
    if options.setClosure:
        close = "_perfectClose"


    for st in signalType:
        st = st.strip()
        stauxi1 = ""; stauxi2 = ""
        if   st == "RPV":
            stauxi1 = ""; stauxi2 = "2t6j"
        elif st == "SYY":
            stauxi1 = "Stealth"; stauxi2 = "2t6j"
        elif st == "SHH":
            stauxi1 = "Stealth"; stauxi2 = "2t4b"

        model = stauxi1+st

        for mass in masssets:
            mass = mass.strip()
            for suf in suffixes:
                print st, mass, options.year, suf
                
                # create the directory
                outDir = model+"_"+mass+"_"+options.year
                if not os.path.isdir("%s/output-files/%s" % (options.outPath, outDir)):
                    os.makedirs("%s/output-files/%s" % (options.outPath, outDir))
                if not options.toy and not options.toyS:
                    outputFiles = [
                        "higgsCombine%s%s%s%s%s%s_AsymLimit.AsymptoticLimits.mH%s.MODEL%s.root" % (options.year, model, mass, options.dataType, suf, close[1:],  mass, model),
                        "higgsCombine%s%s%s%s%s%s.FitDiagnostics.mH%s.MODEL%s.root" % (options.year, model, mass, options.dataType, suf, close[1:], mass, model),
                        "higgsCombine%s%s%s%s%s%s_SignifExp.Significance.mH%s.MODEL%s.root" % (options.year, model, mass, options.dataType, suf, close[1:], mass, model),
                        "higgsCombineSCAN_r_wSig.MultiDimFit.mH%s.MODEL%s.root " % (mass, model),
                        "higgsCombine%s.HybridNew.mH%s.MODEL%s.root" % (options.year, mass, model),
                        "ws_%s_%s_%s_%s_%s%s.root"       % (options.year, model, mass, options.dataType, suf, close),
                        "fitDiagnostics%s%s%s%s%s%s.root" % (options.year, model, mass, options.dataType, suf, close[1:]), 
                        "impacts_%s%s%s.json"       % (options.year, model, mass),
                        "impacts_%s%s%s_%s.pdf"     % (options.year, model, mass, options.dataType),
                        "log_%s%s%s%s%s%s_Asymp.txt"      % (options.year, model, mass, options.dataType, suf, close[1:]),
                        "log_%s%s%s%s%s%s_FitDiag.txt"    % (options.year, model, mass, options.dataType, suf, close[1:]),
                        "log_%s%s%s%s%s%s_Sign_sig.txt"   % (options.year, model, mass, options.dataType, suf, close[1:]),
                        "log_%s%s%s%s%s%s_Sign_noSig.txt" % (options.year, model, mass, options.dataType, suf, close[1:]),
                        "log_%s%s%s_multiDim.txt"   % (options.year, model, mass),
                        "log_%s%s%s_HybridNew.txt"  % (options.year, model, mass),
                        "%s_%s_%s_%s_%s%s.txt"        % (options.year, model, mass, options.dataType, suf, close),
                    ]
                
                    transfer = "transfer_output_remaps = \""
                    for f in outputFiles:
                        transfer += "%s = %s/output-files/%s/%s" % (f, options.outPath, outDir, f)
                        if f != outputFiles[-1]:
                            transfer += "; "
                    transfer += "\"\n"
                        
                    fileParts.append(transfer)
                    fileParts.append("Arguments = %s %s %s %s %s %s %s %s %i %i %i %i %i %s %s %s\n" % (options.inputRoot2016, options.inputRoot2017, options.inputRoot2018pre, options.inputRoot2018post, 
                                                                                                  model, mass, options.year, options.dataType, setClosure, doAsym, doFitDiag, doMulti, doImpact, 
                                                                                                  options.inject, options.syst, suf))
                    fileParts.append("Output = %s/log-files/MyFit_%s_%s.stdout\n"%(options.outPath, model, mass))
                    fileParts.append("Error = %s/log-files/MyFit_%s_%s.stderr\n"%(options.outPath, model, mass))
                    fileParts.append("Log = %s/log-files/MyFit_%s_%s.log\n"%(options.outPath, model, mass))
                    fileParts.append("Queue\n\n")
                else:
                    nSteps = int(round((options.rMax - options.rMin)/options.rStep))
                    jPerR = options.jPerR                
                    if options.toyS: 
                        print "Running toyS"
                        nSteps = options.numJobs - 1
                        jPerR = 1

                    for x in range(0, nSteps+1):                               
                        r = options.rMin + float(x)*options.rStep 
                        if options.toyS:
                            r = 0
                            print "    i = ", options.iterations
                        else:
                            print "    r = ", r
                    
                        for y in range(jPerR):                        
                            print "        seed = ", seed

                            outputFiles = [
                                "ws_%s_%s_%s.root"       % (options.year, model, mass),
                                "higgsCombine%s.HybridNew.mH%s.MODEL%s.%s.root" % (options.year, mass, model, modelr(seed)),
                            ]

                            transfer = "transfer_output_remaps = \""
                            for f in outputFiles:
                                transfer += "%s = %s/output-files/%s/%s" % (f, options.outPath, outDir, f)
                                if f != outputFiles[-1]:
                                    transfer += "; "
                            transfer += "\"\n"

                            fileParts.append(transfer)
                            fileParts.append("Arguments = %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n" % (options.inputRoot2016, options.inputRoot2017, options.inputRoot2018pre, options.inputRoot2018post,
                                                                                                    model, stauxi2, mass, options.year, options.dataType, str(r), str(seed), str(options.numToys), 
                                                                                                    str(options.iterations), str(doToyS), options.syst, suf))
                            fileParts.append("Output = %s/log-files/MyFit_%s_%s_%s_%s.stdout\n"%(options.outPath, model, mass, str(r), str(seed)))
                            fileParts.append("Error = %s/log-files/MyFit_%s_%s_%s_%s.stderr\n"%(options.outPath, model, mass, str(r), str(seed)))
                            fileParts.append("Log = %s/log-files/MyFit_%s_%s_%s_%s.log\n"%(options.outPath, model, mass, str(r), str(seed)))
                            fileParts.append("Queue\n\n")
                            seed+=1
    
    fout = open("condor_submit.txt", "w")
    fout.write(''.join(fileParts))
    fout.close()

    #Tar up area
    filestoTransfer = [environ["CMSSW_BASE"] + "/src/CombineFits/DataCardProducer/cards",
                   ]

    makeExeAndFriendsTarball(filestoTransfer, "exestuff", options.outPath)

    dirToTar  = ""
    for d in [".SCRAM", "biglib", "bin", "cfipython", "config", "doc", "external", "include", "lib", "logs", "objs", "python", "test", "tmp"]:
        dirToTar += "${CMSSW_VERSION}/%s/ " % d
    for d in ["bin", "data", "docs", "interface", "macros", "scripts", "src", "test", "python"]:
        dirToTar += "${CMSSW_VERSION}/src/HiggsAnalysis/CombinedLimit/%s/ " % d
    dirToTar += "${CMSSW_VERSION}/src/CombineHarvester/ "
    system("tar --exclude=*.root --exclude=tmp --exclude=.git --exclude=*.pdf --exclude=*.png -zcf %s/${CMSSW_VERSION}.tar.gz -C ${CMSSW_BASE}/.. %s" % (options.outPath, dirToTar))
    
    if not options.noSubmit: 
        system('mkdir -p %s/log-files' % options.outPath)
        system("echo 'condor_submit condor_submit.txt'")
        system('condor_submit condor_submit.txt')

if __name__ == "__main__":
    main()
