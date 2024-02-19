#!/bin/bash

MODELS=("RPV" "StealthSYY")
CHANNELS=("0l" "1l" "2l" "combo")
DATATYPES=("Data")
OPTIMIZATIONS=()
DRYRUN=0
MASKATAG=""
SCALESYST="1"
SYSTS2SCALE=""
SCALESYSTTAG=""
SCALESYSTFLAG=""
INJECTINTODATAFLAG=""
COMBOARG=""
CUSTOMTAG=""

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
        --lowMass)
            OPTIMIZATIONS+=("MaxSign")
            shift
            ;;
        --highMass)
            OPTIMIZATIONS+=("MassExclusion")
            shift
            ;;
        --maskA)
            MASKATAG="_NoAReg"
            shift
            ;;
        --scaleSyst)
            SCALESYSTFLAG="--scaleSyst $2"
            if [[ "$2" == "0" ]]; then
                SCALESYSTTAG="_NoSyst"
            else
                NEWSCALESYST=$(echo "$2" | tr '.' 'p')
                SCALESYSTTAG="_Syst${NEWSCALESYST}"
            fi 
            shift
            shift
            ;;
        --systsToScale)
            SYSTS2SCALE="--systsToScale"
            while [[ $2 != *"--"* && $# -gt 1 ]]
            do
                SYSTS2SCALE+=" $2"
                shift
            done
            shift
            ;;
        --injectIntoData)
            INJECTINTODATAFLAG="--injectIntoData $2"
            shift
            shift
            ;;
        --customTag)
            CUSTOMTAG="_$2"
            shift
            shift
            ;;
        --doCombo)
            COMBOARG="--combo 0l 1l 2l"
            shift
            ;;
        --dryRun)
            DRYRUN=1
            shift
            ;;
        --help)
            echo "How run this script:"
            echo "./makeDataCards.sh [OPTIONS]"
            echo "[OPTIONS]"
            echo "    --models mod1 mod2 ...      : space-separated list of the models to process"
            echo "    --masses mass1 mass2 ...    : space-separated list of the masses to process"
            echo "    --channels chan1 chan2 ...  : space-separated list of the channels to process ('combo' allowed)"
            echo "    --dataTypes type1 type2 ... : space-separated list of the data types to process"
            echo "    --lowMass ...               : make cards for low mass optimization"
            echo "    --highMass ...              : make cards for high mass optimization"
            echo "    --inputsTag ...             : tag for specifying input ROOT files"
            echo "    --maskA ...                 : mask the A region"
            echo "    --scaleSyst ...             : scale systematics by some amount including removing them"
            echo "    --systsToScale ...          : specify certain systs to scale only"
            echo "    --injectIntoData ...        : Inject signal into data with strength r"
            echo "    --customTag ...             : Custom tag for naming output cards folder"
            echo "    --doCombo ...               : Do combo of all three channels"
            echo "    --dryRun ...                : Print commands to be run only"
            exit 0
            ;;
        *)
            echo "Unknown option \"$1\""
            exit 1
            ;;
    esac
done

if [[ -z "${OPTIMIZATIONS}" ]]; then
    OPTIMIZATIONS=("MaxSign" "MassExclusion")
fi

for CHANNEL in ${CHANNELS[@]}; do
    for MODEL in ${MODELS[@]}; do
        for DATATYPE in ${DATATYPES}; do

            CONFIGTAG=${DATATYPE}
            if [[ ${DATATYPE} == *"pseudo"* ]]; then
                CONFIGTAG="OneLessInclusive"
            fi
            
            for OPT in ${OPTIMIZATIONS[@]}; do
                INPUTSTAG="Fix_11_05_23"
                if [[ "${OPT}" == "MaxSign" ]] && [[ "${MODEL}" == *"SYY"* ]] && [[ "${CHANNEL}" == *"1l"* ]]; then
                    INPUTSTAG="1_29_24"
                fi

                COMMAND="python produceDataCard.py --config configs/v3_5_1_${CONFIGTAG}/cardConfig_${CHANNEL}_${MODEL}_v3_5_1_${OPT}_Min3 --inpath DisCo_outputs_0l_1l_2l_${OPT}_${INPUTSTAG} --outpath ./cards_${OPT}_${DATATYPE}${MASKATAG}${SCALESYSTTAG}${CUSTOMTAG} --year Run2UL --channel ${CHANNEL} --model ${MODEL} --dataType ${DATATYPE} ${SCALESYSTFLAG} ${SYSTS2SCALE} ${INJECTINTODATAFLAG} ${COMBOARG}"
                echo "${COMMAND}"
                if [[ ${DRYRUN} != 1 ]]; then
                    eval ${COMMAND}
                fi
            done
        done
    done
done
