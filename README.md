# ScreenTime

## Requirements

- Python 3.10
- The following Python packages:
  - `tkinter`
  - `pywin32`
  - `psutil`
  - `sqlite3` (built-in with Python)

## Installation

1. Clone the repository:

   `git clone https://github.com/mazarskov/ScreenTime.git`

2. Install the required Python packages:

    `pip install pywin32 psutil`

## Usage

1. Start the application by running **gui.py** located in screen_time
 
    `python gui.py` or `python3 gui.py`

2. The application will start tracking the time spent on each window and display it in the GUI.

3. To exit the application, click the "Exit" button in the GUI or close the window using the X button. The tracked data will be saved to the SQLite database.

## Database Schema
The SQLite database contains a single table window_time with the following schema:

id (INTEGER PRIMARY KEY): Unique identifier for each record.
title (TEXT): The title of the window.
time_spent (INTEGER): The time spent on the window in seconds.