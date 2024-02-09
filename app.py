import tkinter as tk
from tkinter import messagebox
import json
import pandas as pd
import os

class Timer:
    def __init__(self, parent, project_name, project_id):
        self.parent = parent
        self.project_name = project_name
        self.project_id = project_id
        self.font = 'Arial 20'

        self.frame = tk.Frame(parent, bd=2, relief=tk.GROOVE)
        self.frame.pack(expand=True,fill='x', padx=20)

        self.project_label = tk.Label(self.frame, text=f'Project Name: {project_name}\nProject ID: {project_id}', font=self.font)
        self.project_label.pack()

        self.time_label = tk.Label(self.frame, text='00:00', font=self.font)
        self.time_label.pack()

        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack()

        self.start_pause_button = tk.Button(self.button_frame, text="Pause", command=self.start_pause_timer)
        self.start_pause_button.pack(side=tk.LEFT, padx=10)

        self.remove_button = tk.Button(self.button_frame, text="Remove", command=self.remove_timer)
        self.remove_button.pack(side=tk.LEFT, padx=10)

        self.button_frame.pack(side=tk.TOP, anchor=tk.CENTER)

        self.running, self.paused = False, False
        self.after_id = None

    def start_pause_timer(self):
        if not self.running:
            self.start()
        else:
            if not self.paused:
                self.pause_updates()
                self.start_pause_button.config(text="Resume")
            else:
                self.resume_updates()
                self.start_pause_button.config(text="Pause")

    def start(self):
        self.elapsed_time = 0 
        self._display_time()
        self.after_id = self.frame.after(1000, self._update)
        self.running, self.paused = True, False

    def _update(self):
        if self.running and not self.paused:
            self.elapsed_time += 1
            self._display_time()

        if self.running:  # Keep update process going.
            self.after_id = self.frame.after(1000, self._update)

    def _display_time(self):
        mins, secs = divmod(self.elapsed_time, 60)
        self.time_label.config(text='%02d:%02d' % (mins, secs))

    def pause_updates(self):
        if self.running:
            self.paused = True

    def resume_updates(self):
        if self.paused:
            self.paused = False

    def remove_timer(self):
        confirm_remove = messagebox.askyesno("Confirmation", "Are you sure you want to remove this timer?")
        if confirm_remove:
            self.frame.destroy()
            self.app.remove_timer(self)
            self.frame.destroy()

    def save_to_json(self, end_time, time_taken):
        data = {
            "project_name": self.project_name,
            "project_id": self.project_id,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "time_taken": str(time_taken)
        }
        with open('timers.json', 'a') as file:
            json.dump(data, file)
            file.write('\n')

class TimerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Timer App")
        self.master.geometry("800x600")  # Set the size of the main window

        self.timers = []

        self.add_project_button = tk.Button(master, text="Add New Project", command=self.open_add_project_popup)
        self.add_project_button.pack(pady=5)

        self.export_summary_button = tk.Button(master, text="Export Summary", command=self.export_summary)
        self.export_summary_button.pack(pady=5)

        self.project_popup = None
        self.create_project_button = None

    def open_add_project_popup(self):
        self.project_popup = tk.Toplevel(self.master)
        self.project_popup.title("Add New Project")
        self.project_popup.geometry("400x160")  # Set the size of the popup window

        project_name_label = tk.Label(self.project_popup, text="Project Name:")
        project_name_label.pack()
        self.project_name_entry = tk.Entry(self.project_popup)
        self.project_name_entry.pack(fill='x', padx=20)

        project_id_label = tk.Label(self.project_popup, text="Project ID:")
        project_id_label.pack()
        self.project_id_entry = tk.Entry(self.project_popup)
        self.project_id_entry.pack(fill='x', padx=20)

        self.create_project_button = tk.Button(self.project_popup, text="Create", command=self.create_project)
        self.create_project_button.pack(pady=10)

        self.project_popup.bind("<Return>", lambda event: self.create_project())

    def create_project(self):
        project_name = self.project_name_entry.get()
        project_id = self.project_id_entry.get()
        self.create_timer_tile(project_name, project_id)
        self.project_popup.destroy()

    def create_timer_tile(self, project_name, project_id):
        timer = Timer(self.master, project_name, project_id)
        timer.start()
        self.timers.append(timer)

    def return_timers_are_running(self):
        return any([timer.running for timer in self.timers])

    def export_summary(self):
        data = []
        for timer in self.timers:
            total_time = timer.elapsed_time / 3600
            data.append({
                "Project ID": timer.project_id,
                "Project Name": timer.project_name,
                "Total Hours": total_time # Convert to hours
            })

        df = pd.DataFrame(data)
        df["Total Hours"] = df["Total Hours"].apply(lambda x: round(x, 2))
        excel_path = "summary.xlsx"
        df.to_excel(excel_path, index=False)
        os.system(f'start excel "{excel_path}"')

def main():
    root = tk.Tk()
    app = TimerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
