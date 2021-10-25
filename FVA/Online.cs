using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using static FVA.Utils;

namespace FVA
{
    public class Online
    {
        public int HospitalCNT { get => hospitals.Count; }

        private List<Hospital> hospitals;

        // constructor for solving the actual problem
        public Online(Patient firstpatient)
        {
            hospitals = new List<Hospital>();

            StringBuilder output = new StringBuilder();

            Schedule(firstpatient, output);

            int patientCNT = 0;
            for (string line = Console.ReadLine(); line != "x"; line = Console.ReadLine())
                Schedule(new Patient(++patientCNT, line), output);

            PrintFullOutput(output);
        }

        // constructor for solving generated testcases
        public Online(Configuration config)
        {
            hospitals = new List<Hospital>();

            StringBuilder output = new StringBuilder();

            foreach (Patient cur in config.Patients)
                Schedule(cur, output);

            PrintFullOutput(output);
        }

        private void PrintFullOutput(StringBuilder sb)
        {
            // required output
            sb.Append(hospitals.Count().ToString());
            Print(sb.ToString());

            // debug info hospital overview
            DebugPrint("\n---------------------------------------------------------------------------------------\n");
            foreach (Hospital h in hospitals)
                DebugPrint(h.ToString());
        }

        private void Schedule(Patient patient, StringBuilder output)
        {
            List<TimeSlot> shot1List = new List<TimeSlot>();
            List<TimeSlot> shot2List;

            TimeSlot ts1 = null,
                     ts2 = null;

            int maxScore = Int32.MinValue;
            int p1before, p1after, p2before, p2after, score;

            // get possibilities for the first jab
            foreach (Hospital hospital in hospitals)
                hospital.GetSlots(shot1List, PTIMEFIRST, patient.FirstDoseFrom, patient.FirstDoseTo);
            
            // explore possibilities for the first jab
            foreach (TimeSlot timeslot1 in shot1List)
            {
                shot2List = new List<TimeSlot>();
                int startShot2 = timeslot1.EndTime + GAP + patient.Delay;
                int endShot2 = startShot2 + patient.SecondDoseInterval;

                // get possibilities for the second jab
                foreach (Hospital hospital in hospitals)
                    hospital.GetSlots(shot2List, PTIMESECOND, startShot2, endShot2);

                // explore possibilities for the second jab
                foreach (TimeSlot timeslot2 in shot2List)
                {
                    if (timeslot1.Hospital == timeslot2.Hospital)
                        (p1before, p1after, p2before, p2after) = hospitals[timeslot1.Hospital].Distances(timeslot1, timeslot2);
                    else
                    {
                        (p1before, p1after) = hospitals[timeslot1.Hospital].Distances(timeslot1);
                        (p2before, p2after) = hospitals[timeslot2.Hospital].Distances(timeslot2);
                    }

                    score = calcScore(p1before) + calcScore(p1after) + calcScore(p2before) + calcScore(p2after);

                    if (score > maxScore)
                    {
                        maxScore = score;
                        ts1 = timeslot1;
                        ts2 = timeslot2;

                        // a score can never be higher dan 12
                        if (maxScore == 12) break;
                    }
                }

                // a score can never be higher dan 12
                if (maxScore == 12) break;
            }


            if (ts1 == null || ts2 == null)
            {
                // patient does not fit in existing hospitals
                hospitals.Add(new Hospital(hospitals.Count()));
                Schedule(patient, output);
            }
            else
            {
                hospitals[ts1.Hospital].Schedule(patient.ID, ts1);
                hospitals[ts2.Hospital].Schedule(patient.ID, ts2);
                output.Append($"{ ts1.StartTime + Utils.TIMEOFFSET}, { ts1.Hospital + Utils.TIMEOFFSET}, { ts2.StartTime + Utils.TIMEOFFSET}, { ts2.Hospital + Utils.TIMEOFFSET}\n");
            }
        }

        public static int calcScore(int x)
        {
            if (x == int.MaxValue)
                return 3;

            if (x < 0)
                return 0;

            if (x == 0)
                return 3;

            if (x % PTIMEFIRST == 0 || x % PTIMESECOND == 0)
                return 2;

            return Math.Max(calcScore(x - PTIMEFIRST), calcScore(x - PTIMEFIRST));
        }
    }

