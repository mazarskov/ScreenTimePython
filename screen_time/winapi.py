import win32gui
import win32process
import psutil
import time
from db_commands import read_from_db
time_dict = {}


try:
    listo = read_from_db()
    for entry in listo:
        time_dict[entry[0]] = entry[1]
except Exception as e:
    time_dict = {}
    print(e)

def get_focused_window_info():
    try:
            
        # Get the handle of the currently focused window
        hwnd = win32gui.GetForegroundWindow()
    
        # Get the window title
        window_title = win32gui.GetWindowText(hwnd)
    
        # Get the class name of the window
        class_name = win32gui.GetClassName(hwnd)
    
        # Get the process ID of the window
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
    
        # Get the process name using psutil
        try:
            process = psutil.Process(pid)
            process_name = process.name()
        except psutil.NoSuchProcess:
            process_name = None

        SYSTEM_PROCESS_NAMES = [
            "explorer.exe",  # Handles multiple system utilities
            "SearchUI.exe",  # Windows Search
            "SystemSettings.exe",  # Windows Settings
            "ShellExperienceHost.exe",  # Start Menu, etc.
            "dwm.exe",  # Desktop Window Manager
            "sihost.exe",  # Shell Infrastructure Host
            "ctfmon.exe",  # CTF Loader
            "Taskmgr.exe",  # Task Manager
            "LockApp.exe",
            "SearchHost.exe" 
            # Add more process names as needed
]

        # List of known system window titles
        SYSTEM_WINDOW_TITLES = [
            "",  # Many system utilities have empty titles
            "Program Manager",  # Desktop
            "Notification Center",  # Notifications
            "Volume Control",  # Volume Tray
            # Add more titles as needed
]
        if window_title in SYSTEM_WINDOW_TITLES or process_name in SYSTEM_PROCESS_NAMES:
            window_title = "Useless"
            process_name = "Useless"
    
        return {
            "window_title": window_title,
            "class_name": class_name,
            "process_id": pid,
            "process_name": process_name
        }
    except Exception as e:
        print(f"Error retrieving window info: {e}")
        return {
            "window_title": "Unknown",
            "class_name": "Unknown",
            "process_id": -1,
            "process_name": "Unknown"
        }

def format_data(data):
    title = f'{data["window_title"].split(" - ")[-1]}({data["process_name"]})'
    if (title in time_dict):
        time_dict[title] += 1
    else:
        time_dict[title] = 1
    return title


"""
def start_monitoring():
    try:
        while True:
            focused_window_info = get_focused_window_info()
            title = format_data(focused_window_info)
            print(f"Focused Window Info: {title}")
            time.sleep(1)
    except KeyboardInterrupt:
        for key in time_dict:
            print(f'{key}: {time_dict[key]} seconds')
        print("Exiting the program.")
"""