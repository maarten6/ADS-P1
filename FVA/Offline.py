#!/usr/bin/env python3

"""Offline algorithm of the Federal Vaccination Agency, to find the best schedule for vaccinating the population of a small country."""
from ortools.linear_solver import pywraplp

class Patient:
    def __init__(self, r, d, x, l, p1, p2, gap):
        self.r = r
        self.d = d
        self.x = x
        self.l = l
        self.firstPossible = [r, r + p1 + gap + x] #First possible time for first dose, first possible time for second dose (if first dose was taken at r)
        self.lastPossible = [d - p1 + 1, d + gap + x + l - p2 + 1] #Last possible time for first dose, last possible time for second dose (if first dose processing ended at d)
# S <= d - p1 + g + x + l + p1 - p2
class ProgramInput:
    """All info read from input

    Attributes:
        p1            Processing time for first dose
        p2            Processing time for second dose
        gap           Patient-independent delay between first and second dose
        patients      Information of all patients
        mintime[0,1]  Lowest possible time seen for first resp. second dose of any patient
        maxtime[0,1]  Highest possible time seen for first resp. second dose of any patient
    """
    def __init__(self, p1, p2, gap, patients, mintime, maxtime):
        self.p1 = p1
        self.p2 = p2
        self.gap = gap
        self.patients = patients
        self.maxtime = maxtime
        self.mintime = mintime

def parsePatient(line, p1, p2, gap):
    """Turns a comma seperated line into a patient object given the input-wide p1, p2 and gap."""
    patientValues = [int(x.strip()) for x in line.split(',')]
    return Patient(patientValues[0], patientValues[1], patientValues[2], patientValues[3], p1, p2, gap)

def parseInput():
    """Turns the input into a ProgramInput object"""
    p1 = int(input())
    p2 = int(input())
    gap = int(input())
    numPatients = int(input())
    patients = []
    maxtime = [0] * 2
    mintime = [float('inf')] * 2 # Initiate minimum times as infinity
    for i in range(0, numPatients):
        patient = parsePatient(input(), p1, p2, gap)
        patients.append(patient)
        mintime[0] = min(mintime[0], patient.firstPossible[0])
        maxtime[0] = max(maxtime[0], patient.lastPossible[0])
        mintime[1] = min(mintime[1], patient.firstPossible[1])
        maxtime[1] = max(maxtime[1], patient.lastPossible[1])
    if numPatients == 0:
        print(0)
        exit()
    return ProgramInput(p1, p2, gap, patients, mintime, maxtime)

