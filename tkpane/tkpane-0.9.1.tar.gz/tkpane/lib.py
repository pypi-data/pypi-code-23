# panelib.py
#
# PURPOSE
#   A collection of TkPane subclasses.
#
# AUTHORS
#   Dreas Nielsen (RDN)
#
# COPYRIGHT AND LICENSE
#   Copyright (c) 2018, R. Dreas Nielsen
#   This program is free software: you can redistribute it and/or modify it 
#   under the terms of the GNU General Public License as published by the Free 
#   Software Foundation, either version 3 of the License, or (at your option) 
#   any later version. This program is distributed in the hope that it will be 
#   useful, but WITHOUT ANY WARRANTY; without even the implied warranty of 
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
#   Public License for more details. The GNU General Public License is available 
#   at http://www.gnu.org/licenses/.
#
#===============================================================================

"""A collection of TkPane subclasses that may be used as-is or used as templates
for creation of other custom pane classes.
"""

__version__ = "0.3.2"


try:
    import Tkinter as tk
except:
    import tkinter as tk
try:
    import ttk
except:
    from tkinter import ttk
try:
    import tkFileDialog as tk_file
except:
    from tkinter import filedialog as tk_file
try:
    import tkFont as tkfont
except:
    from tkinter import font as tkfont

import time

import tkpane



#===============================================================================
#       Pane styles
# A style is a set of options for pane (frame) configuration and gridding.
#-------------------------------------------------------------------------------
panestyles = {}

class PaneStyle(object):
    """Define a set of configuration options for frames and for widgets."""

    # Default spacing inside pane borders should be 18 pixels per the GNOME HIG 
    # (https://developer.gnome.org/hig/stable/visual-layout.html.en).
    # Assuming a 3-pixel padding around interior widgets and that frames (panes)
    # will be adjacent, default internal padding for frames should be set to
    #    (18 - 3)/2 ~= 7 pixels,
    # This leaves the border around the outermost widgets in the app window
    # smaller than desired.  A frame around the entire application can be created
    # to add this padding.
    #def __init__(self, stylename, frame_config_dict, frame_grid_dict={}):
    def __init__(self, stylename, frame_config_dict={"padx": 7, "pady":7}, frame_grid_dict={}):
        self.config = frame_config_dict
        self.grid = frame_grid_dict
        panestyles[stylename] = self

# Default grid styles are used for all of the built-in pane styles.
PaneStyle("plain", {}, {})
PaneStyle("default")
PaneStyle("ridged",  {"padx": 7, "pady": 7, "borderwidth": 2, "relief": tk.RIDGE})
PaneStyle("grooved", {"padx": 7, "pady": 7, "borderwidth": 2, "relief": tk.GROOVE})
PaneStyle("sunken",  {"padx": 7, "pady": 7, "borderwidth": 2, "relief": tk.SUNKEN})
PaneStyle("statusbar", {"padx": 7, "pady": 2, "borderwidth": 2, "relief": tk.SUNKEN})

current_panestyle = "default"
dialog_style = "default"

def frame_config_opts(style=None):
    return panestyles[style or current_panestyle].config

def frame_grid_opts(style=None):
    return panestyles[style or current_panestyle].grid




#===============================================================================
#       Dialog class
# Used by some panes.  Also usable for other purposes.
# Adapted from effbot: http://effbot.org/tkinterbook/tkinter-dialog-windows.htm.
#-------------------------------------------------------------------------------

class Dialog(tk.Toplevel):
    def __init__(self, parent, title = None):
        tk.Toplevel.__init__(self, parent, **frame_config_opts(dialog_style))
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = None
        body = tk.Frame(self)
        self.initial_focus = self.makebody(body)
        body.pack(padx=3, pady=3)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)
    def makebody(self, master):
        # Create the dialog body.  Return the widget that should have
        # the initial focus.  This method should be overridden.
        pass
    def buttonbox(self):
        # Add a standard button box. This method should be overriden
        # if no buttons, or some other buttons, are to be shown.
        box = tk.Frame(self)
        w = tk.Button(box, text="Cancel", width=8, command=self.cancel)
        w.pack(side=tk.RIGHT, padx=3, pady=3)
        w = tk.Button(box, text="OK", width=8, command=self.ok)
        w.pack(side=tk.RIGHT, padx=3, pady=3)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()
    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.cancel()
    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()
    def validate(self):
        # Override this method as necessary.
        return 1
    def apply(self):
        # Override this method as necessary.
        pass



