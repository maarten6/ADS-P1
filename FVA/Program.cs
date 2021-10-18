using System;

namespace FVA
{
    class Program
    {
        static bool READINPUT = true;
        static void Main(string[] args)
        {
            if (READINPUT)
            {
                if (!int.TryParse(Console.ReadLine(), out Utils.PTIMEFIRST)
                    || !int.TryParse(Console.ReadLine(), out Utils.PTIMESECOND)
                    || !int.TryParse(Console.ReadLine(), out Utils.GAP)
                    )
                {
                    throw new ArgumentException("Input was not in the correct format.");
                }

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
            else
            {
                int patients = 8;
                PatientConfiguration pc = new PatientConfiguration(0, 15, 0, 20, 0, 5, 0, 5);
                TestConfiguration config = new TestConfiguration(3, 3, 0, patients, pc);

                Online online,
                        worst;
                int maxhospitalsseen = int.MinValue;
                for (int i = 0; i < 1e7; ++i) 
                {
                    config = new TestConfiguration(3, 3, 0, patients, pc);
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
        }
    }
}
