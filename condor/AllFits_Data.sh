#!/bin/bash

#CARDS=("cardsInjectNominal_MaxSign_Data" "cardsInjectNominal_MassExclusion_Data")
CARDS=("cardsInjectNominal_MassExclusion_Data")
MODELS=("RPV" "SYY")
CHANNELS=("1l" "0l" "2l" "combo")
DATATYPES=("Data")

DOIMPACTS=0
DOASYMPLIMS=0
DOFITDIAGS=0
DOMULTIDIMS=0
DOALL=0

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
        --impacts)
            DOIMPACTS=1
            shift
            ;;
        --asympLimits)
            DOASYMPLIMS=1
            shift
            ;;
        --fitDiags)
            DOFITDIAGS=1
            shift
            ;;
        --multiDims)
            DOMULTIDIMS=1
            shift
            ;;
        --all)
            DOALL=1
            shift
            ;;
        --help)
            echo "How to run this script:"
            echo "./AllFits_Data.sh [OPTIONS]"
            echo "[OPTIONS]"
            echo "    --models mod1 mod2 ...      : space-separated list of the models to process"
            echo "    --channels chan1 chan2 ...  : space-separated list of the channels to process ('combo' allowed)"
            echo "    --dataTypes type1 type2 ... : space-separated list of the data types to process"
            echo "    --impacts                   : run impacts"
            echo "    --asympLimits               : run asymptotic limits"
            echo "    --fitDiags                  : run fit diagnostics"
            echo "    --multiDims                 : run multi dim fits"
            echo "    --all                       : run four aforementioned types of fits"
            exit 0
            ;;
        *)
            echo "Unknown option \"$1\""
            exit 1
            ;;
    esac
done

for CHANNEL in ${CHANNELS[@]}; do

    for MODEL in ${MODELS[@]}; do

        for DATATYPE in ${DATATYPES[@]}; do

            for CARD in ${CARDS[@]}; do

                # Determine the nominal mass range to submit jobs for based on model and set of data cards
                MASSRANGE=""
                if [[ "${MODEL}" == *"SYY"* && "${CARD}" == *"Max"* ]]; then
                    MASSRANGE="300-650"
                elif [[ "${MODEL}" == *"SYY"* && "${CARD}" == *"Mass"* ]]; then
                    MASSRANGE="700-1400"
                elif [[ "${MODEL}" == *"RPV"* && "${CARD}" == *"Max"* ]]; then
                    MASSRANGE="300-600"
                elif [[ "${MODEL}" == *"RPV"* && "${CARD}" == *"Mass"* ]]; then
                    MASSRANGE="650-700"
                else
                    echo "Could not determine mass range !"
                fi

                if [[ ${DOASYMPLIMS} == 1 ]] || [[ ${DOALL} == 1 ]]; then
                    echo "Asymptotic Fits -> MODEL: ${MODEL}, CHANNEL: ${CHANNEL}, DATATYPE: ${DATATYPE}, MASSRANGE: ${MASSRANGE}, CARDS: ${CARDS}"
                    python condorSubmit.py -d ${MODEL} -t ${DATATYPE} -s ${CHANNEL} -m ${MASSRANGE} -y Run2UL -A --cards=${CARDS} --output=Fit_Run2UL_with_${CARDS}
                fi
                if [[ ${DOFITDIAGS} == 1 ]] || [[ ${DOALL} == 1 ]]; then
                    echo "Fit Diagnostics -> MODEL: ${MODEL}, CHANNEL: ${CHANNEL}, DATATYPE: ${DATATYPE}, MASSRANGE: ${MASSRANGE}, CARDS: ${CARDS}"
                    python condorSubmit.py -d ${MODEL} -t ${DATATYPE} -s ${CHANNEL} -m ${MASSRANGE} -y Run2UL -F --cards=${CARDS} --output=Fit_Run2UL_with_${CARDS}
                fi
                if [[ ${DOMULTIDIMS} == 1 ]] || [[ ${DOALL} == 1 ]]; then
                    echo "MultiDim Fits -> MODEL: ${MODEL}, CHANNEL: ${CHANNEL}, DATATYPE: ${DATATYPE}, MASSRANGE: ${MASSRANGE}, CARDS: ${CARDS}"
                    python condorSubmit.py -d ${MODEL} -t ${DATATYPE} -s ${CHANNEL} -m ${MASSRANGE} -y Run2UL -M --cards=${CARDS} --output=Fit_Run2UL_with_${CARDS}
                fi
                if [[ ${DOIMPACTS} == 1 ]] || [[ ${DOALL} == 1 ]]; then
                    echo "Impacts -> MODEL: ${MODEL}, CHANNEL: ${CHANNEL}, DATATYPE: ${DATATYPE}, MASSRANGE: ${MASSRANGE}, CARDS: ${CARDS}"
                    python condorSubmit.py -d ${MODEL} -t ${DATATYPE} -s ${CHANNEL} -m ${MASSRANGE} -y Run2UL -I --cards=${CARDS} --output=Fit_Run2UL_with_${CARDS}
                fi
            done
        done
    done
done
