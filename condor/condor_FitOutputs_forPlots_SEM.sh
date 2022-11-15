#!/bin/bash

# --------------------------------------------------------------------
# this script:
#   -- make dataCards
#   -- sends condor jobs to make impact plots and root files for plots
# --------------------------------------------------------------------

command=$1

#Configs=("cardConfig_0l" "cardConfig_1l" "cardConfig_2l")
#CHANNELS=("0l" "1l" "2l" "combo")
CHANNELS=("1l" "2l" "combo")
YEARS=("Run2UL")
MODELS=("RPV")
DATATYPES=("pseudoData" "pseudoDataS")
#MASSES=("300" "350" "400" "450" "500" "550" "600" "650" "700" "750" "800" "850" "900" "950" "1000" "1050" "1100" "1150" "1200" "1250" "1300" "1350" "1400")
FITS=("-F -A -I")
MASSES=("300-1400")
#CARDS=("cardsInjectRPV400" "cardsInjectNominal")
CARDS=("cardsInjectNominal")

# --------------
# make dataCards
# --------------
if [ $command == "cards" ]; then
    cd ../DataCardProducer
    
    for YEAR in ${YEARS[@]}; do    
        for MODEL in ${MODELS[@]}; do
                
            python produceDataCard.py --config cardConfig_0l --inpath inputs --outpath cardsInjectNominal --year Run2UL --lepton 0l --model ${MODEL}  
            python produceDataCard.py --config cardConfig_0l --inpath inputs --outpath cardsInjectNominal --year Run2UL --lepton 1l --model ${MODEL}  
            python produceDataCard.py --config cardConfig_0l --inpath inputs --outpath cardsInjectNominal --year Run2UL --lepton 2l --model ${MODEL} 
            #python produceDataCard.py --config cardConfig_0l --inpath inputs --outpath cardsInjectRPV400 --year Run2UL --lepton 0l --model ${MODEL} --injectedSignal ${MODEL}_400            
            #python produceDataCard.py --config cardConfig_0l --inpath inputs --outpath cardsInjectRPV400 --year Run2UL --lepton 1l --model ${MODEL} --injectedSignal ${MODEL}_400
            #python produceDataCard.py --config cardConfig_0l --inpath inputs --outpath cardsInjectRPV400 --year Run2UL --lepton 2l --model ${MODEL} --injectedSignal ${MODEL}_400 
        done
    done
fi

# ----------------
# send condor jobs 
# ----------------
if [ $command == "condor" ]; then
    cd ../condor/
    voms-proxy-init --voms cms --hours 168
    
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
fi
