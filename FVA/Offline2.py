#!/usr/bin/env python3
import os
import pathlib

"""Offline algorithm of the Federal Vaccination Agency, to find the best schedule for vaccinating the population of a small country."""
from ortools.sat.python import cp_model

class Patient:
    def __init__(self, r, d, x, l, p1, p2, gap):
        self.r = r
        self.d = d
        self.x = x
        self.l = l
        self.firstPossible = [r, r + p1 + gap + x] #First possible time for first dose, first possible time for second dose (if first dose was taken at r)
        self.lastPossible = [d - p1 + 1, d + gap + x + l - p2 + 1] #Last possible time for first dose, last possible time for second dose (if first dose processing ended at d)

class PatientVariables:
    def __init__(self, patient, model, programInput):
        self.patient = patient
        self.createTimeDose1(model, programInput)
        self.createTimeDose2(model, programInput)
        self.createMachineVars(model, programInput)
    
    def createTimeDose1(self, model, programInput):
        patient = self.patient
        # The timeslot on which to schedule dose 1
        self.starttimeDose1 = model.NewIntVar(patient.firstPossible[0], patient.lastPossible[0], "starttimeDose1")
        # The timeslot on which the first dose processing time has ended
        self.endtimeDose1 = model.NewIntVar(patient.r, patient.d, "endtimeDose1")
        # The interval from the starttime timeslot to the timeslot after the endtime. The reasoning for this is as follows:
        # Because we look at timeslots, and not a continous timeline, when p1 = 1, starttime==endtime. This means that the interval will
        # be empty, and thus when checking overlap with other intervals it won't find any. This is because when checking overlapping 
        # intervals, the bounds are not seen as a match (e.g. [0,3] and [3,5] don't overlap). This quirk also allows us to add this +1,
        # as it won't be seen in the final overlap anyway.
        # Another way to see this is as viewing the numbers in the interval as "the start of a timeslot". In this case, a patient would
        # be in the hospital from the start of timeslot a, until (just before the start of) timeslot a + p1.
        self.intervalDose1 = model.NewIntervalVar(self.starttimeDose1, programInput.p1, self.endtimeDose1 + 1, "intervalDose1")

    def createTimeDose2(self, model, programInput):
        patient = self.patient
        # The timeslot on which to schedule dose 2
        self.starttimeDose2 = model.NewIntVar(patient.firstPossible[1], patient.lastPossible[1], "starttimeDose2")
        # The timeslot on which the first dose processing time has ended
        self.endtimeDose2 = model.NewIntVar(patient.firstPossible[1], patient.lastPossible[1] + programInput.p2, "endtimeDose2")
         # The interval from the starttime timeslot to the timeslot after the endtime.
        self.intervalDose2 = model.NewIntervalVar(self.starttimeDose2, programInput.p2, self.endtimeDose2 + 1, "intervalDose2")

        # The starttime for dose 2 must lay withing the feasible schedule, it must be greater than T1 + p1 + gap + x
        # @zazey klopt deze grens nu of is het <= ??
        model.Add(self.endtimeDose1 + programInput.gap + patient.x < self.starttimeDose2)
        # To force the upper bound for the starttime, we restrict the endtime. It must be less than, or equal to T1 + p1 + gap + x + l.
        model.Add(self.endtimeDose2 <= self.endtimeDose1 + programInput.gap + patient.x + patient.l)

    def createMachineVars(self, model, programInput):
        patient = self.patient
        # Create vars that will hold the number of the machine of the doses
        self.machineDose1 = model.NewIntVar(1, len(programInput.patients), "machineDose1")
        self.machineDose2 = model.NewIntVar(1, len(programInput.patients), "machineDose2")

        # Create an interval from machineNumber to machineNumber + 1. This will be used in a 2D overlap, to make sure that a 
        # machine isn't booked by two patients on the same timeslot. Note we have to use + 1 for the same reason as intervalDose1.
        self.machineDose1Interval = model.NewIntervalVar(self.machineDose1, 1, self.machineDose1 + 1, "machineDose1Interval")
        self.machineDose2Interval = model.NewIntervalVar(self.machineDose2, 1, self.machineDose2 + 1, "machineDose2Interval")

    def printSolutionLine(self, solver):
        # First create an array of all variables that need their value printed (in the correct order)
        relevantVars = [self.starttimeDose1, self.machineDose1, self.starttimeDose2, self.machineDose2]
        # Map a function over that array, that gets the value of all the variables (keeping them in the same order)
        values = [solver.Value(var) for var in relevantVars]
        # Print all the values
        print(f"{values[0]}, {values[1]}, {values[2]}, {values[3]}")


