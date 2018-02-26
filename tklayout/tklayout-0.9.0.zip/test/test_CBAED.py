#! /usr/bin/python
#
# test_CBAED.py
#
# PURPOSE
#   Test the tkuibuilder library with a simple example.
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
#   ----------- --------------------------------------------------------------------
#   2018-01-26   Created to illustrate an alternative layout to test_ABCDE.py.  RDN.
#===================================================================================

import sys

sys.path.append("../tklayout")

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

import tklayout as tkb

    
def test():
    # Define functions to build each of the panes that will appear in
    # the application.  (These 'build' functions are nested within
    # the 'test' function, but need not be.)

    # Build pane A.
    def build_a(parent):
        w = tk.Label(parent, text="Element A", justify=tk.CENTER)
        w.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NSEW)
    # Build pane B.
    def build_b(parent):
        w = tk.Label(parent, text="Element B", justify=tk.CENTER, fg="blue")
        w.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NSEW)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
    # Build pane C.
    def build_c(parent):
        w =  tk.Label(parent, text="Element C", justify=tk.CENTER)
        w.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NSEW)
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
    # Build pane D.
    def build_d(parent):
        w = tk.Label(parent, text="Element D", justify=tk.CENTER, fg="green")
        w.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
    # Build pane E.
    def build_e(parent):
        w = tk.Label(parent, text="Element E", justify=tk.CENTER)
        w.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)

    # Initialize the application layout object.
    lo = tkb.AppLayout()

    # For simplicity, define frame configuration and frame gridding options
    # that wiil be used for most or all of the frames that enclose the
    # application panes.
    config_opts = {"borderwidth": 3, "relief": tk.GROOVE}
    grid_opts = {"sticky": tk.NSEW}

    # Define the structure of the application panes from the inside
    # out.  Each pane is identified by a string.  The names of the basic
    # panes are assigned by the UI designer.  Groups (rows or columns)
    # of other panes are assigned by the AppLayout object, and are returned
    # by the 'column_elements()' and 'row_elements()' methods.
    # The most deeply nested panes that appear in a single row or column
    # should be defined first, followed by successively higher levels of
    # nesting.  Higher levels of nesting can include the pane groups
    # defined by the AppLayout object. 
    #
    # The arguments for the 'column_elements()' method are:
    #   1. A list of the names assigned to the panes in the column being defined.
    #   2. An optional dictionary of configuration options for the frame that will enclose the elements.
    #   3. An optional dictionary of grid options for the frame that will enclose the elements.
    #   4. An option list of weights one for each row (element) in the column.
    #       If this list is shorter than the number of elements, it will be
    #       recycled as necessary.  If omitted, all rows will be given a
    #       weight of 1.
    #   5. An optional weight for the column in which the elements will be placed.
    #       If omitted, the column will be given a weight of 1.
    #
    # The arguments for the 'row_elements()' method are like those for the
    # 'column_elements()' method, but with rows and columns swapped.
    #
    #
    cb = lo.column_elements(["C", "B"], config_opts, grid_opts, row_weights=[1,1], column_weight=1)
    ae = lo.column_elements(["A", "E"], config_opts, grid_opts, row_weights=[1,1], column_weight=1)
    cbae = lo.row_elements([cb, ae], config_opts, grid_opts, column_weights=[1,1], row_weight=1)
    app = lo.column_elements([cbae, "D"], config_opts, grid_opts, row_weights=[0,1,1], column_weight=1)

    # Create the Tkinter root element
    root = tk.Tk()

    # Create the layout--the set of nested frames--rooted on the Tkinter root
    # element.  The layout could be rooted on some other widget instead, but
    # this is a simple example.
    #
    # The arguments for the 'create_layout()' method are:
    #   1. The master or root widget for the layout.  This should be a frame
    #       or other container.
    #   2. The name assigned to the top-level element.  Except for trivial
    #       uses, this will be a name returned by 'column_elements()' or
    #       'row_elements()'.
    #   3. The row of the top-level element within the root widget (optional,
    #       defaults to 0).
    #   4. The column of the the top-level element within the root widget
    #       (optional, defaults to 0).
    #   5. The weight for the row of the top-level element within the root
    #       widget (optional, defaults to 1).
    #   6. The weight for the column of the top-level element within the
    #       root widget (optional, defaults to 1).
    lo.create_layout(root, app, row=0, column=0, row_weight=1, column_weight=1)

    # Fill in the basic panes with widgets, and set configuration options,
    # actions, callbacks, etc.
    #
    # The argument to the 'build_elements()' method is a dictionary in which
    # the keys are the names assigned to the application panes, and the values
    # are functions that create the widgets within those frames.  Each of those
    # functions must take a frame as an argument, and create widgets within
    # that frame.
    lo.build_elements({"A": build_a, "B": build_b, "C": build_c, "D": build_d, "E": build_e})

    # For debugging (or curiosity).
    #print(lo.layout_as_json(True))

    # Run the application.
    root.mainloop()


test()
