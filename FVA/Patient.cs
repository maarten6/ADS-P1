using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FVA
{
    public class Patient
    {
        public int ID { get; private set; }
        public int FirstDoseFrom { get; private set; }
        public int FirstDoseTo { get; private set; }
        public int Delay { get; private set; }
        public int SecondDoseInterval { get; private set; }

        public Patient(int ID, string line)
        {
            string[] data = line.Split(',');

            if (data.Length != 4
                || !int.TryParse(data[0], out int firstDoseFrom)
                || !int.TryParse(data[1], out int firstDoseTo)
                || !int.TryParse(data[2], out int delay)
                || !int.TryParse(data[3], out int secondDoseInterval)
                )
            {
                throw new ArgumentException("A patient should consist of four integers.");
            }
            else
            {
                this.ID = ID + 1;
                this.FirstDoseFrom = Utils.TESTCASEZEROBASED ? firstDoseFrom : firstDoseFrom - 1;
                this.FirstDoseTo = Utils.TESTCASEZEROBASED ? firstDoseTo : firstDoseTo - 1;
                this.Delay = delay;
                this.SecondDoseInterval = secondDoseInterval;
            }
        }

        public Patient(int ID, int  firstdosefrom, int firstdoseto, int delay, int seconddoseinterval)
        {
            this.ID = ID;
            this.FirstDoseFrom = firstdosefrom;
            this.FirstDoseTo = firstdoseto;
            this.Delay = delay;
            this.SecondDoseInterval = seconddoseinterval;
        }

        public override string ToString() => $"{FirstDoseFrom + Utils.TIMEOFFSET}, {FirstDoseTo + Utils.TIMEOFFSET}, {Delay}, {SecondDoseInterval}";
    }
}
