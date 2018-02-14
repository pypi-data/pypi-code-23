# -*- coding: utf-8 -*-
"""
Created on Wed Dec 27 20:23:47 2017

@author: Daniel
"""

from asammdf import MDF

MDF(r'd:\PythonWorkspace\asammdf\test\tmpdir\arrays.mf4').convert('2.10').save(r'd:\PythonWorkspace\asammdf\test\tmpdir\arrays_210.mdf', overwrite=True)