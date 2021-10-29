# Algorithms for Decision Support
This is the supplementary material that goes along the submitted paper. 

# Project Members
- Maarten Al Sadawi, 6061559.
- Jaan Van Gils, 6200443.
- Izak Haak, 6456677.
- Martijn Jansen, 6513328.

# OfflineAlgorithm
This folder contains the source code of the offline algorithm.
## Generator.py
Can be used to generate a random input for the offline programs. The types are as follows.
- Any: Generates a random sequence of intervals that may or may not overlap
- Consecutive: Generates a random sequence of intervals that can be placed on 1 machine
- Maximum amount of machines: Will generate a random sequence of intervals that can never use more than the specified amount of machines
- Less flexible feasible intervals: Allows for creating an instance that has interval lengths that are p1 * c and p2 * c for a given c
## OfflineChecker.py
Will wait for input that can be fed to an offline algorithm. Will than check if the schedule that OfflineCPSat.py outputs is feasible (all planned times are within bounds specified in input) and whether hospitals are not used by multiple patients in the same timeslot. Will also output the amount of machines that was used according to the offline algorithm.
Moreover it will output how long the algorithm and the checking took.
## OfflineCPSat.py
Will run the input through a CPSAT solver, using constraints as described in the paper.
## OfflineLS.py
Will run the input through a linear solver, using constraints as described in the paper.
## PerformCompare.py
Will run all testcases in the "Testcases" directory, and output whether they finished with an optimal result within the timeout set in the PerformCompare.py script. Moreover will output how long the algorithms took to find this result. After everything is ran, a file "OfflineTable.txt" is created that has LaTeX code to generate a table of the results.

# OnlineAlgorithm
This folder contains the source code of the online algorithm. This project was initially set up to run both the online and offline version of the problem. However during the project we decided to write the offline problem in Python, so this was no longer needed.
## Program.cs
This is the entry point of the program. There are a few booleans that can be set to run the program in various modes. The default mode is the one that was needed for the assignment. All other modes were created for testing purposes.
## Online.cs
In this file the online solver algorithm lives. It has all the scheduling functionallity internally. There are also a few helper classes that are defined in this file: Hospital and TimeSlot. These are used in the Online solver class.
## Patient.cs
Contains the implementation of the Patient class. This class contains all relevant information for a patient.
## Utils.cs
Contains several global variables and printing functions that can be used by all other files.
## Configuration.cs
Contains implementation to create testing configurations. This file is not used in the main functionality of the program, only in the alternative modes to run the program.
## FileHandler.cs
Generic class to handle interaction with the file system. This file is not used in the main functionality of the program, only in the alternative modes to run the program.

# TestInstances
- This folder contains two folders, namely "Offline" and "Online" and they contain the test instances provided to us and used in the paper. The "TestInstances" folder also contains the "Generated" folder that also has "Offline" and "Online". But these have explicit readmes (and are filled when a specific mode is run in the code).
