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

        public Online(Patient firstpatient)
        {
            patients = new List<Patient> { firstpatient };
            hospitals = new List<Hospital> { new Hospital(0, firstpatient) };

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

            List<TimeSlot> shotList = new List<TimeSlot>();
            //List<Tuple<int, int, int>> shot2list = new List<Tuple<int, int, int>>();

            foreach (Hospital hospital in hospitals)
            {
                hospital.ExtendSchedule(patient);

                hospital.GetSlots(shotList, Math.Min(PTIMEFIRST,PTIMESECOND));
            }


            shotList.OrderBy(item => item.StartTime);
            int count = 0;

            TimeSlot ts1 = null, ts2 = null, temp = null;
            foreach (TimeSlot timeslot in shotList)
            {
                if (!ValidShot(timeslot, patient.FirstDoseFrom, patient.FirstDoseTo, PTIMEFIRST, out ts1)) 
                    continue;

                int startts2 = ts1.StartTime + PTIMEFIRST + GAP + patient.Delay;

                ts2 = null;
                foreach (TimeSlot ts2test in shotList)
                    if (ValidShot(ts2test, startts2, startts2 + patient.SecondDoseInterval, PTIMESECOND, out temp))
                    {
                        ts2 = temp;
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
            if (ts1 == null || ts2 == null)
            {
                hospitals.Add(new Hospital(hospitals.Count(), patient));
            }
            else
            {
                hospitals[ts1.Hospital].Schedule(patient.ID, ts1.StartTime, ts1.StartTime + PTIMEFIRST);
                hospitals[ts2.Hospital].Schedule(patient.ID, ts2.EndTime - PTIMESECOND, ts2.EndTime);
            }


            //1: 1,1,0,0,2,2,0,1,1,1,0,0,0,0,2,2,2
            //2: 0,0,0,0,2,2,0,1,1,1,0,0,0,0,2,2,2
            //3: 0,0,0,0,2,2,0,1,1,1,0,0,0,0,2,2,2
            // n*n Matrix die per hospital timeslot afgaaat

        }

        // private bool ValidShot1(TimeSlot ts, Patient p) => ValidShot(ts, p.FirstDoseFrom, PTIMEFIRST);
        private bool ValidShot(TimeSlot ts, int slotstart, int slotend, int timespent, out TimeSlot valid)
        {
            valid = null;
            if (slotend < ts.StartTime || ts.EndTime < slotstart) return false;

            for (int actualstart = ts.StartTime; actualstart <= slotend - timespent && actualstart <= ts.EndTime - timespent; ++actualstart)
                if (actualstart >= slotstart)
                {
                    valid = new TimeSlot(ts.Hospital, actualstart, timespent);
                    return true;
                }

            return false;
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
        public Hospital(int id, Patient p)
        {
            // NOTE: this adds the patient in their first available slots, nothing smart here
            ID = id;
            schedule = new List<int>();

            int startLastTimeSlot = p.FirstDoseTo + GAP + p.Delay;
            int endLastTimeSlot = startLastTimeSlot + p.SecondDoseInterval;

            ExtendSchedule(endLastTimeSlot);

            for (int i = p.FirstDoseFrom; i < p.FirstDoseFrom + PTIMEFIRST; ++i)
                schedule[i] = p.ID;

            for (int i = startLastTimeSlot; i <endLastTimeSlot; ++i)
                schedule[i] = p.ID;
        }

        public void ExtendSchedule(int slot)
        {
            while (schedule.Count < slot) schedule.Add(0);
        }
        public void ExtendSchedule(Patient patient) => ExtendSchedule(patient.FirstDoseTo + GAP + patient.Delay + patient.SecondDoseInterval);

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
