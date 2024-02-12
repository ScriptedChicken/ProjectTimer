import tkinter as tk
from tkinter import messagebox, ttk, StringVar
import json
import pandas as pd
import os

class Timer:
    def __init__(self, parent, project_name, project_id, app):
        self.parent = parent
        self.app = app
        self.project_name = project_name
        self.project_id = project_id
        self.font = 'Arial 20'
        self.elapsed_time = 0

        self.frame = tk.Frame(parent, bd=2, relief=tk.GROOVE)
        self.frame.pack(expand=True,fill='x', padx=20)

        self.project_label = tk.Label(self.frame, text=f'Project Name: {project_name}\nProject ID: {project_id}', font=self.font)
        self.project_label.pack()

        self.time_label = tk.Label(self.frame, text='00:00:00', font=self.font)
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
                self.app.pause_all_timers_except(self)
                self.resume_updates()
                self.start_pause_button.config(text="Pause")

    def start(self):
        self.app.pause_all_timers_except(self)
        self._display_time()
        self.after_id = self.frame.after(1000, self._update)
        self.running, self.paused = True, False

    def _update(self):
        if self.running and not self.paused:
            self.elapsed_time += 1
            self._display_time()
            self.save_to_backup()

        if self.running:  # Keep update process going.
            self.after_id = self.frame.after(1000, self._update)

    def save_to_backup(self):
        backup_data = {}
        for timer in self.app.timers:
            backup_data[timer.project_id] = {
                "project_name": timer.project_name,
                "elapsed_time": timer.elapsed_time
            }
        with open('timer_backup.json', 'w') as file:
            json.dump(backup_data, file)

    def _display_time(self):
        hours, remainder = divmod(self.elapsed_time, 3600)  # 3600 seconds in an hour
        mins, secs = divmod(remainder, 60)
        self.time_label.config(text='%02d:%02d:%02d' % (hours, mins, secs))

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
            for i, timer in enumerate(self.app.timers):
                if timer == self:
                    self.app.timers.pop(i)
                    self.save_to_backup()
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

        self.check_and_load_backup_data()

    def check_and_load_backup_data(self):
        if os.path.exists('timer_backup.json'):
            with open('timer_backup.json', 'r') as file:
                backup_data = json.load(file)
                if backup_data:
                    confirm_reload = messagebox.askyesno("Previous Timers Detected",
                                                          "Previous timer data detected. Do you want to reload them?")
                    if confirm_reload:
                        for project_id, timer_data in backup_data.items():
                            self.create_timer_from_backup(project_id, timer_data)
    
    def create_timer_from_backup(self, project_id, timer_data):
        project_name = timer_data["project_name"]
        timer = Timer(self.master, project_name, project_id, self)
        timer.elapsed_time = timer_data["elapsed_time"]
        timer._display_time()  # Update the displayed time
        timer.start()  # Start the timer
        self.timers.append(timer)

    def open_add_project_popup(self):
        self.project_popup = tk.Toplevel(self.master)
        self.project_popup.title("Add New Project")
        self.project_popup.geometry("400x160")  # Set the size of the popup window

        self.existing_name_id_pairs = self.return_existing_name_id_pairs()

        existing_projects_label = tk.Label(self.project_popup, text="Select from existing projects:")
        existing_projects_label.pack()
        textvariable = StringVar()
        self.existing_projects_combo = ttk.Combobox(self.project_popup, values=list(self.existing_name_id_pairs.keys()), textvariable=textvariable)
        self.existing_projects_combo.pack()
        self.existing_projects_combo.bind('<<ComboboxSelected>>', lambda event: self.update_popup_entries())

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

    def update_popup_entries(self):
        try:
            project_name = self.existing_projects_combo.get()
            project_id = self.existing_name_id_pairs[project_name]
            self.fill_entry(self.project_name_entry, project_name)
            self.fill_entry(self.project_id_entry, project_id)
        except:
            print(f"Could not find '{project_name}' in config")
        
        

    @staticmethod
    def fill_entry(entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, value)

    def return_existing_name_id_pairs(self):
        try:
            with open("config.json", "r") as file:
                existing_name_id_pairs = json.load(file)
        except FileNotFoundError:
            existing_name_id_pairs = {}
            print("FIle not found")
        return existing_name_id_pairs
    
    def write_config(self, project_name, project_id):
        self.existing_name_id_pairs[project_name] = project_id
        with open("config.json", "w") as file:
            json.dump(self.existing_name_id_pairs, file)

    def create_project(self):
        project_name = self.project_name_entry.get()
        project_id = self.project_id_entry.get()
        self.write_config(project_name, project_id)
        self.create_timer_tile(project_name, project_id)
        self.project_popup.destroy()

    def create_timer_tile(self, project_name, project_id):
        timer = Timer(self.master, project_name, project_id, self)
        timer.start()
        self.timers.append(timer)

    def return_timers_are_running(self):
        return any([timer.running for timer in self.timers])
    
    def pause_all_timers_except(self, active_timer):
        for timer in self.timers:
            if timer != active_timer:
                timer.pause_updates()
                timer.start_pause_button.config(text="Resume")

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
