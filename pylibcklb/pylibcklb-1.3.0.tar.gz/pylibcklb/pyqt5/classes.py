## qt class libary file for all classes related to pyqt5
#
# @file		    qt5_classes.py
# @author	    Tobias Ecklebe tobias.ecklebe@outlook.de
# @date		    01.11.2017
# @version	    0.1.0
# @note		    This file includes functions as libary that i think are great for different projects.\n\n
#               To use this file:  from pylibcklb.pyqt5-library.qt5_classes import SomeClassOrFunction\n  
#               
# @pre          The library was developed with python 3.6 64 bit and pyqt5 
#
# @bug          No bugs at the moment.
#
# @warning      No warnings at the moment.
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

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from pylibcklb.ClassLibrary import cDebug, cObserver
from abc import ABCMeta, abstractmethod
import os
import sys
from pylibcklb.metadata import PackageVariables
from pylibcklb.pyqt5.functions import ResizeWindow, ResizeWindow2DisplayScreenWithMultiplicator, CreateMenuBar, CreateEditEntryForMenubar, CreateVerticalLayout, CreateHelpEntryForMenubar

Debug = cDebug(PackageVariables.DebugLevel)

class cApplicationMainWindow_BaseClass(QtWidgets.QMainWindow):

    ## Documentation of the constructor
    #  @param self The object pointer.
    #  @param parent An pointer to the parent where we wont to add the menu bar entry
    #  @param visibility The visibility of the toolbar after initalize
    def __init__(self, name, SizeWidthMultiplicator=0.5, SizeHeightMultiplicator=0.5):  
        QtWidgets.QMainWindow.__init__(self)

        self.InstanceName  = name  
        self.setWindowTitle(name)
        self.CentralWidget = QWidget(self)          
        self.setCentralWidget(self.CentralWidget) 
        self.BaseLayout = CreateVerticalLayout(parent = self.CentralWidget, layout_name = 'BaseVerticalLayout')
        #self.CentralWidget.setLayout(self.BaseLayout)

        ResizeWindow2DisplayScreenWithMultiplicator(self, SizeWidthMultiplicator, SizeHeightMultiplicator)
        self.StartApplication()

    ## Documentation of the destructor 
    #  @param self The object pointer.
    def __del__(self): 
        print(self.InstanceName, 'died')  

    ## Documentation for a method to start the application the right way
    #  @param self The object pointer.     
    def StartApplication(self):
        self.show()
        print(self.InstanceName, 'started') 

    ## Documentation for a method to close the application the right way
    #  @param self The object pointer.  
    #  @param evnt The close event when clicked on the x window button   
    def closeEvent(self, evnt):
        if evnt:
            print(self.InstanceName, 'closed')  
            QtWidgets.QMainWindow.closeEvent(self, evnt)
        else:
            self.close()  

class cApplicationMainWindow_Observer(cApplicationMainWindow_BaseClass, cObserver):

    ## Documentation of the constructor
    #  @param self The object pointer.
    #  @param parent An pointer to the parent where we wont to add the menu bar entry
    #  @param visibility The visibility of the toolbar after initalize
    def __init__(self, name):
        super(self.__class__, self).__init__(name, 0.5, 0.5) 

