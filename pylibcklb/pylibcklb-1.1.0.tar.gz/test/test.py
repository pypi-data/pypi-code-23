## Test file for the pylibcklb package
#
# @file		    test.py
# @author	    Tobias Ecklebe tobias.ecklebe@outlook.de
# @date		    22.11.2017
# @version	    0.1.0
# @bug          No bugs at the moment.
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
from pylibcklb.pyqt5.classes import cStartScreenDialog, cInfoDialog, cApplicationMainWindow_Extended, cApplicationMainWindow_BaseClass
from pylibcklb.FunctionLibrary import SaveChangesOfDictBack2File, CreateFile, HelloWorld
from pylibcklb.pyqt5.functions import *
from pylibcklb.pyqt5.classes import *
import sys
import markdown2
import os
from metadata_for_test  import Gui

def reading(self):
    with open('deed.txt', 'r') as f:
        s = f.read()
        self.whip = ast.literal_eval(s)

#Documentation for the main method
def test():
    # Create a new qt application
    app = QtWidgets.QApplication(sys.argv)
    HelloWorld()
    #ChangeLogText = ''
    #try:
    #    with open(('..\CHANGELOG.md')) as f:                                                
    #        ChangeLogText = markdown2.markdown(f.read()) 
    #    f.close()
    #except (OSError, IOError) as e:
    #    ChangeLogText = str(e)

    #CreateFile(os.getcwd(), 'EFOS.temp', ChangeLogText, Hidden=True)
    window = cApplicationMainWindow_BaseClass('cApplicationMainWindow_BaseClass')
    editor = QtWidgets.QLineEdit(window)
    path = BrowseFolderRelative(editor,'Folderpath')
    #ui = cStartScreenDialog(ChangeLogText=ChangeLogText)    
    #ui2 = cInfoDialog(ChangeLogText=ChangeLogText)

    #window2 = cApplicationMainWindow_Extended('cApplicationMainWindow_MenuBar')

    #print('pre:  '+ str(Gui.GuiVariables_Static))
    #Gui.GuiVariables_Static['StartScreeen'] = False
    #SaveChangesOfDictBack2File(os.getcwd()+'/test','metadata_for_test.py', 'GuiVariables_Static', Gui.GuiVariables_Static)
    #print('post: '+ str(Gui.GuiVariables_Static))

    # Execute the new created application and close all if application is closed
    sys.exit(app.exec_())

class Window(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.stacked_widget = QtWidgets.QStackedWidget()
        #self.button = QtWidgets.QPushButton("Next")

        #self.button.clicked.connect(self.__next_page)

        layout = CreateVerticalLayout(layout_name = 'NewLayout')
        layout.addWidget(self.stacked_widget)
        #layout.addWidget(self.button)

        self.button    = CreatePushButton(layout, self.__next_page, name = 'Next', button_text = 'Next')

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.stacked_widget.addWidget(QtWidgets.QLabel("Page 1"))
        self.stacked_widget.addWidget(QtWidgets.QLabel("Page 2"))
        self.stacked_widget.addWidget(QtWidgets.QLabel("Page 3"))

    def __next_page(self):
        idx = self.stacked_widget.currentIndex()
        if idx < self.stacked_widget.count() - 1:
            self.stacked_widget.setCurrentIndex(idx + 1)
        else:
            self.stacked_widget.setCurrentIndex(0)


if __name__ == "__main__":
    #test()
    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()

    sys.exit(app.exec_())
    #sys.exit(test())

