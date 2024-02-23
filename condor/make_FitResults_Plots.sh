#!/bin/bash

MODELS=("RPV" "StealthSYY")
MASSES=("400" "800")
CHANNELS=("0l" "1l" "2l" "combo")
DATATYPES=("Data")

GETFITS=0
GETIMPACTS=0
GETPVALUES=0
GETLIMITS=0
GETNPCOMPS=0
GETDLLSCANS=0
GETASIMOV=0
GETALL=1

NOGRAFT=0
INPUTSTAG=""

printHelp () {
    echo "How run this script:"
    echo "./make_FitResults_Plots.sh [OPTIONS]"
    echo "[OPTIONS]"
    echo "    --models mod1 mod2 ...      : space-separated list of the models to process"
    echo "    --masses mass1 mass2 ...    : space-separated list of the masses to process"
    echo "    --channels chan1 chan2 ...  : space-separated list of the channels to process ('combo' allowed)"
    echo "    --dataTypes type1 type2 ... : space-separated list of the data types to process"
    echo "    --fits                      : make the fits bonly and sb ABCD-njets plots"
    echo "    --pvalues                   : make the pvalues/signal strength plots"
    echo "    --limits                    : make the expected and observed limits plots"
    echo "    --npComps                   : make the nuisance parameter comparison plots"
    echo "    --dLLscans                  : make the dLL vs r scan plots"
    echo "    --noGraft                   : make pvalues and limits with a single optimization"
    echo "    --asimov                    : get the asimov version of applicable plots"
    echo "    --inputsTag                 : name for choosing particular fit results"
}

while [[ $# -gt 0 ]]
do
    case "$1" in
        --models)
            MODELS=()
            while [[ $2 != *"--"* && $# -gt 1 ]]
            do
                MODELS+=("$2")
                shift
            done
            shift
            ;;
        --masses)
            MASSES=()
            while [[ $2 != *"--"* && $# -gt 1 ]]
            do
                MASSES+=("$2")
                shift
            done
            shift
            ;;
        --channels)
            CHANNELS=()
            while [[ $2 != *"--"* && $# -gt 1 ]]
            do
                CHANNELS+=("$2")
                shift
            done
            shift
            ;;
        --dataTypes)
            DATATYPES=()
            while [[ $2 != *"--"* && $# -gt 1 ]]
            do
                DATATYPES+=("$2")
                shift
            done
            shift
            ;;
        --inputsTag)
            INPUTSTAG="$2"
            shift
            shift
            ;;
        --impacts)
            GETIMPACTS=1
            GETALL=0
            shift
            ;;
        --pvalues)
            GETPVALUES=1
            GETALL=0
            shift
            ;;
        --limits)
            GETLIMITS=1
            GETALL=0
            shift
            ;;
        --fits)
            GETFITS=1
            GETALL=0
            shift
            ;;
        --npComps)
            GETNPCOMPS=1
            GETALL=0
            shift
            ;;
        --dLLscans)
            GETDLLSCANS=1
            GETALL=0
            shift
            ;;
        --noGraft)
            NOGRAFT=1
            shift
            ;;
        --asimov)
            GETASIMOV=1
            shift
            ;;
        --help)
            printHelp
            exit 0
            ;;
        *)
            echo "Unknown option \"$1\""
            printHelp
            exit 1
            ;;
    esac
done

CARDS=("cards_MaxSign" "cards_MassExclusion")
FITPREFIX="Fit_Run2UL_with"

# If particular fit results are selected, propagate that name
TAG=""
if [[ "${INPUTSTAG}" != "" ]]; then
    TAG="_${INPUTSTAG}"
fi