class cApplicationMainWindow_Extended(cApplicationMainWindow_BaseClass):

    ## Documentation of the constructor
    #  @param self The object pointer.
    #  @param parent An pointer to the parent where we wont to add the menu bar entry
    #  @param visibility The visibility of the toolbar after initalize
    def __init__(self, name, SizeWidthMultiplicator=0.5, SizeHeightMultiplicator=0.5, Use_MenuBar=True, MenuBar_EditEntry=True, Use_Undo_MenuBar=True, MenuBar_HelpEntry=True):
        cApplicationMainWindow_BaseClass.__init__(self, name, SizeWidthMultiplicator, SizeHeightMultiplicator) 
    
        self.Menubar = None
        self.MenuBar_Edit = None
        self.Menubar_Edit_Undo = None

        if Use_MenuBar == True:
            self.Menubar = CreateMenuBar(self)
            if MenuBar_EditEntry == True:
                self.MenuBar_Edit = CreateEditEntryForMenubar(self.Menubar)
                self.Menubar_Edit_Undo = cUndoEntry2MenuEditInMenuBar(self.MenuBar_Edit, Use_Undo_MenuBar)

            if MenuBar_HelpEntry  == True: 
                self.MenuBar_Help = CreateHelpEntryForMenubar(self.Menubar)
                self.Menubar_Help_About = cAboutEntry2MenuHelpInMenuBar(self.MenuBar_Help, SizeWidthMultiplicator = SizeWidthMultiplicator, SizeHeightMultiplicator = SizeHeightMultiplicator)

    def SetChangelogText(self, TextOfChangelog):
        self.Menubar_Help_About.ChangeLogText = TextOfChangelog

    def SetProgrammInformationText(self, ProgrammInformationText):
        self.Menubar_Help_About.ProgrammInformationText = ProgrammInformationText

    def SetStateOfCheckBoxStartScreen(self, State):
        self.Menubar_Help_About.CheckBoxStartScreen = State


## Documentation for a class that handles as thread the reading from a directory.
# The reason for a thread is that while the programm searches in a great dir
# the gui will be frozen.
# The following code explaines the example usage:
# @code
## Creates an thread to fix the problem with an frozen gui while searching in the directory
#self.Thread_FilesFromDir = QT5CL.cGetThread_FilesFromDir(CatalogsPath, FileType)
#            
## Next we need to connect the events from that thread to functions we want
## to be run when those signals get fired       
#self.Thread_FilesFromDir.get_dir.connect(self.AddDir2ListWidget)
#self.Thread_FilesFromDir.finished.connect(self.done)
#
## We have all the events we need connected we can start the thread
#self.Thread_XMLFilesFromDir.start()
## At this point we want to allow user to stop/terminate the thread so we enable that button
#self.ButtonLoadCatalogs_Stop.setEnabled(True)
## And we connect the click of that button to the built in terminate method that all QThread instances have
#self.ButtonLoadCatalogs_Stop.clicked.connect(self.Thread_FilesFromDir.terminate)
## We don't want to enable user to start another thread while this one is running so we disable the start button.
#self.ButtonLoadCatalogs_Start.setEnabled(False)
# @endcode
#  @param QThread Inherit from QThread
class cGetThread_FilesFromDir(QThread):

    ## Documentation of the signals to throw away to listening functions
    get_dir = pyqtSignal('QString')

    ## Documentation of the constructor
    #  @param self The object pointer.
    #  @param directory The directory to search in
    #  @param filetype The filetype to search for as string. Example filetype='.xml'
    def __init__(self, directory, filetype):
        QThread.__init__(self)
        self.CatalogsDir = directory  
        self.FileType = filetype     
        return  

    ## Documentation of the destructor
    #  @param self The object pointer.
    def __del__(self): 
        self.wait()
        return

    ## Documentation of the thread run part.
    # Function search in the given directory in all folders and subfolders for
    # files with the xml ending
    # and gives them back over the signal to the listening function.  After
    # that the thread sleeps to give the other function
    # some time to work with the data.
    #  @param self The object pointer.
    def run(self):     
        for path, subdirs, files in os.walk(self.CatalogsDir):
            for filename in files:
                if not filename.endswith(self.FileType): continue
                fullname = os.path.join(path, filename)
                self.get_dir.emit(fullname)
                self.msleep(100)     
        return

