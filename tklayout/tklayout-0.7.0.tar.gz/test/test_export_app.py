#! /usr/bin/python
#
# test_export_app.py
#
# PURPOSE
#   Test the tkuibuilder library with a simple simulation of the
#   export_auditlog application.
#
# NOTES
#   1. The approach to using the tkuibuilder library is:
#       1. Design the layout, identifying panes (widgets or frames) and
#           assigning a name (string) to each.
#       2. Instantiate an AppLayout object from the tkuibuilder library.
#       3. Specify the layout using the 'column_elements()' and
#           'row_elements()' methods of the AppLayout object, and
#           the names that are assigned to the application panes (and
#           the names that are returned by these methods, as necessary).
#       4. Use the 'create_layout()' method of the AppLayout object to
#           build the nested set of Tkinter frames that will contain
#           the application panes.
#       5. Use the 'build_elements()' method of the AppLayout object to
#           specify a function that will populate each pane with widgets.
#
# AUTHORS
#   Dreas Nielsen (RDN)
#
# HISTORY
#    Date         Remarks
#   ----------- -------------------------
#   2018-01-24   Created.  RDN.
#===============================================================================

import sys

sys.path.append("../tkuibuilder")

import Tkinter as tk
import tkuibuilder as tkb

    
def test():
    # Define functions to build each of the panes that will appear in
    # the application.  (These 'build' functions are nested within
    # the 'test' function, but need not be.)

    # Build pane A.
    def build_a(parent):
        w = tk.Label(parent, text="Element A", justify=tk.CENTER)
        w.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NSEW)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
    # Build pane B.
    def build_b(parent):
        w = tk.Label(parent, text="Element B", justify=tk.CENTER, fg="blue")
        w.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NSEW)
    # Build pane C.
    def build_c(parent):
        w =  tk.Label(parent, text="Element C", justify=tk.CENTER)
        w.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NSEW)
    # Build pane D.
    def build_d(parent):
        dir_label = tk.Label(parent, text='Output directory:', anchor=tk.W)
        parent.dir_var = tk.StringVar()
        dir_display = tk.Entry(parent, textvariable=parent.dir_var)
        dir_display.configure(state='readonly')
        dir_button = tk.Button(parent, text='Set', width=8)
        dir_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        dir_display.grid(row=0, column=1, padx=10, sticky=tk.W+tk.E)
        dir_button.grid(row=1, column=0 , padx=10, pady=5, sticky=tk.EW)
        parent.columnconfigure(0, weight=0)
        parent.columnconfigure(1, weight=1)
        parent.configure(bg="red")
    # Build pane E.
    def build_e(parent):
        w = tk.Label(parent, text="Element E", justify=tk.CENTER)
        w.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        parent.configure(bg="green")
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

    # Initialize the application layout object.
    gui_app = tkb.AppLayout()

    # For simplicity, define frame configuration and frame gridding options
    # that wiil be used for most or all of the frames that enclose the
    # application panes.
    config_opts = {"borderwidth": 1, "relief": tk.GROOVE}
    grid_opts = {"sticky": tk.NSEW}

    upper_left = gui_app.column_elements(["user_pane", "servdb_pane"], {}, grid_opts)
    upper = gui_app.row_elements([upper_left, "table_pane"], {}, grid_opts)
    lower = gui_app.column_elements(["output_pane","export_pane"], {}, grid_opts)
    app_pane = gui_app.column_elements([upper, lower], {}, grid_opts)

    # Create the Tkinter root element
    root = tk.Tk()

    gui_app.create_layout(root, app_pane)

    gui_app.build_elements({"user_pane": build_a, "servdb_pane": build_b, "table_pane": build_c, "output_pane": build_d, "export_pane": build_e})

    # Run the application.
    root.mainloop()


test()
