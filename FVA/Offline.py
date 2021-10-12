#!/usr/bin/env python3
# Copyright 2010-2021 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from ortools.linear_solver import pywraplp

class Patient:
    def __init__(self, r, d, x, l):
        self.r = r
        self.d = d
        self.x = x
        self.l = l

class ProgramInput:
    def __init__(self, p1, p2, gap, patients, mintime, maxtime):
        self.p1 = p1
        self.p2 = p2
        self.gap = gap
        self.patients = patients
        self.maxtime = maxtime
        self.mintime = mintime

def parsePatient(line):
    patientValues = [int(x.strip()) for x in line.split(',')]
    return Patient(patientValues[0], patientValues[1], patientValues[2], patientValues[3])

def parseInput():
    p1 = int(input())
    p2 = int(input())
    gap = int(input())
    numPatients = int(input())
    patients = []
    maxtime = [0] * 2
    mintime = [float('inf')] * 2
    for i in range(0, numPatients):
        patient = parsePatient(input())
        patients.append(patient)
        # First dose maximum interval, over all patients
        mintime[0] = min(mintime[0], patient.r)
        maxtime[0] = max(maxtime[0], patient.d)
        # Second dose maximum interval, over all patients
        mintime[1] = min(mintime[1], patient.r + p1 + gap + patient.x)
        maxtime[1] = max(maxtime[1], patient.d + p1 + gap + patient.x + patient.l - 1)
    if numPatients == 0:
        print(0)
        exit()
    return ProgramInput(p1, p2, gap, patients, mintime, maxtime)

