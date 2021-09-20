using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FVA
{
    public class Patient
    {
        public int FirstDoseFrom { get; private set; }
        public int FirstDoseTo { get; private set; }
        public int Delay { get; private set; }
        public int SecondDoseInterval { get; private set; }

        public Patient(string line)
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
                FirstDoseFrom = firstDoseFrom;
                FirstDoseTo = firstDoseTo;
                Delay = delay;
                SecondDoseInterval = secondDoseInterval;
            }
        }
    }
}
