#!/bin/bash 

outDir=FullRun2

runFit () {    
    if [[ "$3" == "shared" ]]
    then
        card=Card${4}_shapesys.txt
        shared=true
    else
        card=Card${4}_shapesys_sep.txt
        shared=false
    fi

    echo '--- Running over systematic '$6', with '$3' parameters' 
    root -l -q 'make_MVA_8bin_ws.C("'$4'", "'$5'", "RPV", "550", "'$1'", "'$2'", '$shared', true)'
    text2workspace.py $card -o ws_$4_RPV_550.root -m 550 --keyword-value MODEL=RPV 
    combine -M FitDiagnostics ws_$4_RPV_550.root -m 550 --keyword-value MODEL=RPV --verbose 2 --cminDefaultMinimizerStrategy 1 --cminFallbackAlgo Minuit2,Migrad,0:0.1 \
        --cminFallbackAlgo Minuit2,Migrad,1:1.0 --cminFallbackAlgo Minuit2,Migrad,0:1.0 --X-rtd MINIMIZER_MaxCalls=999999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH \
        --rMax 5 --robustFit=1 --plots --saveShapes --saveNormalizations -n ${4}RPV550 > log_${4}RPV550_FitDiag.txt
    ./stash_fits.sh ${outDir}_${4}_$6_$3 $4
}

echo '---------------------'
echo '-- Starting 2016'
echo '---------------------'
runFit "TT" ""         "shared" 2016 Keras_2016_v1.1 "nom"
runFit "TT" ""         "sep"    2016 Keras_2016_v1.1 "nom"
runFit "TT" "_JECUp"   "shared" 2016 Keras_2016_v1.1 "JECUp"
runFit "TT" "_JECUp"   "sep"    2016 Keras_2016_v1.1 "JECUp"
runFit "TT" "_JECDown" "shared" 2016 Keras_2016_v1.1 "JECDown"
runFit "TT" "_JECDown" "sep"    2016 Keras_2016_v1.1 "JECDown"
runFit "TT" "_JERUp"   "shared" 2016 Keras_2016_v1.1 "JERUp"
runFit "TT" "_JERUp"   "sep"    2016 Keras_2016_v1.1 "JERUp"
runFit "TT" "_JERDown" "shared" 2016 Keras_2016_v1.1 "JERDown"
runFit "TT" "_JERDown" "sep"    2016 Keras_2016_v1.1 "JERDown"
runFit "TT_fsrUp"   "" "shared" 2016 Keras_2016_v1.1 "FSRUp"
runFit "TT_fsrUp"   "" "sep"    2016 Keras_2016_v1.1 "FSRUp"
runFit "TT_fsrDown" "" "shared" 2016 Keras_2016_v1.1 "FSRDown"
runFit "TT_fsrDown" "" "sep"    2016 Keras_2016_v1.1 "FSRDown"
runFit "TT_isrUp"   "" "shared" 2016 Keras_2016_v1.1 "ISRUp"
runFit "TT_isrUp"   "" "sep"    2016 Keras_2016_v1.1 "ISRUp"
runFit "TT_isrDown" "" "shared" 2016 Keras_2016_v1.1 "ISRDown"
runFit "TT_isrDown" "" "sep"    2016 Keras_2016_v1.1 "ISRDown"

echo '---------------------'
echo '-- Starting 2017'
echo '---------------------'
runFit "TT" ""         "shared" 2017 Keras_2017_v1.1 "nom"
runFit "TT" ""         "sep"    2017 Keras_2017_v1.1 "nom"
runFit "TT" "_JECUp"   "shared" 2017 Keras_2017_v1.1 "JECUp"
runFit "TT" "_JECUp"   "sep"    2017 Keras_2017_v1.1 "JECUp"
runFit "TT" "_JECDown" "shared" 2017 Keras_2017_v1.1 "JECDown"
runFit "TT" "_JECDown" "sep"    2017 Keras_2017_v1.1 "JECDown"
runFit "TT" "_JERUp"   "shared" 2017 Keras_2017_v1.1 "JERUp"
runFit "TT" "_JERUp"   "sep"    2017 Keras_2017_v1.1 "JERUp"
runFit "TT" "_JERDown" "shared" 2017 Keras_2017_v1.1 "JERDown"
runFit "TT" "_JERDown" "sep"    2017 Keras_2017_v1.1 "JERDown"
runFit "TT" "_fsrUp"   "shared" 2017 Keras_2017_v1.1 "FSRUp"
runFit "TT" "_fsrUp"   "sep"    2017 Keras_2017_v1.1 "FSRUp"
runFit "TT" "_fsrDown" "shared" 2017 Keras_2017_v1.1 "FSRDown"
runFit "TT" "_fsrDown" "sep"    2017 Keras_2017_v1.1 "FSRDown"
runFit "TT" "_isrUp"   "shared" 2017 Keras_2017_v1.1 "ISRUp"
runFit "TT" "_isrUp"   "sep"    2017 Keras_2017_v1.1 "ISRUp"
runFit "TT" "_isrDown" "shared" 2017 Keras_2017_v1.1 "ISRDown"
runFit "TT" "_isrDown" "sep"    2017 Keras_2017_v1.1 "ISRDown"