## Documentation for a class that handles 
# The following code explaines the example usage:
# @code
#self.ToolBar = cToolbar(self)
#self.ToolBar.addWidget(self.SomeWidgetThatShouldBeAdded)
# @endcode
#  @param QToolBar Inherit from QToolBar
class cToolbar(QToolBar):

    ## Documentation of the constructor
    #  @param self The object pointer.
    #  @param parent An pointer to the parent where we wont to add the toolbar
    #  @param visibility The visibility of the toolbar after initalize
    def __init__(self, parent, visibility=False):
        QToolBar.__init__(self, parent)

        self.parent = parent
        self.setFloatable(False)
        self.setMovable(False)
        self.parent.addToolBar(Qt.TopToolBarArea, self)
        self.SetVisibility(visibility)
        return

    ## Documentation of an methode to set the visibility in the toolbar
    #  @param self The object pointer.
    #  @param visibility The visibility of the toolbar
    def SetVisibility(self, visibility:bool):
        if visibility == True:
            self.show()
        else: 
            self.hide()
        return

## Documentation for a class that handles the creation of the programm about
class cAboutEntry2MenuHelpInMenuBar(QMenuBar):

    ## Documentation of the constructor
    #  @param self The object pointer.
    #  @param parent An pointer to the parent where we wont to add the menu bar entry
    #  @param visibility The visibility of the toolbar after initalize
    def __init__(self, parent, ChangeLogText='Place for the change log', ProgrammInformationText='Place for programm information', CheckBoxStartScreen=True, SizeHeightMultiplicator=None, SizeWidthMultiplicator=None):
        super(self.__class__, self).__init__() 

        self.ChangeLogText = ChangeLogText
        self.ProgrammInformationText = ProgrammInformationText
        self.CheckBoxStartScreen = CheckBoxStartScreen
        self.action_about = QtWidgets.QAction(self)
        self.action_about.setObjectName("action_about")
        self.action_about.setText("About")
        self.action_about.triggered.connect(self.DisplayProgramInformation)
        self.SizeHeightMultiplicator = SizeHeightMultiplicator
        self.SizeWidthMultiplicator = SizeWidthMultiplicator

        parent.addAction(self.action_about)

    ## Documentation for a method to display the programm informations as pop up window
    #  @param self The object pointer.  
    def DisplayProgramInformation(self): 
        window = QtWidgets.QDialog(self)    
        ui = cInfoDialog(parent=window, ChangeLogText=self.ChangeLogText, SizeHeight = QDesktopWidget().availableGeometry().height() * self.SizeHeightMultiplicator, SizeWidth=QDesktopWidget().availableGeometry().width() * self.SizeWidthMultiplicator)
        ui.label_2.setText(self.ProgrammInformationText)
        ui.checkBox_Startscreen.setEnabled(self.CheckBoxStartScreen)
        if self.CheckBoxStartScreen == False:
            ui.checkBox_Startscreen.hide()
        
        self.center(window)
        window.show()

    # From https://gist.github.com/saleph/163d73e0933044d0e2c4
    def center(self, window):
        # geometry of the main window
        qr = self.frameGeometry()

        # center point of screen
        cp = QDesktopWidget().availableGeometry().center()

        # move rectangle's center point to screen's center point
        qr.moveCenter(cp)

        # top left of rectangle becomes top left of window centering it
        window.move(qr.topLeft())


## Documentation for a class that handles the creation of undo and redo for the menubar
class cUndoEntry2MenuEditInMenuBar(QMenuBar):

    ## Documentation of the constructor
    #  @param self The object pointer.
    #  @param parent An pointer to the parent where we wont to add the menu bar entry
    #  @param visibility The visibility of the toolbar after initalize
    def __init__(self, parent, visibility=False):
        super(self.__class__, self).__init__() 

        # Create the undostack
        self.undoStack = QUndoStack(parent)      

        # Create the undo action  
        self.UndoAction = self.undoStack.createUndoAction(parent)
        self.UndoAction.setShortcuts(QKeySequence.Undo)
        self.UndoAction.setText("Undo")

        # Create the redo action
        self.RedoAction = self.undoStack.createRedoAction(parent)
        self.RedoAction.setShortcuts(QKeySequence.Redo)
        self.RedoAction.setText("Redo")

        if issubclass(type(parent),  QtWidgets.QMenu)  is True:
            parent.addAction(self.UndoAction)
            parent.addAction(self.RedoAction)

    ## Documentation of an methode to get the undo stack to work on it
    #  @param self The object pointer.
    def GetUndoStack(self):
        return self.undostack

    ## Documentation of an methode to set an command to the undostack
    #  @param self The object pointer.
    #  @param Command The command to set into the undostack
    def AddCommand2UndoStack(self, Command:QUndoCommand):
        self.undoStack.push(Command)

    ## Documentation of an methode to set easily an known element to the undostack 
    #  @param self The object pointer.
    #  @param Elemenet The known element where the command is known
    def AddElement2UndoStack(self, Element):
        if type(Element) is QLineEdit:
            self.undoStack.push(Command2Store_QLineEdit(Element))
            return True
        else:
            return False

