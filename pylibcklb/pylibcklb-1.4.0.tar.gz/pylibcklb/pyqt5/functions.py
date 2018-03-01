## qt functions libary file for all functions related to pyqt5
#
# @file		    qt5_functions.py
# @author	    Tobias Ecklebe efos@ecklebe.de
# @date		    25.08.2017
# @version	    0.1.0
# @note		    This file includes functions as libary that i think are great for different projects.\n\n
#               To use this file:  from pylibcklb.pyqt5-library.qt5_functions import SomeClassOrFunction\n     
#               
# @pre          The library was developed with python 3.6 64 bit and pyqt5 
#
# @bug          No bugs at the moment.
#
# @warning      The functions need a self pointer of the qt application! 
#
# @copyright    pylibcklb package
#               Copyright (C) 2017  Tobias Ecklebe
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
from pylibcklb.FunctionLibrary import GetRelativePathFromAbsolutePath
Debug = cDebug(PackageVariables.DebugLevel)

## Documentation for a method to let the user search the correct directory.
#  @param self The object pointer of the the window class
#  @param windowname The name of the pop up window that describe what directory the user has to search
def BrowseFolder(self, windowname):        
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)
    # execute getExistingDirectory dialog and set the directory variable to be equal to the user selected directory and return that
    return QtWidgets.QFileDialog.getExistingDirectory(self, windowname)     

## Documentation for a method to let the user search the correct directory and return an relative path
#  @param self The object pointer of the the window class
#  @param windowname The name of the pop up window that describe what directory the user has to search
def BrowseFolderRelative(self, windowname):      
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)
    dir = BrowseFolder(self,windowname)  
    return GetRelativePathFromAbsolutePath(dir)

## Documentation for a method to let the user search the correct directory to save a file
#   @code 
#   windowname = 'Search the folder to save to'
#   StringOfFiletypes = 'XML File (*.xml)'
#   dir = QT5FL.SaveFolder(self, windowname, StringOfFiletypes)
#   @endcode
#   @param self The object pointer of the the window class
#   @param windowname The name of the pop up window that describe what directory the user has to search
#   @param StringOfFiletypes Filter the files list for a specific type
def SaveFolder(self, windowname,StringOfFiletypes):
    return QtWidgets.QFileDialog.getSaveFileName(self, windowname,os.getcwd(), filter=StringOfFiletypes)[0]      

## Documentation for a method to let the user search the correct directory to load a file
#   @code 
#   windowname = 'Search the folder to load from'
#   StringOfFiletypes = 'XML File (*.xml)'
#   dir = QT5FL.SaveFolder(self, windowname, StringOfFiletypes)
#   @endcode
#   @param self The object pointer of the the window class
#   @param windowname The name of the pop up window that describe what directory the user has to search
#   @param StringOfFiletypes Filter the files list for a specific type
def LoadFolder(self, windowname,StringOfFiletypes):
    return QtWidgets.QFileDialog.getOpenFileName(self, windowname,os.getcwd(), filter=StringOfFiletypes)[0]    

## Documentation for a method to create a message box 
#   @note Is the MESSAGE_TYPE not none and from the MESSAGE_TYPE_LIST an ICON and WINDOW_TITLE is not necessary
#   @param SELF The object pointer of the the window class
#   @param MESSAGE Message to display at first in the box
#   @param INFORMATIVE_MESSAGE Message with more informations
#   @param DETAILED_MESSAGE Message with very detailed informations can be selected by drop down
#   @param WINDOW_TITLE The title of the window to set, only needed if MESSAGE_TYPE is not from MESSAGE_TYPE_LIST
#   @param MESSAGE_TYPE An type from the MESSAGE_TYPE_LIST
#   @param ICON The icon of the window to set, only needed if MESSAGE_TYPE is not from MESSAGE_TYPE_LIST
#   @return Value is True or if MESSAGE_TYPE == 'QUESTION' the answer of the question as true/false
def CreateMessageBox(SELF, MESSAGE = None, INFORMATIVE_MESSAGE = None, DETAILED_MESSAGE = None, WINDOW_TITLE = None, MESSAGE_TYPE = None, ICON = None):
    MESSAGE_TYPE_LIST = ['ERROR', 'WARNING', 'INFORMATION', 'QUESTION']
    msg = QtWidgets.QMessageBox(SELF)

    if MESSAGE_TYPE in MESSAGE_TYPE_LIST:
        if MESSAGE_TYPE == 'ERROR': 
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle('Error')
        elif MESSAGE_TYPE == 'WARNING': 
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle('Warning')        
        elif MESSAGE_TYPE == 'INFORMATION': 
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle('Information')
        elif MESSAGE_TYPE == 'QUESTION': 
            msg.setIcon(QtWidgets.QMessageBox.Question)
            msg.setWindowTitle('Question')
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    else:
        if WINDOW_TITLE is not None:
            msg.setWindowTitle(WINDOW_TITLE)
        else:
            msg.setWindowTitle('Informations')
        if ICON is not None:
            msg.setIcon(ICON)
        else:
            msg.setIcon(QtWidgets.QMessageBox.Information)

    if MESSAGE is not None:
        msg.setText(str(MESSAGE))
    else:
        msg.setText('No message to display')

    if INFORMATIVE_MESSAGE is not None:
        msg.setInformativeText(str(INFORMATIVE_MESSAGE))

    if DETAILED_MESSAGE is not None:
        msg.setDetailedText(str(DETAILED_MESSAGE))
    ret = msg.exec_() 

    if MESSAGE_TYPE == 'QUESTION': 
        if ret == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False
    else: 
        return True

