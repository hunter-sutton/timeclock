# Program: main.py
# Author: Hunter Sutton
# Description: Main program for the TimeClock (CLI) application. The TimeClock application 
#              is an implementation of a time clock system for an individual tracking their
#              time spent on various projects.

# user.json Structure:
# {
#     "name": "John Doe",
#     "jobs": [
#         {
#             "name": "Job 1",
#             "filename": "job1.json",
#             "pay": 10.00
#         },
#         {
#             "name": "Job 2",
#             "filename": "job2.json",
#             "pay": 15.00
#         }
#     ]
# }

# job.json Structure:
# {
#     {
#         "start_time": "2020-01-01 00:00:00",
#         "end_time": "2020-01-01 00:00:00",
#         "hours": 0,
#         "clocked_in": false,
#         "notes": "This is a note about this shift."
#     },
#     {
#         "start_time": "2020-01-01 00:00:00",
#         "end_time": "2020-01-01 00",
#         "hours": 0,
#         "clocked_in": false,
#         "notes": "This is a note about this shift."
#     }
# }

# Import the necessary modules
import datetime
import json
import math
from tabulate import tabulate

# Function: title
# Description: Displays the title of the program
def title():
    print("\033c", end="")
    print("=========================================")
    print("|                                       |")
    print("|          TimeClock (CLI)              |")
    print("|                                       |")
    print("=========================================")

# Function: add_job():
# Description: Prompt the user for a job name and pay rate and add the
#              job to the user.json file. A job.json file is also created
#              for the job.
def add_job():
    print("What is the name of the job?")
    job_name = input("> ")

    print("What is the pay rate for this job?")
    pay_rate = input("> ")

    with open("user.json", "r") as user_file:
        user = json.load(user_file)
        job = {
            "name": job_name,
            "filename": job_name.lower().replace(" ", "_") + ".json",
            "pay": pay_rate
        }
        user["jobs"].append(job)

    with open("user.json", "w") as user_file:
        json.dump(user, user_file)

    with open(job["filename"], "w") as job_file:
        json.dump([], job_file)
    
    print("Job added!")

# Function: used_before
# Description: Checks whether the user has used the program before by checking for the existence of the user.json file.
# Returns:
#   - True if the user.json file exists, False otherwise
def used_before():
    try:
        with open("user.json", "r") as user_file:
            return True
    except FileNotFoundError:
        return False
    
# Function: setup
# Description: Runs used_before() to check whether the user has used the program before. If the user has used 
#              the program before, load the user.json file and welcome the user back. If the user has not used the
#              program before, prompt the user for their name and create a new user.json file.
def setup():
    if used_before():
        with open("user.json", "r") as user_file:
            user = json.load(user_file)
            print("Welcome back, " + user["name"] + "!")
    else:
        print("What is your name?")
        name = input("> ")
        user = {
            "name": name,
            "jobs": []
        }
        with open("user.json", "w") as user_file:
            json.dump(user, user_file)
        print("Welcome, " + name + "!")

# Function: add_job
# Description: Prompts the user for a job name and pay rate and adds the job to the user.json file.
#              A job.json file is also created for the job.
def add_job():
    print("What is the name of the job?")
    job_name = input("> ")
    print("What is the pay rate for this job?")
    pay_rate = input("> ")
    with open("user.json", "r") as user_file:
        user = json.load(user_file)
        job = {
            "name": job_name,
            "filename": job_name.lower().replace(" ", "_") + ".json",
            "pay": pay_rate
        }
        user["jobs"].append(job)
    with open("user.json", "w") as user_file:
        json.dump(user, user_file)
    with open(job["filename"], "w") as job_file:
        json.dump([], job_file)
    print("Job added!")

# Function: choose_job
# Description: Prompts the user for a job to interact with. If the user has
#              no jobs, they are prompted to add a job. Let the last option be
#              to add a new job.
# Returns:
#   - the job the user selected
def choose_job():
    with open("user.json", "r") as user_file:
        user = json.load(user_file)
        if len(user["jobs"]) == 0:
            print("You have no jobs. Would you like to add a job?")
            print("1. Yes")
            print("2. No")
            choice = input("> ")
            if choice == "1":
                add_job()
            else:
                print("Why are you here then?")
                exit()
            return choose_job()
        else:
            print("Which job would you like to interact with?")
            for i in range(len(user["jobs"])):
                print(str(i + 1) + ". " + user["jobs"][i]["name"])
            print(str(len(user["jobs"]) + 1) + ". Add a new job")
            choice = int(input("> "))
            if choice == len(user["jobs"]) + 1:
                add_job()
                return choose_job()
            else:
                return user["jobs"][choice - 1]

# Function: new_shift
# Description: Creates a new shift object and prompts the user for notes.
# Parameters:
#   - the job the user selected
#   - job_data: the data from the job.json file
# Returns:
#   - the shift object
def new_shift(job, job_data):
    # make a new shift object
    shift = {
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": "",
        "hours": 0,
        "clocked_in": True,
        "notes": ""
    }

    # add the new shift to the job_data
    job_data.append(shift)
    with open(job["filename"], "w") as job_file:
        json.dump(job_data, job_file)
    print("Clocked in to " + job["name"] + " at " + shift["start_time"])

