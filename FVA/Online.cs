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
        private int patientCNT { get => patients.Count(); }
        // not sure if this list is needed, but it will certainly be handy for debugging
        private List<Patient> patients;

        private List<Hospital> hospitals;

        public Online()
        {
            patients = new List<Patient>();
            hospitals = new List<Hospital> { new Hospital(0) };

            for (string line = Console.ReadLine(); line != "x"; line = Console.ReadLine())
            {
                Patient cur = new Patient(patientCNT, line);

                

                patients.Add(cur);

                DebugPrint("Scheduling a patient.");
                Schedule(cur);
                DebugPrint("Done scheduling a patient");
            }

            // TODO: print all patient timeslots
            foreach (Hospital h in hospitals)
                DebugPrint(h.ToString());
            Print(hospitals.Count().ToString());
        }


        

        private void Schedule(Patient patient)
        {
            // do scheduling here

            int s = PTIMEFIRST + PTIMESECOND;

            int startLastTimeSlot = patient.FirstDoseTo + GAP + patient.Delay;
            int endLastTimeSlot = startLastTimeSlot + patient.SecondDoseInterval;

            List<TimeSlot> shotList = new List<TimeSlot>();
            //List<Tuple<int, int, int>> shot2list = new List<Tuple<int, int, int>>();

            foreach (Hospital hospital in hospitals)
            {
                hospital.ExtendSchedule(endLastTimeSlot);

                hospital.GetSlots(shotList, Math.Min(PTIMEFIRST,PTIMESECOND));
            }


            shotList.OrderBy(item => item.StartTime);
            int count = 0;

            TimeSlot ts1 = null, ts2 = null;
            foreach (TimeSlot timeslot in shotList)
            {
                ts1 = timeslot;
                if (!ValidShot(ts1, patient.FirstDoseFrom, PTIMEFIRST)) 
                    continue;

                int startts2 = ts1.StartTime + PTIMEFIRST + GAP + patient.Delay;

                ts2 = null;
                foreach (TimeSlot ts2test in shotList)
                    if (ValidShot(ts2test, startts2, PTIMESECOND))
                    {
                        ts2 = ts2test;
                        break;
                    }

                if (ts2 != null) break;

                /*
                count++;
                int hospitalId = timeslot.Hospital,
                    startTime = timeslot.StartTime,
                    length = timeslot.Length;
                int startTimeDose1 = 0;
                int endTimeDose1 = 0;

                int startTimeDose2 = 0;
                int endTimeDose2 = 0;

                */


                /*
                for(int i = timeslot.StartTime; i < timeslot.StartTime + length - PTIMEFIRST; i++)
                {
                    int x = i - startTime + length;
                    int score = 0;

                    if (validShot(i, patient)){
                        int startTimeDose1 = startTime;
                        int endTimeDose1 = StartTime + length;


                        for(int j = count; j < shotList.Count(); j++)
                        {
                        

                            if(i + patient.Delay + GAP < shotList[j].EndTime - PTIMESECOND){
                                int startTimeDose2 = shotList[j].EndTime -  PTIMESECOND;
                                int endTimeDose2 = shotList[j].EndTime;

                        
                        }

                    }
                        

                    if (x == PTIMEFIRST) score++;

                    
                    
                }*/
            }

            hospitals[ts1.Hospital].Schedule(patient.ID, ts1.StartTime, ts1.StartTime + PTIMEFIRST);
            hospitals[ts2.Hospital].Schedule(patient.ID, ts2.EndTime - PTIMESECOND, ts2.EndTime);


            //1: 1,1,0,0,2,2,0,1,1,1,0,0,0,0,2,2,2
            //2: 0,0,0,0,2,2,0,1,1,1,0,0,0,0,2,2,2
            //3: 0,0,0,0,2,2,0,1,1,1,0,0,0,0,2,2,2
            // n*n Matrix die per hospital timeslot afgaaat

        }

        // private bool ValidShot1(TimeSlot ts, Patient p) => ValidShot(ts, p.FirstDoseFrom, PTIMEFIRST);
        private bool ValidShot(TimeSlot ts, int slotstart, int timespent)
        {
            // TODO: fix this stuff so it does what we want
            bool len = ts.Length >= timespent;
            bool tim = ts.EndTime - timespent >= slotstart;
            return len && tim;
        }
        
        // 1,1,0,0,2,2,0,1,1,1,0,0,0,0,2,2,2
        // (1,2,3),(1,6,6),(1,10,13)


    }

    public class Hospital
    {
        private int ID;
        private List<int> schedule;

        public Hospital(int id)
        {
            ID = id;
            schedule = new List<int>();
        }
        
        public void ExtendSchedule(int slot)
        {
            while (schedule.Count < slot) schedule.Add(0);
        }

        public void Schedule(int PatientID, int start, int end)
        {
            ExtendSchedule(end);

            PutSlotInSchedule(PatientID, start, end);
        }

        private void PutSlotInSchedule(int PatientID, int from, int to)
        {
            for (int i = from; i < to; ++i)
            {
                if (schedule[i] != 0) throw new Exception("Illegal planning");

                schedule[i] = PatientID;
            }
        }

        public List<TimeSlot> GetSlots(List<TimeSlot> result, int minimumlength)
        {
            for (int current = 0, start, length; current < schedule.Count; current += length)
            {
                if (schedule[current] != 0)
                    while (schedule[current++] != 0) ;

                start = current;
                length = 1;
                while (current < schedule.Count - 1 && schedule[++current] == 0) ++length;
                result.Add(new TimeSlot(ID, start, length));
            }


            return result;
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
