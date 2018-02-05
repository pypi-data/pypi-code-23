import tkinter as tk


class TopLevelValidation(tk.Toplevel):
    def __init__(self, vc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vc = vc
        self.configure_win()

        self.validation_message = tk.StringVar()
        tk.Label(self, textvariable=self.validation_message).pack()
        tk.Button(self, text='OK', command=self.destroy).pack()

    def configure_win(self):
        self.title('Error')
        self.focus_set()
        self.grab_set()
        self.resizable(width=False, height=False)
        self.protocol('WM_DELETE_WINDOW', self.vc.on_closing_validation)
        self.bind('<Destroy>', self.vc.on_closing_validation)
        self.vc.center_main_window(self, width=300, height=50)
