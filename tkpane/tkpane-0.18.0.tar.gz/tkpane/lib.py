# lib.py
#
# PURPOSE
#   A collection of TkPane subclasses.
#
# AUTHORS
#   Dreas Nielsen
#   Elizabeth Shea
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

__version__ = "0.8.0"


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
PaneStyle("closex", {"padx": 0, "pady": 7})
PaneStyle("closey", {"padx": 7, "pady": 0})
PaneStyle("closexy", {"padx": 0, "pady": 0})
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
        box = ttk.Frame(self)
        w = ttk.Button(box, text="Cancel", width=8, command=self.cancel)
        w.pack(side=tk.RIGHT, padx=3, pady=3)
        w = ttk.Button(box, text="OK", width=8, command=self.ok)
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
        self.msg_label = ttk.Label(parent, text=message)
        self.msg_label.bind("<Configure>", wrap_mp_msg)
        self.msg_label.grid(column=0, row=0, sticky=tk.EW, padx=6, pady=6)
        parent.rowconfigure(0, weight=0)
        parent.columnconfigure(0, weight=1)

    def set_message(self, message):
        """Change the message displayed in the pane."""
        self.msg_label.configure(text=message)
    
    def set_data(self, data):
        """Adds data to the pane's data dictionary.  
        
        Special key supported: "message" changes the displayed message."""
        spkey = "message"
        if spkey in data:
            self.set_message(data[spkey])
        self.set_allbut(data, [spkey])


class UserPane(tkpane.TkPane):
    """Display a user's name and a button to prompt for a user's name and password.
    
    Data keys managed by this pane: "name" and "password".
    
    Name used by this pane: "User authorization".
    
    Overridden methods:
    
    * valid_data
    * clear_pane
    * send_status_message
    * focus
    
    Custom methods:
    
    * set_user
    * set_user_validator
    """

    class GetUserDialog(Dialog):
        def makebody(self, master):
            ttk.Label(master, text="User name:", width=12, anchor=tk.E).grid(row=0, column=0, sticky=tk.E, padx=3, pady=3)
            ttk.Label(master, text="Password:", width=12, anchor=tk.E).grid(row=1, column=0, sticky=tk.E, padx=3, pady=3)
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
        self.user_validator = None
        self.user_label = ttk.Label(self, text='User name:', width=10, anchor=tk.E)
        self.user_var = tk.StringVar()
        self.userkeyname = "name"
        self.passkeyname = "password"
        self.datakeylist = [self.userkeyname, self.passkeyname]
        self.datadict = {}
        self.previous_values = {}
        self.user_display = ttk.Entry(self, textvariable=self.user_var)
        self.user_display.config(state='readonly')
        self.user_button = ttk.Button(self, text='Change', width=8, command=self.set_user)
        self.user_label.grid(row=0, column=0, padx=6, pady=3, sticky=tk.EW)
        self.user_display.grid(row=0, column=1, padx=6, pady=3, sticky=tk.EW)
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
        if self.required:
            v = "name" in self.datadict and "password" in self.datadict
        else:
            v = True
        if v:
            if self.user_validator is not None:
                return self.user_validator(self.datadict["name"], self.datadict["password"])
            else:
                return True
        else:
            return False


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
    
    def enable_pane(self):
        self._enablewidgets([self.user_label,self.user_display, self.user_button])
    
    def disable_pane(self):
        self._disablewidgets([self.user_label,self.user_display, self.user_button])
    
    def set_style(self, ttk_style):
        self._setstyle([self.user_label, self.user_display], ttk_style)
    
    def focus(self):
        """Set the focus to the button."""
        self.user_button.focus_set()

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def set_keys(self, user_key_name, password_key_name):
        """Change the names of the data keys used for the entered data.
        
        :param user_key_name: New name for the key for the user's name.
        :param password_key_name: New name for the key for the user's password.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other UserPane objects on the same UI.
        """
        if self.userkeyname in self.datadict:
            self.datadict[user_key_name] = self.datadict[self.userkeyname]
            del self.datadict[self.userkeyname]
        self.userkeyname = user_key_name
        if self.passkeyname in self.datadict:
            self.datadict[password_key_name] = self.datadict[self.passkeyname]
        self.passkeyname = password_key_name
        self.userkeylist = [user_key_name, password_key_name]

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
    
    def set_user_validator(self, fn):
        """Set the callback function that will be used to check the entered user name and password.
        
        This function must take the user name and password as arguments and return a Boolean.
        """
        self.user_validator = fn



