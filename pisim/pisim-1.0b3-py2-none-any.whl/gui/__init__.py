# -*- coding: utf-8 -*-

"""App GUI definition.

Notice that no documentation is provided for classes actually implementing
the GUI. That's because they're very app-specific and not meant to be
really reused in the future.

List of sub-packages
====================

.. autosummary::
   :toctree: _autosummary

   signals
   commonEntry
"""

import ttk

#: Shortcut for a value of grid's sticky parameter.
stretchSticky = ttk.Tkinter.N+ttk.Tkinter.S+ttk.Tkinter.E+ttk.Tkinter.W

# Defining common style for invalid entries
ttk.Style().configure('valid.TEntry')
ttk.Style().map('valid.TEntry', foreground=[('invalid', 'red')])

# Defining style for interface headlines
ttk.Style().configure('emph.TLabel', font=('-weight bold'))
