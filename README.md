Here is a professional, updated `README.md` that reflects the new features (manual entry, object-oriented design) and usage instructions.

---

# TimeClock (CLI)

TimeClock is a lightweight, persistent command-line interface (CLI) application for tracking work hours across multiple projects or jobs. It allows freelancers and contractors to manage shifts, calculate hours, and view monthly earnings directly from the terminal.

## Features

* **Multiple Job Support:** Track time for unlimited separate jobs or projects.
* **Real-time Tracking:** Clock in and out with a single keystroke.
* **Manual Entry:** Add past shifts or forgot-to-clock-in sessions manually.
* **Timesheets:** View detailed logs with automatic duration calculation.
* **Financial Summaries:** auto-calculated gross pay grouped by month.
* **Notes:** Attach notes to specific shifts (e.g., "Client meeting," "Bug fixing").
* **Local Persistence:** All data is stored locally in human-readable JSON files.

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/timeclock-cli.git
cd timeclock-cli

```


2. **Install dependencies:**
This project requires the `tabulate` library for formatting timesheets.
```bash
pip install tabulate

```


3. **Run the application:**
```bash
python main.py

```



## Usage

### First Run

On the first launch, the application will ask for your name. This creates the initial `user.json` file.

### Job Menu

Once a job is selected, you can:

1. **Clock In:** Starts a timer for the current job.
2. **Clock Out:** Stops the timer, calculates hours, and saves the shift.
3. **View Timesheet:** Displays a table of all shifts and monthly pay totals.
4. **Add Manual Shift:** Useful if you forgot to track time live.
5. **Add/Edit Notes:** Append context to your most recent shift.

## Data Structure

The application uses a linked JSON structure to keep data organized.

### 1. `user.json` (Main Registry)

Stores the user profile and pointers to job files.

```json
{
  "name": "Jane Doe",
  "jobs": [
    {
      "name": "Web Development",
      "filename": "web_development.json",
      "pay": 45.0
    }
  ]
}

```

### 2. `[job_name].json` (Shift Data)

Stores individual shift records for a specific job.

```json
[
  {
    "start_time": "2023-10-27 09:00:00",
    "end_time": "2023-10-27 17:00:00",
    "hours": 8.0,
    "clocked_in": false,
    "notes": "Frontend API integration"
  }
]

```

## Development

The project is built using Python `dataclasses` for structured data management.

* `main.py`: Contains the `TimeClockApp`, `Job`, and `Shift` classes.
* `user.json`: Created automatically.