    public class Hospital
    {
        private int ID;
        public List<int> schedule;
        private int latestPatient;

        public Hospital(int id)
        {
            ID = id;
            schedule = new List<int>(); 
            latestPatient = 0;
        }

        public Tuple<int, int> Distances(TimeSlot t)
        {
            int before = 0,
                after = 0;

            int lastshot = Math.Max(schedule.Count - 1, latestPatient + LONGESTSHOT);

            if (t.StartTime != 0)
                for (int i = t.StartTime - 1; i >= 0 && schedule[i] == 0; --i) ++before;
            if (t.EndTime < schedule.Count)
                for (int i = t.EndTime; i < schedule.Count && schedule[i] == 0; ++i)
                {
                    ++after;
                    if (i >= lastshot)
                        after = int.MaxValue;
                }

            return new Tuple<int, int>(before, after);
        }

        public Tuple<int, int, int, int> Distances(TimeSlot t1, TimeSlot t2)
        {
            if (schedule[t2.StartTime] != 0) throw new Exception("This should never happen");
            schedule[t2.StartTime] = -1;
            (int t1before, int t1after) = Distances(t1);
            schedule[t2.StartTime] = 0;

            if (schedule[t1.EndTime - 1] != 0) throw new Exception("This should never happen");

            (int test, int test2) = Distances(t2);
            schedule[t1.EndTime - 1] = -1;
            (int t2before, int t2after) = Distances(t2);
            schedule[t1.EndTime - 1] = 0;

            if (test2 == t2before)
                t2before = -1;


            return new Tuple<int, int, int, int>(t1before, t1after, t2before, t2after);
        }

        public void ExtendSchedule(int slot)
        {
            while (schedule.Count <= slot) schedule.Add(0);
        }
        public void ExtendSchedule(Patient patient) => ExtendSchedule(patient.FirstDoseTo + GAP + patient.Delay + patient.SecondDoseInterval);

        public void Schedule(int PatientID, TimeSlot ts)
        {
            latestPatient = Math.Max(latestPatient, ts.EndTime);
            ExtendSchedule(ts.EndTime);

            PutSlotInSchedule(PatientID, ts.StartTime, ts.EndTime);
        }

        private void PutSlotInSchedule(int PatientID, int from, int to)
        {
            for (int i = from; i < to; ++i)
            {
                if (schedule[i] != 0) throw new Exception("Illegal planning");

                schedule[i] = PatientID;
            }
        }

        public void GetSlots(List<TimeSlot> result, int shotlength, int shotstart, int shotend)
        {
            ExtendSchedule(shotend);

            int curlen = 0;
            int maxShotLength = shotstart +  latestPatient + LONGESTSHOT;
            for (int currentslot = shotstart; currentslot <= shotend && currentslot <= maxShotLength; currentslot++)
            {
                if (schedule[currentslot] != 0)
                {
                    if (curlen >= shotlength)
                        for (int i = currentslot - curlen; i <= currentslot - shotlength; ++i)
                            result.Add(new TimeSlot(this.ID, i, shotlength));

                    curlen = 0;
                    continue;
                }
                curlen++;
            }

            if (curlen >= shotlength)
                for (int i = Math.Min(shotend, maxShotLength) - curlen + 1; i <= Math.Min(shotend, maxShotLength) - shotlength + 1; ++i)
                    result.Add(new TimeSlot(this.ID, i, shotlength));
        }

        public override string ToString()
        {
            StringBuilder res = new StringBuilder();
            char[] alfabet = "123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_=+[]{};:'\",.<>/?|\\`~".ToCharArray();

            foreach (int item in schedule)
                if (item == 0) res.Append("-");
                else if (item < alfabet.Length) res.Append(alfabet[item]);
                else res.Append((char)item);
   
            return res.ToString();
        }
    }

    public class TimeSlot
    {
        public int Hospital { get; private set; }
        public int StartTime { get; private set; }
        public int EndTime { get; private set; }
        public int Length { get; private set; }

        public TimeSlot(int hospitalID, int start, int length)
        {
            Hospital = hospitalID;
            StartTime = start;
            EndTime = start + length;
            Length = length;
        }
    }
}
