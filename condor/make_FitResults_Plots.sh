#!/bin/bash

# This script makes fit, pvalue and limit plots
# For fit plots    : using condor/make_fit_plots.py 
# For pvalue plots : using condor/make_Pvalue_PlotsTables.py 
# For limit plots  : using condor/make_Limit_Plots.py
#
# 4 type of MC level fits:
#   -- Bkg only fit / (only bkg component for fit)     / using pseudoData        
#   -- Bkg+Sig  fit / (bkg and sig components for fit) / using pseudoData
#   -- Bkg only fit / (only bkg component for fit)     / using pseudoDataS
#   -- Bkg+Sig  fit / (bkg and sig components for fit) / using pseudoDataS 
# ------------------------------------------------------------------------

CARDS=("cards_MaxSign" "cards_MassExclusion")
MODELS=("RPV" "StealthSYY")
MASSES=("400" "800")
CHANNELS=("0l" "1l" "2l" "combo")
DATATYPES=("Data")

GETIMPACTS=0
GETFITS=0
GETPVALUES=0
GETLIMITS=0
GETALL=0
GETNPCOMP=0
MASKA=0
INPUTSTAG=""

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
            shift
            ;;
        --pvalues)
            GETPVALUES=1
            shift
            ;;
        --limits)
            GETLIMITS=1
            shift
            ;;
        --fits)
            GETFITS=1
            shift
            ;;
        --npComp)
            GETNPCOMP=1
            shift
            ;;
        --all)
            GETALL=1
            shift
            ;;
        --maskA)
            MASKA=1
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
            echo "    --impacts                   : get the impacts"
            echo "    --fits                      : get the fits"
            echo "    --pvalues                   : get the pvalues"
            echo "    --limits                    : get the limits"
            echo "    --npComp                    : get the josh plot"
            echo "    --all                       : get all four of the aforementioned results"
            echo "    --inputsTag                 : name for choosing particular fit results"
            echo "    --maskA                     : get fit results for masked A region"
            exit 0
            ;;
        *)
            echo "Unknown option \"$1\""
            exit 1
            ;;
    esac
done

MASKARG=""
TAG=""
if [[ ${MASKA} == 1 ]]; then
    MASKARG="--maskRegA"
    TAG="_NoAReg"
fi

if [[ "${INPUTSTAG}" != "" ]]; then
    TAG="${TAG}_${INPUTSTAG}"
fi

