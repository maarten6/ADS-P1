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
        private int patientCNT { get => patients.Count(); }
        // not sure if this list is needed, but it will certainly be handy for debugging
        private List<Patient> patients;

        private List<Hospital> hospitals;

        // TODO IDEA
        //1: 1,1,0,0,2,2,0,1,1,1,0,0,0,0,2,2,2
        //2: 0,0,0,0,2,2,0,1,1,1,0,0,0,0,2,2,2
        //3: 0,0,0,0,2,2,0,1,1,1,0,0,0,0,2,2,2
        // n*n Matrix die per hospital timeslot afgaaat

        // constructor for solving the actual problem
        public Online(Patient firstpatient)
        {
            patients = new List<Patient> { firstpatient };
            hospitals = new List<Hospital> { new Hospital(0) };

            StringBuilder output = new StringBuilder();

            Schedule(firstpatient, output);

            for (string line = Console.ReadLine(); line != "x"; line = Console.ReadLine())
            {
                Patient cur = new Patient(patientCNT, line);

                // this list is only kept for overview of the programmer. its contents are never used by the code.
                patients.Add(cur);

                DebugPrint("Scheduling a patient.");
                Schedule(cur, output);
                DebugPrint("Done scheduling a patient");
            }

            // required output
            output.Append(hospitals.Count().ToString());
            Print(output.ToString());

            // debug info hospital overview
            DebugPrint("\n---------------------------------------------------------------------------------------\n");
            foreach (Hospital h in hospitals)
                DebugPrint(h.ToString());
        }

        // constructor for solving generated testcases
        public Online(TestConfiguration config)
        {
            patients = new List<Patient>();
            hospitals = new List<Hospital>();

            StringBuilder output = new StringBuilder();

            foreach (Patient cur in config.Patients)
            {
                // this list is only kept for overview of the programmer. its contents are never used by the code.
                patients.Add(cur);

                DebugPrint("Scheduling a patient.");
                Schedule(cur, output);
                DebugPrint("Done scheduling a patient");
            }

            // required output
            output.Append(hospitals.Count().ToString());
            Print(output.ToString());

            // debug info hospital overview
            DebugPrint("\n---------------------------------------------------------------------------------------\n");
            foreach (Hospital h in hospitals)
                DebugPrint(h.ToString());
        }

        private void Schedule(Patient patient, StringBuilder output)
        {
            List<TimeSlot> shot1List = new List<TimeSlot>();
            List<TimeSlot> shot2List = new List<TimeSlot>();

            foreach (Hospital hospital in hospitals)
            {
                hospital.ExtendSchedule(patient); //  TODO IDEA: this same number is calculated for every hospital. Then again, not so much hospitals.
                hospital.GetSlots(shot1List, PTIMEFIRST, patient.FirstDoseFrom, patient.FirstDoseTo);
            }

            shot1List.OrderBy(item => item.StartTime); // TODO: is this needed?
            int timeSlots = PTIMEFIRST + PTIMESECOND;
            int maxScore = Int32.MinValue;

            TimeSlot ts1 = null,
                     ts2 = null;

            int p1before = 0,
                p1after = 0,
                p2before = 0,
                p2after = 0;

            foreach (TimeSlot timeslot1 in shot1List)
            {
                shot2List = new List<TimeSlot>();
                int startShot2 = timeslot1.EndTime + GAP + patient.Delay;
                int endShot2 = startShot2 + patient.SecondDoseInterval;

                foreach (Hospital hospital in hospitals)
                    hospital.GetSlots(shot2List, PTIMESECOND, startShot2, endShot2);

                foreach (TimeSlot timeslot2 in shot2List)
                {
                    if (timeslot1.Hospital == timeslot2.Hospital)
                        (p1before, p1after, p2before, p2after) = hospitals[timeslot1.Hospital].Distances(timeslot1, timeslot2);
                    else
                    {
                        (p1before, p1after) = hospitals[timeslot1.Hospital].Distances(timeslot1);
                        (p2before, p2after) = hospitals[timeslot2.Hospital].Distances(timeslot2);
                    }

                    int score = calcScore(p1before) + calcScore(p1after) + calcScore(p2before) + calcScore(p2after);



                    /*Console.WriteLine(p1before + " " + p1after + " " + p2before + " " + p2after);*/
                    //DebugPrint(timeslot1.StartTime + " " + timeslot2.StartTime + " Score:" + score);

                    if (score > maxScore)
                    {
                        maxScore = score;
                        ts1 = timeslot1;
                        ts2 = timeslot2;
                    }
                }
            }
            if (ts1 == null || ts2 == null)
            {
                hospitals.Add(new Hospital(hospitals.Count()));
                Schedule(patient, output);
            }
            else
            {
                hospitals[ts1.Hospital].Schedule(patient.ID, ts1);
                hospitals[ts2.Hospital].Schedule(patient.ID, ts2);
                output.Append((ts1.StartTime + 1) + ", " + (ts1.Hospital + 1) + ", " + (ts2.StartTime + 1) + ", " + (ts2.Hospital + 1) + "\n");
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
        /*        public int calcScore(int x)
                {
                    if (x == 0)
                        return 3;
                    //2 + 3 + 3 + 2 moet ook kunnen, TODO FIX
                    if (x % (PTIMEFIRST + PTIMESECOND) == 0 || modulo(x) || modulo(x - PTIMEFIRST) || modulo(x - PTIMESECOND))
                        return 2;
                    return 0;
                }
                public bool modulo(int x)
                {
                    return (x % PTIMEFIRST == 0 || x % PTIMESECOND == 0);
                }*/
    }

    public class Hospital
    {
        private int ID;
        public List<int> schedule;

        public Hospital(int id)
        {
            ID = id;
            schedule = new List<int>();
        }

        public Tuple<int, int> Distances(TimeSlot t)
        {
            int before = 0,
                after = 0;

            if (t.StartTime != 0)
                for (int i = t.StartTime - 1; i >= 0 && schedule[i] == 0; --i) ++before;
            if (t.EndTime < schedule.Count)
                for (int i = t.EndTime; i < schedule.Count && schedule[i] == 0; ++i)
                {
                    ++after;
                    if (i == schedule.Count - 1)
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
            for (int currentslot = shotstart; currentslot <= shotend && currentslot < schedule.Count; currentslot++)
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
                for (int i = shotend - curlen + 1; i <= shotend - shotlength + 1; ++i)
                    result.Add(new TimeSlot(this.ID, i, shotlength));
        }

        public override string ToString()
        {
            StringBuilder res = new StringBuilder();
            for (int i = 0; i < schedule.Count(); ++i) res.Append(schedule[i].ToString());

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