## Documentation for a method to create a error message box 
#   @param SELF The object pointer of the the window class
#   @param ERROR_MESSAGE Message to display at first in the box
#   @param ERROR_INFORMATIVE_MESSAGE Message with more informations
#   @param ERROR_DETAILED_MESSAGE Message with very detailed informations can be selected by drop down
#   @return Value is True 
def CreateErrorMessage(SELF, ERROR_MESSAGE, ERROR_INFORMATIVE_MESSAGE, ERROR_DETAILED_MESSAGE = None):
    return CreateMessageBox(SELF, ERROR_MESSAGE, ERROR_INFORMATIVE_MESSAGE, ERROR_DETAILED_MESSAGE, MESSAGE_TYPE = 'ERROR')

## Documentation for a method to create a error message box 
#   @param SELF The object pointer of the the window class
#   @param WARNING_MESSAGE Message to display at first in the box
#   @param WARNING_INFORMATIVE_MESSAGE Message with more informations
#   @param WARNING_DETAILED_MESSAGE Message with very detailed informations can be selected by drop down
#   @return Value is True 
def CreateWarningMessage(SELF, WARNING_MESSAGE, WARNING_INFORMATIVE_MESSAGE, WARNING_DETAILED_MESSAGE = None):
    return CreateMessageBox(SELF, WARNING_MESSAGE, WARNING_INFORMATIVE_MESSAGE, WARNING_DETAILED_MESSAGE, MESSAGE_TYPE = 'WARNING')

## Documentation for a method to create a error message box 
#   @param SELF The object pointer of the the window class
#   @param INFORMATION_MESSAGE Message to display at first in the box
#   @param INFORMATION_INFORMATIVE_MESSAGE Message with more informations
#   @param INFORMATION_DETAILED_MESSAGE Message with very detailed informations can be selected by drop down
#   @return Value is True 
def CreateInformationMessage(SELF, INFORMATION_MESSAGE, INFORMATION_INFORMATIVE_MESSAGE, INFORMATION_DETAILED_MESSAGE = None):
    return CreateMessageBox(SELF, INFORMATION_MESSAGE, INFORMATION_INFORMATIVE_MESSAGE, INFORMATION_DETAILED_MESSAGE, MESSAGE_TYPE = 'INFORMATION')

## Documentation for a method to create a error message box 
#   @param SELF The object pointer of the the window class
#   @param QUESTION_MESSAGE Message to display at first in the box
#   @param QUESTION_INFORMATIVE_MESSAGE Message with more informations
#   @param QUESTION_DETAILED_MESSAGE Message with very detailed informations can be selected by drop down
#   @return The answer of the question as true/false
def CreateQuestionMessage(SELF, QUESTION_MESSAGE, QUESTION_INFORMATIVE_MESSAGE, QUESTION_DETAILED_MESSAGE = None):
    return CreateMessageBox(SELF, QUESTION_MESSAGE, QUESTION_INFORMATIVE_MESSAGE, QUESTION_DETAILED_MESSAGE, MESSAGE_TYPE = 'QUESTION')