class UserPasswordPane(tkpane.TkPane):
    """Display a user's name and a button to prompt for a user's name and password.
    
    Data keys managed by this pane: "name" and "password".
    
    Name used by this pane: "User credentials".
    
    Overridden methods:
    
    * valid_data
    * save_data
    * clear_pane
    * enable_pane
    * disable_pane
    * send_status_message
    * set_style
    * focus
    
    Custom method:
    
    * set_user_validator
    """

    def __init__(self, parent):
        tkpane.TkPane.__init__(self, parent, "User credentials", config_opts=frame_config_opts(), grid_opts=frame_grid_opts())
        self.user_validator = None
        self.user_label = ttk.Label(self, text='User name:', width=10, anchor=tk.E)
        self.pw_label = ttk.Label(self, text='Password:', width=10, anchor=tk.E)
        self.user_var = tk.StringVar()
        self.user_var.trace("w", self.check_namechange)
        self.pw_var = tk.StringVar()
        self.pw_var.trace("w", self.check_pwchange)
        self.userkeyname = "name"
        self.passkeyname = "password"
        self.datakeylist = [self.userkeyname, self.passkeyname]
        self.user_display = ttk.Entry(self, textvariable=self.user_var)
        self.pw_display = ttk.Entry(self, textvariable=self.pw_var, show="*")
        self.user_label.grid(row=0, column=0, padx=6, pady=3, sticky=tk.EW)
        self.pw_label.grid(row=1, column=0, padx=6, pady=3, sticky=tk.EW)
        self.user_display.grid(row=0, column=1, padx=6, pady=3, sticky=tk.EW)
        self.pw_display.grid(row=1, column=1, padx=6, pady=3, sticky=tk.EW)
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
        name = self.user_var.get()
        pw = self.pw_var.get()
        if self.required:
            v = (len(name) > 0 and len(pw) > 0)
        else:
            v = (not (len(name) == 0 and len(pw) > 0))
        if v:
            if self.user_validator is not None:
                return self.user_validator(name, pw)
            else:
                return True
        else:
            return False

    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the Entry widgets."""
        name = self.user_var.get()
        pw = self.pw_var.get()
        if is_valid:
            if name == "":
                self.clear_own()
            else:
                self.datadict["name"] = name
                self.datadict["password"] = pw
        else:
            self.clear_own()

    def send_status_message(self, is_valid):
        """Send a status message reporting data values and/or validity if data have changed."""
        # This overrides the class method because only the user name should be reported.
        if self.datadict != self.original_values:
            if is_valid:
                if "name" in self.datadict:
                    self.report_status(u"User name set to %s." % self.datadict["name"])
                else:
                    self.report_status(u"User name cleared.")
            else:
                self.report_status("User name is invalid.")

    def clear_pane(self):
        self.user_var.set("")
        self.pw_var.set("")
    
    def enable_pane(self):
        self._enablewidgets([self.user_label, self.pw_label, self.user_display, self.pw_display])
    
    def disable_pane(self):
        self._disablewidgets([self.user_label, self.pw_label, self.user_display, self.pw_display])
    
    def set_style(self, ttk_style):
        self._setstyle([self.user_label, self.pw_label, self.user_display, self.pw_display], ttk_style)
    
    def focus(self):
        """Set the focus to the user name."""
        self.user_display.focus_set()

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def set_keys(self, user_key_name, password_key_name):
        """Change the names of the data keys used for the entered data.
        
        :param user_key_name: New name for the key for the user's name.
        :param password_key_name: New name for the key for the user's password.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other UserPasswordPane objects on the same UI.
        """
        if self.userkeyname in self.datadict:
            self.datadict[user_key_name] = self.datadict[self.userkeyname]
            del self.datadict[self.userkeyname]
        self.userkeyname = user_key_name
        if self.passkeyname in self.datadict:
            self.datadict[password_key_name] = self.datadict[self.passkeyname]
        self.passkeyname = password_key_name
        self.userkeylist = [user_key_name, password_key_name]

    def check_namechange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.user_display)
    
    def check_pwchange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.pw_display)

    def set_user_validator(self, fn):
        """Set the callback function that will be used to check the entered user name and password.
        
        This function must take the user name and password as arguments and return a Boolean.
        """
        self.user_validator = fn


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
    * set_style
    * focus
    * set_data
    """
    
    def __init__(self, parent, optiondict=None):
        tkpane.TkPane.__init__(self, parent, "Output directory", frame_config_opts(), frame_grid_opts())
        # Customize attributes
        self.optiondict = {} if optiondict is None else optiondict
        self.datakey = "output_dir"
        self.datakeylist = [self.datakey]
        # Create, configure, and place widgets.
        self.dir_label = tk.Label(self, text='Output directory:', width=18, anchor=tk.E)
        self.dir_var = tk.StringVar()
        self.dir_var.trace("w", self.check_entrychange)
        self.dir_display = ttk.Entry(self, textvariable=self.dir_var)
        self.valid_color = self.dir_display.cget("background")
        self.dir_button = ttk.Button(self, text='Browse', width=8, command=self.set_outputdir)
        self.dir_label.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
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
                self.clear_own()
            else:
                self.datadict[self.datakey] = outputdir
        else:
            self.clear_own()
    
    def clear_pane(self):
        self.dir_var.set("")

    def enable_pane(self):
        self._enablewidgets([self.dir_display, self.dir_button])

    def disable_pane(self):
        self._disablewidgets([self.dir_display, self.dir_button])
    
    def set_style(self, ttk_style):
        self._setstyle([self.dir_display, self.dir_button], ttk_style)
    
    def focus(self):
        """Set the focus to the entry."""
        self.dir_display.focus_set()

    def set_data(self, data):
        """Update the pane's data dictionary.
        
        Special key supported: 'directory' changes the directory name in the entry display.
        """
        spkey = "directory"
        if spkey in data:
            self.dir_var.set(data[spkey])
            self.handle_change_validity(True, self.dir_display)
            self.send_status_message(True)
        self.set_allbut(data, [spkey])

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other OutputDirPane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]

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
    * set_style
    * focus
    * set_data
    """
    def __init__(self, parent, optiondict=None):
        tkpane.TkPane.__init__(self, parent, "Output filename", frame_config_opts(), frame_grid_opts())
        # Customize attributes
        self.optiondict = {} if optiondict is None else optiondict
        self.datakey = "output_filename"
        self.datakeylist = [self.datakey]
        # Create, configure, and place widgets.
        self.dir_label = ttk.Label(self, text='Output file:', width=12, anchor=tk.E)
        self.file_var = tk.StringVar()
        self.file_var.trace("w", self.check_entrychange)
        self.file_display = ttk.Entry(self, textvariable=self.file_var)
        self.valid_color = self.file_display.cget("background")
        self.browse_button = tk.Button(self, text='Browse', width=8, command=self.set_outputfile)
        self.dir_label.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
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
                self.clear_own()
            else:
                self.datadict[self.datakey] = filename
        else:
            self.clear_own()
    
    def clear_pane(self):
        self.file_var.set("")

    def enable_pane(self):
        self._enablewidgets([self.file_display, self.browse_button])

    def disable_pane(self):
        self._disablewidgets([self.file_display, self.browse_button])
    
    def set_style(self, ttk_style):
        self._setstyle([self.dir_label, self.file_display], ttk_style)
    
    def focus(self):
        """Set the focus to the entry."""
        self.file_display.focus_set()

    def set_data(self, data):
        """Update the pane's data dictionary with the provided data.
        
        Special key supported: 'output_filename' changes the filename in the display.
        """
        if self.datakey in data:
            self.file_var.set(data[self.datakey])
            self.handle_change_validity(True, self.file_display)
            self.send_status_message(True)
        self.set_allbut(data, [self.datakey])

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other OutputFilePane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]

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
    * set_style
    * focus
    * set_data
    """

    def __init__(self, parent, optiondict=None):
        tkpane.TkPane.__init__(self, parent, "Input filename", frame_config_opts(), frame_grid_opts())
        # Customize attributes
        self.optiondict = {} if optiondict is None else optiondict
        self.datakey = "input_filename"
        self.datakeylist = [self.datakey]
        # Create, configure, and place widgets.
        self.dir_label = ttk.Label(self, text='Input file:', width=12, anchor=tk.E)
        self.file_var = tk.StringVar()
        self.file_var.trace("w", self.check_entrychange)
        self.file_display = ttk.Entry(self, textvariable=self.file_var)
        self.valid_color = self.file_display.cget("background")
        self.browse_button = ttk.Button(self, text='Browse', width=8, command=self.set_inputfile)
        self.dir_label.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
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
                self.clear_own()
            else:
                self.datadict[self.datakey] = filename
        else:
            self.clear_own()

    
    def clear_pane(self):
        self.file_var.set(u'')

    def enable_pane(self):
        self._enablewidgets([self.dir_label, self.file_display, self.browse_button])

    def disable_pane(self):
        self._disablewidgets([self.dir_label, self.file_display, self.browse_button])

    def set_style(self, ttk_style):
        self._setstyle([self.dir_label, self.file_display, self.browse_button], ttk_style)
    
    def focus(self):
        """Set the focus to the entry."""
        self.file_display.focus_set()

    def set_data(self, data):
        """Update the pane's data dictionary with the provide data.
        
        Special key supported: 'input_filename' changes the filename in the entry widget.
        """
        if self.datakey in data:
            self.file_var.set(data[self.datakey])
            self.handle_change_validity(True, self.file_display)
            self.send_status_message(True)
        self.set_allbut(data, [self.datakey])

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other InputFilePane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]

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
    
    :param key_name: The name to be used with the internal data dictionary to identify the text data; use to avoid name conflicts with other TextPane objecs on the same UI (optional).
    :param optiondict: A dictionary of option names and values for initial configuration of the Text widget (optional).
    :parame initial_text: Initial contents for the Text widget (optional).
    
    Because of the large number of uses of the Text widget, this pane
    provides direct access to the Text widget via the 'textwidget' method.
    To simplify use, this pane also provides direct methods for appending to,
    replacing, and clearing the contents of the Text widget.
    The custom methods 'set_status' and 'clear_status' allow a TextPane to
    be used as a status_reporter callback for any other type of pane.
    
    Data keys managed by this pane: "text" or the key name specified during initialization.
    
    Name used by this pane: "Text".
    
    Overridden methods:
    
    * entry_widgets
    * save_data
    * valid_data
    * clear_pane
    * enable_pane
    * disable_pane
    * set_style
    * focus
    * set_data
    
    Custom methods:
    
    * textwidget
    * replace_all
    * append
    * set_status
    * clear_status
    * set_key
    """

    def __init__(self, parent, key_name=None, optiondict=None, initial_text=None):
        tkpane.TkPane.__init__(self, parent, "Text", frame_config_opts(), frame_grid_opts())
        opts = {} if optiondict is None else optiondict
        self.datakeyname = "text" if key_name is None else key_name
        self.datakeylist = [self.datakeyname]
        self.textwidget = tk.Text(self, exportselection=False, **opts)
        self.textwidget.bind("<Key>", self.check_entrychange)
        self.ysb = ttk.Scrollbar(self, orient='vertical', command=self.textwidget.yview)
        self.xsb = ttk.Scrollbar(self, orient='horizontal', command=self.textwidget.xview)
        self.textwidget.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        if initial_text is not None:
            self.replace_all(initial_text)
        self.textwidget.grid(row=0, column=0, padx=(3,0), pady=(3,0), sticky=tk.NSEW)
        self.ysb.grid(column=1, row=0, padx=(0,3), pady=(3,0), sticky=tk.NS)
        self.xsb.grid(column=0, row=1, padx=(3,0), pady=(0,3), sticky=tk.EW)
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
                self.clear_own()
            else:
                self.datadict["text"] = text
        else:
            self.clear_own()

    def valid_data(self, entry_widget=None):
        text = self.textwidget.get("1.0", tk.END)
        return not (text == "" and self.required)
    
    def clear_pane(self):
        widget_state = self.textwidget.cget("state")
        self.textwidget.configure(state=tk.NORMAL)
        self.textwidget.delete("1.0", tk.END)
        self.textwidget.configure(state=widget_state)
    
    def enable_pane(self):
        self._enablewidgets([self.textwidget, self.xsb, self.ysb])
        self.textwidget.configure(state=tk.NORMAL)
    
    def disable_pane(self):
        self._disablewidgets([self.xsb, self.ysb])
        self.textwidget.configure(state=tk.DISABLED)
    
    def set_style(self, ttk_style):
        """Sets the style of the scrollbars.
        
        Note that the Text widget is not a ttk themed widget, and so no ttk style can be applied.
        """
        self._setstyle([self.xsb, self.ysb], ttk_style)
    
    def focus(self):
        """Set the focus to the text widget."""
        self.textwidget.focus_set()

    def set_data(self, data):
        """Update the pane's data dictionary with the provided data.
        
        Special keys supported: 'text' changes the contents of the text widget.
        """
        if "text" in data:
            self.replace_all(data["text"])
        self.set_allbut(data, ["text"])

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def textwidget(self):
        """Return the text widget object, to allow direct manipulation."""
        return self.textwidget
    
    def check_entrychange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.textwidget)

    def replace_all(self, new_contents):
        self.clear_pane()
        self.textwidget.insert(tk.END, new_contents)
        self.datadict["text"] = new_contents
    
    def append(self, more_text, scroll=True):
        """Inserts the given text at the end of the Text widget's contents."""
        widget_state = self.textwidget.cget("state")
        self.textwidget.configure(state=tk.NORMAL)
        self.textwidget.insert(tk.END, more_text)
        if scroll:
            self.textwidget.see("end")
        self.textwidget.configure(state=widget_state)
    
    def set_status(self, status_msg):
        """Inserts the status message at the end of the Text widget's contents."""
        if len(status_msg) > 0 and status_msg[-1] != u"\n":
            status_msg += u"\n"
        self.append(status_msg)
    
    def clear_status(self):
        """Clear the entire widget."""
        self.clear()
    
    def set_key(self, key_name):
        """Change the name of the data key used for the text data.
        
        :param key_name: New name for the text data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other TextPane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]
    


class StatusProgressPane(tkpane.TkPane):
    """Display a status bar and progress bar.
    
    There are no data keys managed by this pane.
    
    Overridden methods:
    
    * clear_pane
    * set_style
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
        self.statusbar = ttk.Label(parent, text='', textvariable=self.status_msg, relief=tk.RIDGE, anchor=tk.W)
        self.progressmode = 'determinate'
        self.ctrprogress = ttk.Progressbar(parent, mode=self.progressmode, maximum=100,
                                      orient='horizontal', length=150, variable=self.ctrvalue)
        self.statusbar.grid(row=0, column=0, sticky=tk.EW)
        self.ctrprogress.grid(row=0, column=1, sticky=tk.EW)
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

    def set_style(self, ttk_style):
        self._setstyle([self.statusbar, self.ctrprogress], ttk_style)
    
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
    
    def set_data(self, data):
        """Update the pane's data dictionary with the provided data.
        
        Special keys supported: 'message' and 'value'.
        * message: New status message.
        * value: New value for the progress bar.
        """
        if "message" in data:
            self.set_status(data["message"])
        if "value" in data:
            self.set_value(data["value"])
        self.set_allbut(data, ["message", "value"])

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
    * set_data
    
    Custom methods:
    
    * display_data
    """
    def __init__(self, parent, message=None, column_headers=[], rowset=[]):
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
        self.ysb = ttk.Scrollbar(tableframe, orient='vertical', command=self.tbl.yview)
        self.xsb = ttk.Scrollbar(tableframe, orient='horizontal', command=self.tbl.xview)
        self.tbl.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        tableframe.grid(column=0, row=1 if message is not None else 0, sticky=tk.NSEW)
        self.tbl.grid(column=0, row=0, sticky=tk.NSEW)
        self.ysb.grid(column=1, row=0, sticky=tk.NS)
        self.xsb.grid(column=0, row=1, sticky=tk.EW)
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
    
    def set_data(self, data):
        """Update the pane's data dictionary with the provided data.
        
        Special keys supported: 'message' and 'table'.
        * message: Text to replace the message above the table.
        * table: the value should be a two-element tuple, of which the 
        first element is a list of the column header names and the second is a 
        list (rows) of lists (columns) containing the table's data.
        """
        if "message" in data:
            self.msg_label.configure(text=data["message"])
        if "table" in data:
            self.display_data(data["table"][0], data["table"][1])
        self.set_allbut(data, ["message", "table"])

    def clear_pane(self):
        for item in self.tbl.get_children():
            self.tbl.delete(item)
        self.tbl.configure(columns=[""])

    def set_style(self, ttk_style):
        self._setstyle([self.msg_label, self.tbl, self.ysb, self.xsb], ttk_style)
    
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


class TableSelectPane(tkpane.TkPane):
    """Display a specified data table and allow a row to be selected.
        
    :param message: A message to display above the data table.
    :param column_headers: A list of the column names for the data table.
    :param rowset: An iterable that yields lists of values to be used as rows for the data table.
    
    Data key managed by this pane: "table_data".
    
    * table_data: A dictionary of the selected data; keys are the table column names.
    
    Name used by this pane: "Table select".
    
    Overridden methods:
    
    * valid_data
    * save_data
    * clear_pane
    * focus
    * set_data
    
    Custom methods:
    
    * display_data
    """
    def __init__(self, parent, message=None, column_headers=[], rowset=[]):
        tkpane.TkPane.__init__(self, parent, "Table select", frame_config_opts(), frame_grid_opts())
        self.datakeyname = "table_data"
        self.datakeylist = [self.datakeyname]
        # Message frame and control.
        self.msg_label = None
        self.column_headers = []
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
        self.tbl = ttk.Treeview(tableframe, columns=column_headers, selectmode="browse", show="headings")
        self.ysb = ttk.Scrollbar(tableframe, orient='vertical', command=self.tbl.yview)
        self.xsb = ttk.Scrollbar(tableframe, orient='horizontal', command=self.tbl.xview)
        self.tbl.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
        tableframe.grid(column=0, row=1 if message is not None else 0, sticky=tk.NSEW)
        self.tbl.grid(column=0, row=0, sticky=tk.NSEW)
        self.ysb.grid(column=1, row=0, sticky=tk.NS)
        self.xsb.grid(column=0, row=1, sticky=tk.EW)
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

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        return [self.tbl]

    def valid_data(self, entry_widget=None):
        selected = self.tbl.selection()
        return not (len(selected) == 0 and self.required)
    
    def save_data(self, is_valid, entry_widget):
        if is_valid:
            self.datadict[self.datakeyname] = self.tbl.set(self.tbl.selection())
        else:
            if self.datakeyname in self.datadict:
                del self.datadict[self.datakeyname]

    def clear_pane(self):
        if len(self.tbl.selection()) > 0:
            self.tbl.selection_remove(self.tbl.selection()[0])

    def enable_pane(self):
        self._enablewidgets([self.msg_label, self.tbl])
        self.tbl.configure(selectmode="browse")
    
    def disable_pane(self):
        self._disablewidgets([self.msg_label, self.tbl])
        self.tbl.configure(selectmode="none")
    
    def set_style(self, ttk_style):
        self._setstyle([self.msg_label, self.tbl], ttk_style)
    
    def focus(self):
        self.tbl.focus_set()
    
    def set_data(self, data):
        """Update the pane's data dictionary with the provided data.
        
        Special keys supported: 'message' and 'table'.
        * message: Text to replace the message above the table.
        * table: the value should be a two-element tuple, of which the 
        first element is a list of the column header names and the second is a 
        list (rows) of lists (columns) containing the table's data.
        """
        if "message" in data:
            self.msg_label.configure(text=data["message"])
        if "table" in data:
            self.display_data(data["table"][0], data["table"][1])
        self.set_allbut(data, ["message", "table"])

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other TableSelectPane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]

    def set_style(self, ttk_style):
        self._setstyle([self.msg_label, self.tbl, self.ysb, self.xsb], ttk_style)
    
    def display_data(self, column_headers, rowset):
        """Display a new data set on the pane.
        
        :param column_headers: A list of strings for the headers of the data columns.
        :param rowset: A list of lists of data values to display.  The outer list is rows, the inner lists are columns.
        """
        self.column_headers = column_headers
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

    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other EntryPane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]


class OkCancelPane(tkpane.TkPane):
    """Display OK and Cancel buttons.
    
    There are no data keys specific to this pane.
    
    Overridden methods:
    
    * disable_pane
    * enable_pane
    * set_style
    * focus
    
    Custom methods:
    
    * set_cancel_action
    * set_ok_action
    * ok
    * cancel
    """
    def __init__(self, parent, ok_action=None, cancel_action=None):
        def do_nothing(data_dict):
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
        self._enablewidgets([self.ok_btn])

    def disable_pane(self):
        self._disablewidgets([self.ok_btn])

    def set_style(self, ttk_style):
        self._setstyle([self.cancel_btn, self.ok_btn], ttk_style)
    
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
        """Trigger this pane's 'OK' action.  The callback function will be passed this pane's data dictionary."""
        self.ok_action(self.datadict)

    def cancel(self):
        """Trigger this pane's 'Cancel' action."""
        self.cancel_action()


