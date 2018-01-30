import tkinter as tk
from tkinter import ttk
from .betterdialog import BetterDialog

class DateDialog(BetterDialog):

    def content(self, master):
        self.day = tk.StringVar()
        self.month = tk.StringVar()
        self.year = tk.StringVar()

        day_frame = tk.Frame(master)
        month_frame = tk.Frame(master)
        year_frame = tk.Frame(master)

        ttk.Label(day_frame, text="Day: ").pack(side=tk.LEFT)
        tk.Spinbox(
            day_frame,
            from_=1,
            to=31,
            textvariable=self.day
        ).pack(side=tk.RIGHT)

        ttk.Label(month_frame, text="Month: ").pack(side=tk.LEFT)
        tk.Spinbox(
            month_frame,
            from_=1,
            to=12,
            textvariable=self.month
        ).pack(side=tk.RIGHT)

        ttk.Label(year_frame, text="Year: ").pack(side=tk.LEFT)
        tk.Spinbox(
            year_frame,
            from_=2016,
            to=2096,
            textvariable=self.year
        ).pack(side=tk.RIGHT)

        day_frame.pack(side=tk.TOP)
        month_frame.pack(side=tk.TOP)
        year_frame.pack(side=tk.TOP)

    def next_day(self, event=None):
        long_months = [1, 3, 5, 7, 8, 10, 12]
        february = 2

        day = int(self.day.get()) + 1
        month = int(self.month.get())

        if month in long_months:
            if day > 31:
                day = 1
                self.next_month()
        elif month is february:
            if day > 28:
                day = 1
                self.next_month()
        else:
            if day > 30:
                day = 1
                self.next_month()

        self.day.set(str(day))
        self.update_idletasks()

    def next_month(self):
        month = int(self.month.get()) + 1

        if month > 12:
            month = 1
            self.year.set(str(int(self.year.get())+1))

        self.month.set(str(month))


    def execute(self):
        day = self.day.get()
        if len(day) < 2:
            day = "0" + day

        month = self.month.get()
        if len(month) < 2:
            month = "0" + month

        self.datestamp = ".".join([day, month, self.year.get()])


    def buttons(self, master):
        '''Add a standard button box.

        Override if you do not want the standard buttons
        '''

        box = tk.Frame(master)

        ttk.Button(
            box,
            text="Next",
            width=10,
            command=self.next_day
        ).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(
            box,
            text="OK",
            width=10,
            command=self.ok,
            default=tk.ACTIVE
        ).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(
            box,
            text="Cancel",
            width=10,
            command=self.cancel
        ).pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("n", self.next_day)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()
