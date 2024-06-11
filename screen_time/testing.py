from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import threading
import time
from winapi import get_focused_window_info, format_data, time_dict, populate_dict
from db_commands import add_to_db, read_from_db_date
from current_time import get_current_time
import gettext
import os
from config import get_language


localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')
gettext.bindtextdomain('myapp', localedir)
gettext.textdomain('myapp')
_ = gettext.gettext
language = get_language()
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

        home_button = tk.Button(navbar, text=(_("Home")), command=lambda: self.show_frame("HomePage"))
        home_button.pack(side="left", padx=10, pady=10)

        other_button = tk.Button(navbar, text=(_("Other")), command=lambda: self.show_frame("OtherPage"))
        other_button.pack(side="left", padx=10, pady=10)

        settings_button = tk.Button(navbar, text=(_("Settings")), command=lambda: self.show_frame("SettingsPage"))
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

        self.start_button = tk.Button(self, text=(_("Start")), command=controller.start_monitoring, state=tk.DISABLED)
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

class WeeklyCalendarApp:
    def __init__(self, root):
        self.root = root
        self.current_date = datetime.today().date()

        self.create_widgets()
        self.show_week()

    def create_widgets(self):
        self.calendar_frame = ttk.Frame(self.root)
        self.calendar_frame.pack(padx=10, pady=10)

        self.scrollbar = ttk.Scrollbar(self.calendar_frame, orient="horizontal")
        self.scrollbar.grid(row=1, column=0, sticky="ew")

        self.calendar_canvas = tk.Canvas(self.calendar_frame, xscrollcommand=self.scrollbar.set)
        self.calendar_canvas.grid(row=0, column=0, sticky="nsew")

        self.scrollbar.config(command=self.calendar_canvas.xview)

        self.calendar_frame.grid_rowconfigure(0, weight=1)
        self.calendar_frame.grid_columnconfigure(0, weight=1)

        self.prev_week_button = ttk.Button(self.calendar_frame, text="◀", command=self.prev_week)
        self.prev_week_button.grid(row=2, column=0, padx=5, pady=5)

        self.next_week_button = ttk.Button(self.calendar_frame, text="▶", command=self.next_week)
        self.next_week_button.grid(row=2, column=1, padx=5, pady=5)

        self.week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        self.day_labels = []
        for i, day in enumerate(self.week_days):
            label = ttk.Label(self.calendar_canvas, text=day, borderwidth=1, relief="solid")
            label.grid(row=0, column=i, sticky="nsew")
            label.bind("<Button-1>", lambda event, day=self.current_date - timedelta(days=self.current_date.weekday()) + timedelta(days=i): self.on_day_click(day))
            self.day_labels.append(label)

        self.calendar_canvas.update_idletasks()
        self.canvas_width = sum(label.winfo_width() for label in self.day_labels)
        self.canvas_height = self.day_labels[0].winfo_height()
        self.calendar_canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))

    def show_week(self):
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        for i, day_label in enumerate(self.day_labels):
            day = start_of_week + timedelta(days=i)
            day_label.config(text=day.strftime("%A\n%d-%m-%Y"))

    def prev_week(self):
        self.current_date -= timedelta(days=7)
        self.show_week()

    def next_week(self):
        self.current_date += timedelta(days=7)
        self.show_week()

    def on_day_click(self, date):
        print("Clicked on:", date.strftime("%A, %d-%m-%Y"))
        sql_date = (str(date.strftime("%A, %d-%m-%Y")).split(',')[1].strip())
        print(sql_date)
        print(read_from_db_date(sql_date))

class OtherPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="Weekly Calendar View")
        label.pack(pady=10, padx=10)

        # Create a frame to contain the weekly calendar
        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.pack(pady=10, padx=10)

        # Create the weekly calendar app instance
        self.weekly_calendar = WeeklyCalendarApp(self.calendar_frame)

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="This is the settings page")
        label.pack(pady=10, padx=10)

def set_language(lang):
    try:
        lang_translation = gettext.translation('myapp', '.\locales', languages=[lang], fallback=True)
    except FileNotFoundError:
        print(f"Translation files for '{lang}' not found. Falling back to default language.")
        lang_translation = gettext.translation('myapp', '.\locales', languages=['en'], fallback=True)
    lang_translation.install()
    global _
    _ = lang_translation.gettext

if __name__ == "__main__":
    set_language(language)
    print(language)
    app = ScreenTimeApp()
    app.mainloop()
