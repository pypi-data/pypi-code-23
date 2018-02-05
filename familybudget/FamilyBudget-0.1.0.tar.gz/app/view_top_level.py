import tkinter as tk
import tkinter.ttk as ttk
import locale


class TopLevelBasic(tk.Toplevel):
    def __init__(self, vc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vc = vc
        self.configure_win()

        self.labels_text = ('Date', 'Sum', 'Comment')
        self.win_title = None

        self.date_content = tk.StringVar()
        self.date_entry = tk.Entry(self, textvariable=self.date_content)
        self.date_entry.grid(row=3, column=0)

        self.sum_content = tk.DoubleVar()
        tk.Entry(self, textvariable=self.sum_content).grid(row=3, column=1)

        self.comment_content = tk.StringVar()
        self.total_content = tk.IntVar()

        self.place_widgets()

    def configure_win(self):
        self.title(self.win_title)
        self.focus()
        self.grab_set()
        self.resizable(width=False, height=False)
        self.protocol('WM_DELETE_WINDOW', self.vc.on_closing)
        self.vc.center_main_window(self, width=517, height=135)

    def place_widgets(self):
        col_num = 0

        tk.Entry(self, textvariable=self.comment_content).grid(row=3,
                                                               column=2)
        for t in self.labels_text:
            tk.Label(self, text=t).grid(row=2, column=col_num)
            col_num += 1

        tk.Label(self, text='Total').grid(row=0, column=1)
        tk.Label(self, textvariable=self.total_content).grid(row=1, column=1)

    def set_total_amount(self, amount):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        money = locale.currency(amount)
        self.total_content.set(money)


class TopLevelAddingAmount(TopLevelBasic):
    def __init__(self, *args, **kwargs):
        self.win_title = 'Incomes'

        super().__init__(*args, **kwargs)

        tk.Button(self, text='+', command=self.vc.add_new_record).grid(
            row=4, column=1)

    @property
    def amount(self):
        return self.sum_content.get()


class TopLevelSubtractingAmount(TopLevelBasic):
    def __init__(self, *args, **kwargs):
        self.win_title = 'Expenses'

        super().__init__(*args, **kwargs)

    def place_widgets(self):
        super().place_widgets()

        tk.Button(self, text='-', command=self.vc.add_new_record).grid(
            row=4, column=1)

    @property
    def amount(self):
        return -self.sum_content.get()


class TopLevelShowingInfo(tk.Toplevel):
    def __init__(self, vc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vc = vc
        self.configure_win()

        self.data_tree = ttk.Treeview(self)
        self.data_tree['columns'] = (
            'date_col', 'amount_col', 'comment_col', 'total_col')

        vertical_scroll = ttk.Scrollbar(self, orient="vertical",
                                        command=self.data_tree.yview)
        vertical_scroll.pack(side='right', fill='y')
        self.data_tree.configure(yscrollcommand=vertical_scroll.set)

        self.data_tree.column('#0', width=50)
        self.data_tree.column("date_col", width=100)
        self.data_tree.column("amount_col", width=100)
        self.data_tree.column("comment_col", width=100)
        self.data_tree.column("total_col", width=100)

        self.data_tree.heading("#0", text='ID', anchor='w')
        self.data_tree.heading("date_col", text='Date')
        self.data_tree.heading("amount_col", text='Amount')
        self.data_tree.heading("comment_col", text='Comment')
        self.data_tree.heading("total_col", text='Total')

        self.data_tree.pack()

    def configure_win(self):
        self.title('Archive')
        self.focus()
        self.grab_set()
        self.resizable(width=False, height=False)
        self.protocol('WM_DELETE_WINDOW', self.vc.on_closing)
        self.vc.center_main_window(self, width=455, height=200)

    def insert_data_to_tree(self, current_id, row):
        self.data_tree.insert('', 'end', text=str(current_id),
                              values=(row[1], row[2], row[3], row[4]))