echo '---------------------'
echo '-- Starting 2018pre'
echo '---------------------'
runFit "TT" ""         "shared" 2018pre Keras_2018pre_v1.0 "nom"
runFit "TT" ""         "sep"    2018pre Keras_2018pre_v1.0 "nom"
runFit "TT" "_JECUp"   "shared" 2018pre Keras_2018pre_v1.0 "JECUp"
runFit "TT" "_JECUp"   "sep"    2018pre Keras_2018pre_v1.0 "JECUp"
runFit "TT" "_JECDown" "shared" 2018pre Keras_2018pre_v1.0 "JECDown"
runFit "TT" "_JECDown" "sep"    2018pre Keras_2018pre_v1.0 "JECDown"
runFit "TT" "_JERUp"   "shared" 2018pre Keras_2018pre_v1.0 "JERUp"
runFit "TT" "_JERUp"   "sep"    2018pre Keras_2018pre_v1.0 "JERUp"
runFit "TT" "_JERDown" "shared" 2018pre Keras_2018pre_v1.0 "JERDown"
runFit "TT" "_JERDown" "sep"    2018pre Keras_2018pre_v1.0 "JERDown"
runFit "TT" "_fsrUp"   "shared" 2018pre Keras_2018pre_v1.0 "FSRUp"
runFit "TT" "_fsrUp"   "sep"    2018pre Keras_2018pre_v1.0 "FSRUp"
runFit "TT" "_fsrDown" "shared" 2018pre Keras_2018pre_v1.0 "FSRDown"
runFit "TT" "_fsrDown" "sep"    2018pre Keras_2018pre_v1.0 "FSRDown"
runFit "TT" "_isrUp"   "shared" 2018pre Keras_2018pre_v1.0 "ISRUp"
runFit "TT" "_isrUp"   "sep"    2018pre Keras_2018pre_v1.0 "ISRUp"
runFit "TT" "_isrDown" "shared" 2018pre Keras_2018pre_v1.0 "ISRDown"
runFit "TT" "_isrDown" "sep"    2018pre Keras_2018pre_v1.0 "ISRDown"

echo '---------------------'
echo '-- Starting 2018post'
echo '---------------------'
runFit "TT" ""         "shared" 2018post Keras_2018post_v1.0 "nom"
runFit "TT" ""         "sep"    2018post Keras_2018post_v1.0 "nom"
runFit "TT" "_JECUp"   "shared" 2018post Keras_2018post_v1.0 "JECUp"
runFit "TT" "_JECUp"   "sep"    2018post Keras_2018post_v1.0 "JECUp"
runFit "TT" "_JECDown" "shared" 2018post Keras_2018post_v1.0 "JECDown"
runFit "TT" "_JECDown" "sep"    2018post Keras_2018post_v1.0 "JECDown"
runFit "TT" "_JERUp"   "shared" 2018post Keras_2018post_v1.0 "JERUp"
runFit "TT" "_JERUp"   "sep"    2018post Keras_2018post_v1.0 "JERUp"
runFit "TT" "_JERDown" "shared" 2018post Keras_2018post_v1.0 "JERDown"
runFit "TT" "_JERDown" "sep"    2018post Keras_2018post_v1.0 "JERDown"
runFit "TT" "_fsrUp"   "shared" 2018post Keras_2018post_v1.0 "FSRUp"
runFit "TT" "_fsrUp"   "sep"    2018post Keras_2018post_v1.0 "FSRUp"
runFit "TT" "_fsrDown" "shared" 2018post Keras_2018post_v1.0 "FSRDown"
runFit "TT" "_fsrDown" "sep"    2018post Keras_2018post_v1.0 "FSRDown"
runFit "TT" "_isrUp"   "shared" 2018post Keras_2018post_v1.0 "ISRUp"
runFit "TT" "_isrUp"   "sep"    2018post Keras_2018post_v1.0 "ISRUp"
runFit "TT" "_isrDown" "shared" 2018post Keras_2018post_v1.0 "ISRDown"
runFit "TT" "_isrDown" "sep"    2018post Keras_2018post_v1.0 "ISRDown"