#===============================================================================
#       Pane classes
#-------------------------------------------------------------------------------

class MessagePane(tkpane.TkPane):
    """Display a text message.
    
    :param message: The message to display..
    
    This pane does not manage any data.
    
    Name used by this pane: "Message".
    
    Overridden methods:
    * set
    
    Custom methods:
    * set_message
    """
    def __init__(self, parent, message):
        tkpane.TkPane.__init__(self, parent, "Message", frame_config_opts(), frame_grid_opts())
        self.msg_label = None
        def wrap_mp_msg(event):
            self.msg_label.configure(wraplength=event.width - 5)
        msgframe = ttk.Frame(master=parent)
        self.msg_label = ttk.Label(msgframe, text=message)
        self.msg_label.bind("<Configure>", wrap_mp_msg)
        self.msg_label.grid(column=0, row=0, sticky=tk.EW, padx=6, pady=6)
        msgframe.rowconfigure(0, weight=0)
        msgframe.columnconfigure(0, weight=1)
        msgframe.grid(row=0, column=0, sticky=tk.EW)
        parent.rowconfigure(0, weight=0)
        parent.columnconfigure(0, weight=1)

    def set_message(self, message):
        """Change the message displayed in the pane."""
        self.msg_label.configure(text=message)
    
    def set(self, data):
        """Changes the text of the message.
        
        Key supported: 'message'.
        """
        if "message" in data:
            self.set_message(data["message"])


class UserPane(tkpane.TkPane):
    """Display a user's name, and prompt for a user's name and password.
    
    Data keys managed by this pane: "name" and "password".
    
    Name used by this pane: "User authorization".
    
    Overridden methods:
    
    * clear_pane
    * send_status_message
    * focus
    """

    class GetUserDialog(Dialog):
        def makebody(self, master):
            tk.Label(master, text="User name:", width=12, anchor=tk.E).grid(row=0, column=0, sticky=tk.E, padx=3, pady=3)
            tk.Label(master, text="Password:", width=12, anchor=tk.E).grid(row=1, column=0, sticky=tk.E, padx=3, pady=3)
            self.e1 = tk.Entry(master, width=36)
            self.e2 = tk.Entry(master, width=36, show="*")
            self.e1.grid(row=0, column=1, sticky=tk.W, padx=3, pady=3)
            self.e2.grid(row=1, column=1, sticky=tk.W, padx=3, pady=3)
            return self.e1
        def validate(self):
            return self.e1.get() != u'' and self.e2.get() != u''
        def apply(self):
            self.result = {u"name": self.e1.get(), u"password": self.e2.get()}

    def __init__(self, parent):
        tkpane.TkPane.__init__(self, parent, "User authorization", config_opts=frame_config_opts(), grid_opts=frame_grid_opts())
        user_label = tk.Label(self, text='User name:', width=10, anchor=tk.E)
        self.user_var = tk.StringVar()
        self.datakeylist = ["name", "password"]
        self.datadict = {}
        self.previous_values = {}
        user_display = tk.Entry(self, textvariable=self.user_var)
        user_display.config(state='readonly')
        self.user_button = tk.Button(self, text='Change', width=8, command=self.set_user)
        user_label.grid(row=0, column=0, padx=6, pady=3, sticky=tk.EW)
        user_display.grid(row=0, column=1, padx=6, pady=3, sticky=tk.EW)
        self.user_button.grid(row=1, column=1, padx=6, pady=1, sticky=tk.W)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        parent.rowconfigure(0, weight=0)
        parent.columnconfigure(0, weight=1)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def valid_data(self, widget=None):
        """Return True or False indicating whether or not a name and password have been entered."""
        # Although this method is meant to check the data in the widgets, because
        # name and password can be entered only from a dialog box, and the dialog
        # box requires entry, and the values are then assigned to the data
        # dictionary, this routine checks the data dictionary rather than the widgets.
        return self.required and "name" in self.datadict.keys() and "password" in self.datadict.keys()


    def send_status_message(self, is_valid):
        """Send a status message reporting data values and/or validity if data have changed."""
        # This overrides the class method because only the user name should be reported.
        if self.datadict != self.original_values:
            if is_valid:
                if "name" in self.datadict.keys():
                    self.report_status(u"User name set to %s." % self.datadict["name"])
                else:
                    self.report_status(u"User name cleared.")
            else:
                self.report_status("User name is invalid.")

    def clear_pane(self):
        self.user_var.set(u'')
        self.user_pw = None
    
    def focus(self):
        """Set the focus to the button."""
        self.user_button.focus_set()

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def set_user(self):
        # Open a dialog box to prompt for the user's name and password.
        dlg = self.GetUserDialog(self)
        if dlg.result is not None:
            self.user_var.set(dlg.result["name"])
            self.user_pw = dlg.result["password"]
            self.datadict["name"] = dlg.result["name"]
            self.datadict["password"] = dlg.result["password"]
            self.report_status(u"Name set to %s." % dlg.result[u"name"])
            self.handle_change_validity(True, None)
            self.send_status_message(True)