## Documenation of a method to set the drag and drop mode of a qtreeview
# @param treeview a view with the type qtreeview
# @param expr The Mode as string that should be set: 'DragOnly',
# 'DropOnly', 'DropAndDrop'
def SetDragDropMode(treeview, expr='NoDragDrop'):
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)
    if expr == 'DragOnly':
        treeview.setDragDropMode(QAbstractItemView.DragOnly)
    elif expr == 'DropOnly':
        treeview.setDragDropMode(QAbstractItemView.DropOnly)
    elif expr == 'DropAndDrop':
        treeview.setDragDropMode(QAbstractItemView.DragDrop)
    else:
        treeview.setDragDropMode(QAbstractItemView.NoDragDrop)
    return

## Documentation for a method to size the window correct
#   @param self The object pointer of the the window class
#   @param SizeWidth The width of the window to set
#   @param SizeHeight The height of the window to set
#   @return True if the parameters are all correct, else False
def ResizeWindow(self, SizeWidth:int=None, SizeHeight:int=None): 
    if ((SizeWidth is not None) and (SizeHeight is not None)):
        self.resize(SizeWidth, SizeHeight)
        return True
    return False

## Documentation for a method to size the window correct with the use of mulitplicators
#   @param self The object pointer of the the window class
#   @param SizeWidthMultiplicator The multiplicator which tells how many of the display width should be used.
#   @param SizeHeightMultiplicator The multiplicator which tells how many of the display height should be used.
#   @return True if the parameters are all correct, else False
def ResizeWindow2DisplayScreenWithMultiplicator(SELF, SizeWidthMultiplicator=None, SizeHeightMultiplicator=None):  

        if SizeWidthMultiplicator == None:
            SizeWidthMultiplicator = 1

        if SizeHeightMultiplicator == None:
            SizeHeightMultiplicator = 1

        SizeWidth   = QDesktopWidget().availableGeometry().width() * SizeWidthMultiplicator
        SizeHeight  = QDesktopWidget().availableGeometry().height() * SizeHeightMultiplicator

        return ResizeWindow(SELF, SizeWidth, SizeHeight)

## Documentation for a method to create an menubar at the parent main window
#   @param parent The object pointer of the main window
#   @return Menubar only if menubar has been created else none 
def CreateMenuBar(parent:QtWidgets.QMainWindow):
    if issubclass(type(parent),  QtWidgets.QMainWindow) is True: 
        menuBar = QtWidgets.QMenuBar(parent)
        parent.setMenuBar(menuBar) 
        return menuBar
    else:
        return None

## Documentation for a method to create an edit entry in the menubar
#   @param parent The object pointer of the menubar
#   @return menu entry only if menu entry has been created else none 
def CreateEditEntryForMenubar(parent:QtWidgets.QMenuBar):
    if issubclass(type(parent),  QtWidgets.QMenuBar) is True: 
        menuEdit = QtWidgets.QMenu(parent)
        menuEdit.setObjectName("menuEdit")
        menuEdit.setTitle("Edit")
        parent.addAction(menuEdit.menuAction())
        return menuEdit
    else:
        return None

## Documentation for a method to create an help entry in the menubar
#   @param parent The object pointer of the menubar
#   @return menu entry only if menu entry has been created else none 
def CreateHelpEntryForMenubar(parent:QtWidgets.QMenuBar):
    if issubclass(type(parent),  QtWidgets.QMenuBar) is True: 
        menuEdit = QtWidgets.QMenu(parent)
        menuEdit.setObjectName("menuHelp")
        menuEdit.setTitle("Help")
        parent.addAction(menuEdit.menuAction())
        return menuEdit
    else:
        return None

## Documentation for a method to create an bush button in the parent layout
#   @param ParentLayout The layout to add at
#   @param Function2Call The function to call when clicked
#   @param parent The parent widget to add at
#   @param name The object name
#   @param button_text text to display on the button
#   @param enabled The state of the push button
#   @return pointer to the generated push button
def CreatePushButton(ParentLayout, Function2Call, parent = None, name = 'pushButton', button_text = 'pushButton', enabled = True ):

    if parent is None:
        pushButton = QtWidgets.QPushButton()
    else:
        pushButton = QtWidgets.QPushButton(parent)

    pushButton.setObjectName(name)
    pushButton.setText(button_text)
    pushButton.clicked.connect(Function2Call)
    pushButton.setEnabled(enabled)
    ParentLayout.addWidget(pushButton)
    return pushButton

