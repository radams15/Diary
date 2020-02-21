import time
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from os import path
from datetime import datetime


import pygubu

from storage import Storage
from record import Record
from encryption import Crypt

state_invert = {"normal":"disabled", "disabled":"normal"}

SAVE_FILE = "diary.data"
BACKUP_NUM = 3
BACKUP_DIR = "diary_backup/"

REVERSE_ORDER = False

password = None

class MainApp:
    def __init__(self, master):
        self.builder = builder = pygubu.Builder()
        builder.add_from_file('main.ui')
        self.mainwindow = builder.get_object('mainwindow', master)

        builder.connect_callbacks(self)

    def new_clicked(self):
        builder3 = pygubu.Builder()
        builder3.add_from_file('new_window.ui')
        top3 = tk.Toplevel(self.mainwindow)
        new_window = builder3.get_object('mainwindow', top3)

        time_entry: ttk.Entry = builder3.get_object("time_entry", top3)
        title_entry: ttk.Entry = builder3.get_object("title_entry", top3)
        body: tk.Text = builder3.get_object("body", top3)
        now_button: ttk.Button = builder3.get_object("now_button", top3)
        lock_button: ttk.Button = builder3.get_object("lock_button", top3)
        save_button: ttk.Button = builder3.get_object("save_button", top3)

        def time_now():
            time_entry.delete(0, "end")
            t = time.time()
            t_dt = datetime.fromtimestamp(t)
            t_str = t_dt.strftime("%A %B %d %Y %X")
            time_entry.insert(0, t_str)

        now_button["command"] = time_now
        lock_button.grid_remove()
        body.configure(state="normal")

        def save():
            time_data, title, body_text = time_entry.get(), title_entry.get(), body.get("1.0", tk.END)
            storage.save_record(Record(time_data, title, body_text))
            top3.destroy()

        save_button["command"] = save


    def read_clicked(self):
        builder2 = pygubu.Builder()
        builder2.add_from_file('read_window.ui')
        top3 = tk.Toplevel(self.mainwindow)
        read_window = builder2.get_object('mainwindow', top3)

        tree: ttk.Treeview = builder2.get_object("entries", top3)
        tree["columns"] = ("date", "title", "time")
        tree['show'] = 'headings'

        exclusionlist = ["time"]
        displaycolumns = []
        for col in tree["columns"]:
            if not str(col) in exclusionlist:
                displaycolumns.append(col)
        tree["displaycolumns"] = displaycolumns

        tree.column("date", stretch=0,  anchor=tk.N)
        tree.column("title", stretch=0,  anchor=tk.N)
        tree.heading("date", text="Date")
        tree.heading("title", text="Title")
        tree.heading("time")
        tree.bind("<Double-1>", lambda event, arg=tree: self.on_doubleclick(event, arg))
        self.tree = tree
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        records = sorted(storage.read(), key=lambda x: x.date, reverse=not REVERSE_ORDER)
        for i, record in enumerate(records):
            self.tree.insert("", "end", i, value=(record.format_date(), record.title, record.date.timestamp()))

    def on_doubleclick(self, event, tree: ttk.Treeview):
        item_id = tree.selection()[0]
        item = tree.item(item_id)
        epoch_date = float(item["values"][2])

        record = storage.read_date(epoch_date)

        builder3 = pygubu.Builder()
        builder3.add_from_file('new_window.ui')
        top3 = tk.Toplevel(self.mainwindow)
        edit_window: ttk.Frame = builder3.get_object('mainwindow', top3)
        callbacks = {}
        builder3.connect_callbacks(callbacks)

        time_entry: ttk.Entry = builder3.get_object("time_entry", top3)
        title_entry: ttk.Entry = builder3.get_object("title_entry", top3)
        body: tk.Text = builder3.get_object("body", top3)
        now_button: ttk.Button = builder3.get_object("now_button", top3)
        lock_button: ttk.Button = builder3.get_object("lock_button", top3)
        save_button: ttk.Button = builder3.get_object("save_button", top3)
        delete_button: ttk.Button = builder3.get_object("delete_button", top3)

        def time_now():
            time_entry.delete(0, "end")
            t = time.time()
            t_dt = datetime.fromtimestamp(t)
            t_str = t_dt.strftime("%A %B %d %Y %X")
            time_entry.insert(0, t_str)
        now_button["command"] = time_now

        def lock():
            time_entry.configure(state=state_invert[str(time_entry.cget("state"))])
            title_entry.configure(state=state_invert[str(title_entry.cget("state"))])
            body.configure(state=state_invert[str(body.cget("state"))])

        def delete_entry():
            should_delete = messagebox.askquestion("Really Delete?")
            if should_delete == "yes":
                storage.delete_record(record)
                top3.destroy()
                self.refresh()

        delete_button["command"] = delete_entry
        lock_button["command"] = lock

        body.configure(state="normal")
        body.insert("end", record.body)
        body.configure(state="disabled")
        title_entry.insert("end", record.title)
        time_entry.insert("end", record.format_date())
        time_entry.configure(state="disabled")
        title_entry.configure(state="disabled")

        def save():
            time_data, title, body_text = time_entry.get(), title_entry.get(), body.get("1.0", tk.END)
            body_text = body_text.rstrip()
            storage.update_record(record, Record(time_data, title, body_text))
            top3.destroy()
            self.refresh()

        save_button["command"] = save


class PasswordApp:
    def __init__(self, master):
        self.builder = builder = pygubu.Builder()
        builder.add_from_file('password_window.ui')
        self.mainwindow = builder.get_object('mainwindow', master)

        builder.connect_callbacks(self)
        master.bind("<Return>", self.ok)

        self.pw_box: ttk.Entry = self.builder.get_object("password_box")
        self.builder.get_object("ok_button")["command"] = self.ok

        self.pw_box.focus_set()

        self.master = master

    def ok(self, event=None):
        global password
        password = self.pw_box.get()
        if not password:
            return
        self.master.destroy()


if __name__ == '__main__':

    ENCRYPT = True

    root = tk.Tk()
    password_app = PasswordApp(root)
    root.mainloop()
    if not password:
        exit()

    crypt = Crypt(password)

    storage = Storage(SAVE_FILE, crypt, BACKUP_DIR, save_crypt=ENCRYPT)

    root = tk.Tk()
    main_app = MainApp(root)
    root.mainloop()

    storage.backup(BACKUP_NUM)
    storage.save()
