import tkinter as tk  # python 3
from tkinter import font  as tkfont, ttk  # python 3

# import Tkinter as tk     # python 2
# import tkFont as tkfont  # python 2
from tkinter.ttk import Separator
from wuRegister.requestWuWien import RequestWuWien
requester = None

class WuApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.small_font = tkfont.Font(family='Helvetica', size=11, slant="italic")
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        w = 450  # width for the Tk root
        h = 280  # height for the Tk root
        ws = self.winfo_screenwidth()  # width of the screen
        hs = self.winfo_screenheight()  # height of the screen
        x = (ws / 2) - (w / 2)
        y = (hs / 2) - (h / 2)

        self.title("Wu automatischer Login")
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        py = 30
        px = 85
        container = tk.Frame(self)
        container.pack(side="top", pady=py, padx=px)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, LoadingPage, SuccessPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # Root = Tk()


        tk.Label(self, text="Gib die Anmeldedaten ein:").grid(columnspan=2)

        f = Separator(self, orient="horizontal")
        f.grid(row=1, column=0, sticky="we", padx=5, pady=5, columnspan=2)

        self.v1 = tk.StringVar()

        tk.Entry(self, textvariable=self.v1).grid(row=2, column=1)
        #self.v1.set("Beispiel: h123456")
        tk.Label(self, text="Username:").grid(row=2, column=0, sticky="W")

        # x max text box area
        self.v2 = tk.StringVar()
        tk.Entry(self, textvariable=self.v2).grid(row=3, column=1)
        #self.v2.set("Beispiel: 123456")
        tk.Label(self, text="Password").grid(row=3, column=0, sticky="W")
        # x step text box area
        self.v3 = tk.StringVar()
        tk.Entry(self, textvariable=self.v3).grid(row=4, column=1)
        #self.v3.set("Beispiel: SPP=123456")
        tk.Label(self, text="Anmeldeübersicht:").grid(row=4, column=0, sticky="W")

        self.v4 = tk.StringVar()
        tk.Entry(self, textvariable=self.v4).grid(row=5, column=1)
        #self.v4.set("Beispiel: SPAN_654321_123456")
        tk.Label(self, text="Anmeldefenster:").grid(row=5, column=0, sticky="W")

        self.v5 = tk.StringVar()
        tk.Entry(self, textvariable=self.v5).grid(row=6, column=1)
        #self.v5.set("Beispiel: 18:30")
        tk.Label(self, text="Uhrzeit:").grid(row=6, column=0, sticky="W")
        self.v6 = tk.StringVar(self)
        self.v6.set("Prüfung")  # default value
        tk.OptionMenu(self, self.v6, "Prüfung", "Lehrveranstaltung").grid(row=7, column=1)
        f = Separator(self, orient="horizontal")
        f.grid(row=8, column=0, sticky="we", padx=5, pady=5, columnspan=2)

        tk.Button(self, text="Start", command=lambda: self.anmelden(controll=controller)).grid(row=9, column=0)
        tk.Button(self, text="Quit", command=self.quitter).grid(row=9, column=1)

    def quitter(self):
        if requester:
            requester.cancelTimer()
        exit(0)

    def anmelden(self, controll):
        username = self.v1.get()
        password = self.v2.get()
        anmeldeFensterTag = self.v3.get()
        anmeldeSpan = self.v4.get()
        uhrzeit = self.v5.get()

        hours = int(uhrzeit.split(":")[0])
        minutes = int(uhrzeit.split(":")[1])
        poolCount = 3
        if self.v6.get() == "Prüfung":
            isPRF = True
        else:
            isPRF = False
        requester = RequestWuWien(hours=hours, minutes=minutes, user=username, passw=password,
                                  tagLoginWindow=anmeldeFensterTag, tagLogin=anmeldeSpan, isPRF=isPRF,
                                  requesterCount=poolCount)
        requester.setController(controll)
        requester.requestCookie()
        requester.login()
        controll.show_frame("LoadingPage")
        app.iconify()
        # sub = Frame(root)


class SuccessPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        wrapLen = 280
        label = tk.Label(self, text="Die Anmeldung wurde erfolgreich durchgeführt.", font=controller.small_font, justify=tk.CENTER, wraplength=wrapLen)
        label.pack(side="top",pady=10, expand=True)
        button = tk.Button(self, text="Gehe zur Startseite",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack(side="top")


class LoadingPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        label = tk.Label(self, text="Anmeldung läuf...", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        pb_hD = ttk.Progressbar(self, orient='horizontal', mode='indeterminate')
        pb_hD.pack(expand=True, fill=tk.X, side=tk.TOP)
        pb_hD.start(10)
        button = tk.Button(self, text="Stop",
                           command=lambda: self.stopLoading(controll=controller))
        button.pack()

    def stopLoading(self, controll):
        if requester:
            requester.cancelTimer()
        controll.show_frame("StartPage")


if __name__ == "__main__":
    app = WuApp()
    app.mainloop()
