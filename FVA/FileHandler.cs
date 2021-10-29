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

        private static void WriteToFile(string path, string result) => File.WriteAllText(ROOT + path + EXTENTION, result);
        public static void WriteResults(string results) => WriteToFile(OUTPUTLOCATION, results);
        public static void WriteTestCase(bool online, string name, string testcase) => WriteToFile("generated/" + (online ? "online/" : "offline/") + name, testcase);

        public static IEnumerable<string> ReadLines(string filename)
        {
            StreamReader reader;
            try 
            { 
                reader = new StreamReader(ROOT + filename + (filename.EndsWith('t') ? "" : EXTENTION));
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
