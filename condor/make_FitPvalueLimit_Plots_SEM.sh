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
DATE=("1.27.2022")
CARDS=("cardsInjectNominal_11_13_23_MaxSign_Min3" "cardsInjectNominal_11_13_23_MassExclusion_Min3")
#CARDS=("cardsInjectRPV400" "cardsInjectNominal")
YEARS=("Run2UL")
MODELS=("RPV")
MASSES=("400" "600" "800")
CHANNELS=("0l" "1l" "2l" "combo")
#CHANNELS=("combo")
#CHANNELS=("1l")
DATATYPES=("pseudoData" "pseudoDataS")

for YEAR in ${YEARS[@]}; do
    
#    for CARD in ${CARDS[@]}; do

        for MODEL in ${MODELS[@]}; do
            # --------------
            # make fit plots
            # --------------
            if [[ $command == "fit" ]] || [[ $command == "all" ]]; then
                echo "making fit plots -------------------------------------------"
                python make_fit_plots.py --path Fit_${YEAR}_with_${CARDS[0]} --all --postfit_b --plotdata --plotsig
                python make_fit_plots.py --path Fit_${YEAR}_with_${CARDS[0]} --all --postfit_sb --plotdata --plotsig
                python make_fit_plots.py --path Fit_${YEAR}_with_${CARDS[1]} --all --postfit_b --plotdata --plotsig
                python make_fit_plots.py --path Fit_${YEAR}_with_${CARDS[1]} --all --postfit_sb --plotdata --plotsig
                #python make_fit_plots.py --path Fit_${YEAR}_with_${CARDS} -s ${MODEL} -m 550 --channel 0l 1l -d ${DATATYPE} --plotb --plotdata
                #python make_fit_plots.py --path Fit_${YEAR}_with_${CARDS} -s ${MODEL} -m 550 --channel 0l 1l -d ${DATATYPE} --plotsb --plotdata
            fi

                    # ----------------
                    # make limit plots
                    # ----------------                  
                    if [[ $command == "limit" ]] || [[ $command == "all" ]]; then 
                        echo "making limit plots -------------------------------------------"
                        #python make_Limit_Plots.py --inputDir 'Fit_'"${YEAR}"'_with_'"${CARDS}" --year ${YEAR} --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} 
                        python make_Limit_Plots.py --inputDirs Fit_${YEAR}_with_${CARDS[0]} Fit_${YEAR}_with_${CARDS[1]} --outputDir GraftedLimitPlots_${CARDS[0]} --year ${YEAR} --model RPV --channel combo --dataType pseudoData --wip --graft 600
                        python make_Limit_Plots.py --inputDirs Fit_${YEAR}_with_${CARDS[0]} Fit_${YEAR}_with_${CARDS[1]} --outputDir GraftedLimitPlots_${CARDS[0]} --year ${YEAR} --model StealthSYY --channel combo --dataType pseudoData --wip --graft 650

                        python make_Limit_Plots.py --inputDirs Fit_${YEAR}_with_${CARDS[0]} Fit_${YEAR}_with_${CARDS[1]} --outputDir GraftedLimitPlots_${CARDS[0]} --year ${YEAR} --model RPV --channel combo --dataType pseudoData --wip --graft 600 --asimov
                        python make_Limit_Plots.py --inputDirs Fit_${YEAR}_with_${CARDS[0]} Fit_${YEAR}_with_${CARDS[1]} --outputDir GraftedLimitPlots_${CARDS[0]} --year ${YEAR} --model StealthSYY --channel combo --dataType pseudoData --wip --graft 650 --asimov
                        #python make_Limit_Plots.py --inputDir 'Fit_'"${YEAR}"'_with_'"${CARDS}" --year ${YEAR} --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} --wip
                        #python make_Limit_Plots.py --inputDir 'Fit_'"${YEAR}"'_with_'"${CARDS}" --year ${YEAR} --model ${MODEL} --channel ${CHANNEL} --dataType ${DATATYPE} --asimov --wip
                    fi

            for CHANNEL in ${CHANNELS[@]}; do
        
                for DATATYPE in ${DATATYPES[@]}; do

                    for MASS in ${MASSES[@]}; do
                    
                        # ---------------------
                        # copy the impact plots
                        # ---------------------
                        if [[ $command == "impact" ]] || [[ $command == "all" ]]; then
                            if [[ ${MASS} -le 600 ]]; then
                                mkdir Fit_${YEAR}_with_${CARDS[0]}/output-files/plots_dataCards_TT_allTTvar/impact_plots/
                                cd Fit_${YEAR}_with_${CARDS[0]}/output-files/${MODEL}_${MASS}_Run2UL/
                                scp -r impacts_${YEAR}${MODEL}${MASS}_${CHANNEL}_${DATATYPE}*.pdf ../plots_dataCards_TT_allTTvar/impact_plots/
                                cd ../../../
                            else
                                mkdir Fit_${YEAR}_with_${CARDS[1]}/output-files/plots_dataCards_TT_allTTvar/impact_plots/
                                cd Fit_${YEAR}_with_${CARDS[1]}/output-files/${MODEL}_${MASS}_Run2UL/
                                scp -r impacts_${YEAR}${MODEL}${MASS}_${CHANNEL}_${DATATYPE}*.pdf ../plots_dataCards_TT_allTTvar/impact_plots/
                                cd ../../../
                            fi
                        fi

                        # ------------------------
                        # make pvalue plots/tables
                        # ------------------------
                        if [[ $command == "pvalue" ]] || [[ $command == "all" ]]; then
                            echo "making pvalue plots -------------------------------------------"
                            #python make_Pvalue_PlotsTables.py --basedir Fit_${YEAR}_with_${CARDS} --outdir pvalue_plots --models ${MODEL} --channels ${CHANNEL} --pdf=pvalue_with_${CARDS} --dataTypes ${DATATYPE}
                            #python make_Pvalue_PlotsTables.py --basedir Fit_${YEAR}_with_${CARDS} --outdir pvalue_plots --models ${MODEL} --channels ${CHANNEL} --pdf=pvalue_with_${CARDS} --dataTypes ${DATATYPE} --asimov
                            python make_Pvalue_PlotsTables.py --basedirs Fit_${YEAR}_with_${CARDS[0]} Fit_${YEAR}_with_${CARDS[1]} --outdir GraftedPvaluePlots_${CARDS[0]} --models StealthSYY --wip --graft 650
                            python make_Pvalue_PlotsTables.py --basedirs Fit_${YEAR}_with_${CARDS[0]} Fit_${YEAR}_with_${CARDS[1]} --outdir GraftedPvaluePlots_${CARDS[0]} --models RPV --wip --graft 600
                            python make_Pvalue_PlotsTables.py --basedirs Fit_${YEAR}_with_${CARDS[0]} Fit_${YEAR}_with_${CARDS[1]} --outdir GraftedPvaluePlots_${CARDS[0]} --models StealthSYY --wip --graft 650 --asimov
                            python make_Pvalue_PlotsTables.py --basedirs Fit_${YEAR}_with_${CARDS[0]} Fit_${YEAR}_with_${CARDS[1]} --outdir GraftedPvaluePlots_${CARDS[0]} --models RPV --wip --graft 600 --asimov
                            #python make_Pvalue_PlotsTables.py --basedir Fit_${YEAR}_with_${CARDS} --outdir pvalue_plots --models ${MODEL} --channels 0l 1l 2l combo --pdf=pvalue_with_${CARDS} --dataTypes ${DATATYPE} --wip
                            #python make_Pvalue_PlotsTables.py --basedir Fit_${YEAR}_with_${CARDS} --outdir pvalue_plots --models ${MODEL} --channels 0l 1l 2l combo --pdf=pvalue_with_${CARDS} --dataTypes ${DATATYPE} --asimov --wip
                            
                        fi
#                    done
                done
            done
        done
    done
done


