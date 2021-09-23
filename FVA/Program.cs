using System;

namespace FVA
{
    class Program
    {
        static void Main(string[] args)
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
                    patients[i] = new Patient(Console.ReadLine());

                new Offline(patients);

            }
            else
            {
                Utils.DebugPrint("Solving the online problem.");
                new Online();
            }
        }
    }
}
