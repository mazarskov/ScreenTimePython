# gui.py
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
from winapi import get_focused_window_info, format_data, time_dict
from db_commands import add_to_db

class ScreenTimeApp(tk.Tk):
    def __init__(self, root):
        self.root = root
        self.root.title("ScreenTime")
        self.root.geometry("600x500")
        self.root.resizable(False, False)  # Disable resizing

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (HomePage,):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

        
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
        self.text_area.pack(padx=10, pady=10)

        self.start_button = tk.Button(root, text="Start", command=self.start_monitoring, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Exit", command=self.exit_app)
        self.stop_button.pack(pady=5)

        self.is_monitoring = False
        self.monitoring_thread = None

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

        self.start_monitoring()  # Start tracking as soon as the app opens

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
        add_to_db(time_dict)
        self.stop_monitoring()
        self.root.quit()

    def monitor(self):
        while self.is_monitoring:
            focused_window_info = get_focused_window_info()
            format_data(focused_window_info)
            self.update_text_area()
            time.sleep(1)

    def update_text_area(self):
        self.text_area.delete(1.0, tk.END)  # Clear the text area
        for key in time_dict:
            self.text_area.insert(tk.END, f'{key}: {time_dict[key]} seconds\n')
        self.text_area.see(tk.END)  # Scroll to the end of the text area

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=20)
        self.text_area.pack(padx=10, pady=10)

        self.start_button = tk.Button(root, text="Start", command=self.start_monitoring, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="Exit", command=self.exit_app)
        self.stop_button.pack(pady=5)

        self.is_monitoring = False
        self.monitoring_thread = None

        #self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

        self.start_monitoring()  # Start tracking as soon as the app opens

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
        add_to_db(time_dict)
        self.stop_monitoring()
        self.root.quit()

    def monitor(self):
        while self.is_monitoring:
            focused_window_info = get_focused_window_info()
            format_data(focused_window_info)
            self.update_text_area()
            time.sleep(1)

    def update_text_area(self):
        self.text_area.delete(1.0, tk.END)  # Clear the text area
        for key in time_dict:
            self.text_area.insert(tk.END, f'{key}: {time_dict[key]} seconds\n')
        self.text_area.see(tk.END)  # Scroll to the end of the text area


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTimeApp(root)
    root.mainloop()