class EntryPane(tkpane.TkPane):
    """Display a Tkinter Entry widget.
    
    :param pane_name: The name to be used to identify this pane in status messages.
    :param prompt: The prompt to be presented in a Label widget adjacent to the entry.
    :param key_name: The name to be used with the internal data dictionary to identify the entry data; use to avoid name conflicts with other EntryPane objects on the same UI (optional).

    Data keys managed by this pane: "entry" or the key name specified during initialization.
    
    Name used by this pane: user-defined on initialization.
    
    Overridden methods:
    
    * entry_widgets
    * valid_data
    * save_data
    * clear_pane
    * enable_pane
    * disable_pane
    * set_style
    * focus
    * set_data
    
    Custom method:
    
    * set_key
    """

    def __init__(self, parent, pane_name, prompt, key_name=None):
        tkpane.TkPane.__init__(self, parent, pane_name, frame_config_opts(), frame_grid_opts())
        self.datakeyname = "entry" if key_name is None else key_name
        self.datakeylist = [self.datakeyname]
        self.prompt = ttk.Label(self, text=prompt, width=max(12, len(prompt)), anchor=tk.E)
        self.entry_var = tk.StringVar()
        self.entrywidget = ttk.Entry(self, textvariable=self.entry_var, exportselection=False)
        self.prompt.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        self.entrywidget.grid(row=0, column=1, padx=3, pady=3, sticky=tk.EW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.entry_var.trace("w", self.check_entrychange)

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
                self.clear_own()
            else:
                self.datadict[self.datakeyname] = text
        else:
            self.clear_own()

    def clear_pane(self):
        self.entry_var.set("")
    
    def enable_pane(self):
        self._enablewidgets([self.prompt, self.entrywidget])
    
    def disable_pane(self):
        self._disablewidgets([self.prompt, self.entrywidget])
    
    def set_style(self, ttk_style):
        self._setstyle([self.prompt, self.entrywidget], ttk_style)
    
    def focus(self):
        """Set the focus to the entry."""
        self.entrywidget.focus_set()

    def set_data(self, data):
        """Update the pane's data dictionary with the provided data.
        
        Special key supported: 'prompt' changes the pane's prompt.
        """
        spkey = "prompt"
        if spkey in data:
            self.prompt.configure(text=data[spkey])
        self.set_allbut(data, [spkey])

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def check_entrychange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.entrywidget)
    
    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other EntryPane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]


