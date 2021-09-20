using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FVA
{
    public static class Utils
    {
        public static bool DEBUG = false;
        // note that offline == !online
        public static bool OFFLINE;
        // processing time of the first dose
        public static int PTIMEFIRST;
        // processing time of the second dose
        public static int PTIMESECOND;
        // gap between first and second dose
        public static int GAP;

        public static void DebugPrint(string line) => Print(line, false);
        public static void Print(string line) => Print(line, true);
        private static void Print(string line, bool alwaysprint)
        {
            if (DEBUG || alwaysprint) Console.WriteLine(line);
        }

    }
}