class OutputDirPane(tkpane.TkPane):
    """Get and display an output directory.
    
    :param optiondict: a dictionary of option names and values for the Tkinter 'askdirectory' method (optional).
    
    Data key managed by this pane: "output_dir".
    
    Name used by this pane: "Output directory".
    
    Overridden methods:
    
    * entry_widgets
    * valid_data
    * save_data
    * clear_pane
    * disable_pane
    * enable_pane
    * focus
    * set
    """
    datakey = u"output_dir"
    
    def __init__(self, parent, optiondict=None):
        tkpane.TkPane.__init__(self, parent, "Output directory", frame_config_opts(), frame_grid_opts())
        # Customize attributes
        self.optiondict = {} if optiondict is None else optiondict
        self.datakeylist = [self.datakey]
        # Create, configure, and place widgets.
        dir_label = tk.Label(self, text='Output directory:', width=18, anchor=tk.E)
        self.dir_var = tk.StringVar()
        self.dir_var.trace("w", self.check_entrychange)
        self.dir_display = tk.Entry(self, textvariable=self.dir_var)
        self.valid_color = self.dir_display.cget("background")
        self.dir_button = tk.Button(self, text='Browse', width=8, command=self.set_outputdir)
        dir_label.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        self.dir_display.grid(row=0, column=1, padx=3, pady=3, sticky=tk.EW)
        self.dir_button.grid(row=1, column=1, padx=3, pady=1, sticky=tk.W)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        parent.rowconfigure(0, weight=0)
        parent.columnconfigure(0, weight=1)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        """Return a list of widgets used for data entry."""
        return [self.dir_display]

    def valid_data(self, widget=None):
        """Return True or False indicating the validity of the directory entry.
        
        Overrides TkPane class method.
        """
        import os.path
        outputdir = self.dir_display.get()
        if outputdir == "":
            return not self.required
        else:
            return os.path.isdir(outputdir)

    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the entry widget.
        
        Overrides TkPane class method.
        """
        outputdir = self.dir_display.get()
        if is_valid:
            if outputdir == "":
                self.clear_data([self.datakey])
            else:
                self.datadict[self.datakey] = outputdir
        else:
            self.clear_data([self.datakey])
    
    def clear_pane(self):
        self.dir_var.set("")

    def enable_pane(self):
        self.dir_display.configure(state='normal')
        self.dir_button.configure(state=['normal'])

    def disable_pane(self):
        self.dir_display.configure(state='readonly')
        self.dir_button.configure(state=['disabled'])
    
    def focus(self):
        """Set the focus to the entry."""
        self.dir_display.focus_set()

    def set(self, data):
        """Change the directory name in the entry display.
        
        Key supported: 'directory'.
        """
        if "directory" in data:
            self.dir_var.set(data["directory"])
            self.handle_change_validity(True, self.dir_display)
            self.send_status_message(True)

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def check_entrychange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.dir_display)
    
    def set_outputdir(self):
        dir = tk_file.askdirectory(**self.optiondict)
        if dir != "":
            self.dir_var.set(dir)
            self.handle_change_validity(True, self.dir_display)
            self.send_status_message(True)


class OutputFilePane(tkpane.TkPane):
    """Get and display an output filename.
    
    :param optiondict: a dictionary of option names and values for the Tkinter 'asksaveasfilename' method (optional).
    
    Data key managed by this pane: "output_filename".
    
    Name used by this pane: "Output filename".
    
    Overridden methods:
    
    * entry_widgets
    * valid_data
    * save_data
    * clear_pane
    * disable_pane
    * enable_pane
    * focus
    * set
    """
    datakey = "output_filename"

    def __init__(self, parent, optiondict=None):
        tkpane.TkPane.__init__(self, parent, "Output filename", frame_config_opts(), frame_grid_opts())
        # Customize attributes
        self.optiondict = {} if optiondict is None else optiondict
        self.datakeylist = [self.datakey]
        # Create, configure, and place widgets.
        dir_label = tk.Label(self, text='Output file:', width=12, anchor=tk.E)
        self.file_var = tk.StringVar()
        self.file_var.trace("w", self.check_entrychange)
        self.file_display = tk.Entry(self, textvariable=self.file_var)
        self.valid_color = self.file_display.cget("background")
        self.browse_button = tk.Button(self, text='Browse', width=8, command=self.set_outputfile)
        dir_label.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        self.file_display.grid(row=0, column=1, padx=3, pady=3, sticky=tk.EW)
        self.browse_button.grid(row=1, column=1, padx=3, pady=1, sticky=tk.W)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        parent.rowconfigure(0, weight=0)
        parent.columnconfigure(0, weight=1)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        """Return a list of widgets used for data entry."""
        return [self.file_display]

    def valid_data(self, widget=None):
        """Return True or False indicating the validity of the filename entry.
        
        Overrides TkPane class method.
        """
        import os.path
        filename = self.file_display.get()
        if filename == "":
            return not self.required
        else:
            filedir = os.path.dirname(filename)
            if filedir == "":
                return True
            else:
                return os.path.isdir(filedir)

    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the entry widget.
        
        Overrides TkPane class method.
        """
        # entry_widget should be self.file_display.
        filename = self.file_display.get()
        if is_valid:
            if filename == "":
                self.clear_data([self.datakey])
            else:
                self.datadict[self.datakey] = filename
        else:
            self.clear_data([self.datakey])
    
    def clear_pane(self):
        self.file_var.set("")

    def enable_pane(self):
        self.file_display.configure(state='normal')
        self.browse_button.configure(state=['normal'])

    def disable_pane(self):
        self.file_display.configure(state='readonly')
        self.browse_button.configure(state=['disabled'])
    
    def focus(self):
        """Set the focus to the entry."""
        self.file_display.focus_set()

    def set(self, data):
        """Change the filename in the entry display.
        
        Key supported: 'output_filename'.
        """
        if datakey in data:
            self.file_var.set(data[datakey])
            self.handle_change_validity(True, self.file_display)
            self.send_status_message(True)

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def check_entrychange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.file_display)
    
    def set_outputfile(self):
        fn = tk_file.asksaveasfilename(**self.optiondict)
        if fn != "":
            self.file_var.set(fn)
            self.handle_change_validity(True, self.file_display)
            self.send_status_message(True)