class ButtonPane(tkpane.TkPane):
    """Display a simple text button with configurable text and action.
    
    :param pane_name: The name to be used to identify this pane in status messages.
    :param button_text: The text to display on the button.
    :param button_action: A callback to perform an action when the button is clicked.
    :param width: The width of the button, in characters (optional).
    
    There are no data keys specific to this pane.
    
    Overridden methods:
    
    * disable_pane
    * enable_pane
    * set_style
    * focus
    * set_data
    
    Custom methods:
    
    * set_button_action
    * do_button_action
    """
    def __init__(self, parent, button_text, pane_name="button", button_action=None, width=None):
        def do_nothing(data_dict):
            pass
        tkpane.TkPane.__init__(self, parent, pane_name, frame_config_opts(), frame_grid_opts())
        self.button_text = button_text
        self.action = button_action if button_action is not None else do_nothing
        self.btn = ttk.Button(self, text=self.button_text, command=self.do_button_action)
        if width is not None:
            self.btn.configure(width=width)
        self.btn.grid(row=0, column=1, padx=3, sticky=tk.E)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        parent.rowconfigure(0, weight=0)
        parent.columnconfigure(0, weight=1)

    def enable_pane(self):
        self._enablewidgets([self.btn])

    def disable_pane(self):
        self._disablewidgets([self.btn])

    def set_style(self, ttk_style):
        self._setstyle([self.btn], ttk_style)
    
    def focus(self):
        """Set the focus to the button."""
        self.btn.focus_set()
    
    def set_data(self, data_dict):
        """Update the pane's data dictionary with the provided data.
        
        Special keys are:
        * button_text: Contains the text to place on the button.
        * button_width: Contains the width for the button.
        
        All other data in the passed dictionary are added to the button's own data dictionary.
        """
        if "button_text" in data_dict:
            self.btn.configure(text=data_dict["button_text"])
        if "button_width" in data_dict:
            self.btn.configure(width=data_dict["button_width"])
        self.set_allbut(data, ["button_text", "button_width"])

    def set_button_action(self, button_action):
        """Specify the callback function to be called when the button is clicked."""
        self.action = button_action if button_action is not None else do_nothing
        self.btn.configure(command=self.action)

    def do_button_action(self):
        """Trigger this pane's action.  The callback function will be passed this pane's data dictionary."""
        self.action(self.datadict)


