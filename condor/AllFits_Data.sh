#!/bin/bash

CARDS=("cards_MaxSign" "cards_MassExclusion")
MODELS=("RPV" "SYY")
CHANNELS=("1l" "0l" "2l" "combo")
DATATYPES=("Data")
USERMASSRANGE=""

DOIMPACTS=0
DOASYMPLIMS=0
DOFITDIAGS=0
DOMULTIDIMS=0
DOLOWMASSES=0
DOHIGHMASSES=0
DRYRUN=0
MASKABCD=("A" "B" "C" "D")
MASKNJETS=("6" "7" "8" "9" "10" "11" "12")
DOMASK=0
FITSTAG=""
CARDSTAG=""

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
        --lowMasses)
            DOLOWMASSES=1
            shift
            ;;
        --highMasses)
            DOHIGHMASSES=1
            shift
            ;;
        --massRange)
            USERMASSRANGE="$2"
            shift
            shift
            ;;
        --maskABCD)
            DOMASK=1
            MASKABCD=()
            while [[ $2 != *"--"* && $# -gt 1 ]]
            do
                MASKABCD+=("$2")
                shift
            done
            shift
            ;;
        --maskNjets)
            DOMASK=1
            MASKNJETS=()
            while [[ $2 != *"--"* && $# -gt 1 ]]
            do
                MASKNJETS+=("$2")
                shift
            done
            shift
            ;;
        --fitsTag)
            FITSTAG="_$2"
            shift
            shift
            ;;
        --cardsTag)
            CARDSTAG="_$2"
            shift
            shift
            ;;
        --dryRun)
            DRYRUN=1
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
            echo "    --lowMasses                 : run low mass optimization fits"
            echo "    --highMasses                : run high mass optimization fits"
            echo "    --massRange                 : specific masses to run on"
            echo "    --maskABCD                  : list of ABCD regions to exclude"
            echo "    --maskNjets                 : list of Njets bins to exclude"
            echo "    --fitsTag                   : tag for customizing outputs"
            echo "    --cardsTag                  : tag for grabbing specific cards"
            echo "    --dryRun                    : do not run condor submit"
            exit 0
            ;;
        *)
            echo "Unknown option \"$1\""
            exit 1
            ;;
    esac
done

MASKASTR=""
if [[ "${MASKA}" == 1 ]]; then
    MASKASTR="_NoAReg"
fi

DOALLMASSES=0
if [[ "${DOLOWMASSES}" == 0 && "${DOHIGHMASSES}" == 0 ]]; then
    DOALLMASSES=1
fi

DOALLFITS=0
if [[ "${DOIMPACTS}" == 0 && "${DOASYMPLIMS}" == 0 && "${DOFITDIAGS}" == 0 && "${DOMULTIDIMS}" == 0 ]]; then
    DOALLFITS=1
fi

if [[ "${CARDSTAG}" != "" ]] && [[ "${FITSTAG}" == "" ]]; then
    FITSTAG=${CARDSTAG}
fi

for CHANNEL in ${CHANNELS[@]}; do

    # Make a string of bins to mask, to be passed to run_fits_disco.sh
    BINMASKFLAG=""
    if [[ "${DOMASK}" == 1 ]]; then
        for MASKA in ${MASKABCD[@]}; do
            AUX=""
            if [[ "${MASKA}" == "A" ]]; then
                AUX="Sig"
            fi
            for MASKJ in ${MASKNJETS[@]}; do
                if [[ "${BINMASKFLAG}" != "" ]]; then
                    BINMASKFLAG+=","
                fi
                BINMASKFLAG+="mask_YUL_${AUX}${MASKA}${MASKJ}_${CHANNEL}=1"
            done
        done
        BINMASKFLAG="--binMask ${BINMASKFLAG}"
    fi
        
    for MODEL in ${MODELS[@]}; do
        for DATATYPE in ${DATATYPES[@]}; do
            for CARD in ${CARDS[@]}; do

                # Do only low or high mass optimization fits depending on user
                if [[ "${CARD}" == *"Max"* && ${DOLOWMASSES} == 0 && ${DOALLMASSES} == 0 ]] || [[ "${CARD}" == *"Mass"* && ${DOHIGHMASSES} == 0 && ${DOALLMASSES} == 0 ]]; then
                    continue
                fi

                # Determine the nominal mass range to submit jobs for based on model and set of data cards
                MASSRANGE=""
                if [[ "${USERMASSRANGE}" == *"-"* ]]; then
                    MASSRANGE=${USERMASSRANGE}
                else
                    if [[ "${MODEL}" == *"SYY"* && "${CARD}" == *"Max"* ]]; then
                        MASSRANGE="300-650"
                    elif [[ "${MODEL}" == *"SYY"* && "${CARD}" == *"Mass"* ]]; then
                        MASSRANGE="700-1400"
                    elif [[ "${MODEL}" == *"RPV"* && "${CARD}" == *"Max"* ]]; then
                        MASSRANGE="300-600"
                    elif [[ "${MODEL}" == *"RPV"* && "${CARD}" == *"Mass"* ]]; then
                        MASSRANGE="650-1400"
                    else
                        echo "Could not determine mass range !"
                    fi
                fi

                FITFLAGS=()
                if [[ ${DOASYMPLIMS} == 1 ]] || [[ ${DOALLFITS} == 1 ]]; then
                    FITFLAGS+=("-A")
                fi
                if [[ ${DOFITDIAGS} == 1 ]] || [[ ${DOALLFITS} == 1 ]]; then
                    FITFLAGS+=("-F")
                fi
                if [[ ${DOIMPACTS} == 1 ]] || [[ ${DOALLFITS} == 1 ]]; then
                    FITFLAGS+=("-I")
                fi
                if [[ ${DOMULTIDIMS} == 1 ]] || [[ ${DOALLFITS} == 1 ]]; then
                    FITFLAGS+=("-M")
                fi

                for FITFLAG in ${FITFLAGS[@]}; do
                    COMMAND="python condorSubmit.py -d ${MODEL} -t ${DATATYPE} -s ${CHANNEL} -m ${MASSRANGE} -y Run2UL ${FITFLAG} ${BINMASKFLAG} --cards=${CARD}_${DATATYPE}${MASKASTR}${CARDSTAG} --output=Fit_Run2UL_with_${CARD}_${DATATYPE}${MASKASTR}${FITSTAG}"
                    echo -e "\n"
                    echo ${COMMAND}
                    if [[ ${DRYRUN} == 0 ]]; then
                        sleep 1
                        eval ${COMMAND} 
                    fi
                done
            done
        done
    done
done