class InputFilePane(tkpane.TkPane):
    """Get and display an input filename.
    
    :param optiondict: a dictionary of option names and values for the Tkinter 'askopenfilename' method (optional).
    
    Data key managed by this pane: "input_filename".
    
    Name used by this pane: "Input filename".
    
    Overridden methods:
    
    * entry_widgets
    * valid_data
    * save_data
    * clear_pane
    * disable_pane
    * enable_pane
    * focus
    * set
    """

    datakey = "input_filename"
    
    def __init__(self, parent, optiondict=None):
        tkpane.TkPane.__init__(self, parent, "Input filename", frame_config_opts(), frame_grid_opts())
        # Customize attributes
        self.optiondict = {} if optiondict is None else optiondict
        self.datakeylist = [self.datakey]
        # Create, configure, and place widgets.
        dir_label = tk.Label(self, text='Input file:', width=12, anchor=tk.E)
        self.file_var = tk.StringVar()
        self.file_var.trace("w", self.check_entrychange)
        self.file_display = tk.Entry(self, textvariable=self.file_var)
        self.valid_color = self.file_display.cget("background")
        self.browse_button = tk.Button(self, text='Browse', width=8, command=self.set_inputfile)
        dir_label.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        self.file_display.grid(row=0, column=1, padx=3, pady=3, sticky=tk.EW)
        self.browse_button.grid(row=1, column=1, padx=3, pady=1, sticky=tk.W)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        parent.rowconfigure(0, weight=0)
        parent.columnconfigure(0, weight=1)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        """Return a list of widgets used for data entry."""
        return [self.file_display]

    def valid_data(self, widget):
        """Return True or False indicating the validity of the filename entry.
        
        Overrides TkPane class method.
        """
        import os.path
        filename = self.file_display.get()
        if filename == "":
            return not self.required
        else:
            return os.path.isfile(filename)
    
    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the entry widget.
        
        Overrides TkPane class method.
        """
        # entry_widget should be self.file_display.
        filename = self.file_display.get()
        if is_valid:
            if filename == "":
                self.clear_data([self.datakey])
            else:
                self.datadict[self.datakey] = filename
        else:
            self.clear_data([self.datakey])

    
    def clear_pane(self):
        self.file_var.set(u'')

    def enable_pane(self):
        self.file_display.configure(state='normal')
        self.browse_button.configure(state=['normal'])

    def disable_pane(self):
        self.file_display.configure(state='readonly')
        self.browse_button.configure(state=['disabled'])

    def focus(self):
        """Set the focus to the entry."""
        self.file_display.focus_set()

    def set(self, data):
        """Change the filename in the entry widget.
        
        Keys supported: 'input_filename'.
        """
        if datakey in data:
            self.file_var.set(data[datakey])
            self.handle_change_validity(True, self.file_display)
            self.send_status_message(True)

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def check_entrychange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.file_display)
    
    def set_inputfile(self):
        fn = tk_file.askopenfilename(**self.optiondict)
        if fn != "":
            # The order of the following steps is important.
            self.file_var.set(fn)
            self.handle_change_validity(True, self.file_display)
            self.send_status_message(True)


class TextPane(tkpane.TkPane):
    """Display a Tkinter Text widget.
    
    :param optiondict: A dictionary of option names and values for initial configuration of the Text widget (optional).
    :parame initial_text: Initial contents for the Text widget (optional).
    
    Because of the large number of uses of the Text widget, this pane
    provides direct access to the Text widget via the 'textwidget' method.
    To simplify use, this pane also provides direct methods for appending to,
    replacing, and clearing the contents of the Text widget.
    The custom methods 'set_status' and 'clear_status' allow a TextPane to
    be used as a status_reporter callback for any other type of pane.
    
    Data keys managed by this pane: "text".
    
    Name used by this pane: "Text".
    
    Overridden methods:
    
    * entry_widgets
    * save_data
    * valid_data
    * clear_pane
    * enable_pane
    * disable_pane
    * focus
    * set
    
    Custom methods:
    
    * textwidget
    * replace_all
    * append
    * set_status
    * clear_status
    """

    def __init__(self, parent, optiondict=None, initial_text=None):
        tkpane.TkPane.__init__(self, parent, "Text", frame_config_opts(), frame_grid_opts())
        opts = {} if optiondict is None else optiondict
        self.datakeylist = ["text"]
        self.textwidget = tk.Text(self, **opts)
        self.textwidget.bind("<Key>", self.check_entrychange)
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.textwidget.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.textwidget.xview)
        self.textwidget.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        if initial_text is not None:
            self.replace_all(initial_text)
        self.textwidget.grid(row=0, column=0, padx=3, pady=3, sticky=tk.NSEW)
        ysb.grid(column=1, row=0, sticky=tk.NS)
        xsb.grid(column=0, row=1, sticky=tk.EW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        return [self.textwidget]
    
    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the text widget."""
        text = self.textwidget.get("1.0", tk.END)
        if is_valid:
            if text == "":
                self.clear_data()
            else:
                self.datadict["text"] = text
        else:
            self.clear_data()

    def valid_data(self, entry_widget=None):
        text = self.textwidget.get("1.0", tk.END)
        return not (text == "" and self.required)
    
    def clear_pane(self):
        widget_state = self.textwidget.cget("state")
        self.textwidget.configure(state=tk.NORMAL)
        self.textwidget.delete("1.0", tk.END)
        self.textwidget.configure(state=widget_state)
    
    def enable_pane(self):
        self.textwidget.configure(state=tk.NORMAL)
    
    def disable_pane(self):
        self.textwidget.configure(state=tk.DISABLED)
    
    def replace_all(self, new_contents):
        self.clear_pane()
        self.textwidget.insert(tk.END, new_contents)
        self.datadict["text"] = new_contents
    
    def append(self, more_text, scroll=True):
        """Inserts the given text at the end of the Text widget's contents."""
        self.textwidget.insert(tk.END, more_text)
        if scroll:
            self.textwidget.see("end")
    
    def set_status(self, status_msg):
        """Inserts the status message at the end of the Text widget's contents."""
        if len(status_msg) > 0 and status_msg[-1] != u"\n":
            status_msg += u"\n"
        widget_state = self.textwidget.cget("state")
        self.textwidget.configure(state=tk.NORMAL)
        self.append(status_msg)
        self.textwidget.configure(state=widget_state)
    
    def clear_status(self):
        """Clear the entire widget."""
        self.clear()
    
    def focus(self):
        """Set the focus to the text widget."""
        self.textwidget.focus_set()

    def set(self, data):
        """Change the contents of the text widget.
        
        Keys supported: 'text'.
        """
        if "text" in data:
            self.replace_all(data["text"])

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def textwidget(self):
        """Return the text widget object, to allow direct manipulation."""
        return self.textwidget
    
    def check_entrychange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.textwidget)
    


