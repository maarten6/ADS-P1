#!/usr/bin/env python3

"""Offline algorithm of the Federal Vaccination Agency, to find the best schedule for vaccinating the population of a small country."""
from ortools.linear_solver import pywraplp

class Patient:
    def __init__(self, r, d, x, l, p1, p2, gap):
        self.r = r
        self.d = d
        self.x = x
        self.l = l
        self.firstPossible = [r, r + p1 + gap + x] #First possible time for first dose, first possible time for second dose(if first dose was taken at r)
        self.lastPossible = [d - p1 + 1, d + gap + x + l + 1] #Last possible time for first dose, last possible time for second dose(if first dose processing ended at d)

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

def getFirstUncommon(checkList, referenceList):
    """Returns the first item that is in referenceList that is not in checkList"""
    for i in range(0, len(referenceList)):
        if i >= len(checkList) or checkList[i] is not referenceList[i]:
            return referenceList[i]

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

        # Setting up all yj variables
        for timeslot in range (0, numTimeslotsDose1):
            yj = solver.IntVar(0, 1, f'y(job:{job}, time:{programInput.mintime[0] + timeslot})')
            dose1[job][timeslot] = yj
            currentTime = timeslot + programInput.mintime[0]
            # Current time is either before or after shots can be taken: set yj to always 0
            if currentTime < patient.firstPossible[0] or currentTime > patient.lastPossible[0]:
                constraintD = solver.Constraint(0, 0)
                constraintD.SetCoefficient(yj, 1)        

        # Set up all the a variables for this job
        for timeslot in range (0, numTimeslotsDose1):
            at = solver.IntVar(0, 1, 'a')
            a[timeslot] = at
            currentTime = timeslot + programInput.mintime[0]

            # Base case for a: ar = 1-y
            if currentTime == patient.firstPossible[0]:
                constraintA = solver.Constraint(1, 1)
                constraintA.SetCoefficient(at, 1)
                constraintA.SetCoefficient(dose1[job][timeslot], 1)

            # All times before the first dose can be taken should have at=1
            elif currentTime < patient.firstPossible[0]:
                constraintA = solver.Constraint(1, 1)
                constraintA.SetCoefficient(at, 1)

            # All times after first dose can be taken should have at=0
            elif currentTime > patient.lastPossible[0]:
                constraintA = solver.Constraint(0, 0)
                constraintA.SetCoefficient(at, 1)

            # All times in the first dose interval should have at = a(t-1) - y
            # Thus at - a(t-1) + y = 0
            else:
                constraintA = solver.Constraint(0, 0)
                constraintA.SetCoefficient(at, 1)
                constraintA.SetCoefficient(a[timeslot -1], -1)
                constraintA.SetCoefficient(dose1[job][timeslot], 1)

        # T: Time that first dose is taken. This time is 1 + SUM a
        # T = 1 + SUM a   =>   T - SUM a = 1
        T = solver.IntVar(0, programInput.maxtime[0], f'T(job:{job})')
        Ts[job] = T
        constraintT = solver.Constraint(programInput.mintime[0], programInput.mintime[0])
        constraintT.SetCoefficient(T, 1)
        for timeslot in range (0, numTimeslotsDose1):
            constraintT.SetCoefficient(a[timeslot], -1)

        # Set up the z variables
        for timeslot in range (0, numTimeslotsDose2):
            currentTime = timeslot + programInput.mintime[1]
            zj = solver.IntVar(0, 1, f'z(job:{job}, time:{currentTime})')
            dose2[job][timeslot] = zj
            
            # Current time is either before or after shots can be taken: set zj to always 0
            if currentTime < patient.firstPossible[1] or currentTime > patient.lastPossible[1]:
                constraintZ = solver.Constraint(0, 0)
                constraintZ.SetCoefficient(zj, 1)   

        # b: 1 if the patient has not gotten their second dose yet
        # Set up all the b variables for this job
        b = [None] * numTimeslotsDose2
        for timeslot in range (0, numTimeslotsDose2):
            bt = solver.IntVar(0, 1, 'b')
            b[timeslot] = bt
            currentTime = timeslot + programInput.mintime[1]
            if currentTime == patient.firstPossible[1]:
                # Base case for b: b_(firstPossible2ndDoseTime) = 1-y   =>   bt + y = 1
                constraintB = solver.Constraint(1, 1)
                constraintB.SetCoefficient(bt, 1)
                constraintB.SetCoefficient(dose2[job][timeslot], 1)

            # All times before the second dose can be taken should have bt=1
            elif currentTime < patient.firstPossible[1]:
                constraintB = solver.Constraint(1, 1)
                constraintB.SetCoefficient(bt, 1)

            # All times after second dose can be taken should have bt=0
            elif currentTime > patient.lastPossible[1]:
                constraintB = solver.Constraint(0, 0)
                constraintB.SetCoefficient(bt, 1)

            # All times in the second dose interval should have bt = b(t-1) - z
            # Thus bt - b(t-1) + z = 0
            else:
                constraintB = solver.Constraint(0, 0)
                constraintB.SetCoefficient(bt, 1)
                constraintB.SetCoefficient(b[timeslot -1], -1)
                constraintB.SetCoefficient(dose2[job][timeslot], 1)

        # S: Time that second dose is taken
        S = solver.IntVar(0, solver.infinity(), f'T(job:{job})')
        Ses[job] = S

        # S = FIRST TIME FOR SECOND DOSE + SUM bt
        constraintS = solver.Constraint(programInput.mintime[1], programInput.mintime[1])
        constraintS.SetCoefficient(S, 1)
        for timeslot in range (0, numTimeslotsDose2):
            constraintS.SetCoefficient(b[timeslot], -1)

        # S \in [T + p1 + gap + x, T + p1 + gap + x + l - p2 + 1]
        print([programInput.mintime[1] + programInput.p1 + programInput.gap + patient.x, programInput.mintime[1] + programInput.p1 + programInput.gap + patient.x + patient.l - programInput.p2])
        constraintZ = solver.Constraint(programInput.p1 + programInput.gap + patient.x, programInput.p1 + programInput.gap + patient.x + patient.l - programInput.p2)
        constraintZ.SetCoefficient(S, 1)
        constraintZ.SetCoefficient(T, -1)

    #M: total number of machines
    M = solver.IntVar(0, programInput.patients, 'M')
    # [END variables]

    # [START constraints]
    # SUM yjt + SUM zjt <= M
    for timeslot in range (programInput.mintime[0], programInput.mintime[0] + numTimeslots):
        constraint = solver.Constraint(-solver.infinity(), 0)

        # First we check if there can be any patients for dose 1 in this timeslot
        # First we check if there can be any patients for dose 2 in this timeslot
        contains1 = programInput.mintime[0] <= timeslot and timeslot <= programInput.maxtime[0]
        contains2 = programInput.mintime[1] <= timeslot and timeslot <= programInput.maxtime[1]

        if contains1: #Patients for dose 1 are in this timeslot, sum them op
            index1 = timeslot - programInput.mintime[0]
            for index in range(max (index1-programInput.p1 + 1, 0), index1 + 1):
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
        timeFirst = int(Ts[job].solution_value())
        timeSecond = int(Ses[job].solution_value())

        machineListFirst = busyHospitals[timeFirst]
        machineFirst = getFirstUncommon(machineListFirst, allHospitals)

        for time in range(timeFirst, timeFirst + programInput.p1):
            busyHospitals[time].append(machineFirst)
        

        machineListSecond = busyHospitals[timeSecond]
        machineSecond = getFirstUncommon(machineListSecond, allHospitals)
        print(machineListSecond)

        for time in range(timeSecond, timeSecond + programInput.p2):
            busyHospitals[time].append(machineSecond)

        print(f"Schedule {job} at {timeFirst} (H:{machineFirst}) and {timeSecond}(H:{machineSecond})")
    # [END print_solution]


SolveILP(parseInput())
# [END program]