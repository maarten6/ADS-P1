using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FVA
{
    public static class Utils
    {
        public const bool DEBUG = true;
        public const bool TESTCASEZEROBASED = false;

        public static Random PRNG = new Random(69);

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