class StatusProgressPane(tkpane.TkPane):
    """Display a status bar and progress bar.
    
    There are no data keys managed by this pane.
    
    Overridden methods:
    
    * clear_pane
    * values
    
    Custom methods:
    
    * set_status(message): Sets the status bar message.
    * set_determinate(): Sets the progress bar to determinate mode.
    * set_indeterminate(): Sets the progress bar to indeterminate mode.
    * set_value(value): Sets a determinate progress bar to the specified value (0-100).
    * start(): Starts an indefinite progress bar.
    * stop(): Stops an indefinite progress bar.
    """
    def __init__(self, parent):
        tkpane.TkPane.__init__(self, parent, "Status", frame_config_opts("statusbar"), frame_grid_opts("statusbar"))
        self.status_msg = tk.StringVar()
        self.status_msg.set('')
        self.ctrvalue = tk.DoubleVar()
        self.ctrvalue.set(0)
        statusbar = ttk.Label(parent, text='', textvariable=self.status_msg, relief=tk.RIDGE, anchor=tk.W)
        self.progressmode = 'determinate'
        ctrprogress = ttk.Progressbar(parent, mode=self.progressmode, maximum=100,
                                      orient='horizontal', length=150, variable=self.ctrvalue)
        statusbar.grid(row=0, column=0, sticky=tk.EW)
        ctrprogress.grid(row=0, column=1, sticky=tk.EW)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(1, weight=1)
        parent.rowconfigure(0, weight=0)
        parent.columnconfigure(0, weight=1)

    def values(self):
        return {'status': self.satus_msg.get(), 'progress': self.ctrvalue.get()}

    def clear_pane(self):
        """Clears the status bar and progress bar."""
        self.status_msg.set('')
        self.ctrvalue.set(0)
        self.stop()

    def set_status(self, message):
        """Sets the status bar message."""
        self.status_msg.set(message)

    def clear_status(self):
        """Clears the status bar message."""
        self.status_msg.set('')

    def set_determinate(self):
        """Sets the progress bar to definite mode."""
        self.progressmode = "indeterminate"
        self.ctrprogress.configure(mode=self.progressmode)

    def set_indeterminate(self):
        """Sets the progress bar to indefinite mode."""
        self.progressmode = "indeterminate"
        self.ctrprogress.configure(mode=self.progressmode)

    def set_value(self, value):
        """Sets the progress bar indicator.
        
        The 'value' argument should be between 0 and 100, and will be trimmed to
        this range if it is not.
        """
        if self.progressmode == "determinate":
            self.ctrvalue.set(max(min(float(value), 100.0), 0.0))
    
    def set(self, data):
        """Change the status message and/or the progress bar value.
        
        Keys supported: 'message' and 'value'.
        """
        if "message" in data:
            self.set_status(data["message"])
        if "value" in data:
            self.set_value(data["value"])

    def start(self):
        """Start an indefinite progress bar running."""
        if self.progressmode == "indeterminate":
            self.ctrprogress.start()

    def stop(self):
        """Stop an indefinite progress bar."""
        if self.progressmode == "determinate":
            pass


