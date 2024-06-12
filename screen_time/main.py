from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import threading
import time
from logic.winapi import get_focused_window_info, format_data, time_dict, populate_dict
from database.db_commands import add_to_db, read_from_db_date, read_from_db
from logic.current_time import get_current_time
import gettext
import os
from logic.config import get_language, modify_config
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os


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
        for F in (HomePage, OtherPage, SettingsPage, AboutPage, DatabasePage):
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

        other_button = tk.Button(navbar, text=(_("Report")), command=lambda: self.show_frame("OtherPage"))
        other_button.pack(side="left", padx=10, pady=10)

        settings_button = tk.Button(navbar, text=(_("Settings")), command=lambda: self.show_frame("SettingsPage"))
        settings_button.pack(side="left", padx=10, pady=10)

        other_button = tk.Button(navbar, text=(_("Database")), command=lambda: self.show_frame("DatabasePage"))
        other_button.pack(side="left", padx=10, pady=10)

        other_button = tk.Button(navbar, text=(_("About")), command=lambda: self.show_frame("AboutPage"))
        other_button.pack(side="left", padx=10, pady=10)

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

        self.stop_button = tk.Button(self, text=(_("Exit")), command=controller.exit_app)
        self.stop_button.pack(pady=5)

        self.update_text_area()

    def update_text_area(self):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.delete(1.0, tk.END)
        for key in time_dict:
            if key == "Unknown(Unknown)":
                continue
            else:
                self.text_area.insert(tk.END, f'{key}: {time_dict[key]} seconds\n')
        self.text_area.config(state=tk.DISABLED)
        self.text_area.see(tk.END)

class WeeklyCalendar:
    def __init__(self, root):
        self.root = root
        self.current_date = datetime.today().date()

        self.create_widgets()
        self.show_week()

    def create_widgets(self):
        self.calendar_frame = ttk.Frame(self.root)
        self.calendar_frame.pack(padx=10, pady=10)

        self.scrollbar = ttk.Scrollbar(self.calendar_frame, orient="horizontal")
        self.scrollbar.grid(row=1, column=0, columnspan=3, sticky='ew')

        self.calendar_canvas = tk.Canvas(self.calendar_frame, xscrollcommand=self.scrollbar.set)
        self.calendar_canvas.grid(row=0, column=0, columnspan=3, sticky="nsew")

        self.scrollbar.config(command=self.calendar_canvas.xview)

        self.calendar_frame.grid_rowconfigure(0, weight=1)
        self.calendar_frame.grid_columnconfigure(1, weight=1)

        self.prev_week_button = ttk.Button(self.calendar_frame, text="◀", command=self.prev_week)
        self.prev_week_button.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.next_week_button = ttk.Button(self.calendar_frame, text="▶", command=self.next_week)
        self.next_week_button.grid(row=2, column=2, padx=5, pady=5, sticky="e")

        self.week_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.day_labels = []
        self.create_day_labels()

        self.details_frame = ttk.Frame(self.root)
        self.details_frame.pack(padx=10, pady=10, fill="x")
        
        self.details_label = ttk.Label(self.details_frame, text=(_("Click on a date to see details here.")))
        self.details_label.pack(padx=10, pady=10, fill="x")

    def create_day_labels(self):
        for label in self.day_labels:
            label.grid_forget()

        self.day_labels = []
        for i, day in enumerate(self.week_days):
            date = self.current_date - timedelta(days=self.current_date.weekday()) + timedelta(days=i)
            label = ttk.Label(self.calendar_canvas, text=day, borderwidth=1, relief="solid")
            label.grid(row=0, column=i, sticky="nsew")
            label.bind("<Button-1>", lambda event, date=date: self.on_day_click(date))
            self.day_labels.append(label)

        self.calendar_canvas.update_idletasks()
        self.canvas_width = sum(label.winfo_width() for label in self.day_labels)
        self.canvas_height = self.day_labels[0].winfo_height()
        self.calendar_canvas.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))

    def show_week(self):
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        for i, day_label in enumerate(self.day_labels):
            day = start_of_week + timedelta(days=i)
            marked = self.is_marked(day.strftime("%d-%m-%Y"))
            #print(day.strftime("%A\n%d-%m-%Y").split(',')[0].strip() + " a")
            #print(day.strftime("%d-%m-%Y"))
            if marked:
                day_label.config(background="red")
            else:
                day_label.config(background="SystemButtonFace")
            day_label.config(text=day.strftime("%A\n%d-%m-%Y"))

    def is_marked(self, day):
        fin = read_from_db_date(day)
        if fin == []:
            return False
        else:
            return True
    def prev_week(self):
        self.current_date -= timedelta(days=7)
        self.show_week()

    def next_week(self):
        self.current_date += timedelta(days=7)
        self.show_week()

    def on_day_click(self, date):
        print("Clicked on:", date.strftime("%A, %d-%m-%Y"))
        sql_date = (str(date.strftime("%A, %d-%m-%Y")).split(',')[1].strip())
        data = read_from_db_date(sql_date)
        if data == []:
            formatted_data = (_("No data for this day"))
            if hasattr(self, 'plot_canvas'):
                self.plot_canvas.get_tk_widget().destroy()
        else:

            formatted_data = f"Selected date: {sql_date}\nYour screen time during this day:\n"
            for app, time in data:
                formatted_data += f"{app} for {time} seconds\n"
            print(sql_date)
            print(read_from_db_date(sql_date))
            self.create_plot(read_from_db_date(sql_date))
        self.details_label.config(text=formatted_data)

    
    def create_plot(self, data):
        total_seconds = sum(entry[1] for entry in data)

        percentages = [(entry[0], entry[1] / total_seconds * 100) for entry in data]

        labels, percentages = zip(*percentages)
        fig, ax = plt.subplots()
        patches, texts, autotexts = ax.pie(percentages, labels=labels, autopct='%1.1f%%', startangle=140)  

        for text in texts:
            text.set_fontsize(7)  # Adjust font size of labels
        for autotext in autotexts:
            autotext.set_fontsize(7) 

        if hasattr(self, 'plot_canvas'):
            self.plot_canvas.get_tk_widget().destroy()
        self.plot_canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
class OtherPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text=(_("Weekly Calendar View")), font=("Helvetica", 16))
        label.pack(pady=10, padx=10)

        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.pack(pady=10, padx=10)

        self.weekly_calendar = WeeklyCalendar(self.calendar_frame)

class SettingsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="This is the settings page", font=("Helvetica", 16))
        label.pack(pady=10, padx=10)
        button = tk.Button(self, text="Switch to Russian", command=self.change_ru)
        button.pack(pady=15, padx=15)
        button2 = tk.Button(self, text="Switch to English", command=self.change_en)
        button2.pack(pady=15, padx=17)
        label2 = tk.Label(self, text=f'currently selected language: {language}')
        label2.pack(pady=20, padx=20)
        label3 = tk.Label(self, text="NOTE! You have to restart the app to change language. Sorry :(")
        label3.pack(pady=25, padx=25)
        button3 = tk.Button(self, text="Exit", command=controller.exit_app)
        button3.pack(pady=35, padx=35)

    def change_lang(self, lang):
        language = lang
        modify_config(lang)
    
    def change_ru(self):
        self.change_lang("lang=ru")
    
    def change_en(self):
        self.change_lang("lang=en")


class AboutPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="Developed by Maksim Azarskov")
        label2 = tk.Label(self, text="ScreenTime was developed for the Software Development Project course")
        label3 = tk.Label(self, text="Last update: 12.06.2024")
        label4 = tk.Label(self, text="More features coming soon!")
        label.pack(pady=10, padx=10)
        label2.pack(pady=10, padx=10)
        label3.pack(pady=10, padx=10)
        label4.pack(pady=10, padx=10)

class DatabasePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="Info about the local database", font=("Helvetica", 16))
        label.pack(pady=10, padx=10)
        database_filename = "screentime.db"
        database_path = self.find_database_path(database_filename)

        if database_path:
            # Retrieve database file information
            creation_time = datetime.fromtimestamp(os.path.getctime(database_path))
            size_bytes = os.path.getsize(database_path)
            size_kb = size_bytes / 1024

            database_path = os.path.abspath(database_path)
            info_labels = [
                f"Location: {database_path}",
                f"Creation Date: {creation_time}",
                f"Size: {size_kb:.2f} KB"
            ]

            for info in info_labels:
                label = ttk.Label(self, text=info)
                label.pack(pady=5)
            formatted_data = ""
            data = read_from_db()
            for name, seconds, date in data:
                formatted_data += f'{name} for {str(seconds)} seconds on {date}.\n'
            self.details_label = ttk.Label(self, text=formatted_data)
            self.details_label.pack(padx=10, pady=10, fill="x")
        else:
            label = ttk.Label(self, text="Database file not found.")
            label.pack(pady=5)

    def find_database_path(self, filename):
        # Search for the database file in the current directory
        for root, dirs, files in os.walk("."):
            if filename in files:
                return os.path.join(root, filename)
        return None
    
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
