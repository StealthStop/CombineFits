import sys, os
from os import system, environ
import optparse 
import subprocess
import time
import itertools

def red(string):
     CRED = "\033[91m"
     CEND = "\033[0m"
     return CRED + str(string) + CEND

def cyan(string):
     CRED = "\033[96m"
     CEND = "\033[0m"
     return CRED + str(string) + CEND

def orange(string):
     CRED = "\033[93m"
     CEND = "\033[0m"
     return CRED + str(string) + CEND

# Pass a list of files to tar up
def makeExeAndFriendsTarball(filestoTransfer, fname, path):
    outputtar = "%s/%s.tar.gz"%(path, fname)
    if os.path.exists(outputtar):
        print(orange("Tar \"%s\" already exists, so not overwriting !"%(outputtar)))
        return

    system("mkdir -p %s" % fname)
    for fn in filestoTransfer:

        #if "DataCardProducer" in fn:
        #    system("cd %s; ln -s %s cards" % (fname, fn))
        #else:
        system("cd %s; ln -s %s" % (fname, fn))

    tarallinputs = "tar czvf %s %s --dereference"% (outputtar, fname)
    print tarallinputs
    system(tarallinputs)
    system("rm -r %s" % fname)

# Parse an option from the command for exanding a range into a list
# E.g. "300-1400" ==> ["300", "350", "400", ..., "1400"]
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

def getBinEdgeList(edgeScan, edgeScan1, edgeScan2):
    edgeScan  = eval(edgeScan)
    edgeScan1 = eval(edgeScan1)
    edgeScan2 = eval(edgeScan2)

    e1, e2 = None, None
    if edgeScan:
        e1 = edgeScan
        e2 = edgeScan
    elif edgeScan1 and edgeScan2:
        e1 = edgeScan1
        e2 = edgeScan2
    else:
        print("Did not pass in bin edge range. Assuming you are running the fits normally.")
        return [(None,None)]

    l = list(itertools.product(e1,e2))
    print("e1 = ", e1)
    print("e2 = ", e2)
    print(l)
    print(len(l))
    return l

