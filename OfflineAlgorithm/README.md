An overview of the files and their functions.

# Generator.py

Can be used to generate a random input for the offline programs. The types are as follows.
- Any: Generates a random sequence of intervals that may or may not overlap
- Consecutive: Generates a random sequence of intervals that can be placed on 1 machine
- Maximum amount of machines: Will generate a random sequence of intervals that can never use more than the specified amount of machines
- Less flexible feasible intervals: Allows for creating an instance that has interval lengths that are p1*c and p2*c for a given c

# OfflineChecker.py

Will wait for input that can be fed to an offline algorithm. Will than check if the schedule that OfflineCPSat.py outputs is feasible (all planned times are within bounds specified in input) and whether hospitals are not used by multiple patients in the same timeslot. Will also output the amount of machines that was used according to the offline algorithm.
Moreover it will output how long the algorithm and the checking took.

# OfflineCPSat.py

Will run the input through a CPSAT solver, using constraints as described in the paper.

# OfflineLS.py

Will run the input through a linear solver, using constraints as described in the paper.

# PerformCompare.py

Will run all testcases in the "Testcases" directory, and output whether they finished with an optimal result within the timeout set in the PerformCompare.py script. Moreover will output how long the algorithms took to find this result. After everything is ran, a file "OfflineTable.txt" is created that has LaTeX code to generate a table of the results.