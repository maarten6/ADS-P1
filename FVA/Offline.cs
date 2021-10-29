using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FVA
{
    public class Offline
    {
        private int patientCNT;
        private Patient[] patients;
        public Offline(Patient[] patients)
        {
            patientCNT = patients.Length;
            this.patients = patients;

            // we planned to do offline scheduling here, we decided to do this in Python later
        }
    }
}