class TableDisplayPane(tkpane.TkPane):
    """Display a specified data table.
        
    :param message: A message to display above the data table.
    :param column_headers: A list of the column names for the data table.
    :param rowset: An iterable that yields lists of values to be used as rows for the data table.
    
    There are no data keys managed by this pane.
    
    Overridden methods:
    
    * clear_pane
    * set
    
    Custom methods:
    
    * display_data
    """
    def __init__(self, parent, message, column_headers, rowset):
        tkpane.TkPane.__init__(self, parent, "Table display", frame_config_opts(), frame_grid_opts())
        # Message frame and control.
        self.msg_label = None
        def wrap_msg(event):
            self.msg_label.configure(wraplength=event.width - 5)
        if message is not None:
            msgframe = ttk.Frame(master=self, padding="3 3 3 3")
            self.msg_label = ttk.Label(msgframe, text=message)
            self.msg_label.bind("<Configure>", wrap_msg)
            self.msg_label.grid(column=0, row=0, sticky=tk.EW)
            msgframe.rowconfigure(0, weight=0)
            msgframe.columnconfigure(0, weight=1)
            msgframe.grid(row=0, column=0, pady=3, sticky=tk.EW)
        tableframe = ttk.Frame(master=self, padding="3 3 3 3")
        # Create and configure the Treeview table widget and scrollbars.
        self.tbl = ttk.Treeview(tableframe, columns=column_headers, selectmode="none", show="headings")
        ysb = ttk.Scrollbar(tableframe, orient='vertical', command=self.tbl.yview)
        xsb = ttk.Scrollbar(tableframe, orient='horizontal', command=self.tbl.xview)
        self.tbl.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        tableframe.grid(column=0, row=1 if message is not None else 0, sticky=tk.NSEW)
        self.tbl.grid(column=0, row=0, sticky=tk.NSEW)
        ysb.grid(column=1, row=0, sticky=tk.NS)
        xsb.grid(column=0, row=1, sticky=tk.EW)
        tableframe.columnconfigure(0, weight=1)
        tableframe.rowconfigure(0, weight=1)
        # Display the data
        self.display_data(column_headers, rowset)
        # Make the table resizeable
        if message is not None:
            self.rowconfigure(0, weight=0)
            self.rowconfigure(1, weight=1)
        else:
            self.rowconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
    
    def set(self, data):
        """Change the message and/or the data table displayed on the pane.
        
        Keys supported: 'message' and 'table'.  If the argumen thas a key 
        "table", that key's value should be a two-element tuple, of which the 
        first element is a list of the column header names and the second is a 
        list (rows) of lists (columns) containing the table's data.
        """
        if "message" in data:
            self.msg_label.configure(text=data["message"])
        if "table" in data:
            self.display_data(data["table"][0], data["table"][1])

    def clear_pane(self):
        for item in self.tbl.get_children():
            self.tbl.delete(item)
        self.tbl.configure(columns=[""])

    def display_data(self, column_headers, rowset):
        """Display a new data set on the pane.
        
        :param column_headers: A list of strings for the headers of the data columns.
        :param rowset: A list of lists of data values to display.  The outer list is rows, the inner lists are columns.
        """
        self.clear_pane()
        # Reconfigure TreeView columns
        self.tbl.configure(columns=column_headers)
        # Get the data to display.
        nrows = range(len(rowset))
        ncols = range(len(column_headers))
        hdrwidths = [len(column_headers[j]) for j in ncols]
        datawidthtbl = [[len(rowset[i][j] if isinstance(rowset[i][j], basestring) else unicode(rowset[i][j])) for i in nrows] for j in ncols]
        datawidths = [max(cwidths) for cwidths in datawidthtbl]
        colwidths = [max(hdrwidths[i], datawidths[i]) for i in ncols]
        # Set the font.
        ff = tkfont.nametofont("TkFixedFont")
        tblstyle = ttk.Style()
        tblstyle.configure('tblstyle', font=ff)
        self.tbl.configure()["style"] = tblstyle
        charpixels = int(1.3 * ff.measure(u"0"))
        pixwidths = [charpixels * col for col in colwidths]
        # Fill the Treeview table widget with data
        for i in range(len(column_headers)):
            self.tbl.column(column_headers[i], width=pixwidths[i])
            self.tbl.heading(column_headers[i], text=column_headers[i])
        for i, row in enumerate(rowset):
            enc_row = [c if c is not None else '' for c in row]
            self.tbl.insert(parent='', index='end', iid=str(i), values=enc_row)


