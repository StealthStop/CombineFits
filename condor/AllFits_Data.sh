# Run 1L fits first
python condorSubmit.py -d RPV -t Data -s 1l -m 650-1400 -y Run2UL -A --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s 1l -m 650-1400 -y Run2UL -F --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s 1l -m 650-1400 -y Run2UL -M --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s 1l -m 650-1400 -y Run2UL -I --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data

python condorSubmit.py -d SYY -t Data -s 1l -m 700-1400 -y Run2UL -A --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s 1l -m 700-1400 -y Run2UL -F --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s 1l -m 700-1400 -y Run2UL -M --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s 1l -m 700-1400 -y Run2UL -I --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data

python condorSubmit.py -d RPV -t Data -s 1l -m 300-600 -y Run2UL -A --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s 1l -m 300-600 -y Run2UL -F --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s 1l -m 300-600 -y Run2UL -M --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s 1l -m 300-600 -y Run2UL -I --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data

python condorSubmit.py -d SYY -t Data -s 1l -m 300-650 -y Run2UL -A --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s 1l -m 300-650 -y Run2UL -F --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s 1l -m 300-650 -y Run2UL -M --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s 1l -m 300-650 -y Run2UL -I --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data


# Then queue 0L fits
python condorSubmit.py -d RPV -t Data -s 0l -m 650-1400 -y Run2UL -A --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s 0l -m 650-1400 -y Run2UL -F --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s 0l -m 650-1400 -y Run2UL -M --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s 0l -m 650-1400 -y Run2UL -I --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data

python condorSubmit.py -d SYY -t Data -s 0l -m 700-1400 -y Run2UL -A --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s 0l -m 700-1400 -y Run2UL -F --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s 0l -m 700-1400 -y Run2UL -M --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s 0l -m 700-1400 -y Run2UL -I --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data

python condorSubmit.py -d RPV -t Data -s 0l -m 300-600 -y Run2UL -A --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s 0l -m 300-600 -y Run2UL -F --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s 0l -m 300-600 -y Run2UL -M --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s 0l -m 300-600 -y Run2UL -I --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data

python condorSubmit.py -d SYY -t Data -s 0l -m 300-650 -y Run2UL -A --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s 0l -m 300-650 -y Run2UL -F --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s 0l -m 300-650 -y Run2UL -M --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s 0l -m 300-650 -y Run2UL -I --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data


# Then queue 2L fits
python condorSubmit.py -d RPV -t Data -s 2l -m 650-1400 -y Run2UL -A --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s 2l -m 650-1400 -y Run2UL -F --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s 2l -m 650-1400 -y Run2UL -M --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s 2l -m 650-1400 -y Run2UL -I --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data

python condorSubmit.py -d SYY -t Data -s 2l -m 700-1400 -y Run2UL -A --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s 2l -m 700-1400 -y Run2UL -F --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s 2l -m 700-1400 -y Run2UL -M --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s 2l -m 700-1400 -y Run2UL -I --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data

python condorSubmit.py -d RPV -t Data -s 2l -m 300-600 -y Run2UL -A --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s 2l -m 300-600 -y Run2UL -F --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s 2l -m 300-600 -y Run2UL -M --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s 2l -m 300-600 -y Run2UL -I --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data

python condorSubmit.py -d SYY -t Data -s 2l -m 300-650 -y Run2UL -A --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s 2l -m 300-650 -y Run2UL -F --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s 2l -m 300-650 -y Run2UL -M --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s 2l -m 300-650 -y Run2UL -I --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data


# Finally queue combo fits
python condorSubmit.py -d RPV -t Data -s combo -m 650-1400 -y Run2UL -A --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s combo -m 650-1400 -y Run2UL -F --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s combo -m 650-1400 -y Run2UL -M --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d RPV -t Data -s combo -m 650-1400 -y Run2UL -I --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data

python condorSubmit.py -d SYY -t Data -s combo -m 700-1400 -y Run2UL -A --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s combo -m 700-1400 -y Run2UL -F --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s combo -m 700-1400 -y Run2UL -M --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data
python condorSubmit.py -d SYY -t Data -s combo -m 700-1400 -y Run2UL -I --cards=cards_MassExclusion_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MassExclusion_Data

python condorSubmit.py -d RPV -t Data -s combo -m 300-600 -y Run2UL -A --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s combo -m 300-600 -y Run2UL -F --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s combo -m 300-600 -y Run2UL -M --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d RPV -t Data -s combo -m 300-600 -y Run2UL -I --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data

python condorSubmit.py -d SYY -t Data -s combo -m 300-650 -y Run2UL -A --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s combo -m 300-650 -y Run2UL -F --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s combo -m 300-650 -y Run2UL -M --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
python condorSubmit.py -d SYY -t Data -s combo -m 300-650 -y Run2UL -I --cards=cards_MaxSign_Data/ --output=Fit_Run2UL_with_cardsInjectNominal_MaxSign_Data
