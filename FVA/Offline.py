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
"""Small example to illustrate solving a MIP problem."""
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
        mintime[0] = min(mintime[0], patient.r)
        maxtime[0] = max(maxtime[0], patient.d)
        mintime[1] = min(mintime[1], patient.r + p1 + gap + patient.x)
        maxtime[1] = max(maxtime[1], patient.d + gap + patient.x + patient.l)
    return ProgramInput(p1, p2, gap, patients, mintime, maxtime)

def SolveILP(programInput):
    """Integer  programming sample."""
    # [START solver]
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')
    patients = programInput.patients
    numTimeslots = programInput.maxtime[1] - programInput.mintime[0] + 1
    numTimeslotsDose1 = programInput.maxtime[0] - programInput.mintime[0] +1
    numTimeslotsDose2 = programInput.maxtime[1] - programInput.mintime[1] +1

    # [END solver]

    # [START variables] 
    # y_jtm: 1, if the first dose of job j is taken on timeslot t on machine m
    #        0, otherwise
    # z_jtm: 1, if the second dose of job j is taken on timeslot t on machine m
    #        0, otherwise
    # T_j  : Timeslot where dose 1 is taken of job j
    # m_t  : Amount of machines used on timeslot t
    # M    : Maximal number of concurrent machines over all timeslots

    # Initialise arrays that holds variables of dose 1 and dose 2
    dose1 = [None] * len(patients)
    dose2 = [None] * len(patients)
    for job in range (0, len(patients)):
        dose1[job] = [None] * numTimeslotsDose1
        dose2[job] = [None] * numTimeslotsDose2

    # Create ILP variables
    for job in range (0, len(patients)):
        patient = patients[job]
        for timeslot in range (0, numTimeslotsDose1):
            yj = solver.IntVar(0, 1, f'y(job:{job}, time:{programInput.mintime[0] + timeslot})')
            dose1[job][timeslot] = yj
            #yj = 0 if timeslot < r_j or > d_j
            currentTime = timeslot + programInput.mintime[0]
            if  currentTime < patient.r or currentTime > patient.d:
                constraintD = solver.Constraint(0, 0)
                constraintD.SetCoefficient(yj, 1)
        for timeslot in range (0, numTimeslotsDose2):
            zj = solver.IntVar(0, 1, f'z(job:{job}, time:{programInput.mintime[1] + timeslot})')
            dose2[job][timeslot] = zj
            currentTime = timeslot + programInput.mintime[1]
            if  currentTime < patient.r + programInput.p1 + programInput.gap + patient.x -1 or currentTime > patient.d + programInput.p1 + programInput.gap + patient.x + patient.l -2:
                constraintD = solver.Constraint(0, 0)
                constraintD.SetCoefficient(zj, 1)

    M = solver.IntVar(0.0, solver.infinity(), 'M')
    #y = solver.IntVar(0.0, solver.infinity(), 'y')
    #z = solver.IntVar(0.0, solver.infinity(), 'z')
    # [END variables]

    # [START constraints]
    # SUM yjt <= M
    for timeslot in range (programInput.mintime[0], programInput.mintime[0] + numTimeslots):
        constraint = solver.Constraint(-solver.infinity(), 0)
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

    # SUM yj = 1 and SUM zj = 1
    for job in range (0, len(patients)):
        constraint = solver.Constraint(1, 1)
        for timeslot in range (0, numTimeslotsDose1):
            constraint.SetCoefficient(dose1[job][timeslot], 1)

        constraint = solver.Constraint(1, 1)
        for timeslot in range (0, numTimeslotsDose2):
            constraint.SetCoefficient(dose2[job][timeslot], 1)
        

    # # 3*x - 5*y + 7*z <= 45
    # constraint1 = solver.Constraint(-solver.infinity(), 45)
    # constraint1.SetCoefficient(x, 3)
    # constraint1.SetCoefficient(y, -5)
    # constraint1.SetCoefficient(z, 7)
    # # [END constraints]

    # [START objective]
    # Minimize M
    objective = solver.Objective()
    objective.SetCoefficient(M, 1)
    objective.SetMinimization()
    # [END objective]

    # Solve the problem and print the solution.
    # [START print_solution]
    solver.Solve()
    # Print the objective value of the solution.
    print('Amount of hospitals required = %d' % solver.Objective().Value())
    print()
    # Print the value of each variable in the solution.
    for job in range (0, len(patients)):
        timeFirst = -1
        timeSecond = -1
        for timeslot in range (0, numTimeslotsDose1):
            variable = dose1[job][timeslot]
            if variable.solution_value() == 1:
                if timeFirst != -1:
                    print(f"Dose 1 scheduled multiple times for {job}")
                else:
                    timeFirst = programInput.mintime[0] + timeslot
        for timeslot in range (0, numTimeslotsDose2):
            variable = dose2[job][timeslot]
            if variable.solution_value() == 1:
                if timeSecond != -1:
                    print(f"Dose 1 scheduled multiple times for {job}")
                else:
                    timeSecond = programInput.mintime[1] +timeslot
        print(f"Schedule {job} at {timeFirst} and {timeSecond}")
    # [END print_solution]


SolveILP(parseInput())
# [END program]