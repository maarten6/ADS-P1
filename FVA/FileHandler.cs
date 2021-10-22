using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FVA
{
    static class FileHandler
    {
        private static string ROOT = "../../../testcases/";
        public const string
            EXTENTION = ".txt",
            INPUTLOCATION = "INPUT",
            OUTPUTLOCATION = "OUTPUT";

        public static void WriteResults(string result) => File.WriteAllText(ROOT + OUTPUTLOCATION + EXTENTION, result);
        public static void WriteResults(IEnumerable<string> results)
        {
            var sb = new StringBuilder();

            foreach (string result in results)
                sb.Append(result + "\n");

            WriteResults(sb.ToString());
        }

        public static IEnumerable<string> ReadLines(string filename)
        {
            StreamReader reader;
            try 
            { 
                reader = new StreamReader(ROOT + filename + EXTENTION);
            }
            catch (IOException e)
            {
                Console.WriteLine("The file could not be read:");
                Console.WriteLine(e.Message);
                throw new Exception(filename + " is not a valid file");
            }

            string line;
            while ((line = reader.ReadLine()) != null)
                if (line != "")
                    yield return line;
            reader.Close();
        }
    }
}
