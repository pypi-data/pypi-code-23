## qt multipage libary file for all functions related to pyqt5
#
# @file		    multipage.py
# @author	    Tobias Ecklebe efos@ecklebe.de
# @date		    24.01.2018
# @version	    0.1.0
# @note		    This file includes functions for multipage usage in pyqt as libary that i think are great for different projects.\n\n
#               To use this file:  from pylibcklb.pyqt5-library.qt5_functions import SomeClassOrFunction\n     
#               
# @pre          The library was developed with python 3.6 64 bit and pyqt5 
#
# @bug          No bugs at the moment.
#
# @warning      The functions need a self pointer of the qt application! 
#
# @copyright    pylibcklb package
#               Copyright (C) 2018  Tobias Ecklebe
#
#               This program is free software: you can redistribute it and/or modify
#               it under the terms of the GNU Lesser General Public License as published by
#               the Free Software Foundation, either version 3 of the License, or
#               (at your option) any later version.
#
#               This program is distributed in the hope that it will be useful,
#               but WITHOUT ANY WARRANTY; without even the implied warranty of
#               MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#               GNU Lesser General Public License for more details.
#
#               You should have received a copy of the GNU Lesser General Public License
#               along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import os  
import sys
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pylibcklb.ClassLibrary import cDebug 
from pylibcklb.metadata import PackageVariables
Debug = cDebug(PackageVariables.DebugLevel)


def CreateVerticalLayout(self, layoutname:str, parent=None):
    VerticalLayout = QtWidgets.QVBoxLayout(parent)
    VerticalLayout.setContentsMargins(0, 0, 0, 0)
    VerticalLayout.setObjectName(layoutname)
    VerticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
    return VerticalLayout

def CreateHorizontalLayout(self, layoutname:str, parent=None):
    HorizontalLayout = QtWidgets.QHBoxLayout(parent)
    HorizontalLayout.setContentsMargins(0, 0, 0, 0)
    HorizontalLayout.setObjectName(layoutname)
    HorizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
    return HorizontalLayout

## Documentation for a method that sets the central widget layout
#  @param self The object pointer.
#  @param layout The layout to set
def SetCentralWidgetLayout(self, layout):
    widget = QtWidgets.QWidget()
    widget.setLayout(layout)
    self.setCentralWidget(widget)

## Documentation for a method that changes to the first page of the stacked widget
#  @param self The object pointer.
def CallFirstPage(self, stackedWidget):
    stackedWidget.setCurrentIndex(0)    


