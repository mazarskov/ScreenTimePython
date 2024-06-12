# ScreenTime

## Overview

ScreenTime is a Python application that tracks the time spent on each window and displays it in a graphical user interface (GUI). The tracked data is saved to an SQLite database.


## Requirements

- Python 3.10
- SQLite version 3.42.0 
- The following Python packages:
  - `pywin32`
  - `psutil`
  - `sqlite3` (built-in with Python)
  - `tkinter` (built-in with Python)

## Installation

1. Clone the repository:

   `git clone https://github.com/mazarskov/ScreenTime.git`

2. Install the required Python packages:

    `pip install pywin32 psutil`

## Usage

1. Navigate to the project directory 
    
    `cd ScreenTime`

2. Start the application by running **main.py** located in screen_time.
 
    `python screen_time/main.py` or `python3 screen_time/main.py`

3. The application will start tracking the time spent on each window and display it in the GUI.

4. To exit the application, click the "Exit" button in the GUI or close the window using the X button. The tracked data will be saved to the SQLite database.

## Database Schema
The SQLite database contains a single table window_time with the following schema:

- `id` (INTEGER PRIMARY KEY): Unique identifier for each record.
- `title` (TEXT): The title of the window.
- `time_spent` (INTEGER): The time spent on the window in seconds.
- `date` (TEXT): Date when the record was made. DD-MM-YYYY format.