from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
from winapi import get_focused_window_info, format_data, time_dict, populate_dict
from db_commands import add_to_db
from current_time import get_current_time

class ScreenTimeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ScreenTime")
        self.geometry("600x500")
        self.resizable(False, False)  # Disable resizing

        self.is_monitoring = False
        self.monitoring_thread = None

        self.create_navbar()

        # Create the container for all the frames
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create the navigation bar
        

        self.frames = {}
        for F in (HomePage, OtherPage, SettingsPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

        self.last_date = get_current_time()
        self.protocol("WM_DELETE_WINDOW", self.exit_app)

        # Start monitoring as soon as the app opens
        self.start_monitoring()

    def create_navbar(self):
        navbar = tk.Frame(self, bg="lightgrey")
        navbar.pack(side="top", fill="x")

        home_button = tk.Button(navbar, text="Home", command=lambda: self.show_frame("HomePage"))
        home_button.pack(side="left", padx=10, pady=10)

        other_button = tk.Button(navbar, text="Other", command=lambda: self.show_frame("OtherPage"))
        other_button.pack(side="left", padx=10, pady=10)

        settings_button = tk.Button(navbar, text="Settings", command=lambda: self.show_frame("SettingsPage"))
        settings_button.pack(side="left", padx=10, pady=10)

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def start_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self.monitor)
            self.monitoring_thread.start()

    def stop_monitoring(self):
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitoring_thread is not None:
                self.monitoring_thread.join()

    def exit_app(self):
        add_to_db(time_dict, get_current_time())
        self.stop_monitoring()
        self.quit()

    def monitor(self):
        while self.is_monitoring:
            current_date = get_current_time()
            if current_date != self.last_date:
                add_to_db(time_dict, self.last_date)
                time_dict.clear()
                populate_dict(time_dict)
                self.last_date = current_date
            focused_window_info = get_focused_window_info()
            format_data(focused_window_info)
            self.update_text_area()
            time.sleep(1)

    def update_text_area(self):
        self.frames["HomePage"].update_text_area()
        self.after(1000, self.update_text_area)  # Schedule the update_text_area to be called every second

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=50, height=20)
        self.text_area.pack(padx=10, pady=10)
        self.text_area.config(state=tk.DISABLED) 

        self.start_button = tk.Button(self, text="Start", command=controller.start_monitoring, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self, text="Exit", command=controller.exit_app)
        self.stop_button.pack(pady=5)

        self.update_text_area()

    def update_text_area(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)  # Clear the text area
        for key in time_dict:
            if key == "Unknown(Unknown)":
                continue
            else:
                self.text_area.insert(tk.END, f'{key}: {time_dict[key]} seconds\n')
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)  # Scroll to the end of the text area

class OtherPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="This is the other page")
        label.pack(pady=10, padx=10)

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="This is the settings page")
        label.pack(pady=10, padx=10)

if __name__ == "__main__":
    app = ScreenTimeApp()
    app.mainloop()
