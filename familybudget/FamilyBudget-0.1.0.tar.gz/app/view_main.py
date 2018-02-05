import tkinter as tk


class MainWindow(tk.Frame):
    def __init__(self, vc, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.pack()

        self.vc = vc
        self.make_widgets()

    def make_widgets(self):
        tk.Button(self, text='Incomes', command=self.vc.open_incomes).pack(
            fill=tk.X, pady=5)
        tk.Button(self, text='Expenses', command=self.vc.open_expenses).pack(
            fill=tk.X, pady=5)
        tk.Button(self, text='Archive', command=self.vc.open_archive).pack(
            fill=tk.X, pady=5)