## Documentation for a class that handles the creation of undo and redo for the toolbar
# The following code explaines the example usage:
# @code
#self.ToolBar_Undo = cUndoToolbar(self) 
# @endcode
#  @param QToolBar Inherit from QToolBar
class cUndoToolbar(cToolbar):

    ## Documentation of the constructor
    #  @param self The object pointer.
    #  @param parent An pointer to the parent where we wont to add the toolbar
    #  @param visibility The visibility of the toolbar after initalize
    def __init__(self, parent, visibility=False):
        super(self.__class__, self).__init__(parent) 

        # Create the undostack
        self.undoStack = QUndoStack(self)      

        # Create the undo action  
        self.UndoAction = self.undoStack.createUndoAction(self, self.tr("&Undo"))
        self.UndoAction.setShortcuts(QKeySequence.Undo)

        # Create the redo action
        self.RedoAction = self.undoStack.createRedoAction(self, self.tr("&Redo"))
        self.RedoAction.setShortcuts(QKeySequence.Redo)

        # Add the actions to the created toolbar (toolbar were created through inheritence of cToolbar)
        self.addAction(self.UndoAction)
        self.addAction(self.RedoAction)

        # Set the visibility to the init state
        self.SetVisibility(visibility)
        return

    ## Documentation of an methode to get the undo stack to work on it
    #  @param self The object pointer.
    def GetUndoStack(self):
        return self.undostack

    ## Documentation of an methode to set an command to the undostack
    #  @param self The object pointer.
    #  @param Command The command to set into the undostack
    def AddCommand2UndoStack(self, Command:QUndoCommand):
        self.undoStack.push(Command)

    ## Documentation of an methode to set easily an known element to the undostack 
    #  @param self The object pointer.
    #  @param Elemenet The known element where the command is known
    def AddElement2UndoStack(self, Element):
        if type(Element) is QLineEdit:
            self.undoStack.push(Command2Store_QLineEdit(Element))
            return True
        else:
            return False

## Documentation for a class that informs over the function that should be implemented when adding new commands 
#  @param QUndoCommand Inherit from QUndoCommand
class cUndoCommand(QUndoCommand):
    __metaclass__ = ABCMeta

    @abstractmethod
    ## Documentation of the constructor
    #  @param self The object pointer.
    def __init__(self):
        # Call init function of inherit class
        QUndoCommand.__init__(self) 

    ## Documentation of an function prototype
    #  @param self The object pointer.
    def undo(self):
        pass

    ## Documentation of an function prototype
    #  @param self The object pointer.
    def redo(self):
        pass

## Documentation for a class that handles the edit of an qlineedit element
#  @param cUndoCommand Inherit from cUndoCommand
class cCommand2Store_QLineEdit(cUndoCommand):

    ## Documentation of the constructor
    #  @param self The object pointer.
    #  @param LineEdit An pointer to an element of the type QLineEdit
    def __init__(self, LineEdit : QLineEdit):
        super(self.__class__, self).__init__() 
        
        # Record the field that has changed.
        self.LineEdit = field
         
        # Record the text at the time the command was created.
        self.text = LineEdit.text()

    ## Documentation of the undo for the qlineedit element
    #  @param self The object pointer.
    def undo(self):
        self.LineEdit.setText(self.text)

    ## Documentation of the redo for the qlineedit element
    #  @param self The object pointer.
    def redo(self):
        self.LineEdit.setText(self.text)