def SolveILP(programInput):
    # [START solver]
    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')
    patients = programInput.patients
    numTimeslots = programInput.maxtime[1] - programInput.mintime[0] + 1
    numTimeslotsDose1 = programInput.maxtime[0] - programInput.mintime[0] + 1
    numTimeslotsDose2 = programInput.maxtime[1] - programInput.mintime[1] + 1

    # [END solver]

    # [START variables] 
    # y_jt: 1, if the first dose of job j is taken on timeslot t
    #        0, otherwise
    # a_jt: 1, if the first dose of job j has not been taken before t
    #        0, otherwise
    # z_jt: 1, if the second dose of job j is taken on timeslot t
    #        0, otherwise
    # b_jt: 1, if the second dose of job j has not been taken before t
    #        0, otherwise
    # T_j  : Timeslot where dose 1 is taken of job j
    # S_j  : Timeslot where dose 1 is taken of job j
    # M    : Maximal number of concurrent machines over all timeslots

    # Initialise arrays that holds variables of dose 1 and dose 2
    dose1 = [None] * len(patients) #Holds all y variables
    dose2 = [None] * len(patients) #Holds all z variables
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

        # Setting up all yj variables
        for timeslot in range (0, numTimeslotsDose1):
            yj = solver.IntVar(0, 1, f'y(job:{job}, time:{programInput.mintime[0] + timeslot})')
            dose1[job][timeslot] = yj
            currentTime = timeslot + programInput.mintime[0]
            # Current time is either before or after shots can be taken: set yj to always 0
            if currentTime < patient.firstPossible[0] or currentTime > patient.lastPossible[0]:
                constraintD = solver.Constraint(0, 0)
                constraintD.SetCoefficient(yj, 1)        
            

        # T: Time that first dose is taken
        # T = SUM yj*t   =>   T - SUM yj*t = 0
        T = solver.IntVar(patient.firstPossible[0], patient.lastPossible[0], f'T(job:{job})')
        Ts[job] = T
        constraintTMinSum = solver.Constraint(0, 0)
        constraintTMinSum.SetCoefficient(T, 1)
        for timeslot in range (0, numTimeslotsDose1):
            currentTime = timeslot + programInput.mintime[0]
            constraintTMinSum.SetCoefficient(dose1[job][timeslot], -currentTime)

        # Set up the z variables
        for timeslot in range (0, numTimeslotsDose2):
            currentTime = timeslot + programInput.mintime[1]
            zj = solver.IntVar(0, 1, f'z(job:{job}, time:{currentTime})')
            dose2[job][timeslot] = zj
            
            # Current time is either before or after shots can be taken: set zj to always 0
            if currentTime < patient.firstPossible[1] or currentTime > patient.lastPossible[1]:
                constraintZ = solver.Constraint(0, 0)
                constraintZ.SetCoefficient(zj, 1)

        # S: Time that second dose is taken
        # S = SUM zj*t   =>   S - SUM zj*t = 0
        S = solver.IntVar(programInput.mintime[1], programInput.maxtime[1], f'S(job:{job})')
        Ses[job] = S
        constraintSMinSum = solver.Constraint(0, 0)
        constraintSMinSum.SetCoefficient(S, 1)
        for timeslot in range (0, numTimeslotsDose2):
            currentTime = timeslot + programInput.mintime[1]
            constraintSMinSum.SetCoefficient(dose2[job][timeslot], -currentTime)

        # S ∈ [T + p1 + gap + x, T + p1 + gap + x + l - p2]
        print([programInput.p1 + programInput.gap + patient.x, programInput.p1 + programInput.gap + patient.x + patient.l - programInput.p2])
        constraintFeasibleScheduleS = solver.Constraint(programInput.p1 + programInput.gap + patient.x, programInput.p1 + programInput.gap + patient.x + patient.l - programInput.p2)
        constraintFeasibleScheduleS.SetCoefficient(S, 1)
        constraintFeasibleScheduleS.SetCoefficient(T, -1)

    #M: total number of machines
    M = solver.IntVar(0, len(patients), 'M')
    # [END variables]

    # [START constraints]
    # FORALL t: SUM yjt + SUM zjt <= M
    # FORALL t: SUM yjt + SUM zjt - M <= 0
    for timeslot in range (programInput.mintime[0], programInput.maxtime[1] + 1):
        constraint = solver.Constraint(-len(patients), 0)

        # First we check if there can be any patients for dose 1 in this timeslot
        # First we check if there can be any patients for dose 2 in this timeslot
        contains1 = timeslot <= programInput.maxtime[0]
        contains2 = programInput.mintime[1] <= timeslot

        if contains1: #Patients for dose 1 are in this timeslot, sum them op
            index1 = timeslot - programInput.mintime[0] #Transform timeslot into index for dose1 array, t
            for index in range(max (index1-programInput.p1 + 1, 0), index1 + 1): # In this timeslot, patients that got a dose in a previous timeslot, may still be in the hospital
                for job in range (0, len(patients)):
                    constraint.SetCoefficient(dose1[job][index], 1)
        if contains2: #Patients for dose 2 are in this timeslot, sum them op
            index2 = timeslot - programInput.mintime[1]
            for index in range(max (index2-programInput.p2 + 1, 0), index2 + 1):
                for job in range (0, len(patients)):
                    constraint.SetCoefficient(dose2[job][index], 1)
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

    # Keep track of in what hospitals a patient is present
    busyHospitals = [None] * (programInput.maxtime[1]+1)
    for time in range(0, programInput.maxtime[1]):
        busyHospitals[time] = []
    allHospitals = range(0, len(patients))

    # For each patient, get their T and S value and print it out
    for job in range (0, len(patients)):
        timeFirstDose = int(Ts[job].solution_value())
        timeSecondDose = int(Ses[job].solution_value())

        machineFirstDose = -1
        machineSecondDose = -1

        print(f"Schedule job {job} at timeslot {timeFirstDose} (machine number:{machineFirstDose}) and {timeSecondDose}(machine number:{machineSecondDose})")
    # [END print_solution]


SolveILP(parseInput())
# [END program]