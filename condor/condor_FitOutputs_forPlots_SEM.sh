#!/bin/bash

# --------------------------------------------------------------------
# this script:
#   -- make dataCards
#   -- sends condor jobs to make impact plots and root files for plots
# --------------------------------------------------------------------

# --------------
# make dataCards
# --------------
cd ../DataCardProducer/
python produceDataCard.py --outpath cardsInjectNominal -c cardConfig_includingSystTT -p inputs --all
#python produceDataCard.py --outpath cardsInjectRPV400 -c cardConfig_includingSystTT --injectedSignal RPV_400 -p inputs --all


# ----------------
# send condor jobs 
# ----------------
cd ../condor/
voms-proxy-init --voms cms --hours 168

CHANNELS=("0l" "1l" "combo")
#CHANNELS=("1l")
YEARS=("Run2UL")
MODELS=("RPV")
DATATYPES=("pseudoData" "pseudoDataS")
FITS=("-F -A -I")
MASSES=("300-1400")
#CARDS=("cardsInjectRPV400" "cardsInjectNominal")
CARDS=("cardsInjectNominal")

for YEAR in ${YEARS[@]}; do
    for CHANNEL in ${CHANNELS[@]}; do
        for MODEL in ${MODELS[@]}; do
            for DATATYPE in ${DATATYPES[@]}; do
                for FIT in "${FITS[@]}"; do
                    for MASS in ${MASSES[@]}; do 
                        for CARD in ${CARDS[@]}; do

                            CMD="python condorSubmit.py --cards ${CARD} -y ${YEAR} -d ${MODEL} -m ${MASS} -t ${DATATYPE} ${FIT} -s ${CHANNEL} --output Fit_${YEAR}_with_${CARD}"

                            echo "Running: $CMD"
                            eval $CMD
                        done
                    done
                done
            done
        done
    done
done

