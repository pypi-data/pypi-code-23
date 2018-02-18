# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import division
from __future__ import print_function

"""
Some examples to show how to use jscatter

Functions show the code or run the examples in example directory.

"""


import os
import glob
import webbrowser
_path_ = os.path.realpath(os.path.dirname(__file__))
_expath=_path_
datapath=os.path.join(_expath,'exampleData')

def _getexamples():
    exfiles=glob.glob(_expath+'/example_*.py')
    return sorted(exfiles)

def showExampleList():
    """
    Show a list of all examples.

    """
    print('Example path : ',_expath)
    exfiles=_getexamples()
    for i,ff in enumerate(exfiles):
        print(i,'  ',os.path.basename(ff))

def runExample(example):
    """
    Runs example

    Parameters
    ----------
    example: string,int
        Filename or number of the example to run


    """
    if isinstance(example,int):
        exfiles = _getexamples()
        example=exfiles[example]
        sorted(example)
        print('-----------------------------------')
        print(example)
    cwd = os.getcwd()
    os.chdir(_expath)
    with open(example) as f:   exec(f.read(),{})
    os.chdir(cwd)
    return

def showExample(example='.'):
    """
    Opens example in browser or default editor

    Parameters
    ----------
    example : string, int
        Filename or number.
        If '.' the folder with the examples is opened.

    """
    if isinstance(example,int):
        exfiles = _getexamples()
        example=exfiles[example]
    webbrowser.open(os.path.join(_expath,example))

def runAll():
    """
    Run all examples.

    """
    exfiles = _getexamples()
    for ff in exfiles:
        print('----------------------------------')
        print(os.path.basename(ff))
        runExample(os.path.basename(ff))