# ------------------------------------------------------
# Begin main looping over options to get different plots
# ------------------------------------------------------
for DATATYPE in ${DATATYPES[@]}; do

    for CHANNEL in ${CHANNELS[@]}; do
    
        for MODEL in ${MODELS[@]}; do
    
            # --------------------------------------------------------------------
            # Set the crossover point between low mass and high mass optimizations
            # --------------------------------------------------------------------
            GRAFT="600"
            if [[ "${MODEL}" == *"SYY"* ]]; then
                GRAFT="650"
            fi

            # --------------------------------
            # Copy over the impacts on request
            # --------------------------------
            for MASS in ${MASSES[@]}; do
            
                # ---------------------
                # copy the impact plots
                # ---------------------
                if [[ ${GETIMPACTS} == 1 ]] || [[ ${GETALL} == 1 ]]; then
                    echo "Copying over impact plots -----------------------------------"
                    if [[ ${MASS} -le 600 ]]; then
                        mkdir Fit_Run2UL_with_${CARDS[0]}_${DATATYPE}/output-files/plots_dataCards_TT_allTTvar/impact_plots/
                        cd Fit_Run2UL_with_${CARDS[0]}_${DATATYPE}/output-files/${MODEL}_${MASS}_Run2UL/
                        scp -r impacts_Run2UL${MODEL}${MASS}_${CHANNEL}_${DATATYPE}*.pdf ../plots_dataCards_TT_allTTvar/impact_plots/
                        cd ../../../
                    else
                        mkdir Fit_Run2UL_with_${CARDS[1]}_${DATATYPE}/output-files/plots_dataCards_TT_allTTvar/impact_plots/
                        cd Fit_Run2UL_with_${CARDS[1]}_${DATATYPE}/output-files/${MODEL}_${MASS}_Run2UL/
                        scp -r impacts_Run2UL${MODEL}${MASS}_${CHANNEL}_${DATATYPE}*.pdf ../plots_dataCards_TT_allTTvar/impact_plots/
                        cd ../../../
                    fi
                fi

                # ----------------------------
                # Make the NP comparison plots
                # ----------------------------
                if [[ ${GETNPCOMP} == 1 ]] || [[ ${GETALL} == 1 ]]; then
                    THECARDS=
                    if [[ "${MASS}" -gt "${GRAFT}" ]]; then
                        THECARDS=${CARDS[1]}
                    else
                        THECARDS=${CARDS[0]}
                    fi
                    python makeNPplots.py --fitDir Fit_Run2UL_with_${THECARDS}_${DATATYPE}${TAG} --mass ${MASS} --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE}
                fi
   
                # -------------------------
                # Make fit plots on request
                # -------------------------
                if [[ ${GETFITS} == 1 ]]; then
                    echo "Making the fit plots -------------------------------------------"
                    THECARDS=
                    if [[ "${MASS}" -gt "${GRAFT}" ]]; then
                        THECARDS=${CARDS[1]}
                    else
                        THECARDS=${CARDS[0]}
                    fi
                    python make_fit_plots.py --path Fit_Run2UL_with_${THECARDS}_${DATATYPE}${TAG} --dataType ${DATATYPE} --channel ${CHANNEL} --mass ${MASS} --signal ${MODEL} ${MASKARG}
                fi
            done
    
            # ---------------------------
            # Make limit plots on request
            # ---------------------------                  
            if [[ ${GETLIMITS} == 1 ]] || [[ ${GETALL} == 1 ]]; then 
                echo "Making limit plots -------------------------------------------"
                python make_Limit_Plots.py --inputDirs Fit_Run2UL_with_${CARDS[0]}_${DATATYPE}${TAG} Fit_Run2UL_with_${CARDS[1]}_${DATATYPE}${TAG} --outputDir GraftedLimitPlots_${CARDS[0]}_${DATATYPE}${TAG} --year Run2UL --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} --wip --graft ${GRAFT} --noRatio
                python make_Limit_Plots.py --inputDirs Fit_Run2UL_with_${CARDS[0]}_${DATATYPE}${TAG} Fit_Run2UL_with_${CARDS[1]}_${DATATYPE}${TAG} --outputDir GraftedLimitPlots_${CARDS[0]}_${DATATYPE}${TAG} --year Run2UL --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} --wip --graft ${GRAFT} --asimov --noRatio
            fi
    
            # -----------------------------------
            # Make pvalue plots/tables on request
            # -----------------------------------
            if [[ ${GETPVALUES} == 1 ]] || [[ ${GETALL} == 1 ]]; then
                echo "Making pvalue plots -------------------------------------------"
                python make_Pvalue_PlotsTables.py --basedirs Fit_Run2UL_with_${CARDS[0]}_${DATATYPE}${TAG} Fit_Run2UL_with_${CARDS[1]}_${DATATYPE}${TAG} --outdir GraftedPvaluePlots_${CARDS[0]}_${DATATYPE}${TAG} --channels ${CHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE}
                python make_Pvalue_PlotsTables.py --basedirs Fit_Run2UL_with_${CARDS[0]}_${DATATYPE}${TAG} Fit_Run2UL_with_${CARDS[1]}_${DATATYPE}${TAG} --outdir GraftedPvaluePlots_${CARDS[0]}_${DATATYPE}${TAG} --channels ${CHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE} --asimov
                python make_Pvalue_PlotsTables.py --basedirs Fit_Run2UL_with_${CARDS[0]}_${DATATYPE}${TAG} Fit_Run2UL_with_${CARDS[1]}_${DATATYPE}${TAG} --outdir GraftedPvaluePlots_${CARDS[0]}_${DATATYPE}${TAG} --channels ${CHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE} --asimov --expSig 1p0
                python make_Pvalue_PlotsTables.py --basedirs Fit_Run2UL_with_${CARDS[0]}_${DATATYPE}${TAG} Fit_Run2UL_with_${CARDS[1]}_${DATATYPE}${TAG} --outdir GraftedPvaluePlots_${CARDS[0]}_${DATATYPE}${TAG} --channels ${CHANNEL} --models ${MODEL} --wip --graft ${GRAFT} --dataType ${DATATYPE} --asimov --expSig 0p2
            fi
        done
    done
done