def SolveILP(programInput):
    """Integer  programming sample."""
    # [START solver]
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')
    patients = programInput.patients
    numTimeslots = programInput.maxtime[1] - programInput.mintime[0] + 1
    # Note that this is the maximum feasible interval of dose 1 by considering all patiens
    numTimeslotsDose1 = programInput.maxtime[0] - programInput.mintime[0] + 1
    # Note that this is the maximum feasible interval of dose 2 by considering all patiens
    numTimeslotsDose2 = programInput.maxtime[1] - programInput.mintime[1] + 1

    # [END solver]

    # [START variables] 
    # y_jt: 1, if the first dose of job j is taken on timeslot t
    #        0, otherwise
    # z_jt: 1, if the second dose of job j is taken on timeslot t
    #        0, otherwise
    # T_j  : Timeslot where dose 1 is taken of job j
    # m_t  : Amount of machines used on timeslot t
    # M    : Maximal number of concurrent machines over all timeslots

    # Initialise arrays that holds variables of dose 1 and dose 2
    dose1 = [None] * len(patients)
    dose2 = [None] * len(patients)
    # The timeslot number where dose 1, of each job is done
    Ts = [None] * len(patients)
    # The timeslot number where dose 2 of each job is done
    Ses = [None] * len(patients)
    for job in range (0, len(patients)):
        dose1[job] = [None] * numTimeslotsDose1
        dose2[job] = [None] * numTimeslotsDose2

    # Create ILP variables
    for job in range (0, len(patients)):
        patient = patients[job]
        # Set up an array for the a variables of this job
        # a: 1 if the patient has not gotten their first dose yet
        a = [None] * numTimeslotsDose1

        # Setting up al yj variables
        for timeslot in range (0, numTimeslotsDose1):
            yj = solver.IntVar(0, 1, f'y(job:{job}, time:{programInput.mintime[0] + timeslot})')
            dose1[job][timeslot] = yj
            currentTime = timeslot + programInput.mintime[0]
            if  currentTime < patient.r or currentTime > patient.d:
                # yj = 0 if timeslot < r_j or > d_j
                constraintD = solver.Constraint(0, 0)
                constraintD.SetCoefficient(yj, 1)        

        # Set up all the a variables for this job
        for timeslot in range (0, numTimeslotsDose1):
            at = solver.IntVar(0, 1, 'a')
            a[timeslot] = at
            currentTime = timeslot + programInput.mintime[0]
            if currentTime == patient.r:
                # Base case for a: ar = 1-y
                constraintA = solver.Constraint(1, 1)
                constraintA.SetCoefficient(at, 1)
                constraintA.SetCoefficient(dose1[job][timeslot], 1)
            elif currentTime < patient.r:
                # All other times should have at of 0
                constraintA = solver.Constraint(1, 1)
                constraintA.SetCoefficient(at, 1)

            elif currentTime > patient.d:
                # All other times should have at of 0
                constraintA = solver.Constraint(0, 0)
                constraintA.SetCoefficient(at, 1)

            else:
                # at = a(t-1) - y
                constraintA = solver.Constraint(0, 0)
                constraintA.SetCoefficient(at, 1)
                constraintA.SetCoefficient(a[timeslot -1], -1)
                constraintA.SetCoefficient(dose1[job][timeslot], 1)

        # T: Time that first dose is taken
        T = solver.IntVar(0, solver.infinity(), f'T(job:{job})')
        Ts[job] = T
        constraintT = solver.Constraint(1, 1)
        constraintT.SetCoefficient(T, 1)
        for timeslot in range (0, numTimeslotsDose1):
            constraintT.SetCoefficient(a[timeslot], -1)

        # Set up the z variables
        for timeslot in range (0, numTimeslotsDose2):
            zj = solver.IntVar(0, 1, f'z(job:{job}, time:{programInput.mintime[1] + timeslot})')
            dose2[job][timeslot] = zj
            currentTime = timeslot + programInput.mintime[1]

        # b: 1 if the patient has not gotten their second dose yet
        # Set up all the b variables for this job
        b = [None] * numTimeslotsDose2
        for timeslot in range (0, numTimeslotsDose2):
            bt = solver.IntVar(0, 1, 'a')
            b[timeslot] = bt
            currentTime = timeslot + programInput.mintime[1]
            firstPossible2nd = patient.r + programInput.gap + patient.x + 1
            if currentTime == firstPossible2nd:
                # Base case for a: ar = 1-y
                constraintB = solver.Constraint(1, 1)
                constraintB.SetCoefficient(bt, 1)
                constraintB.SetCoefficient(dose2[job][timeslot], 1)
            elif currentTime < firstPossible2nd:
                constraintA = solver.Constraint(1, 1)
                constraintA.SetCoefficient(bt, 1)
            else:
                # at = a(t-1) - y
                constraintA = solver.Constraint(0, 0)
                constraintA.SetCoefficient(bt, 1)
                constraintA.SetCoefficient(b[timeslot -1], -1)
                constraintA.SetCoefficient(dose2[job][timeslot], 1)

        # S: Time that second dose is taken
        S = solver.IntVar(0, solver.infinity(), f'T(job:{job})')
        Ses[job] = S
        constraintS = solver.Constraint(programInput.mintime[1], programInput.mintime[1])
        constraintS.SetCoefficient(S, 1)

        # S = SUM bt
        for timeslot in range (0, numTimeslotsDose2):
            constraintS.SetCoefficient(b[timeslot], -1)

        # Note especially that the +1 is required as the first plausible value comes AFTER the gap. Otherwise the interval would include the timeslot where the gap ends.
        # This forces that S \in T+[programInput.gap + patient.x + 1, programInput.gap + patient.x + patient.l - programInput.p2 + 1]
        # I.e. that S is in the second feasible interval
        constraintZ = solver.Constraint(programInput.gap + patient.x + 1, programInput.gap + patient.x + patient.l - programInput.p2 + 1)
        constraintZ.SetCoefficient(S, 1)
        constraintZ.SetCoefficient(T, -1)

    #M: total number of machines
    M = solver.IntVar(0.0, solver.infinity(), 'M')
    # [END variables]

    # [START constraints]
    # SUM yjt <= M
    for timeslot in range (programInput.mintime[0], programInput.mintime[0] + numTimeslots):
        constraint = solver.Constraint(-solver.infinity(), 0)

        # First we check if there can be any patients for dose 1 in this timeslot
        # First we check if there can be any patients for dose 2 in this timeslot
        contains1 = programInput.mintime[0] <= timeslot and timeslot <= programInput.maxtime[0]
        contains2 = programInput.mintime[1] <= timeslot and timeslot <= programInput.maxtime[1]

        if contains1: #Patients for dose 1 are in this timeslot, sum them op
            index1 = timeslot - programInput.mintime[0]
            for job in range (0, len(patients)):
                constraint.SetCoefficient(dose1[job][index1], 1)
        if contains2: #Patients for dose 2 are in this timeslot, sum them op
            index2 = timeslot - programInput.mintime[1]
            for job in range (0, len(patients)):
                constraint.SetCoefficient(dose2[job][index2], 1)
        constraint.SetCoefficient(M, -1)

    # Patient gets only 1 of each dose
    for job in range (0, len(patients)):
        # SUM yjt = 1
        constraint = solver.Constraint(1, 1)
        for timeslot in range (0, numTimeslotsDose1):
            constraint.SetCoefficient(dose1[job][timeslot], 1)

        # SUM zjt = 1
        constraint = solver.Constraint(1, 1)
        for timeslot in range (0, numTimeslotsDose2):
            constraint.SetCoefficient(dose2[job][timeslot], 1)

    # # [END constraints]

    # [START objective]
    # Minimize M (number of machines)
    objective = solver.Objective()
    objective.SetCoefficient(M, 1)
    objective.SetMinimization()
    # [END objective]

    # Solve the problem and print the solution.
    # [START print_solution]
    result = solver.Solve()
    if result == solver.INFEASIBLE:
        print("Could not find solution")
        exit(1)

    # Print the objective value of the solution.
    print('Amount of hospitals required = %d' % solver.Objective().Value())
    print()

    # Keep track of how many patients are already in the hospital at a given time
    nextMachineNumber = [1] * programInput.maxtime[1]

    # For each patient, get their T and S value and print it out
    for job in range (0, len(patients)):
        timeFirst = int(Ts[job].solution_value())
        timeSecond = int(Ses[job].solution_value())

        machineFirst = nextMachineNumber[timeFirst]
        nextMachineNumber[timeFirst] += 1
        machinSecond = nextMachineNumber[timeSecond]
        nextMachineNumber[timeSecond] += 1

        print(f"Schedule {job} at {timeFirst} (H:{machineFirst}) and {timeSecond}(H:{machinSecond})")
    # [END print_solution]


SolveILP(parseInput())
# [END program]