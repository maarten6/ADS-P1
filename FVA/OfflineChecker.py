#!/usr/bin/env python3

"""Output checker for Offline.py, the program by the Federal Vaccination Agency to schedule vaccinations. Will check if the output is consistent with the input"""
import Offline as offline
import sys
import os


class PatientOutput:
    def __init__(self, line):
        ints = [int(x.strip()) for x in line.split(',')]
        self.T1 = ints[0]
        self.M1 = ints[1]
        self.T2 = ints[2]
        self.M2 = ints[3]

    def checkRange(self, patientInput, programInput):
        t1Correct = patientInput.r <= self.T1 <= patientInput.d - programInput.p1 + 1
        t2Correct = self.T1 + programInput.p1 + programInput.gap + patientInput.x <= self.T2 <= self.T1 + programInput.p1 + programInput.gap + patientInput.x + patientInput.l - programInput.p2
        return t1Correct and t2Correct

if __name__ == "__main__":
    #os.remove('output.txt')
    oldOut = sys.stdout
    fd = open('output.txt', 'w+')

    sys.stdout = fd
    programInput = offline.parseInput()
    offline.SolveILP(programInput)
    fd.close()
    sys.stdout = oldOut

    machinesInUse = [None] * (len(programInput.patients) + 1)
    for i in range(1, len(machinesInUse)):
        machinesInUse[i] = { }

    fd = open('output.txt', 'r')
    patients = []
    lines = fd.read().split('\n')
    for line in lines:
        try:
            patients.append(PatientOutput(line))
        except:
            pass

    print(f"Total machines: {lines[len(lines)-2]}")

    for i in range(0, len(patients)):
        if not patients[i].checkRange(programInput.patients[i], programInput):
            print(f"Inconsistency with job {i}")
        else:
            print(f"Consistency with job {i}")
        
        allTimesInUse = range(patients[i].T1, patients[i].T1 + programInput.p1)
        for time in allTimesInUse:
            if time in machinesInUse[patients[i].M1]:
                print(f"Hospital {patients[i].M1} double booked at time {time} for dose 1 by job {i+1} and job {machinesInUse[patients[i].M1][time]+1}")
            else:
                machinesInUse[patients[i].M1][time] = i

        allTimesInUse = range(patients[i].T2, patients[i].T2 + programInput.p2)
        for time in allTimesInUse:
            if time in machinesInUse[patients[i].M2]:
                print(f"Hospital {patients[i].M2} double booked at time {time} for dose 2 by job {i+1} and job {machinesInUse[patients[i].M2][time]+1}")
            else:
                machinesInUse[patients[i].M2][time] = i
    