#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  5 20:10:25 2018

@author: aguimera
"""


import PyGFET.DBSearch as DBSearch
from PyGFET.DataClass import PyFETPlotDataClass as GFETPlt

# define the dictionary for sql select constructor
Conditions = {'Wafers.Name = ': ('B10803W17', ),
              'CharTable.IsOK > ': (0, )}

Data, Trts = DBSearch.GetFromDB(Conditions=Conditions,
                                Table='DCcharacts')

Plot = GFETPlt()
Plot.AddAxes(('Ids', 'Gm'))