def main():
    repo = "HiggsAnalysis/CombinedLimit"
    seed = int(time.time())
    
    parser = optparse.OptionParser("usage: %prog [options]\n")
    parser.add_option ('-d',               dest='signalType',        type='string', default = '',      help="List of signal model, comma separated")
    parser.add_option ('-t',               dest='dataType',          type='string', default = 'data',  help="Specify if running over data or pseudo data")
    parser.add_option ('-s', '--channel',  dest='channel',           type='string', default = 'None',  help="Specify which final state (0l or 1l)")
    parser.add_option ('-m',               dest='masssets',          type='string', default = '',      help="List of mass models, comma separated or range (e.g. 300-1400)")
    parser.add_option ('-y',               dest='year',              type='string', default = 'Run2UL',help="year")
    parser.add_option ('-c',               dest='noSubmit',    action='store_true', default = False,   help="Do not submit jobs.  Only create condor_submit.txt.")
    parser.add_option ('-A',               dest='doAsym',      action='store_true', default = False,   help="Specify AsymptoticLimits and Significance fit command to run")
    parser.add_option ('-F',               dest='doFitDiag',   action='store_true', default = False,   help="Specify FitDiagnostics fit command to run")
    parser.add_option ('-M',               dest='doMulti',     action='store_true', default = False,   help="Specify MultiDimFit fit command to run")
    parser.add_option ('-I',               dest='doImpact',    action='store_true', default = False,   help="Specify impact fit command to run")
    parser.add_option ('--output',         dest='outPath',           type='string', default = '.',     help="Name of directory where output of each condor job goes")
    parser.add_option ('--toy',            dest='toy',         action='store_true', default = False,   help="Limits: Submit toy jobs instead of the normal set of fits")
    parser.add_option ('-T',               dest='numToys',           type='int',    default = 1000,    help="Specify number of toys per job")
    parser.add_option ('--rMin',           dest='rMin',              type='float',  default = 0.05,    help="Specify minimum r value")
    parser.add_option ('--rMax',           dest='rMax',              type='float',  default = 1.00,    help="Specify maximum r value")
    parser.add_option ('--rStep',          dest='rStep',             type='float',  default = 0.05,    help="Specify step size")
    parser.add_option ('--jPerR',          dest='jPerR',             type='int',    default = 5,       help="Specify jobs per r setting")
    parser.add_option ('--toyS',           dest='toyS',        action='store_true', default = False,   help="Sig.:   Submit toy jobs instead of the normal set of fits")
    parser.add_option ('--nJobs',          dest='numJobs',           type='int',    default = -1,      help="Can specify the number of jobs for toyS")
    parser.add_option ('-i',               dest='iterations',        type='int',    default =  1,      help="Can specify the number of iterations for toyS")
    parser.add_option ('--cards',          dest='cards',             type='string', default = 'cards', help="Folder containing data cards")
    parser.add_option ('--edgeScan',       dest='edgeScan',          type='string', default = 'None',  help="Specify the bin edges you want to scan along disc 1 and disc 2")
    parser.add_option ('--edgeScan1',      dest='edgeScan1',         type='string', default = 'None',  help="Specify the bin edges you want to scan along disc 1")
    parser.add_option ('--edgeScan2',      dest='edgeScan2',         type='string', default = 'None',  help="Specify the bin edges you want to scan along disc 2")


    # Parse command line arguments
    options, args = parser.parse_args()

    # Split up custom command line string arguments into simple lists
    # E.g. "300-1400" ==> ["300", "350", "400", ..., "1400"]
    signalType = getOptionList(options.signalType, "No dataset specified")
    masssets   = getOptionList(options.masssets, "No mass model specified")

    doAsym    = 1 if options.doAsym    else 0
    doFitDiag = 1 if options.doFitDiag else 0
    doMulti   = 1 if options.doMulti   else 0
    doImpact  = 1 if options.doImpact  else 0
    doToyS    = 1 if options.toyS      else 0 

    if doAsym:
        extra = "_Asym"
    if doFitDiag:
        extra = "_FitDiag"
    if doMulti:
        extra = "_Multi"
    if doImpact:
        extra = "_Impact"

    # If user specifies not fits, assume to do all of them
    if not doAsym and not doFitDiag and not doMulti and not doImpact:
        doAsym    = 1
        doFitDiag = 1
        doMulti   = 1
        doImpact  = 1

    executable = "run_fits_disco.sh"
    if options.toy or options.toyS:
        executable = "run_toys.sh"

    # If running the bin edge scan figure out the list of possible bin edges
    binEdgeList = getBinEdgeList(options.edgeScan, options.edgeScan1, options.edgeScan2)

    # Construct list of options to write to condor submit txt file
    fileParts = []
    fileParts.append("Universe   = vanilla\n")
    fileParts.append("Executable = %s\n" % executable)
    fileParts.append("Should_Transfer_Files = YES\n")
    fileParts.append("WhenToTransferOutput = ON_EXIT\n")
    if "combo" not in options.channel:
        fileParts.append("RequestMemory = 1024\n")
    else:
        fileParts.append("RequestMemory = 2048\n")
    fileParts.append("x509userproxy = $ENV(X509_USER_PROXY)\n\n")
    fileParts.append("Transfer_Input_Files = {0}/CMSSW_10_2_13.tar.gz, {0}/exestuff.tar.gz\n".format(options.outPath))

    # If no specific channel is specified by the user
    # assume to run over all channel combinations
    if options.channel == "None":
        channels = ['0l', '1l', '2l','combo']
    else:
        channels = [options.channel]

    #if not os.path.isdir("%s/output-files/%s"%(options.outPath,options.cards)):
    #    os.system("cp -r %s/src/CombineFits/DataCardProducer/%s %s/output-files"%(environ["CMSSW_BASE"],options.cards,options.outPath))
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
            for channel in channels:
                for disc1Edge, disc2Edge in binEdgeList:
                    binEdgeName = "_{}_{}".format(disc1Edge, disc2Edge) if disc1Edge else ""
                    for asimov in [0, 1]:
                        print("Making directory for {} {} {}: bin edges 0.{} 0.{}".format(mass, channel, st, disc1Edge, disc2Edge))
                        # Create the directory for cards and output files
                        outDir = model+"_"+mass+"_"+options.year+binEdgeName
                        if not os.path.isdir("%s/output-files/%s" % (options.outPath, outDir)):
                            os.makedirs("%s/output-files/%s" % (options.outPath, outDir))
                        if not os.path.isdir("%s/output-files/%s"%(options.outPath,options.cards)):
                            #print("Copying cards...")
                            os.makedirs("%s/output-files/%s"%(options.outPath,options.cards))
                            #os.system("cp -r %s/src/CombineFits/DataCardProducer/%s %s/output-files"%(environ["CMSSW_BASE"],options.cards,options.outPath))
                        #print("Card copy finished")

                        if not options.toy and not options.toyS:

                            tagName = "%s%s%s%s_%s%s"%(options.year, model, mass, options.dataType, channel, binEdgeName)

                            outputFiles = [
                                "higgsCombine%s_AsymLimit.AsymptoticLimits.mH%s.MODEL%s.root"    % (tagName, mass, model),
                                "higgsCombine%s.FitDiagnostics.mH%s.MODEL%s.root"                % (tagName, mass, model),
                                "higgsCombine%s_SignifExp.Significance.mH%s.MODEL%s.root"        % (tagName, mass, model),
                                "higgsCombine%sSCAN_r_wSig.MultiDimFit.mH%s.MODEL%s.root"        % (tagName, mass, model),
                                "ws_%s.root"                                                     % (tagName),
                                "fitDiagnostics%s.root"                                          % (tagName), 
                                "impacts_%s.json"                                                % (tagName),
                                "impacts_%s%s%s_%s_%s.pdf"                                       % (options.year, model, mass, channel, options.dataType),
                                "log_%s_Asymp.txt"                                               % (tagName),
                                "log_%s_FitDiag.txt"                                             % (tagName),
                                "log_%s_Sign.txt"                                                % (tagName),
                                "log_%s_step1.txt"                                               % (tagName),
                                "log_%s_step2.txt"                                               % (tagName),
                                "log_%s_step3.txt"                                               % (tagName),
                                "higgsCombine%s_AsymLimit.AsymptoticLimits.mH%s.MODEL%s.root"    % (tagName, mass, model),
                                "higgsCombine%s_AsymLimit_Asimov.AsymptoticLimits.mH%s.MODEL%s.root"    % (tagName, mass, model),
                                "higgsCombine%s_Asimov.FitDiagnostics.mH%s.MODEL%s.root"         % (tagName, mass, model),
                                "higgsCombine%s_SignifExp_Asimov.Significance.mH%s.MODEL%s.root" % (tagName, mass, model),
                                "fitDiagnostics%s_Asimov.root"                                   % (tagName), 
                                "impacts_%s_Asimov.json"                                         % (tagName),
                                "impacts_%s%s%s_%s_%s_Asimov.pdf"                                % (options.year, model, mass, channel, options.dataType),
                                "log_%s_Asymp_Asimov.txt"                                        % (tagName),
                                "log_%s_FitDiag_Asimov.txt"                                      % (tagName),
                                "log_%s_Sign_Asimov.txt"                                         % (tagName),
                                "log_%s_step1_Asimov.txt"                                        % (tagName),
                                "log_%s_step2_Asimov.txt"                                        % (tagName),
                                "log_%s_step3_Asimov.txt"                                        % (tagName),
                                "Run2UL_%s_%s_pseudoDataS_%s%s.txt"                              % (model, mass, channel, binEdgeName),
                                "Run2UL_%s_%s_pseudoData_%s%s.txt"                               % (model, mass, channel, binEdgeName),
                            ]
                        
                            transfer = "transfer_output_remaps = \""
                            for f in outputFiles:
                                if "%s%s.txt"% (channel, binEdgeName) in f:
                                    transfer += "%s = %s/output-files/%s/%s" % (f, options.outPath, options.cards, f)
                                else:
                                    transfer += "%s = %s/output-files/%s/%s" % (f, options.outPath, outDir, f)
                                if f != outputFiles[-1]:
                                    transfer += "; "
                            transfer += "\"\n"
                                
                            fileParts.append(transfer)
                            fileParts.append("Arguments = %s %s %s %s %i %i %i %i %s %i %s\n" % (model, mass, options.year, options.dataType, doAsym, doFitDiag, doMulti, doImpact, channel, asimov, binEdgeName))
                            extraAsimov = ""
                            if asimov == 1:
                                extraAsimov += "_Asimov"
                            fileParts.append("Output = %s/log-files/MyFit_%s_%s_%s_%s%s%s%s.stdout\n"%(options.outPath, model, mass, options.dataType, channel, extra, extraAsimov, binEdgeName))
                            fileParts.append("Error = %s/log-files/MyFit_%s_%s_%s_%s%s%s%s.stderr\n"%(options.outPath, model, mass, options.dataType, channel, extra, extraAsimov, binEdgeName))
                            fileParts.append("Log = %s/log-files/MyFit_%s_%s_%s_%s%s%s%s.log\n"%(options.outPath, model, mass, options.dataType, channel, extra, extraAsimov, binEdgeName))
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
                                    fileParts.append("Arguments = %s %s %s %s %s %s %s %s %s %s %s\n" % (model, stauxi2, mass, options.year, options.dataType, str(r), str(seed), str(options.numToys), 
                                                                                                            str(options.iterations), str(doToyS), channel))
                                    fileParts.append("Output = %s/log-files/MyFit_%s_%s_%s_%s.stdout\n"%(options.outPath, model, mass, str(r), str(seed)))
                                    fileParts.append("Error = %s/log-files/MyFit_%s_%s_%s_%s.stderr\n"%(options.outPath, model, mass, str(r), str(seed)))
                                    fileParts.append("Log = %s/log-files/MyFit_%s_%s_%s_%s.log\n"%(options.outPath, model, mass, str(r), str(seed)))
                                    fileParts.append("Queue\n\n")
                                    seed+=1
    
    fout = open("condor_submit.txt", "w")
    fout.write(''.join(fileParts))
    fout.close()

    #Tar up area
    filestoTransfer = [environ["CMSSW_BASE"] + "/src/CombineFits/DataCardProducer/produceDataCard.py"] #[environ["CMSSW_BASE"] + "/src/CombineFits/DataCardProducer/%s"%(options.cards)]
    filestoTransfer += [environ["CMSSW_BASE"] + "/src/CombineFits/DataCardProducer/dataCardProducer.py"]
    filestoTransfer += [environ["CMSSW_BASE"] + "/src/CombineFits/DataCardProducer/cardConfig_0l_scan.py"]
    filestoTransfer += [environ["CMSSW_BASE"] + "/src/CombineFits/DataCardProducer/cardConfig_1l_scan.py"]
    filestoTransfer += [environ["CMSSW_BASE"] + "/src/CombineFits/DataCardProducer/cardConfig_2l_scan.py"]
    filestoTransfer += [environ["CMSSW_BASE"] + "/src/CombineFits/DataCardProducer/inputsAll"]

    makeExeAndFriendsTarball(filestoTransfer, "exestuff", options.outPath)

    CMSSW_VERSION = os.environ["CMSSW_VERSION"]

    dirToTar  = ""
    for d in [".SCRAM", "biglib", "bin", "cfipython", "config", "doc", "external", "include", "lib", "logs", "objs", "python", "test", "tmp"]:
        dirToTar += "%s/%s/ " %(CMSSW_VERSION,d) 
    for d in ["bin", "data", "docs", "interface", "macros", "scripts", "src", "test", "python"]:
        dirToTar += "%s/src/HiggsAnalysis/CombinedLimit/%s/ " %(CMSSW_VERSION,d)
    dirToTar += "%s/src/CombineHarvester/ "%(CMSSW_VERSION)

    cmsswtar = "%s/%s.tar.gz"%(options.outPath, CMSSW_VERSION)
    
    if not os.path.exists(cmsswtar):
        system("tar --exclude=*.root --exclude=tmp --exclude=.git --exclude=*.pdf --exclude=*.png -zcf %s/%s.tar.gz -C ${CMSSW_BASE}/.. %s" % (options.outPath, CMSSW_VERSION, dirToTar))
    else:
        print(orange("Tar \"%s\" already exists, so not overwriting !"%(cmsswtar)))
    
    if not options.noSubmit: 
        system('mkdir -p %s/log-files' % options.outPath)
        system("echo 'condor_submit condor_submit.txt'")
        system('condor_submit condor_submit.txt')

if __name__ == "__main__":
    main()