## Documentation for a class that helds all stuff for the use of an changelogbrowser
#  @param QtWidgets.QTextBrowser Inherit from QtWidgets.QTextBrowser
class cChangeLogBrowser(QtWidgets.QTextBrowser):

    ## Documentation of the constructor
    #  @param self The object pointer.
    def __init__(self, ChangeLogText=None):
        # Call init function of inherit class
        QtWidgets.QTextBrowser.__init__(self) 

        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setAutoFormatting(QtWidgets.QTextEdit.AutoNone)
        self.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.setPlaceholderText("")
        self.setObjectName("ChangeLogBrowser")
        if ChangeLogText is not None:
            self.setHtml(ChangeLogText)
        #self.setMaximumSize(QtCore.QSize(950, 16777215))

## Documentation for a class that helds all stuff for the use of an start screeen dialog
#  @param QWidget Inherit from QWidget 
class cStartScreenDialog(QWidget):

    ## Documentation of the constructor
    #  @param self The object pointer.
    def __init__(self, parent = None, ChangeLogText=None, WindowName=None, SizeWidth=None, SizeHeight=None):  
        QWidget.__init__(self, parent)

        if SizeWidth == None:
            SizeWidth   = QDesktopWidget().availableGeometry().width() * 0.5
        if SizeHeight == None:
            SizeHeight  = QDesktopWidget().availableGeometry().height() * 0.5

        ResizeWindow(self, SizeWidth, SizeHeight)
        self.setMaximumSize(QtCore.QSize(SizeWidth, SizeHeight))

        self.setObjectName("Dialog")
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.ChangeLogBrowser = cChangeLogBrowser(ChangeLogText)
        self.verticalLayout.addWidget(self.ChangeLogBrowser)

        self.checkBox_Startscreen = QtWidgets.QCheckBox(self)
        self.checkBox_Startscreen.setObjectName("checkBox_Startscreen")
        self.verticalLayout.addWidget(self.checkBox_Startscreen)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        if WindowName is not None:
            self.setWindowTitle(WindowName)
        self.show()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Welcome"))
        self.checkBox_Startscreen.setText(_translate("Dialog", "Show this message again"))

## Documentation for a class that helds all stuff for the use of an info dialog
#  @param QWidget Inherit from QWidget 
class cInfoDialog(QWidget):

    ## Documentation of the constructor
    #  @param self The object pointer.
    def __init__(self, parent = None, ChangeLogText=None, WindowName=None, SizeWidth=None, SizeHeight=None):   
        QWidget.__init__(self, parent)

        if SizeWidth == None:
            SizeWidth   = QDesktopWidget().availableGeometry().width() * 0.5
        if SizeHeight == None:
            SizeHeight  = QDesktopWidget().availableGeometry().height() * 0.5

        ResizeWindow(self, SizeWidth, SizeHeight)
        self.setMaximumSize(QtCore.QSize(SizeWidth, SizeHeight))

        self.setObjectName("Dialog")
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setMaximumSize(QtCore.QSize(SizeWidth * 0.95, SizeHeight * 0.4))
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)

        self.ChangeLogBrowser = cChangeLogBrowser(ChangeLogText)
        self.verticalLayout.addWidget(self.ChangeLogBrowser)

        #self.verticalLayout.setStretch(0, 1)

        self.checkBox_Startscreen = QtWidgets.QCheckBox(self)
        self.checkBox_Startscreen.setObjectName("checkBox_Startscreen")
        self.verticalLayout.addWidget(self.checkBox_Startscreen)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        if WindowName is not None:
            self.setWindowTitle(WindowName)

        self.show()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "About"))
        self.label_2.setText(_translate("Dialog", "TextLabel"))
        self.checkBox_Startscreen.setText(_translate("Dialog", "Show startscreen on startup"))