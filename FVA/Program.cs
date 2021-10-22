using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace FVA
{
    class Program
    {
        static bool
            CONSOLEINPUT = false,
            RUNRANDOM = false,
            GENERATERANDOM = true,
            FILEINPUT = false;
                    
        static void Main(string[] args)
        {
            if (CONSOLEINPUT)
            {
                if (!int.TryParse(Console.ReadLine(), out Utils.PTIMEFIRST)
                    || !int.TryParse(Console.ReadLine(), out Utils.PTIMESECOND)
                    || !int.TryParse(Console.ReadLine(), out Utils.GAP)
                    )
                {
                    throw new ArgumentException("Input was not in the correct format.");
                }

                Utils.LONGESTSHOT = Math.Max(Utils.PTIMEFIRST, Utils.PTIMESECOND);

                string line = Console.ReadLine();

                Utils.OFFLINE = int.TryParse(line, out int patientCnt);

                if (Utils.OFFLINE)
                {
                    Utils.DebugPrint($"Solving the offline problem with {patientCnt} patients.");
                    Patient[] patients = new Patient[patientCnt];

                    for (int i = 0; i < patientCnt; ++i)
                        patients[i] = new Patient(i, Console.ReadLine());

                    new Offline(patients);

                }
                else
                {
                    Utils.DebugPrint("Solving the online problem.");

                    if (line == "x")
                        Utils.Print("0");
                    else
                        new Online(new Patient(0, line));
                }
            }
            else if (RUNRANDOM)
            {
                int patients = 8;
                PatientConfiguration pc = new PatientConfiguration(0, 15, 0, 20, 0, 5, 0, 5);
                RandomConfiguration config = new RandomConfiguration(3, 3, 0, patients, pc);

                Online online,
                        worst;
                int maxhospitalsseen = int.MinValue;
                for (int i = 0; i < 1e7; ++i) 
                {
                    config = new RandomConfiguration(3, 3, 0, patients, pc);
                    online = new Online(config);


                    if (maxhospitalsseen < online.HospitalCNT)
                    {
                        worst = online;
                        maxhospitalsseen = online.HospitalCNT;
                        if (maxhospitalsseen == patients)
                            break;
                    }
                }

                Utils.DebugPrint($"worst found: {maxhospitalsseen}");
            }
            else if (GENERATERANDOM)
            {
                int generateX = 2;

                int shot1 = 3,
                    shot2 = 3,
                    gap = 0,
                    patients = 8;

                PatientConfiguration pc = new PatientConfiguration(0, 15, 0, 20, 0, 5, 0, 5);
                RandomConfiguration config;
                StringBuilder testcasestringOffline, testcasestringOnline;

                for (int i = 0; i < generateX; ++i)
                {
                    // patients = Utils.PRNG.Next(5, 8); // set integers can be randomised like so

                    config = new RandomConfiguration(shot1, shot2, gap, patients, pc);

                    testcasestringOffline = new StringBuilder();
                    testcasestringOnline = new StringBuilder();
                    testcasestringOffline.Append($"{shot1}\n{shot2}\n{gap}\n{patients}\n");
                    testcasestringOnline.Append($"{shot1}\n{shot2}\n{gap}\n");

                    foreach (Patient p in config.Patients)
                    {
                        string ps = p.ToString() + "\n";
                        testcasestringOffline.Append(ps);
                        testcasestringOnline.Append(ps);
                    }

                    testcasestringOnline.Append("x");

                    FileHandler.WriteTestCase(false, $"{patients}-{i}", testcasestringOffline.ToString());
                    FileHandler.WriteTestCase(true, $"{patients}-{i}", testcasestringOnline.ToString());
                }

            }
            else if (FILEINPUT)
            {
                var results = new List<TestResult>();
                int topX = 10;

                Online online;
                Configuration config;

                foreach (string offlineresultstring in FileHandler.ReadLines(FileHandler.INPUTLOCATION).ToList())
                {
                    results.Add(new TestResult(offlineresultstring));

                    string[] lines = FileHandler.ReadLines(results.Last().FileName).ToArray();

                    if (!int.TryParse(lines[0], out int shot1)
                        || !int.TryParse(lines[1], out int shot2)
                        || !int.TryParse(lines[2], out int gap)
                        )
                        throw new ArgumentException();
                    else
                        config = new Configuration(shot1, shot2, gap);

                    for (int i = 3; i < lines.Length - 1; ++i)
                        config.AddPatient(new Patient(i - 2, lines[i]));

                    online = new Online(config);

                    results.Last().SetOnlineResult(online);
                }

                results.Sort();

                var sb = new StringBuilder();
                for (int i = 0; i < Math.Min(topX, results.Count); ++i)
                    sb.Append(results[i].ToString() + "\n");

                FileHandler.WriteResults(sb.ToString());
            }
        }
    }
}
