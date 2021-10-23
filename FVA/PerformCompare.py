#!/usr/bin/env python3

"""Performance checker for Offline.py, the program by the Federal Vaccination Agency to schedule vaccinations."""
import Offline as offlineOld
import Offline2 as offline
import sys
import os
from time import perf_counter
import multiprocessing as mp
import numpy as np
import pandas as pd

def evaluateFileOld(programInput, avgTime, result):
    evaluateFile(offlineOld, programInput, avgTime, result)

def evaluateFileNew(programInput, avgTime, result):
    evaluateFile(offline, programInput, avgTime, result)

def evaluateFile(module, programInput, avgTime, result):
    oldOut = sys.stdout

    times = []

    # Run the solvers a given amount of times on the input, store total time they took
    fd = open(os.devnull, 'w')
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
    #open and read the file after the appending:
    f = open("tableOffline.txt", "r")
    print(f.read())

    filenames = next(os.walk("Offline/"), (None, None, []))[2]  # [] if no file
    rows = []
    df = pd.DataFrame()

    for file in filenames:
        row = []
        print(f"==========={file}==========")
        oldIn = sys.stdin
        oldOut = sys.stdout
        
        if (file == "1000000.txt"):
            continue

        row.append(file)
        # Start by reading and parsing the file
        fin = open(f"Offline/{file}", "r")
        sys.stdin = fin
        programInput = offline.parseInput()
        fin.close()
        sys.stdin = oldIn

        avgTime = mp.Value("d", -1, lock=False)
        result = mp.Value("u", '?', lock=False)
        p=mp.Process(target = evaluateFileNew, args = (programInput, avgTime, result))
        p.start()

        p.join(15)

        print("New (CP-SAT) algorithm:")
        if p.is_alive():
            print("Took to long...")
            p.kill()
            p.join()
            resultNew = "?"
            CPSAT = 'X'
        else: 
            avgNew = avgTime.value
            resultNew = result.value
            print(resultNew)
            print(f"Avg: {avgNew}")
            CPSAT = round(avgNew,3)

        p=mp.Process(target = evaluateFileOld, args = (programInput, avgTime, result))
        p.start()

        p.join(15)

        print("Old (ILP) algorithm:")
        if p.is_alive():
            print("Took to long...")
            p.kill()
            p.join()
            resultOld = "?"
            LS = 'X'
        else:
            avgOld = avgTime.value
            resultOld = result.value
            print(resultOld)
            print(f"Avg: {avgOld}")
            LS = round(avgOld,3)
        if resultOld == resultNew == 'S':
            speedup = round(avgOld / avgNew, 3)
            print(f"On average, new one was {avgOld / avgNew} times faster than old one\n\n\n")
        else: 
            speedup = '-'
        row = pd.DataFrame({'Filename': [file], 'LS': [LS], 'CP-SAT': [CPSAT], 'LS/CP-SAT': [speedup]})
        df = df.append(row, ignore_index=True)

    f = open('tableOffline.txt', 'w')
    f.write(df.to_latex(index=False))
    f.close()