import ROOT
import math
import sys
import os
import json
import subprocess
import numpy as np
import array as arr
from os import system
from ROOT import TFile, gROOT, gStyle

debug = True

def print_db(input):
    if (debug):
        print input

def main():

    # ---------------------
    # get the data cards
    # ---------------------
    paths = [
        "OldSeed_Cards" ,
        "TopSeed_Cards" ,
    ]

    dataCards = [
        # ------------
        # RPV
        # ------------
        "CardRPV350_diffavg.txt" ,
        "CardRPV550_diffavg.txt" ,
        "CardRPV850_diffavg.txt" ,
        # mass1 vs pt1 / mass & pt & scalarPt ranks
        "CardRPV350_m1vsPt_Mass.txt" ,
        "CardRPV550_m1vsPt_Mass.txt" ,
        "CardRPV850_m1vsPt_Mass.txt" ,
        "CardRPV350_m1vsPt_Pt.txt" ,
        "CardRPV550_m1vsPt_Pt.txt" ,
        "CardRPV850_m1vsPt_Pt.txt" ,
        "CardRPV350_m1vsPt_SPt.txt" ,
        "CardRPV550_m1vsPt_SPt.txt" ,
        "CardRPV850_m1vsPt_SPt.txt" ,     
        "CardRPV350_m1vsSPt_SPt.txt" ,
        "CardRPV550_m1vsSPt_SPt.txt" ,
        "CardRPV850_m1vsSPt_SPt.txt" ,
        # mass2 vs pt2 / mass & pt & scalarPt ranks
        "CardRPV350_m2vsPt_Mass.txt" ,
        "CardRPV550_m2vsPt_Mass.txt" ,
        "CardRPV850_m2vsPt_Mass.txt" ,
        "CardRPV350_m2vsPt_Pt.txt" ,
        "CardRPV550_m2vsPt_Pt.txt" ,
        "CardRPV850_m2vsPt_Pt.txt" ,
        "CardRPV350_m2vsPt_SPt.txt" ,
        "CardRPV550_m2vsPt_SPt.txt" ,
        "CardRPV850_m2vsPt_SPt.txt" ,
        "CardRPV350_m2vsSPt_SPt.txt" ,
        "CardRPV550_m2vsSPt_SPt.txt" ,
        "CardRPV850_m2vsSPt_SPt.txt" ,
        # mass1 vs mass2 / mass & pt & scalarPt ranks
        "CardRPV350_stop12_Mass.txt" ,
        "CardRPV550_stop12_Mass.txt" ,
        "CardRPV850_stop12_Mass.txt" , 
        "CardRPV350_stop12_Pt.txt" ,
        "CardRPV550_stop12_Pt.txt" ,
        "CardRPV850_stop12_Pt.txt" ,
        "CardRPV350_stop12_SPt.txt" ,
        "CardRPV550_stop12_SPt.txt" ,
        "CardRPV850_stop12_SPt.txt" ,
        
        # ------------
        # SHH
        # ------------
        "CardSHH350_diffavg.txt" ,
        "CardSHH550_diffavg.txt" ,
        "CardSHH850_diffavg.txt" ,
        # mass1 vs pt1 / mass & pt & scalarPt ranks
        "CardSHH350_m1vsPt_Mass.txt" ,
        "CardSHH550_m1vsPt_Mass.txt" ,
        "CardSHH850_m1vsPt_Mass.txt" ,
        "CardSHH350_m1vsPt_Pt.txt" ,
        "CardSHH550_m1vsPt_Pt.txt" ,
        "CardSHH850_m1vsPt_Pt.txt" ,
        "CardSHH350_m1vsPt_SPt.txt" ,
        "CardSHH550_m1vsPt_SPt.txt" ,
        "CardSHH850_m1vsPt_SPt.txt" ,
        "CardSHH350_m1vsSPt_SPt.txt" ,
        "CardSHH550_m1vsSPt_SPt.txt" ,
        "CardSHH850_m1vsSPt_SPt.txt" ,
        # mass2 vs pt2 / mass & pt & scalarPt ranks
        "CardSHH350_m2vsPt_Mass.txt" ,
        "CardSHH550_m2vsPt_Mass.txt" ,
        "CardSHH850_m2vsPt_Mass.txt" ,
        "CardSHH350_m2vsPt_Pt.txt" ,
        "CardSHH550_m2vsPt_Pt.txt" ,
        "CardSHH850_m2vsPt_Pt.txt" ,
        "CardSHH350_m2vsPt_SPt.txt" ,
        "CardSHH550_m2vsPt_SPt.txt" ,
        "CardSHH850_m2vsPt_SPt.txt" ,
        "CardSHH350_m2vsSPt_SPt.txt" ,
        "CardSHH550_m2vsSPt_SPt.txt" ,
        "CardSHH850_m2vsSPt_SPt.txt" ,
        # mass1 vs mass2 / mass & pt & scalarPt ranks
        "CardSHH350_stop12_Mass.txt" ,
        "CardSHH550_stop12_Mass.txt" ,
        "CardSHH850_stop12_Mass.txt" ,
        "CardSHH350_stop12_Pt.txt" ,
        "CardSHH550_stop12_Pt.txt" ,
        "CardSHH850_stop12_Pt.txt" ,
        "CardSHH350_stop12_SPt.txt" ,
        "CardSHH550_stop12_SPt.txt" ,
        "CardSHH850_stop12_SPt.txt" ,

        # ------------
        # SYY
        # ------------
        "CardSYY350_diffavg.txt" ,
        "CardSYY550_diffavg.txt" ,
        "CardSYY850_diffavg.txt" ,
        # mass1 vs pt1 / mass & pt & scalarPt ranks
        "CardSYY350_m1vsPt_Mass.txt" ,
        "CardSYY550_m1vsPt_Mass.txt" ,
        "CardSYY850_m1vsPt_Mass.txt" ,
        "CardSYY350_m1vsPt_Pt.txt" ,
        "CardSYY550_m1vsPt_Pt.txt" ,
        "CardSYY850_m1vsPt_Pt.txt" ,
        "CardSYY350_m1vsPt_SPt.txt" ,
        "CardSYY550_m1vsPt_SPt.txt" ,
        "CardSYY850_m1vsPt_SPt.txt" ,
        "CardSYY350_m1vsSPt_SPt.txt" ,
        "CardSYY550_m1vsSPt_SPt.txt" ,
        "CardSYY850_m1vsSPt_SPt.txt" ,
        # mass2 vs pt2 / mass & pt & scalarPt ranks
        "CardSYY350_m2vsPt_Mass.txt" ,
        "CardSYY550_m2vsPt_Mass.txt" ,
        "CardSYY850_m2vsPt_Mass.txt" ,
        "CardSYY350_m2vsPt_Pt.txt" ,
        "CardSYY550_m2vsPt_Pt.txt" ,
        "CardSYY850_m2vsPt_Pt.txt" ,
        "CardSYY350_m2vsPt_SPt.txt" ,
        "CardSYY550_m2vsPt_SPt.txt" ,
        "CardSYY850_m2vsPt_SPt.txt" ,
        "CardSYY350_m2vsSPt_SPt.txt" ,
        "CardSYY550_m2vsSPt_SPt.txt" ,
        "CardSYY850_m2vsSPt_SPt.txt" ,
        # mass1 vs mass2 / mass & pt & scalarPt ranks
        "CardSYY350_stop12_Mass.txt" ,
        "CardSYY550_stop12_Mass.txt" ,
        "CardSYY850_stop12_Mass.txt" ,
        "CardSYY350_stop12_Pt.txt" ,
        "CardSYY550_stop12_Pt.txt" ,
        "CardSYY850_stop12_Pt.txt" ,
        "CardSYY350_stop12_SPt.txt" ,
        "CardSYY550_stop12_SPt.txt" ,
        "CardSYY850_stop12_SPt.txt" ,    

    ]

    os.system("rm Significance.txt")
    os.system("rm ExpectedSignificance.txt")

    # ---------------------------
    # loop over the data cards
    # ---------------------------
    for datacard in dataCards:
        print("------------------------------------------------------------------------------")
        print_db("Getting data cards: " + datacard)
        print("------------------------------------------------------------------------------")
         
        # ----------------------
        # loop over the paths
        # ----------------------
        for path in paths:
            #print("\n")
            print_db("Going to path: " + path)

            # --------------------------------
            # saving the outputs as a txt file
            # --------------------------------
            with open('Significance.txt', 'a') as f:
                f.write("------------------------------------------------------------------------------\n")
                f.write("GettingDataCards: " + datacard + "\n")
                f.write("GoingToPath: " + path + "\n")
                f.write("------------------------------------------------------------------------------\n")
                f.close()

            # --------------------------------
            # running the combine tool command
            # --------------------------------
            command = ('combine -M Significance ' + path + "/" + datacard + ' -t -1 --expectSignal=1')
            os.system(command + '&>> Significance.txt')      


    # -----------------------------------------------
    # read the txt file to get only significance line
    # -----------------------------------------------
    ExpectedSignificance = {}

    with open("Significance.txt", "r") as f:
        all_lines = f.readlines()
        
        for line in all_lines:
            if "GettingDataCards: " in line:
                datacard_ = line.split(" ")[-1].rstrip("\n")
            if "GoingToPath: " in line:
                path_ = line.split(" ")[-1].rstrip("\n")
            if "Significance: " in line:
                significance = float(line.split(" ")[-1].rstrip("\n"))
               
                file1 = open("ExpectedSignificance.txt", "a")
                file1.writelines("Data Card: %s  |  Seed Method: %s  |  Significance: %f\n" % (datacard_, path_, significance))
 
                # ----------------------------------------        
                # create a dictionary to convert into JSON
                # ----------------------------------------
                ExpectedSignificance = {
                    "data card   " : datacard_,
                    "seed method " : path_,
                    "significance" : significance,
                }

                # -----------------
                # convert into JSON
                # -----------------
                x = json.dumps(ExpectedSignificance, indent=1)
                with open('ExpectedSignificance_json.txt', 'a') as f:
                    f.write(x)
                    f.close()
 
    file1.close()
  
if __name__ == "__main__":
    main()                
