import win32gui
import win32process
import psutil
import time

time_dict = {}
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

        if process_name == "explorer.exe" and window_title == "":
            window_title = "Desktop"

        if window_title == "Program Manager" and process_name == "explorer.exe":
            window_title = "Desktop"
    
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