class EmptyPane(tkpane.TkPane):
    """A pane with no widgets that can be used as a spacer."""
    def __init__(self, parent):
        tkpane.TkPane.__init__(self, parent, "empty_pane", frame_config_opts(), frame_grid_opts())
        self.pack(expand=True, fill=tk.BOTH)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)


class CheckboxPane(tkpane.TkPane):
    """Display a Tkinter Checkbutton widget to accept True and False values.
    
    :param pane_name: The name to be used to identify this pane in status messages.
    :param prompt: The text associated with the checkbox.
    :param valid_state: Either True or False to indicate that either the checked or unchecked state (only) is to be considered valid.  If not specified (the default), the checkbox will always be considered to have valid data.
    :param key_name: The name to be used with the internal data dictionary to identify the entry data; use to avoid name conflicts with other CheckboxPane objects on the same UI (optional).
    :param config_opts: A dictionary of configuration options for the Checkbutton widget.

    Data keys managed by this pane: "check" or the key name specified during initialization.
    The value of this item is always True or False, and defaults to False.
    
    Name used by this pane: user-defined on initialization.
    
    Overridden methods:
    
    * entry_widgets
    * valid_data
    * save_data
    * clear_pane
    * enable_pane
    * disable_pane
    * set_style
    * focus
    * set_data
    
    Custom methods:
    
    * set_key
    """

    def __init__(self, parent, pane_name, prompt, valid_state=None, key_name=None, config_opts=None):
        tkpane.TkPane.__init__(self, parent, pane_name, frame_config_opts(), frame_grid_opts())
        self.valid_state = valid_state
        self.datakeyname = "check" if key_name is None else key_name
        self.datakeylist = [self.datakeyname]
        self.checkvar = tk.BooleanVar()
        self.checkvar.set(False)
        self.datadict[self.datakeyname] = self.checkvar.get()
        self.checkbox = ttk.Checkbutton(self, text=prompt, variable=self.checkvar, onvalue=True, offvalue=False)
        if config_opts is not None:
            self.checkbox.configure(**config_opts)
        self.checkbox.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.checkvar.trace("w", self.check_checkchange)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        return [self.checkbox]
    
    def valid_data(self, widget):
        """Returns an indication of whether the checkbox is in a valid state."""
        if self.valid_state is None:
            return True
        else:
            return self.checkvar.get() == self.valid_state

    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the Checkbutton widget."""
        state = self.checkvar.get()
        self.datadict[self.datakeyname] = state

    def clear_pane(self):
        self.checkvar.set(False)
    
    def enable_pane(self):
        self._enablewidgets([self.checkbox])
    
    def disable_pane(self):
        self._disablewidgets([self.checkbox])
    
    def set_style(self, ttk_style):
        self._setstyle([self.checkbox], ttk_style)
    
    def focus(self):
        """Set the focus to the checkbox."""
        self.checkbox.focus_set()

    def set_data(self, data):
        """Update the pane's data dictionary with the provided data.
        
        Special key supported: 'prompt' changes the pane's prompt.
        """
        spkey = "prompt"
        if spkey in data:
            self.checkbox.configure(text=data[spkey])
        self.set_allbut(data, [spkey])

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def check_checkchange(self, *args):
        self.handle_change_validity(self.valid_data(self.checkbox), self.checkbox)
    
    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other CheckboxPane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]


class ListboxPane(tkpane.TkPane):
    """Display a Tkinter Listbox.
    
    :param pane_name: The name to be used to identify this pane in status messages.
    :param items: The list of items to be initially displayed in the listbox.
    :param rows: The number of rows (items) to be shown; the listbox will have a scrollbar (optional).
    :param key_name: The name to be used with the internal data dictionary to identify the selected list entries; use to avoid name conflicts with other ListboxPane objects on the same UI (optional).
    :param mode: The selection mode to use; "single", "browse", "multiple", or "extended" (optional; default is "extended").

    Data key managed by this pane: "listbox" or the key name specified during initialization.
    
    The value of the data managed by this pane is a list of the selected items.
    
    Name used by this pane: user-defined on initialization.
    
    Overridden methods:
    
    * entry_widgets
    * valid_data
    * save_data
    * clear_pane
    * enable_pane
    * disable_pane
    * set_style
    * focus
    
    Custom methods:
    
    * set_newitems
    * set_key
    """

    def __init__(self, parent, pane_name, items, rows=None, width=None, key_name=None, mode=None):
        tkpane.TkPane.__init__(self, parent, pane_name, frame_config_opts(), frame_grid_opts())
        self.datakeyname = "listbox" if key_name is None else key_name
        self.datakeylist = [self.datakeyname]
        self.scroller = ttk.Scrollbar(self, orient=tk.VERTICAL)
        ht = 10 if rows is None else rows
        selmode = "extended" if mode is None else mode
        self.listbox = tk.Listbox(self, selectmode=selmode, exportselection=False, yscrollcommand=self.scroller.set, height=ht)
        if width is not None:
            self.listbox.configure(width=width)
        self.listbox.bind("<<ListboxSelect>>", self.check_entrychange)
        self.scroller.config(command=self.listbox.yview)
        for item in items:
            self.listbox.insert(tk.END, item)
        self.listbox.grid(row=0, column=0, padx=(3,0), pady=3, sticky=tk.NSEW)
        self.scroller.grid(row=0, column=1, padx=(0,3), pady=3, sticky=tk.NS)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        return [self.listbox]
    
    def valid_data(self, widget):
        """Returns an indication of whether the listbox is both required and has at least one selection."""
        if self.required:
            selected = self.listbox.curselection()
            if isinstance(selected, tuple):
                return len(selected) > 0
            else:
                return selected is not None
        else:
            return True

    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the Listbox widget."""
        if is_valid:
            items = map(int, self.listbox.curselection())
            self.datadict[self.datakeyname] = [self.listbox.get(i) for i in items]
        else:
            self.clear_own()

    def clear_pane(self):
        self.listbox.selection_clear(0, tk.END)
    
    def enable_pane(self):
        self.listbox.configure(state=tk.NORMAL)
    
    def disable_pane(self):
        self.listbox.configure(state=tk.DISABLED)
    
    def set_style(self, ttk_style):
        """Sets the style of the scrollbar accompanying the listbox.
        
        The Listbox widget is not a themed ttk widget and cannot have a style applied.
        """
        self._setstyle([self.scroller], ttk_style)
    
    def focus(self):
        """Set the focus to the listbox."""
        self.listbox.focus_set()

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def check_entrychange(self, event):
        self.handle_change_validity(self.valid_data(self.listbox), self.listbox)

    def set_newitems(self, items):
        """Change the items displayed in the list.  This will clear any selection."""
        contents = self.listbox.get(0, tk.END)
        if any(list(set(contents) ^ set(items))):
            self.clear_pane()
            if self.datakeyname in self.datadict:
                del self.datadict[self.datakeyname]
            self.listbox.delete(0, tk.END)
            for item in items:
                self.listbox.insert(tk.END, item)
            self.handle_change_validity(self.valid_data(self.listbox), self.listbox)

    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other ListboxPane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]