class ProgramInput:
    """All info read from input

    Attributes:
        p1            Processing time for first dose
        p2            Processing time for second dose
        gap           Patient-independent delay between first and second dose
        patients      Information of all patients
        mintime[0/1]  Lowest possible time seen for first resp. second dose of any patient
        maxtime[0/1]  Highest possible time seen for first resp. second dose of any patient
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

def parseInput(data):
    """Turns the input into a ProgramInput object"""
    p1 = int(data)
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
    # Create the model and solver
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()

    patients = programInput.patients

    # Set up all the variables for each patient
    patientVariables = [PatientVariables(patient, model, programInput) for patient in patients]

    # Array that will keep all the intervalDose1 and intervalDose2 intervals
    intervals = []
    # Array that will keep all the intervals of the corresponding dose1 and dose2 machines
    machineIntervals = []
    # Array that will keep all the corresponding numbers of the machines
    machines = []

    for patient in patientVariables:
        intervals.append(patient.intervalDose1)
        intervals.append(patient.intervalDose2)
        machineIntervals.append(patient.machineDose1Interval)
        machineIntervals.append(patient.machineDose2Interval)
        machines.append(patient.machineDose1)
        machines.append(patient.machineDose2)
    
    # We do a 2D overlap that works in the following way.
    # The overlap will check if there is an overlap between the time intervals and the machinenumber intervals.
    # There is only an overlap if the machine number is the same and at least some part of the time interval overlaps with another.
    # This would correspond with a hospital being booked for 2 patients at the same time. As we do not want it, we tell the model
    # to not allow such overlappings.
    #
    #  4                  OVERLAP
    #  3                     V
    #  2            |-----|=====|-----|
    #  1      |-----------|-----------|
    # m\t     |  1  |  2  |  3  |  4  |  5  |  6  |  7  |  8
    # This example shows p=2. We notice an overlap occurs when m=2 and t1=[2,4] and t2=[3,5]. Note: that the indices here indicate the start of a
    # timeslot, and as the endtime spans a full timeslot, it will be set to the beginning of the next timeslot, but it won't overlap with that.
    model.AddNoOverlap2D(intervals, machineIntervals)

    # Create a variable that holds the highest machine number that was found, we will minimise this later
    highestMachineNumber = model.NewIntVar(1, len(patients), "M")
    model.AddMaxEquality(highestMachineNumber, machines)

    # Minimise the highest machine number. The reason that we can use this maximum, is that every machine is used only over a processing time.
    # (This is enforced by the overlap constraint). This means that any maximum number that we see, must be the number of concurrent machine that are
    # required at a single point in time. This is true because we minimise M, thus the solver will try to minimise the machine numbers. The only way a
    # machine cannot be lower is if that time was already taken up by another job.
    model.Minimize(highestMachineNumber)

    # Solve the model and print the solution
    status = solver.Solve(model)
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for patient in patientVariables:
            patient.printSolutionLine(solver)
        print(f"{solver.Value(highestMachineNumber)}")
        return f"{solver.Value(highestMachineNumber)}"
    else:
        print("Could not find a solution")
        return "-1"

    
    

def runAllTests():
    dirhere = str(pathlib.Path(__file__).parent.resolve())
    # Folder Path
    path =  dirhere + "\\offlineproblems\\"

    # Change the directory
    os.chdir(path)

    # Read text File

   
    list = []
    filenames = []
    def read_text_file(path,file):
        with open(f"{path}{file}", 'r') as f:
            inputlist = f.read().splitlines()
            
                  

            # print("LIST STARTS HERE-=-------------------------------------------------------------------")
            # for x in range(len(inputlist)):
            #     print (inputlist[x])

            # print("LIST ENDS HERE-=-------------------------------------------------------------------")

            p1 = int(inputlist[0])
            p2 = int(inputlist[1])
            gap = int(inputlist[2])
            numPatients = int(inputlist[3])
            patients = []
            maxtime = [0] * 2
            mintime = [float('inf')] * 2 # Initiate minimum times as infinity

            for i in range(0, numPatients):
                patient = parsePatient(inputlist[4 + i], p1, p2, gap)
                patients.append(patient)
                mintime[0] = min(mintime[0], patient.firstPossible[0])
                maxtime[0] = max(maxtime[0], patient.lastPossible[0])
                mintime[1] = min(mintime[1], patient.firstPossible[1])
                maxtime[1] = max(maxtime[1], patient.lastPossible[1])
                
            if numPatients == 0:
                print(0)
                #exit()
                
            print ("SOLUTION BELOW-------------------------------------------------------------------------")
            if numPatients < 120:
                solution = SolveILP(ProgramInput(p1, p2, gap, patients, mintime, maxtime))
                print(solution)
                
                list.append((file,solution))    
            

    

    # iterate through all file
    for file in os.listdir():
        # Check whether file is in text format or not
        if file.endswith(".txt"):
            
            
            # call read text file function
            read_text_file(path,file)
    
    f = open("output.txt", "w")
    for i in list:
        print(i[0]+ ' ' + i[1])
        f.write(i[0]+ " " + i[1] + "\n")

    #print(list, ' ')

            

if __name__ == "__main__":
    data = input()

    if data == "":
        runAllTests()
    else:
        SolveILP(parseInput(data))