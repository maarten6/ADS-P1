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
        Random rnd;
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
            rnd = new Random(69);

            this.FirstDoseFromLB = FirstDoseFromLB + 1;
            this.FirstDoseFromUB = FirstDoseFromUB + 1;
            this.FirstDoseToLB = FirstDoseToLB + 1;
            this.FirstDoseToUB = FirstDoseToUB + 1;
            this.DelayLB = DelayLB + 1;
            this.DelayUB = DelayUB + 1;
            this.SecondDoseIntervalLB = SecondDoseIntervalLB + 1;
            this.SecondDoseIntervalUB = SecondDoseIntervalUB + 1;
        }

        public Patient GeneratePatient(int ID)
        {
            // TODO: add sanity checks
           /* int firstDoseFrom = rnd.Next(FirstDoseFromLB, FirstDoseFromUB),
                firstDoseTo = rnd.Next(FirstDoseToLB, FirstDoseToUB),
                delay = rnd.Next(DelayLB, DelayUB),
                secondDoseInterval = rnd.Next(SecondDoseIntervalLB, SecondDoseIntervalUB);*/

            int firstDoseFrom = 1,
               firstDoseTo = 4,
               delay = 2,
               secondDoseInterval = 8;

            return new Patient(ID, firstDoseFrom, firstDoseTo, delay, secondDoseInterval);
        }
    }
}
