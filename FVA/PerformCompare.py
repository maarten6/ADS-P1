#!/usr/bin/env python3

"""Performance checker for Offline.py, the program by the Federal Vaccination Agency to schedule vaccinations."""
import Offline as offlineOld
import Offline2 as offline
import sys
import os
from time import perf_counter

if __name__ == "__main__":
    #os.remove('output.txt')
    programInput = offline.parseInput()
    oldTimes = []
    newTimes = []

    oldOut = sys.stdout
    fd = open(os.devnull, 'w')
    sys.stdout = fd
    for i in range(0, 10):
        start = perf_counter()
        offline.SolveILP(programInput)
        end = perf_counter()
        newTimes.append(end - start)

        start = perf_counter()
        offlineOld.SolveILP(programInput)
        end = perf_counter()
        oldTimes.append(end - start)

    fd.close()
    sys.stdout = oldOut

    print("Old (ILP) algorithm:")
    print(oldTimes)
    avgOld = sum(oldTimes)/len(oldTimes)
    print(f"Avg: {avgOld}")
    print()
    print("New (CP-SAT) algorithm:")
    print(newTimes)
    avgNew = sum(newTimes)/len(newTimes)
    print(f"Avg: {avgNew}")
    print(f"On avg, new took {avgNew / avgOld} of time old takes")