## Documentation for a method to create an editable line in the parent layout
#   @param ParentLayout The layout to add at
#   @param Function2Call The function to call when text changed
#   @param parent The parent widget to add at
#   @param name The object name
#   @param text text to display in the line
#   @param enabled The state of the line
#   @return pointer to the generated line
def CreateEditableLine(ParentLayout, Function2Call, parent = None, name = 'lineedit', text = 'example text', enabled = True ):

    if parent is None:
        editor = QtWidgets.QLineEdit()
    else:
        editor = QtWidgets.QLineEdit(parent)

    editor.clear()
    editor.setObjectName(name)
    editor.setText(text)
    editor.textChanged.connect(Function2Call)
    editor.setEnabled(enabled)
    ParentLayout.addWidget(editor)
    return editor 

## Documentation for a method to create an horizontal layout
#   @param parent The parent widget to add at
#   @param parent_layout The layout to add at
#   @param layout_name The object name
#   @return pointer to the generated layout
def CreateHorizontalLayout(parent = None, parent_layout = None, layout_name = "horizontalLayout"):

    layout = None 

    if (parent is None): 
        layout = QtWidgets.QHBoxLayout()
    else:
        layout = QtWidgets.QHBoxLayout(parent)

    if layout is not None:
        layout.setObjectName(layout_name)

    if (parent_layout is not None): 
        parent_layout.addLayout(layout)

    return layout

## Documentation for a method to create an vertical layout
#   @param parent The parent widget to add at
#   @param parent_layout The layout to add at
#   @param layout_name The object name
#   @return pointer to the generated layout
def CreateVerticalLayout(parent = None, parent_layout = None, layout_name = "verticalLayout"):

    layout = None 

    if (parent is None): 
        layout = QtWidgets.QVBoxLayout()
    else:
        layout = QtWidgets.QVBoxLayout(parent)

    if layout is not None:
        layout.setObjectName(layout_name)

    if (parent_layout is not None): 
        parent_layout.addLayout(layout)

    return layout

## Documentation for a method to get the values from an calender widget
#   @param calenderwidget The calender to get the date from
#   @return day, month and year
def GetDateFromCalenderWidget(calenderwidget):
    date = QDate()
    date = calenderwidget.selectedDate()
    return date.day(), date.month(), date.year()

## Documentation for a method to wait on boolean signal to go on with the process
#   @param Signal Boolean signal where we want to wait on true
#   @return new boolean state of the signal
def WaitOnSignal(Signal:bool):   
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)
    i = 0
    while ( Signal != True ):
        # not doing anything                                                                                                                                                                                                   
        if ( i % 100000 == 0 ):
            Debug.Print(Debug.LEVEL_All, "Waiting for user to push button next")
        QCoreApplication.processEvents()
        i += 1;

    Signal = False
    return Signal

## Documentation for a method to wait on boolean signal to go on with the process
#   @param Signal Boolean signal where we want to wait on true
#   @return new boolean state of the signal
def WatchMutexAndCallFunction(Mutex, Function2Call):   
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)
    i = 0
    while ( Mutex.locked() == True):
        # not doing anything                                                                                                                                                                                                   
        if ( i % 100000 == 0 ):
            Debug.Print(Debug.LEVEL_All, "Waiting for mutex release")
        QCoreApplication.processEvents()
        i += 1;

    Function2Call()
    return 

## Documentation for a method to clean an layout
#   @note Base code comes from https://stackoverflow.com/a/23087057
#   @param layout2clear Layout to clean
def ClearLayout(layout2clear):
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)
    
    if layout2clear != None:
        while layout2clear.count():
            child = layout2clear.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                ClearLayout(child.layout())

## Documentation for a method to get the name of the current page from an dict 
# @note PageDict = {'main':0, 'options':1}
# @param stackedWidget Pointer to the widget with the pages
# @param PageDict The dict with the pages and pagenumbers
# @return Name of the page or none if is not in page
def GetNameOfCurrentPage(stackedWidget, PageDict):
    for key in PageDict.keys():
        if PageDict[key] == stackedWidget.currentIndex():
            return key
    return None

## Documentation for a method to remove the widget and his childs from the layout
#  @param widget The widget to remove
#  @param layout The Layout where the widget should be removed
def RemoveWidgetFromParentLayout(widget, layout):
    import sip
    layout.removeWidget(widget)
    sip.delete(widget)
    widget = None
    return widget