# Function: clock_out
# Description: Clocks out the user out from the selected job. The user is prompted for notes.
#              If the user has not clocked in, they are prompted to clock in.
# Parameters:
#   - the job the user selected
def clock_out(job):
    with open(job["filename"], "r") as job_file:
        job_data = json.load(job_file)
        if job_data[-1]["clocked_in"]:

            # record the end time and date
            job_data[-1]["end_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # calculate the hours, rounding up to the nearest 30 minutes
            start_time = datetime.datetime.strptime(job_data[-1]["start_time"], "%Y-%m-%d %H:%M:%S")
            end_time = datetime.datetime.strptime(job_data[-1]["end_time"], "%Y-%m-%d %H:%M:%S")
            job_data[-1]["hours"] = math.ceil((end_time - start_time).total_seconds() / 3600)

            # clock out
            job_data[-1]["clocked_in"] = False
            print("Clocked out of " + job["name"] + " at " + job_data[-1]["end_time"])
            print("Would you like to add any notes?")
            print("1. Yes")
            print("2. No")
            selection = input("> ")
            if selection == "1":
                print("Enter your notes:")
                job_data[-1]["notes"] = input("> ")
            with open(job["filename"], "w") as job_file:
                json.dump(job_data, job_file)
        else:
            print("You are not clocked in to " + job["name"])

# Function: clock_in
# Description: Prompts the user for a job to clock into and then clocks the user into that job. If the user is already
#              clocked into a job, they are prompted to clock out of that job first.
# Parameters:
#   - the job the user selected
def clock_in(job):
    # check if the user is already clocked in
    with open(job["filename"], "r") as job_file:
        job_data = json.load(job_file)
        if len(job_data) > 0:
            if job_data[-1]["clocked_in"]:
                print("You are already clocked in to " + job["name"] + ". Would you like to clock out?")
                print("1. Yes")
                print("2. No")
                selection = input("> ")
                if selection == "1":
                    clock_out(job)
                else:
                    print("Have fun working then, bud.")
                    exit()
            else:
                # create a JSON object for the shift to be inserted into the job.json file
                new_shift(job, job_data)
        else:
            new_shift(job, job_data)

# Function: view_timesheet
# Description: Prints the timesheet for the selected job in a formatted table using the tabulate library.
#              The data should be separated at the 25th day of each month. The total number of hours for each
#              month should be printed after each month.
# Parameters:
#   - the job the user selected
def view_timesheet(job):
    with open(job["filename"], "r") as job_file:
        job_data = json.load(job_file)
        if len(job_data) == 0:
            print("You have no shifts for " + job["name"])
        else:
            # sort the job_data by start_time
            job_data = sorted(job_data, key=lambda k: k["start_time"])

            # print the shifts in a formatted table using the tabulate library
            print(tabulate(job_data, headers="keys", tablefmt="grid", showindex="always"))

            # print the total hours for each month
            print("Total Hours:")
            total_hours = 0
            for i in range(len(job_data)):
                total_hours += job_data[i]["hours"]
                if i == len(job_data) - 1:
                    print(str(job_data[i]["start_time"])[:7] + ": " + str(total_hours))
                elif job_data[i]["start_time"][:7] != job_data[i + 1]["start_time"][:7]:
                    print(str(job_data[i]["start_time"])[:7] + ": " + str(total_hours))
                    total_hours = 0

# Function: add_notes
# Description: Prompts the user for a shift to add notes to. The user is then
#              prompted for the notes.
# Parameters:
#   - the job the user selected
def add_notes(job):
    with open(job["filename"], "r") as job_file:
        job_data = json.load(job_file)
        if len(job_data) == 0:
            print("You have no shifts for " + job["name"])
        else:
            # sort the job_data by start_time
            job_data = sorted(job_data, key=lambda k: k["start_time"])

            # print the shifts in a formatted table using the tabulate library
            print(tabulate(job_data, headers="keys", tablefmt="grid", showindex="always"))

            # prompt the user for a shift to add notes to
            print("Which shift would you like to add notes to?")
            selection = input("> ")
            if selection.isdigit():
                if int(selection) < len(job_data):
                    print("Enter your notes:")
                    job_data[int(selection)]["notes"] = input("> ")
                    with open(job["filename"], "w") as job_file:
                        json.dump(job_data, job_file)
                else:
                    print("Invalid selection.")
            else:
                print("Invalid selection.")

# Function: intereact_job
# Description: Prompts the user to choose an action to perform on the job.
# Parameters:
#   - job: the job to interact with
def job_menu(job):
    print("What would you like to do with " + job["name"] + "?")
    print("1. Clock in")
    print("2. Clock out")
    print("3. Add notes")
    print("4. View timesheet")
    print("5. Go back")
    selection = input("> ")
    if selection == "1":
        clock_in(job)
    elif selection == "2":
        clock_out(job)
    elif selection == "3":
        add_notes(job)
    elif selection == "4":
        view_timesheet(job)
    elif selection == "5":
        pass
    else:
        print("Invalid selection. Please try again.")
        job_menu(job)

if __name__ == "__main__":
    title()
    setup()
    while True:
        job = choose_job()
        job_menu(job)