class NotebookPane(tkpane.TkPane):
    """Create and populate a Tkinter Notebook widget.
    
    :param pane_name: The name to be used to identify this pane in status messages.
    :param tab_specs: A list or tuple of two-element tuples; each two-element tuple contains the tab's label and a `build` function that is passed the Notebook widget and should populate the tab page with widgets and return the frame enclosing all widgets on that page.
    
    This pane does not manage any data.
    
    Name used by this pane: user-defined on initialization.
    
    Overridden methods:
    
    * set_style
    
    Custom methods:
    
    * notebook_widget
    """

    def __init__(self, parent, pane_name, tab_specs):
        tkpane.TkPane.__init__(self, parent, pane_name, frame_config_opts(), frame_grid_opts())
        self.tabids = {}
        self.tabframes = {}
        self.nb_widget = ttk.Notebook(self)
        id_no = 0
        for tab in tab_specs:
            tabframe = tab[1](self.nb_widget)
            self.nb_widget.add(tabframe, text=tab[0])
            self.tabids[tab[0]] = id_no
            self.tabframes[tab[0]] = tabframe
            id_no += 1
        self.nb_widget.enable_traversal()
        self.nb_widget.grid(row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def set_style(self, ttk_style):
        self._setstyle([self.nb_widget], ttk_style)
    
    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def notebook_widget(self):
        """Return the Notebook widget."""
        return self.nb_widget
    
    def tab_id(self, tab_name):
        """Return the tab ID (integer) corresponding to the tab's name or label."""
        return self.tabid[tab_name]

    def tab_frames(self):
        """Return a dictionary of tab names and the frame enclosing the contents for the tab."""
        return self.tabframes

    def tab_frame(self, tab_name):
        """Return the frame corresponding to the tab's name or label."""
        return self.tabframes[tab_name]



class ScalePane(tkpane.TkPane):
    """Display a Tkinter Scale widget.
    
    :param pane_name: The name to be used to identify this pane in status messages.
    :param orientation: 
    :param length: 
    :param min_value: 
    :param max_value: 
    :param init_value: 
    :param key_name: The name to be used with the internal data dictionary to identify the entry data; use to avoid name conflicts with other EntryPane objects on the same UI (optional).
    :param config_opts: A dictionary of scale widget configuration options

    Data keys managed by this pane: "scale" or the key name specified during initialization.
    
    Name used by this pane: user-defined on initialization.
    
    This pane (the Scale widget) is considered to always have valid data.
    
    Overridden methods:
    
    * entry_widgets
    * save_data
    * enable_pane
    * disable_pane
    * set_style
    * focus
    
    Custom methods:
    
    * scalewidget
    * set_key
    """

    def __init__(self, parent, pane_name, orientation, length, min_value, max_value, init_value, key_name=None, config_opts=None):
        tkpane.TkPane.__init__(self, parent, pane_name, frame_config_opts(), frame_grid_opts())
        self.datakeyname = "scale" if key_name is None else key_name
        self.datakeylist = [self.datakeyname]
        self.entry_var = tk.DoubleVar()
        self.entry_var.set(init_value)
        self.entrywidget = ttk.Scale(self, variable=self.entry_var, length=length, orient=orientation, from_=min_value, to=max_value, value=init_value)
        if config_opts is not None:
            self.entrywidget.configure(**config_opts)
        sticky = tk.EW if orientation == tk.HORIZONTAL else tk.NS
        self.entrywidget.grid(row=0, column=0, padx=3, pady=3, sticky=sticky)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.entry_var.trace("w", self.check_entrychange)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        return [self.entrywidget]

    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the Scale widget."""
        scale_value = self.entry_var.get()
        self.datadict[self.datakeyname] = scale_value

    def enable_pane(self):
        self._enablewidgets([self.entrywidget])
    
    def disable_pane(self):
        self._disablewidgets([self.entrywidget])
    
    def set_style(self, ttk_style):
        self._setstyle([self.entrywidget], ttk_style)
    
    def focus(self):
        """Set the focus to the entry."""
        self.entrywidget.focus_set()

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................
    
    def scalewidget(self):
        """Returns the Scale widget."""
        return self.entrywidget

    def check_entrychange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.entrywidget)
    
    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other ScalePane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]


class SpinboxPane(tkpane.TkPane):
    """Display a Tkinter Spinbox widget with a prompt.
    
    :param pane_name: The name to be used to identify this pane in status messages.
    :param prompt: The prompt to be presented in a Label widget adjacent to the entry.
    :param min_value: The minimum value that can be selected.
    :param max_value: The maximum value that can be selected.
    :param key_name: The name to be used with the internal data dictionary to identify the entry data; use to avoid name conflicts with other EntryPane objects on the same UI (optional).

    Data keys managed by this pane: "spinbox" or the key name specified during initialization.
    
    Name used by this pane: user-defined on initialization.
    
    Overridden methods:
    
    * entry_widgets
    * valid_data
    * save_data
    * clear_pane
    * enable_pane
    * disable_pane
    * focus
    * set_data
    
    Custom method:
    
    * set_key
    """

    def __init__(self, parent, pane_name, prompt, min_value, max_value, key_name=None, optiondict=None):
        tkpane.TkPane.__init__(self, parent, pane_name, frame_config_opts(), frame_grid_opts())
        self.min_value = min_value
        self.datakeyname = "spinbox" if key_name is None else key_name
        self.datakeylist = [self.datakeyname]
        self.prompt = ttk.Label(self, text=prompt, width=max(12, len(prompt)), anchor=tk.E)
        self.entry_var = tk.StringVar()
        self.entrywidget = tk.Spinbox(self, from_=min_value, to=max_value, textvariable=self.entry_var, width=len(str(max_value))+1, exportselection=False)
        self.entry_var.set(min_value)
        if optiondict is not None:
            self.entrywidget.configure(**optiondict)
        self.prompt.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        self.entrywidget.grid(row=0, column=1, padx=3, pady=3, sticky=tk.W)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.entry_var.trace("w", self.check_entrychange)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        return [self.entrywidget]

    def valid_data(self, entry_widget=None):
        text = self.entry_var.get()
        return not (text == "" and self.required)
    
    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the Spinbox widget."""
        text = self.entry_var.get()
        if is_valid:
            if text == "":
                self.clear_own()
            else:
                self.datadict[self.datakeyname] = text
        else:
            self.clear_own()

    def clear_pane(self):
        self.entry_var.set(self.min_value)
    
    def enable_pane(self):
        self._enablewidgets([self.prompt, self.entrywidget])
    
    def disable_pane(self):
        self._disablewidgets([self.prompt, self.entrywidget])
    
    def focus(self):
        """Set the focus to the entry."""
        self.entrywidget.focus_set()

    def set_data(self, data):
        """Update the pane's data dictionary with the provided data.
        
        Special key supported: 'prompt' changes the pane's prompt.
        """
        spkey = "prompt"
        if spkey in data:
            self.prompt.configure(text=data[spkey])
        self.set_allbut(data, [spkey])

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def check_entrychange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.entrywidget)
    
    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other SpinboxPane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]


