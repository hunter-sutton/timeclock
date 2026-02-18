import json
import datetime
import os
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional
from pathlib import Path
from tabulate import tabulate

# --- Constants ---
USER_FILE = Path("user.json")
DATE_FMT = "%Y-%m-%d %H:%M:%S"
SHORT_DATE_FMT = "%Y-%m-%d"
TIME_FMT = "%H:%M"

# --- Helper Functions ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_current_time_str() -> str:
    return datetime.datetime.now().strftime(DATE_FMT)

def str_to_dt(date_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_str, DATE_FMT)

# --- Data Models ---

@dataclass
class Shift:
    start_time: str
    end_time: Optional[str] = None
    hours: float = 0.0
    clocked_in: bool = True
    notes: str = ""

    @property
    def start_dt(self) -> datetime.datetime:
        return str_to_dt(self.start_time)

    def clock_out(self):
        self.end_time = get_current_time_str()
        self.clocked_in = False
        self.recalculate_hours()

    def recalculate_hours(self):
        if self.start_time and self.end_time:
            start = str_to_dt(self.start_time)
            end = str_to_dt(self.end_time)
            duration = (end - start).total_seconds() / 3600
            self.hours = round(duration, 2)

class Job:
    def __init__(self, name: str, filename: str, pay: float):
        self.name = name
        self.filename = Path(filename)
        self.pay = pay
        self.shifts: List[Shift] = []
        self.load_shifts()

    def load_shifts(self):
        if not self.filename.exists():
            return
        
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.shifts = [Shift(**s) for s in data]
        except (json.JSONDecodeError, TypeError):
            print(f"Warning: Could not read shift data for {self.name}.")
            self.shifts = []

    def save_shifts(self):
        with open(self.filename, 'w') as f:
            json.dump([asdict(s) for s in self.shifts], f, indent=2)

    def clock_in(self):
        if self.is_clocked_in:
            print(f"You are already clocked in to {self.name}.")
            return

        new_shift = Shift(start_time=get_current_time_str())
        self.shifts.append(new_shift)
        self.save_shifts()
        print(f"Clocked in to {self.name} at {new_shift.start_time}")

    def clock_out(self):
        if not self.is_clocked_in:
            print("You are not currently clocked in.")
            return

        current_shift = self.shifts[-1]
        current_shift.clock_out()
        
        print(f"Clocked out at {current_shift.end_time}")
        print(f"Duration: {current_shift.hours} hours")
        
        if self._confirm("Would you like to add notes?"):
            current_shift.notes = input("Enter notes: ").strip()
        
        self.save_shifts()

    def add_manual_shift(self):
        print("\n--- Add Manual Shift ---")
        
        # 1. Get Date
        while True:
            date_input = input(f"Date ({SHORT_DATE_FMT}) [Enter for Today]: ").strip()
            if not date_input:
                target_date = datetime.date.today()
                break
            try:
                target_date = datetime.datetime.strptime(date_input, SHORT_DATE_FMT).date()
                break
            except ValueError:
                print(f"Invalid format. Please use {SHORT_DATE_FMT}")

        # 2. Get Times
        print(f"Adding shift for: {target_date}")
        start_time_obj = self._get_valid_time("Start Time (24h HH:MM): ", target_date)
        
        # Validation loop to ensure end time is after start time
        while True:
            end_time_obj = self._get_valid_time("End Time   (24h HH:MM): ", target_date)
            
            # Handle overnight shifts (if end time is earlier than start time, assume next day)
            if end_time_obj < start_time_obj:
                if self._confirm("End time is before start time. Is this an overnight shift ending the next day?"):
                    end_time_obj += datetime.timedelta(days=1)
                    break
                else:
                    print("End time cannot be before start time. Please try again.")
            else:
                break

        # 3. Create Shift
        duration = (end_time_obj - start_time_obj).total_seconds() / 3600
        
        notes = input("Notes (optional): ").strip()

        new_shift = Shift(
            start_time=start_time_obj.strftime(DATE_FMT),
            end_time=end_time_obj.strftime(DATE_FMT),
            hours=round(duration, 2),
            clocked_in=False,
            notes=notes
        )

        self.shifts.append(new_shift)
        self.save_shifts()
        print(f"Successfully added shift ({new_shift.hours} hours).")

    def _get_valid_time(self, prompt: str, base_date: datetime.date) -> datetime.datetime:
        """Helper to get a valid time string and combine it with a date."""
        while True:
            time_str = input(prompt).strip()
            try:
                t = datetime.datetime.strptime(time_str, TIME_FMT).time()
                return datetime.datetime.combine(base_date, t)
            except ValueError:
                print("Invalid format. Use HH:MM (e.g., 09:00 or 14:30).")

    @property
    def is_clocked_in(self) -> bool:
        return self.shifts and self.shifts[-1].clocked_in

    def _confirm(self, prompt: str) -> bool:
        while True:
            choice = input(f"{prompt} (y/n): ").lower().strip()
            if choice in ['y', 'yes']: return True
            if choice in ['n', 'no']: return False

