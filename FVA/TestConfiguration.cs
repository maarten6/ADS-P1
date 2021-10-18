using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FVA
{
    public class TestConfiguration
    {
        public  List<Patient> Patients { get; private set; }

        public TestConfiguration(int firstshot, int secondshot, int gap, int patients, PatientConfiguration pc)
        {
            Utils.PTIMEFIRST = firstshot;
            Utils.PTIMESECOND = secondshot;
            Utils.GAP = gap;

            this.Patients = new List<Patient>();

            for (int i = 1; i <= patients; ++i)
                this.Patients.Add(pc.GeneratePatient(i));
        }
    }

    public class PatientConfiguration
    {
        private int
            FirstDoseFromLB,
            FirstDoseFromUB,
            FirstDoseToLB,
            FirstDoseToUB,
            DelayLB,
            DelayUB,
            SecondDoseIntervalLB,
            SecondDoseIntervalUB;

        public PatientConfiguration(int FirstDoseFromLB, int FirstDoseFromUB, int FirstDoseToLB, int FirstDoseToUB, int DelayLB, int DelayUB, int SecondDoseIntervalLB, int SecondDoseIntervalUB)
        {
            this.FirstDoseFromLB = FirstDoseFromLB;
            this.FirstDoseFromUB = FirstDoseFromUB;
            this.FirstDoseToLB = FirstDoseToLB;
            this.FirstDoseToUB = FirstDoseToUB;
            this.DelayLB = DelayLB;
            this.DelayUB = DelayUB;
            this.SecondDoseIntervalLB = SecondDoseIntervalLB;
            this.SecondDoseIntervalUB = SecondDoseIntervalUB;
        }

        public Patient GeneratePatient(int ID)
        {
            int time = Utils.GAP + Utils.PTIMEFIRST + Utils.PTIMESECOND;
            // TODO: add sanity checks
            int firstDoseFrom = Utils.PRNG.Next(FirstDoseFromLB, FirstDoseFromUB);
            while (firstDoseFrom  + Utils.PTIMEFIRST >= FirstDoseToUB)
                firstDoseFrom = Utils.PRNG.Next(FirstDoseFromLB, FirstDoseFromUB);

            int firstDoseTo = Utils.PRNG.Next(FirstDoseToLB, FirstDoseToUB);
            while (firstDoseFrom + Utils.PTIMEFIRST > firstDoseTo)
                firstDoseTo = Utils.PRNG.Next(FirstDoseToLB, FirstDoseToUB);

            int delay = Utils.PRNG.Next(DelayLB, DelayUB);
            int secondDoseInterval = Utils.PRNG.Next(SecondDoseIntervalLB, SecondDoseIntervalUB);
            while (secondDoseInterval < Utils.PTIMESECOND)
                secondDoseInterval = Utils.PRNG.Next(SecondDoseIntervalLB, SecondDoseIntervalUB);


            return new Patient(ID, firstDoseFrom, firstDoseTo, delay, secondDoseInterval);
        }
    }
}