class ComboboxPane(tkpane.TkPane):
    """Display a Tkinter Combobox widget with a prompt.
    
    :param pane_name: The name to be used to identify this pane in status messages.
    :param prompt: The prompt to be presented in a Label widget adjacent to the entry.
    :param items: The list of items to be included in the drop-down list.
    :param item_only: A Boolean indicating whether or not items from the list are the only valid entries.  Default: False.
    :param key_name: The name to be used with the internal data dictionary to identify the entry data; use to avoid name conflicts with other EntryPane objects on the same UI (optional).

    Data keys managed by this pane: "combobox" or the key name specified during initialization.
    
    Name used by this pane: user-defined on initialization.
    
    Overridden methods:
    
    * entry_widgets
    * valid_data
    * save_data
    * clear_pane
    * enable_pane
    * disable_pane
    * set_style
    * focus
    * set_data
    
    Custom method:
    
    * set_key
    """

    def __init__(self, parent, pane_name, prompt, items, item_only=False, key_name=None):
        tkpane.TkPane.__init__(self, parent, pane_name, frame_config_opts(), frame_grid_opts())
        self.items = items
        self.item_only = item_only
        self.datakeyname = "combobox" if key_name is None else key_name
        self.datakeylist = [self.datakeyname]
        self.prompt = ttk.Label(self, text=prompt, width=max(12, len(prompt)), anchor=tk.E)
        self.entry_var = tk.StringVar()
        self.entrywidget = ttk.Combobox(self, textvariable=self.entry_var, values=items, width=max(map(len, map(str, items)))+1, exportselection=False)
        self.prompt.grid(row=0, column=0, padx=3, pady=3, sticky=tk.EW)
        self.entrywidget.grid(row=0, column=1, padx=3, pady=3, sticky=tk.W)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        self.entry_var.trace("w", self.check_entrychange)

    #---------------------------------------------------------------------------
    #   Overrides of class methods.
    #...........................................................................

    def entry_widgets(self):
        return [self.entrywidget]

    def valid_data(self, entry_widget=None):
        text = self.entry_var.get()
        if self.required:
            if self.item_only:
                return text in self.items
            else:
                return text != ""
        else:
            if self.item_only:
                return text in self.items
            else:
                return True
    
    def save_data(self, is_valid, entry_widget):
        """Update the pane's data dictionary with data from the Combobox widget."""
        text = self.entry_var.get()
        if is_valid:
            if text == "":
                self.clear_own()
            else:
                self.datadict[self.datakeyname] = text
        else:
            self.clear_own()

    def clear_pane(self):
        self.entry_var.set("")
    
    def enable_pane(self):
        self._enablewidgets([self.prompt, self.entrywidget])
    
    def disable_pane(self):
        self._disablewidgets([self.prompt, self.entrywidget])
    
    def set_style(self, ttk_style):
        self._setstyle([self.prompt, self.entrywidget], ttk_style)
    
    def focus(self):
        """Set the focus to the entry."""
        self.entrywidget.focus_set()

    def set_data(self, data):
        """Update the pane's data dictionary with the provided data.
        
        Special key supported: 'prompt' changes the pane's prompt.
        """
        spkey = "prompt"
        if spkey in data:
            self.prompt.configure(text=data[spkey])
        self.set_allbut(data, [spkey])

    #---------------------------------------------------------------------------
    #   Custom methods.
    #...........................................................................

    def check_entrychange(self, *args):
        self.handle_change_validity(self.valid_data(None), self.entrywidget)
    
    def set_key(self, key_name):
        """Change the name of the data key used for the entered data.
        
        :param key_name: New name for the data key.
        
        This method allows the name of the data key to be customized to
        eliminate conflicts with other EntryPane objects on the same UI.
        """
        if self.datakeyname in self.datadict:
            self.datadict[key_name] = self.datadict[self.datakeyname]
            del self.datadict[self.datakeyname]
        self.datakeyname = key_name
        self.datakeylist = [key_name]

    def set_newitems(self, items):
        """Change the items displayed in the list.  This will clear any selection."""
        if any(list(set(self.items) ^ set(items))):
            self.clear_pane()
            if self.datakeyname in self.datadict:
                del self.datadict[self.datakeyname]
            self.entrywidget.configure(values=items)
            self.items = items
            self.handle_change_validity(self.valid_data(self.entrywidget), self.entrywidget)

