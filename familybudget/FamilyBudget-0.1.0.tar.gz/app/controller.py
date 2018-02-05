import _tkinter as _tk
import datetime

from src.model import DBConnection
from src.view_main import MainWindow
from src.view_top_level import (TopLevelAddingAmount, TopLevelShowingInfo,
                                TopLevelSubtractingAmount)
from src.view_validation import TopLevelValidation


class FamilyBudgetController(object):
    def __init__(self, parent):
        self.parent = parent
        self.model = DBConnection(self)
        self.view = MainWindow(self)

        self.new_win = None
        self.validation_win = None

        self.center_main_window(parent)

        self.datetime_now = datetime.datetime.now().strftime("%d/%m/%Y")

    @staticmethod
    def center_main_window(obj, width=200, height=115):
        screen_width = obj.winfo_screenwidth()
        screen_height = obj.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        obj.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def open_incomes(self):
        self.new_win = TopLevelAddingAmount(self)
        self.new_win.set_total_amount(self.model.last_total_amount)
        self.parent.withdraw()
        self.new_win.date_content.set(self.datetime_now)
        self.new_win.wait_window()

    def open_expenses(self):
        self.new_win = TopLevelSubtractingAmount(self)
        self.new_win.set_total_amount(self.model.last_total_amount)
        self.parent.withdraw()
        self.new_win.date_content.set(self.datetime_now)
        self.new_win.wait_window()

    def open_archive(self):
        self.new_win = TopLevelShowingInfo(self)
        self.parent.withdraw()
        self.show_stored_data()
        self.new_win.wait_window()

    def on_closing(self):
        self.parent.deiconify()
        self.new_win.destroy()

    def on_closing_validation(self, event=None):
        self.new_win.deiconify()
        if event is None:
            self.validation_win.destroy()

    def _validate_entry(self, msg):
        self.new_win.withdraw()
        self.validation_win = TopLevelValidation(self)
        self.validation_win.validation_message.set(msg)
        self.validation_win.wait_window()

    def add_new_record(self):
        try:
            date = self.new_win.date_content.get()
            datetime.datetime.strptime(date, "%d/%m/%Y")
        except (ValueError, _tk.TclError):
            self._validate_entry(msg='Date must be in "dd/mm/year" format')
            return

        try:
            amount = self.new_win.amount
            if abs(amount) <= 0.0:
                raise ValueError
        except (ValueError, _tk.TclError):
            self._validate_entry(
                msg='Sum must be a number that is greater than 0')
            return

        comment = self.new_win.comment_content.get()
        if comment == "":
            self._validate_entry(msg='You must type a comment')
            return

        last_total_amount = self.model.last_total_amount + amount

        self.model.add_record(date, amount, comment, last_total_amount)

        self.new_win.set_total_amount(self.model.last_total_amount)

    def show_stored_data(self):
        rows = self.model.get_all_rows()
        current_id = len(rows)
        for r in reversed(rows):
            self.new_win.insert_data_to_tree(current_id, r)
            current_id -= 1
