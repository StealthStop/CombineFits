#!/bin/bash

# -----------------------------------------------------------------------
# How run this script:
# ./make_FitPvalueLimit_Plots_SEM.sh all
# ./make_FitPvalueLimit_Plots_SEM.sh impact
# ./make_FitPvalueLimit_Plots_SEM.sh fit
# ./make_FitPvalueLimit_Plots_SEM.sh limit
# ./make_FitPvalueLimit_Plots_SEM.sh pvalue
#
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

command=$1
DATE=("04.11.2022")
CARDS=("cardsInjectNominal")
#CARDS=("cardsInjectRPV400" "cardsInjectNominal")
YEARS=("Run2UL")
MODELS=("RPV")
MASSES=("550")
#CHANNELS=("0l" "1l" "2l" "combo")
CHANNELS=("1l" "2l" "combo")
DATATYPES=("pseudoData" "pseudoDataS")

for YEAR in ${YEARS[@]}; do
    
    for CARD in ${CARDS[@]}; do

        for CHANNEL in ${CHANNELS[@]}; do
    
            for MODEL in ${MODELS[@]}; do
    
                for MASS in ${MASSES[@]}; do

                    for DATATYPE in ${DATATYPES[@]}; do
                    
                        # ---------------------
                        # copy the impact plots
                        # ---------------------
                        if [[ $command == "impact" ]]; then
                            mkdir Fit_${YEAR}_with_${CARD}/output-files/plots_dataCards_TT_allTTvar/impact_plots/
                            cd Fit_${YEAR}_with_${CARD}/output-files/${MODEL}_${MASS}_Run2UL/
                            scp -r impacts_${YEAR}${MODEL}${MASS}_${CHANNEL}_${DATATYPE}*.pdf ../plots_dataCards_TT_allTTvar/impact_plots/
                            cd ../../../
                        fi

                        # --------------
                        # make fit plots
                        # --------------
                        if [[ $command == "fit" ]] || [[ $command == "all" ]]; then
                            echo "making fit plots -------------------------------------------"
                            python make_fit_plots.py --path Fit_${YEAR}_with_${CARD} --all --plotb --plotdata
                            python make_fit_plots.py --path Fit_${YEAR}_with_${CARD} --all --plotsb --plotdata
                            #python make_fit_plots.py --path Fit_${YEAR}_with_${CARD} -s ${MODEL} -m 550 --channel 0l 1l -d ${DATATYPE} --plotb --plotdata
                            #python make_fit_plots.py --path Fit_${YEAR}_with_${CARD} -s ${MODEL} -m 550 --channel 0l 1l -d ${DATATYPE} --plotsb --plotdata
                        fi
                        
                        # ----------------
                        # make limit plots
                        # ----------------                  
                        if [[ $command == "limit" ]] || [[ $command == "all" ]]; then 
                            echo "making limit plots -------------------------------------------"
                            #python make_Limit_Plots.py --inputDir 'Fit_'"${YEAR}"'_with_'"${CARD}" --year ${YEAR} --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} 
                            python make_Limit_Plots.py --inputDir 'Fit_'"${YEAR}"'_with_'"${CARD}" --year ${YEAR} --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} --wip
                        fi

                        # ------------------------
                        # make pvalue plots/tables
                        # ------------------------
                        if [[ $command == "pvalue" ]] || [[ $command == "all" ]]; then
                            echo "making pvalue plots -------------------------------------------"
                            #python make_Pvalue_PlotsTables.py --basedir Fit_${YEAR}_with_${CARD} --outdir pvalue_plots --models ${MODEL} --channels ${CHANNEL} --pdf=pvalue_with_${CARD} --dataTypes ${DATATYPE}
                            #python make_Pvalue_PlotsTables.py --basedir Fit_${YEAR}_with_${CARD} --outdir pvalue_plots --models ${MODEL} --channels ${CHANNEL} --pdf=pvalue_with_${CARD} --dataTypes ${DATATYPE} --asimov
                            python make_Pvalue_PlotsTables.py --basedir Fit_${YEAR}_with_${CARD} --outdir pvalue_plots --models ${MODEL} --channels 1l 2l combo --pdf=pvalue_with_${CARD} --dataTypes ${DATATYPE} --wip
                            python make_Pvalue_PlotsTables.py --basedir Fit_${YEAR}_with_${CARD} --outdir pvalue_plots --models ${MODEL} --channels 1l 2l combo --pdf=pvalue_with_${CARD} --dataTypes ${DATATYPE} --asimov --wip
                            
                        fi
                    done
                done
            done
        done
    done
done


