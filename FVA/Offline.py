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
    maxtime = [0, 0]
    mintime = [9999999, 9999999] #TODO: change to infinity
    for i in range(0, numPatients):
        patient = parsePatient(input())
        patients.append(patient)
        mintime[0] = min(mintime[0], patient.r)
        maxtime[0] = max(maxtime[0], patient.d)
        #mintime[1] = min(mintime[1], patient.r + p1 + gap + patient.x)
        #maxtime[1] = max(maxtime[1], patient.d + gap + patient.x + patient.l)
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

    # Initialise array that holds variables of dose1
    dose1 = [None] * len(patients)
    for job in range (0, len(patients)):
        dose1[job] = [None] * numTimeslotsDose1

    # Create ILP variables
    for job in range (0, len(patients)):
        for timeslot in range (0, numTimeslotsDose1):
            yj = solver.IntVar(0, 1, f'y(job:{job}, time:{programInput.mintime[0] + timeslot})')
            dose1[job][timeslot] = yj
            #yj = 0 if timeslot < r_j or > d_j
            if patients[job].r >= (timeslot + programInput.mintime[0]) or patients[job].d <= (timeslot + programInput.mintime[0]):
                constraintD = solver.Constraint(0, 0)
                constraintD.SetCoefficient(yj, 1)

    M = solver.IntVar(0.0, solver.infinity(), 'M')
    #y = solver.IntVar(0.0, solver.infinity(), 'y')
    #z = solver.IntVar(0.0, solver.infinity(), 'z')
    # [END variables]

    # [START constraints]
    # SUM yjt <= M
    for timeslot in range (0, numTimeslotsDose1):
        constraint = solver.Constraint(-solver.infinity(), 0)
        for job in range (0, len(patients)):
            constraint.SetCoefficient(dose1[job][timeslot], 1)
        constraint.SetCoefficient(M, -1)

    # SUM yj == 1
    for job in range (0, len(patients)):
        constraint = solver.Constraint(1, 1)
        for timeslot in range (0, numTimeslotsDose1):
            constraint.SetCoefficient(dose1[job][timeslot], 1)

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
        for timeslot in range (0, numTimeslotsDose1):
            variable = dose1[job][timeslot]
            if variable.solution_value() == 1:
                print('%s = %d' % (variable.name(), variable.solution_value()))
    # [END print_solution]


SolveILP(parseInput())
# [END program]