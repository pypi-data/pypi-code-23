#!/usr/bin/env python
"""
Prooffreader's Python Hodepodge
"""

import sys

def get_modules():
    """Returns list of modules in this package, followed by *
    if it's a folder-based module instead of a .py file"""
    import os
    thispath = os.path.dirname(os.path.abspath(__file__))
    fps = []
    for fp in os.listdir(thispath):
        if fp.endswith('.py') and not fp[0]=='_':
            fps.append(fp[:-3])
        elif (fp[0] not in ('.', '_') and
              os.path.isdir(fp)):
            fps.append(fp+' *')
    return sorted(fps)

def print_ipython_multiple_outputs():
    print("from IPython.core.interactiveshell import InteractiveShell\n"
          "InteractiveShell.ast_node_interactivity = \"all\"")