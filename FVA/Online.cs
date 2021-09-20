using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FVA
{
    public class Online
    {
        private int patientCNT { get => patients.Count(); }
        // not sure if this list is needed, but it will certainly be handy for debugging
        private List<Patient> patients;
        public Online()
        {
            for (string line = Console.ReadLine(); line != "x"; line = Console.ReadLine())
            {
                Patient cur = new Patient(line);
                patients.Add(cur);
                Schedule(cur);
            }
        }

        private void Schedule(Patient patient)
        {
            // do scheduling here
        }
    }
}
