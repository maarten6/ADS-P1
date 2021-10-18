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

        public TestConfiguration()
        {
            Utils.PTIMEFIRST = 3;
            Utils.PTIMESECOND = 3;
            Utils.GAP = 3;

            this.Patients = new List<Patient>();
        }
    }
}
