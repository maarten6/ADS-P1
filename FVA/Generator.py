#!/usr/bin/env python3

"""Input generator for Offline.py, the program by the Federal Vaccination Agency to schedule vaccinations."""
import sys
import os
import random
from enum import Enum

class InputType(Enum):
    Fixed = 0 # Fixed schedule, multiple machines possible
    Consecutive = 1 # Fixed schedule, one after another, thus optimal used 1 machine
    ForceMachineMax = 2 # Fixed schedule, there are not allowed to be more than the provided amount of machines at a given time
    Multiplication = 3 # Semi-fixed schedule, multiple machines possible


if __name__ == "__main__":

    PATIENT_GAP_UPPER_BOUND = 10 # Upper bound for patient x range
    print("Type of input? Any[0] | Consecutive [1] | Maximum amount of machines [2] | Less flexible feasible intervals [3]")
    generationType = int(input())
    generatorMode = InputType(generationType)
    print("P1 value?")
    p1 = int(input())
    print("P2 value?")
    p2 = int(input())
    print("Total jobs?")
    jobCount = int(input())

    if generatorMode is InputType.ForceMachineMax:
        print("Max machines?")
        machineMax = int(input())

    if generatorMode is InputType.Multiplication:
        print("P multiplier?")
        pMulti = int(input())
    else:
        pMulti = 1

    fd = open('input.txt', 'w')

    gapSize = random.randint(0, 20)

    # Store all basic information in array
    lines = []
    lines.append(str(p1))
    lines.append(str(p2))
    lines.append(str(gapSize))
    lines.append(str(jobCount))

    next_r = 1 # r that the next iteration of InputType.Consecutive should use

    # Array to store how many machines are used currently. Used by InputType.ForceMachineMax
    totalPossibleTime = jobCount * ((p1 + p2) * pMulti + gapSize + PATIENT_GAP_UPPER_BOUND)
    totalMachinesAtTime = [0] * totalPossibleTime

    for i in range(0, jobCount):
        r = -1
        d = -1
        x = -1
        l = -1

        if generatorMode == InputType.Fixed or generatorMode == InputType.ForceMachineMax or generatorMode == InputType.Multiplication:
            # Fixed schedule, multiple machines possible
            r = random.randint(1, jobCount)
            d = r + p1 * pMulti - 1
            x = random.randint(0, PATIENT_GAP_UPPER_BOUND)
            l = p2 * pMulti

        if generatorMode == InputType.ForceMachineMax:
            # Check if the generated r,d,x,l fall within specification (i.e. don't exceed set maximum machine count)
            mayPlace = False
            while not mayPlace:
                mayPlace = True
                for slot in range(r, d+1):
                    if totalMachinesAtTime[slot] >= machineMax:
                        mayPlace = False
                for slot in range(d + gapSize + x + 1, d + gapSize + x + 1 + l):
                    if totalMachinesAtTime[slot] >= machineMax:
                        mayPlace = False
                if mayPlace:
                    for slot in range(r, d+1):
                        totalMachinesAtTime[slot] += 1
                    for slot in range(d + gapSize + x + 1, d + gapSize + x + 1 + l):
                        totalMachinesAtTime[slot] += 1
                else: 
                    r = totalPossibleTime
                    d = r + p1 * pMulti - 1
                    x = random.randint(0, PATIENT_GAP_UPPER_BOUND)
                    l = p2 * pMulti
                    oldPossible = totalPossibleTime
                    totalPossibleTime += p1 * pMulti + p2 * pMulti + x + gapSize
                    for slot in range(oldPossible, totalPossibleTime):
                        totalMachinesAtTime.append(0)

        if generatorMode == InputType.Consecutive:
            # Fixed schedule, one after another
            r = next_r
            d = r + p1 * pMulti - 1
            x = random.randint(0, PATIENT_GAP_UPPER_BOUND)
            l = p2 * pMulti
            next_r = d + x + gapSize + 1 + l

        lines.append(f"{r}, {d}, {x}, {l}")

    # Add newline character to all strings
    for i in range(0, len(lines)):
        lines[i] += "\n"
    
    fd.writelines(lines)

    # Count how many machines were made, output this as it should be the optimum
    if generatorMode == InputType.ForceMachineMax:
        machines = 0
        for i in range(0, len(totalMachinesAtTime)):
            machines = max(machines, totalMachinesAtTime[i])
        print(f"Optimum should have {machines} machines")