# Begin main looping over options to make the different plots
for DATATYPE in ${DATATYPES[@]}; do
    for CHANNEL in ${CHANNELS[@]}; do
        for MODEL in ${MODELS[@]}; do
    
            # Set the crossover point between low-mass and high-mass optimizations
            GRAFT="600"
            if [[ ${MODEL} == *"SYY"* ]]; then
                GRAFT="650"
            fi

            for MASS in ${MASSES[@]}; do
                for CARD in ${CARDS[@]}; do

                    # Getting results based on particular optimization
                    if [[ ${NOGRAFT} == 0 ]]; then
                        if ( [[ ${MASS} -gt ${GRAFT} ]] && [[ ${CARD} == ${CARDS[0]} ]] ) || ( [[ ${MASS} -le ${GRAFT} ]] && [[ ${CARD} == ${CARDS[1]} ]] ); then
                            continue
                        fi
                    fi

                    FITDIR="${FITPREFIX}_${CARD}_${DATATYPE}${TAG}"
    
                    # Make the NP comparison plots
                    if [[ ${GETNPCOMPS} == 1 ]] || [[ ${GETALL} == 1 ]]; then
                        python makeNPplots.py --fitDir ${FITDIR} --mass ${MASS} --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE}
                    fi

                    # Make fit plots on request
                    if [[ ${GETFITS} == 1 ]] || [[ ${GETALL} == 1 ]]; then
                        python make_fit_plots.py --path ${FITDIR} --dataType ${DATATYPE} --channel ${CHANNEL} --mass ${MASS} --signal ${MODEL}
                    fi

                    # Make delta log likelihood plot
                    if [[ ${GETDLLSCANS} == 1 ]] || [[ ${GETALL} == 1 ]]; then
                        DLLOUTPATH="${FITDIR}/dLLscan_plots"
                        mkdir -p ${DLLOUTPATH}
                        plot1DScan.py ${FITDIR}/output-files/${MODEL}_${MASS}_Run2UL/higgsCombineRun2UL${MODEL}${MASS}${DATATYPE}_${CHANNEL}_dLLscan.MultiDimFit.mH${MASS}.MODEL${MODEL}.root --main-color 4 --output scan --y-max 17 --y-cut 11
                        mv scan.pdf ${DLLOUTPATH}/Run2UL_${MODEL}_${MASS}_${CHANNEL}_LogLikelihoodScan_prelim.pdf && rm scan*
                    fi

                    # Make the impact plots from the json
                    if [[ ${GETIMPACTS} == 1 ]] || [[ ${GETALL} == 1 ]]; then
                        IMPACTSINPATH="${FITDIR}/output-files/${MODEL}_${MASS}_Run2UL/"
                        IMPACTSOUTPATH="${FITDIR}/impact_plots"
                        IMPACTSNAME="impacts_Run2UL${MODEL}${MASS}_${CHANNEL}_${DATATYPE}"
                        IMPACTSTAG="impacts_Run2UL${MODEL}${MASS}${DATATYPE}_${CHANNEL}"
                        mkdir -p ${IMPACTSOUTPATH}

                        ASIMOVTAGS=("")
                        if [[ ${GETASIMOV} == 1 ]]; then
                            ASIMOVTAGS=("_Asimov" "_Asimov_0p2" "_Asimov_1p0")
                        fi 
                        for ASIMOVTAG in ${ASIMOVTAGS[@]}; do
                            plotImpacts.py -i ${IMPACTSINPATH}/${IMPACTSTAG}${ASIMOVTAG}.json -o ${IMPACTSNAME}${ASIMOVTAG}
                            plotImpacts.py -i ${IMPACTSINPATH}/${IMPACTSTAG}${ASIMOVTAG}.json -o ${IMPACTSNAME}${ASIMOVTAG}_blind --blind
                        done
                        mv ${IMPACTSNAME}*.pdf ${IMPACTSOUTPATH}
                    fi
                done
            done

            ASIMOVFLAG=""
            EXPSIGS=("")
            if [[ ${GETASIMOV} == 1 ]]; then
                ASIMOVFLAG="--asimov"
                EXPSIGS=("" "--expSig 0p2" "--expSig 1p0")
            fi

            # For pvalue plots, can feed in all channels together
            THECHANNEL=${CHANNEL}
            if [[ ${CHANNEL} == "combo" ]]; then
                THECHANNEL="0l 1l 2l combo"
            fi

            GRAFTTAG="${CARDS[0]}_${DATATYPE}${TAG}"
            FITDIRS="${FITPREFIX}_${CARDS[0]}_${DATATYPE}${TAG} ${FITPREFIX}_${CARDS[1]}_${DATATYPE}${TAG}"
            for CARD in ${CARDS[@]}; do
    
                # If not grafting, get all results for one optimization
                if [[ ${NOGRAFT} == 0 ]] && [[ ${CARD} == ${CARDS[1]} ]]; then
                    continue
                elif [[ ${NOGRAFT} == 1 ]]; then
                    GRAFTTAG="${CARD}_${DATATYPE}${TAG}"
                    FITDIRS="${FITPREFIX}_${GRAFTTAG} ${FITPREFIX}_${GRAFTTAG}"
                fi

                # Make limit plots on request
                if [[ ${GETLIMITS} == 1 ]] || [[ ${GETALL} == 1 ]]; then 
                    python make_Limit_Plots.py --inputDirs ${FITDIRS} --outputDir GraftedLimitPlots_${GRAFTTAG} --year Run2UL --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} --wip --graft ${GRAFT} ${ASIMOVFLAG} --noRatio
                fi
    
                # Make pvalue plots/tables on request
                if [[ ${GETPVALUES} == 1 ]] || [[ ${GETALL} == 1 ]]; then
                    for EXPSIG in ${EXPSIGS[@]}; do
                        python make_Pvalue_PlotsTables.py --basedirs ${FITDIRS} --outdir GraftedPvaluePlots_${GRAFTTAG} --channels ${THECHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE} ${ASIMOVFLAG} ${EXPSIG}
                    done
                fi
            done
        done
    done
done
