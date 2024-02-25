from tkinter import messagebox, Frame, Label, Button, GROOVE, LEFT, TOP, CENTER, Text, END
import json

class Timer:
    def __init__(self, parent, project_name, project_id, app, notes=None):
        self.parent = parent
        self.app = app
        self.project_name = project_name
        self.project_id = project_id
        self.font = 'Arial 20'
        self.elapsed_time = 0

        self.frame = Frame(parent, bd=2, relief=GROOVE)
        self.frame.pack(expand=True,fill='x', padx=20)

        self.project_label = Label(self.frame, text=f'Project Name: {project_name}\nProject ID: {project_id}', font=self.font)
        self.project_label.pack()

        self.time_label = Label(self.frame, text='00:00:00', font=self.font)
        self.time_label.pack()

        self.notes_box = Text(self.frame, height=3, width=70)
        if notes:
            self.set_notes(notes)
        self.notes_box.pack()

        self.button_frame = Frame(self.frame)
        self.button_frame.pack()

        self.start_pause_button = Button(self.button_frame, text="Pause", command=self.start_pause_timer)
        self.start_pause_button.pack(side=LEFT, padx=10)

        self.remove_button = Button(self.button_frame, text="Remove", command=self.remove_timer)
        self.remove_button.pack(side=LEFT, padx=10)

        self.button_frame.pack(side=TOP, anchor=CENTER)

        self.running, self.paused = False, False
        self.after_id = None

    def get_notes(self):
        return self.notes_box.get("1.0", END)

    def set_notes(self, notes):
        self.notes_box.insert(END, notes)

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
                "elapsed_time": timer.elapsed_time,
                "notes": timer.get_notes()
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