#!/usr/bin/env python3

"""Performance checker for Offline*.py, the programs by the Federal Vaccination Agency to schedule vaccinations."""
import OfflineLS as offlineILP
import OfflineCPSAT as offlineCPSAT
import sys
import os
from time import perf_counter
import multiprocessing as mp
import pandas as pd
import re

# This function is from: https://stackoverflow.com/questions/4813061/non-alphanumeric-list-order-from-os-listdir
# Sorting based on alphabetical and numerical values
def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split("([0-9]+)", key) ] 
    return sorted(data, key=alphanum_key)

def evaluateFileOld(programInput, avgTime, result):
    evaluateFile(offlineILP, programInput, avgTime, result)

def evaluateFileNew(programInput, avgTime, result):
    evaluateFile(offlineCPSAT, programInput, avgTime, result)

def evaluateFile(module, programInput, avgTime, result):
    oldOut = sys.stdout

    times = []

    # Run the solvers a given amount of times on the input, store total time they took
    fd = open(os.devnull, "w")
    sys.stdout = fd
    for i in range(0, 1):
        start = perf_counter()
        result.value = module.SolveILP(programInput)
        end = perf_counter()
        times.append(end - start)

    fd.close()
    sys.stdout = oldOut

    # Print statistics
    avgTime.value = sum(times) / len(times)

if __name__ == "__main__":
    testInstanceDir = "../TestInstances/Offline"
    filenames = sorted_alphanumeric(os.listdir(testInstanceDir))

    # Initialise the table
    df = pd.DataFrame()

    for file in filenames:
        print(f"==========={file}==========")
        oldIn = sys.stdin
        oldOut = sys.stdout
        
        if (file == "1000000.txt"):
            continue

        # Start by reading and parsing the file
        fin = open(f"{testInstanceDir}/{file}", "r")
        sys.stdin = fin
        programInput = offlineCPSAT.parseInput()
        fin.close()
        sys.stdin = oldIn

        avgTime = mp.Value("d", -1, lock=False)
        result = mp.Value("u", "?", lock=False)
        avgTimeVarOld = mp.Value("d", -1, lock=False)
        resultVarOld = mp.Value("u", "?", lock=False)
        p=mp.Process(target = evaluateFileNew, args = (programInput, avgTime, result))
        p.start()
        
        # Time limit for preprocessing of the data, set to 30 minutes
        p.join(60)

        print("New (CP-SAT) algorithm:")
        if p.is_alive():
            print("Took to long...")
            p.kill()
            p.join()
            resultNew = "?"
            CPSAT = "X"
        else: 
            avgNew = avgTime.value
            resultNew = result.value
            print(resultNew)
            print(f"Avg: {avgNew}")
            CPSAT = round(avgNew, 3)

        p=mp.Process(target = evaluateFileOld, args = (programInput, avgTimeVarOld, resultVarOld))
        p.start()

        p.join(60)

        print("Old (ILP) algorithm:")
        if p.is_alive():
            print("Took to long...")
            p.kill()
            p.join()
            resultOld = "?"
            LS = "X"
        else:
            avgOld = avgTimeVarOld.value
            resultOld = resultVarOld.value
            print(resultOld)
            print(f"Avg: {avgOld}")
            LS = round(avgOld,3)
        if resultOld == resultNew == "S":
            speedup = round(avgOld / avgNew, 3)
            print(f"On average, new one was {avgOld / avgNew} times faster than old one\n\n\n")
        else: 
            speedup = "-"
        row = pd.DataFrame({"Filename": [file], "LS": [LS], "CP-SAT": [CPSAT], "LS/CP-SAT": [speedup]})
        df = df.append(row, ignore_index=True)

    f = open("tableOffline.txt", "w")
    f.write(df.to_latex(index=False))
    f.close()