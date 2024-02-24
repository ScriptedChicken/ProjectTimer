from tkinter import messagebox, StringVar, Button, Toplevel, Label, Entry, Tk, END
from tkinter.ttk import Combobox
import json
import pandas as pd
import os
from timer import Timer

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Timer App")
        self.master.geometry("800x600")  # Set the size of the main window

        self.timers = []

        self.add_project_button = Button(master, text="Add New Project", command=self.open_add_project_popup)
        self.add_project_button.pack(pady=5)

        self.export_summary_button = Button(master, text="Export Summary", command=self.export_summary)
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
        self.project_popup = Toplevel(self.master)
        self.project_popup.title("Add New Project")
        self.project_popup.geometry("400x160")  # Set the size of the popup window

        self.existing_name_id_pairs = self.return_existing_name_id_pairs()

        existing_projects_label = Label(self.project_popup, text="Select from existing projects:")
        existing_projects_label.pack()
        textvariable = StringVar()
        self.existing_projects_combo = Combobox(self.project_popup, values=list(self.existing_name_id_pairs.keys()), textvariable=textvariable)
        self.existing_projects_combo.pack()
        self.existing_projects_combo.bind('<<ComboboxSelected>>', lambda event: self.update_popup_entries())

        project_name_label = Label(self.project_popup, text="Project Name:")
        project_name_label.pack()
        self.project_name_entry = Entry(self.project_popup)
        self.project_name_entry.pack(fill='x', padx=20)

        project_id_label = Label(self.project_popup, text="Project ID:")
        project_id_label.pack()
        self.project_id_entry = Entry(self.project_popup)
        self.project_id_entry.pack(fill='x', padx=20)

        self.create_project_button = Button(self.project_popup, text="Create", command=self.create_project)
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
        entry.delete(0, END)
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
    root = Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
