# -*- coding: utf-8 -*-
"""
Created on Sun Jan 28 13:16:21 2018

@author: jaredmt

description: this contains a list of all my custom functions

Prerequisites: numpy, sympy, matplotlib, scipy, openpyxl, pandas, tkinter
"""

'''
command prompt at scripts folder: (close all IDE's before updating)
install modules:
pip install module1 module2 module3 

update modules:
pip install --upgrade module1 module2 module3 

list outdated :
pip list --outdated --format=freeze

'''


'''==================imports==================='''
'''
all actual imports need to be called within each function
(don't worry, python only imports once)

below is a list of actual imports used in functions
(***THESE FUNCTIONS MUST BE EXCLUDED FROM PYINSTALLER SPEC FILE IF NOT USED***):


copy for .spec: (remove modules that are needed)
exclude_list=['fractions','numpy','openpyxl','requests','pandas','sympy','tkinter']
'''

#import all submodules
#from .main.main import isimported,ceil,num2frac,str2func,checkEval,error
'''
import jmt.main.main as jtmain
import jmt.list.list as jtlist
import jmt.string.string as jtstring
import jmt.excel.excel as jtexcel
import jmt.tkinter.tkinter as jttkinter
import jmt.pandas.pandas as jtpandas
import jmt.sympy.sympy as jtsympy
'''

'''
from .main.main import *
from .list.list import *
from .string.string import *
from .excel.excel import *
from .tkinter.tkinter import *
from .pandas.pandas import *
from .sympy.sympy import *
'''

'''
#this doesn't remove the main.main
from jmt.main.main import isimported
'''
from .jtmain import *
from .jtlist import *
from .jtstring import *
from .jtexcel import *
from .jttkinter import *
from .jtpandas import *
from .jtsympy import *
from .jtmdb import *