class OkCancelPane(tkpane.TkPane):
    """Display OK and Cancel buttons.
    
    There are no data keys specific to this pane.
    
    Overridden methods:
    
    * disable_pane
    * enable_pane
    * focus
    
    Custom methods:
    
    * set_cancel_action
    * set_ok_action
    * ok
    * cancal
    """
    def __init__(self, parent, ok_action=None, cancel_action=None):
        def do_nothing():
            pass
        tkpane.TkPane.__init__(self, parent, "OK/Cancel", frame_config_opts(), frame_grid_opts())
        self.ok_action = ok_action if ok_action is not None else do_nothing
        self.cancel_action = cancel_action if cancel_action is not None else do_nothing 
        self.cancel_btn = ttk.Button(self, text="Cancel", command=self.cancel_action)
        self.cancel_btn.grid(row=0, column=1, padx=3, sticky=tk.E)
        self.ok_btn = ttk.Button(self, text="OK", command=self.ok_action)
        self.ok_btn.grid(row=0, column=0, padx=3, sticky=tk.E)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)
        parent.rowconfigure(0, weight=0)
        parent.columnconfigure(0, weight=1)

    def enable_pane(self):
        self.ok_btn.state(['!disabled'])

    def disable_pane(self):
        self.ok_btn.state(['disabled'])

    def focus(self):
        """Set the focus to the OK button."""
        self.ok_btn.focus_set()

    def set_ok_action(self, ok_action):
        """Specify the callback function to be called when the 'OK' button is clicked."""
        self.ok_action = ok_action if ok_action is not None else do_nothing
        self.ok_btn.configure(command=self.ok_action)

    def set_cancel_action(self, cancel_action):
        """Specify the callback function to be called when the 'Cancel' button is clicked."""
        self.cancel_action = cancel_action if cancel_action is not None else do_nothing 
        self.cancel_btn.configure(command=self.cancel_action)

    def ok(self):
        """Trigger this pane's 'OK' action."""
        self.ok_action()

    def cancel(self):
        """Trigger this pane's 'Cancel' action."""
        self.cancel_action()


