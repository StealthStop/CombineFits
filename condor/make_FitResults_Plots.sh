#!/bin/bash

CARDS=("cards_MaxSign" "cards_MassExclusion")
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
FITPREFIX="Fit_Run2UL_with"

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
            exit 0
            ;;
        *)
            echo "Unknown option \"$1\""
            exit 1
            ;;
    esac
done

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
                        plot1DScan.py ${FITDIR}/output-files/${MODEL}_${MASS}_Run2UL/higgsCombineRun2UL${MODEL}${MASS}${DATATYPE}_${CHANNEL}_dLLscan.MultiDimFit.mH${MASS}.MODEL${MODEL}.root --main-color 4 --output scan
                        mv scan.pdf ${DLLOUTPATH}/Run2UL_${MODEL}_${MASS}_${CHANNEL}_LogLikelihoodScan_prelim.pdf && rm scan*
                    fi

                    # Make the impact plots from the json
                    if [[ ${GETIMPACTS} == 1 ]] || [[ ${GETALL} == 1 ]]; then
                        IMPACTSINPATH="${FITDIR}/output-files/${MODEL}_${MASS}_Run2UL/"
                        IMPACTSOUTPATH="${FITDIR}/impact_plots"
                        IMPACTSNAME="impacts_Run2UL${MODEL}${MASS}_${CHANNEL}_${DATATYPE}"
                        IMPACTSTAG="impacts_Run2UL${MODEL}${MASS}${DATATYPE}_${CHANNEL}"
                        mkdir -p ${IMPACTSOUTPATH}
                        if [[ ${GETASIMOV} == 1 ]]; then
                            plotImpacts.py -i ${IMPACTSINPATH}/${IMPACTSTAG}_Asimov.json     -o ${IMPACTSNAME}_Asimov
                            plotImpacts.py -i ${IMPACTSINPATH}/${IMPACTSTAG}_Asimov_0p2.json -o ${IMPACTSNAME}_Asimov_0p2
                            plotImpacts.py -i ${IMPACTSINPATH}/${IMPACTSTAG}_Asimov_1p0.json -o ${IMPACTSNAME}_Asimov_1p0
                        else
                            plotImpacts.py -i ${IMPACTSINPATH}/${IMPACTSTAG}.json -o ${IMPACTSNAME}
                            plotImpacts.py -i ${IMPACTSINPATH}/${IMPACTSTAG}.json -o ${IMPACTSNAME}_blind --blind
                        fi
                        mv ${IMPACTSNAME}*.pdf ${IMPACTSOUTPATH}
                    fi
                done
            done

            TAGHIGH="${CARDS[1]}_${DATATYPE}${TAG}"
            TAGLOW="${CARDS[0]}_${DATATYPE}${TAG}"
            FITDIRHIGH="${FITPREFIX}_${TAGHIGH}"
            FITDIRLOW="${FITPREFIX}_${TAGLOW}"
    
            # Make limit plots on request
            if [[ ${GETLIMITS} == 1 ]] || [[ ${GETALL} == 1 ]]; then 
                if [[ ${NOGRAFT} == 0 ]]; then
                    if [[ ${GETASIMOV} == 0 ]]; then
                        python make_Limit_Plots.py --inputDirs ${FITDIRLOW} ${FITDIRHIGH} --outputDir GraftedLimitPlots_${TAGLOW} --year Run2UL --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} --wip --graft ${GRAFT} --noRatio
                    else
                        python make_Limit_Plots.py --inputDirs ${FITDIRLOW} ${FITDIRHIGH} --outputDir GraftedLimitPlots_${TAGLOW} --year Run2UL --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} --wip --graft ${GRAFT} --asimov --noRatio
                    fi
                else
                    python make_Limit_Plots.py --inputDirs ${FITDIRLOW} ${FITDIRLOW} --outputDir GraftedLimitPlots_${TAGLOW}_NoGraft --year Run2UL --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} --wip --graft ${GRAFT} --noRatio
                    python make_Limit_Plots.py --inputDirs ${FITDIRHIGH} ${FITDIRHIGH} --outputDir GraftedLimitPlots_${TAGHIGH}_NoGraft --year Run2UL --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} --wip --graft ${GRAFT} --noRatio
                fi
            fi
    
            # Make pvalue plots/tables on request
            if [[ ${GETPVALUES} == 1 ]] || [[ ${GETALL} == 1 ]]; then
                # If not grafting, get all results for one optimization
                if [[ ${NOGRAFT} == 0 ]]; then
                    if [[ ${GETASIMOV} == 0 ]]; then
                        if [[ ${CHANNEL} == "combo" ]]; then
                            python make_Pvalue_PlotsTables.py --basedirs ${FITDIRLOW} ${FITDIRHIGH} --outdir GraftedPvaluePlots_${TAGLOW} --channels 0l 1l 2l combo --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE}
                        else
                            python make_Pvalue_PlotsTables.py --basedirs ${FITDIRLOW} ${FITDIRHIGH} --outdir GraftedPvaluePlots_${TAGLOW} --channels ${CHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE}
                        fi
                    else
                        python make_Pvalue_PlotsTables.py --basedirs ${FITDIRLOW} ${FITDIRHIGH} --outdir GraftedPvaluePlots_${TAGLOW} --channels ${CHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE} --asimov
                        python make_Pvalue_PlotsTables.py --basedirs ${FITDIRLOW} ${FITDIRHIGH} --outdir GraftedPvaluePlots_${TAGLOW} --channels ${CHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE} --asimov --expSig 1p0
                        python make_Pvalue_PlotsTables.py --basedirs ${FITDIRLOW} ${FITDIRHIGH} --outdir GraftedPvaluePlots_${TAGLOW} --channels ${CHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE} --asimov --expSig 0p2
                    fi
                else
                    python make_Pvalue_PlotsTables.py --basedirs ${FITDIRLOW} ${FITDIRLOW} --outdir GraftedPvaluePlots_${TAGLOW}_NoGraft --channels ${CHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE}
                    python make_Pvalue_PlotsTables.py --basedirs ${FITDIRHIGH} ${FITDIRHIGH} --outdir GraftedPvaluePlots_${TAGHIGH}_NoGraft --channels ${CHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE}
                fi
            fi
        done
    done
done
