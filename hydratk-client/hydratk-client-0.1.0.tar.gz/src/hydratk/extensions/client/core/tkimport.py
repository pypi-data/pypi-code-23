# -*- coding: utf-8 -*-
"""Tkinter import aliases

.. module:: client.core.tkimport
   :platform: Windows, Unix
   :synopsis: Tkinter import aliases
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

import sys
PYTHON_MAJOR_VERSION = sys.version_info[0]

if (PYTHON_MAJOR_VERSION == 2):
    reload(sys)
    sys.setdefaultencoding('UTF8')
    import Tkinter as tk
    import ttk as ttk
    import tkMessageBox
    import tkFileDialog
    from ScrolledText import ScrolledText
else:
    import tkinter as tk
    from tkinter import ttk as ttk
    import tkinter.messagebox as tkMessageBox
    import tkinter.filedialog as tkFileDialog
    from tkinter.scrolledtext import ScrolledText

import platform

tk = tk
ttk = ttk
tkmsg = tkMessageBox
tkfd = tkFileDialog
tkst = ScrolledText

c_os = platform.system()