class EntryPane(tkpane.TkPane):
    """Display a Tkinter Entry widget.
    
    Data keys managed by this pane: "entry".
    
    Name used by this pane: user-defined on initialization.
    
    Overridden methods:
    
    * entry_widgets
    * valid_data
    * save_data
    * clear_pane
    * enable_pane
    * disable_pane
    * focus
    * set
    """

    def __init__(self, parent, pane_name, prompt):
        tkpane.TkPane.__init__(self, parent, pane_name, frame_config_opts(), frame_grid_opts())
        self.datakeylist = ["entry"]
        self.prompt = ttk.Label(self, text=prompt, width=max(12, len(prompt)), anchor=tk.E)
        self.entry_var = tk.StringVar()
        self.entry_var.trace("w", self.check_entrychange)
        self.entrywidget = tk.Entry(self, textvariable=self.entry_var)
        self.prompt.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        self.entrywidget.grid(row=0, column=1, padx=3, pady=3, sticky=tk.EW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        return [self.entrywidget]

    def valid_data(self, entry_widget=None):
        text = self.entry_var.get()
        return not (text == "" and self.required)
    
    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the Entry widget."""
        text = self.entry_var.get()
        if is_valid:
            if text == "":
                self.clear_data()
            else:
                self.datadict["entry"] = text
        else:
            self.clear_data()

    def clear_pane(self):
        self.entry_var.put("")
    
    def enable_pane(self):
        self.entrywidget.configure(state=tk.NORMAL)
    
    def disable_pane(self):
        self.textwidget.configure(state="readonly")
    
    def focus(self):
        """Set the focus to the entry."""
        self.entrywidget.focus_set()

    def set(self, data):
        """If the argument has a 'prompt' key, change the pane's prompt to that key's value."""
        if "prompt" in data:
            self.prompt.configure(text=data["prompt"])
    
    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def check_entrychange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.entrywidget)