class TimeClockApp:
    def __init__(self):
        self.user_name = ""
        self.jobs: List[Job] = []
        self.load_user()

    def load_user(self):
        if not USER_FILE.exists():
            self.setup_new_user()
        else:
            try:
                with open(USER_FILE, 'r') as f:
                    data = json.load(f)
                    self.user_name = data.get("name", "User")
                    for job_data in data.get("jobs", []):
                        self.jobs.append(Job(**job_data))
            except json.JSONDecodeError:
                print("User file corrupted.")
                self.setup_new_user()

    def save_user(self):
        data = {
            "name": self.user_name,
            "jobs": [
                {"name": j.name, "filename": str(j.filename), "pay": j.pay} 
                for j in self.jobs
            ]
        }
        with open(USER_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def setup_new_user(self):
        print("Welcome to TimeClock!")
        self.user_name = input("What is your name? > ").strip()
        self.save_user()

    def add_new_job(self):
        print("\n--- Add New Job ---")
        while True:
            name = input("Job Name: ").strip()
            if not name:
                print("Name cannot be empty.")
                continue
            if any(j.name.lower() == name.lower() for j in self.jobs):
                print("Job already exists.")
                continue
            break

        while True:
            try:
                pay = float(input("Hourly Pay Rate: $"))
                if pay < 0: raise ValueError
                break
            except ValueError:
                print("Please enter a valid positive number.")

        safe_name = "".join([c if c.isalnum() else "_" for c in name.lower()])
        filename = f"{safe_name}.json"

        new_job = Job(name, filename, pay)
        new_job.save_shifts() 
        
        self.jobs.append(new_job)
        self.save_user()
        print(f"Job '{name}' added successfully.")

    def view_timesheet(self, job: Job):
        if not job.shifts:
            print("No shifts recorded.")
            return

        table_data = []
        monthly_totals = {}

        # Sort by date
        sorted_shifts = sorted(job.shifts, key=lambda s: s.start_dt)

        for shift in sorted_shifts:
            start_dt = shift.start_dt
            month_key = start_dt.strftime("%Y-%B") 
            
            monthly_totals[month_key] = monthly_totals.get(month_key, 0) + shift.hours

            # Handle display for currently active shifts
            end_display = "ACTIVE"
            if shift.end_time:
                 end_display = str_to_dt(shift.end_time).strftime("%H:%M")

            row = {
                "Date": start_dt.strftime("%Y-%m-%d"),
                "Start": start_dt.strftime("%H:%M"),
                "End": end_display,
                "Hours": f"{shift.hours:.2f}",
                "Notes": shift.notes[:30] + "..." if len(shift.notes) > 30 else shift.notes
            }
            table_data.append(row)

        print(f"\nTimesheet for: {job.name} (${job.pay:.2f}/hr)")
        print(tabulate(table_data, headers="keys", tablefmt="simple"))
        
        print("\n--- Monthly Totals ---")
        for month, hours in monthly_totals.items():
            gross = hours * job.pay
            print(f"{month}: {hours:.2f} hours (${gross:.2f})")
        input("\nPress Enter to continue...")

    def job_menu(self, job: Job):
        while True:
            clear_screen()
            status = "CLOCKED IN" if job.is_clocked_in else "CLOCKED OUT"
            print(f"--- Managing: {job.name} [{status}] ---")
            print("1. Clock In")
            print("2. Clock Out")
            print("3. View Timesheet")
            print("4. Add Manual Shift (Past/Forgot)")
            print("5. Add/Edit Notes to Last Shift")
            print("6. Back to Main Menu")
            
            choice = input("> ").strip()
            
            if choice == '1':
                job.clock_in()
                input("Press Enter...")
            elif choice == '2':
                job.clock_out()
                input("Press Enter...")
            elif choice == '3':
                self.view_timesheet(job)
            elif choice == '4':
                job.add_manual_shift()
                input("Press Enter...")
            elif choice == '5':
                if not job.shifts:
                    print("No shifts available.")
                else:
                    print(f"Current Note: {job.shifts[-1].notes}")
                    job.shifts[-1].notes = input("New Note: ")
                    job.save_shifts()
            elif choice == '6':
                break

    def main_menu(self):
        while True:
            clear_screen()
            print("=========================================")
            print(f"| TimeClock - User: {self.user_name:<19} |")
            print("=========================================")
            
            if not self.jobs:
                print("No jobs found.")
                print("1. Add New Job")
                print("2. Exit")
            else:
                for idx, job in enumerate(self.jobs):
                    status = "*" if job.is_clocked_in else " "
                    print(f"{idx + 1}. [{status}] {job.name}")
                print(f"{len(self.jobs) + 1}. Add New Job")
                print(f"{len(self.jobs) + 2}. Exit")

            choice = input("> ").strip()
            if not choice.isdigit():
                continue
            
            val = int(choice)
            
            if not self.jobs:
                if val == 1: self.add_new_job()
                elif val == 2: sys.exit()
            else:
                if 1 <= val <= len(self.jobs):
                    self.job_menu(self.jobs[val - 1])
                elif val == len(self.jobs) + 1:
                    self.add_new_job()
                elif val == len(self.jobs) + 2:
                    sys.exit()

if __name__ == "__main__":
    try:
        app = TimeClockApp()
        app.main_menu()
    except KeyboardInterrupt:
        print("\nGoodbye!")