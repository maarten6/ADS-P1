# Algorithms for Decision Support
This is the supplementary material that goes along the submitted paper. 

# Project Members
- Maarten Al Sadawi, 6061559.
- Jaan Van Gils, 6200443.
- Izak Haak, 6456677.
- Martijn Jansen, 6513328.

# Structure - FVA
- This folder contains the source code of the online algorithm.
- This folder also contains the "TestInstances" folder which contains the folders "Offline" and "Online" and they contain the test instances provided to us and used in the paper. The "TestInstances" folder also contains the "Generated" folder that also has "Offline" and "Online". But these have explicit readmes (and are filled when a specific mode is run in the code).
- Finally, it contains the "OfflineAlgorithm" folder that contains the source code of both ILP solvers, as well as additional extra scripts as explained in the readme within that folder.

# Overview of the online algorithm files
This project was initially set up to run both the online and offline version of the problem. However during the project we decided to write the offline problem in Python, so this was no longer needed.
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