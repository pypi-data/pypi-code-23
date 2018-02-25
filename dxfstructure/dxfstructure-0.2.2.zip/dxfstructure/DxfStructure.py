'''
--------------------------------------------------------------------------
Copyright (C) 2017 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2017-08-10
This file is part of DxfStructure (structural engineering dxf drawing system).
http://struthon.org/

DxfStructure is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

DxfStructure is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
'''

import sys
import os
import uuid
import codecs
import re

from PyQt4 import QtCore, QtGui
import mistune
import ezdxf

from qtui.mainwindow_ui import Ui_MainWindow
from pycore.environment import DRAWING, CONCRETE_MODEL, STEEL_MODEL, SCANER, CREATOR, CHECKER, SCHEDULE, EXECUTOR
from pycore import section_base_report

APP_PATH = os.path.dirname(os.path.abspath(__file__))
_appname = 'DxfStructure'
_version = '0.2.2'

class MAINWINDOW(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #---Button clicked events - Concrete Model
        self.ui.pushButton_Concrete_Check.clicked.connect(Concrete_Check)
        self.ui.pushButton_Concrete_Check_and_save.clicked.connect(Concrete_Check_and_save)
        self.ui.pushButton_Concrete_Show_dep_and_save.clicked.connect(Concrete_Show_depndence_and_save)
        self.ui.pushButton_Concrete_Process.clicked.connect(Concrete_Process_data)
        self.ui.pushButton_Concrete_Process_renum.clicked.connect(Concrete_Process_data_with_renumerate)
        self.ui.pushButton_Concrete_Process_renum_schedules.clicked.connect(Concrete_Process_data_with_enumerate_and_schedules)
        self.ui.pushButton_Concrete_help.clicked.connect(lambda: dosyntax("myapp.show_memo('x_help_concrete.md')"))
        #---Button clicked events - Steel Model
        self.ui.pushButton_Steel_Check.clicked.connect(Steel_Check)
        self.ui.pushButton_Steel_Check_and_save.clicked.connect(Steel_Check_and_save)
        self.ui.pushButton_Steel_Show_dep_and_save.clicked.connect(Steel_Show_depndence_and_save)
        self.ui.pushButton_Steel_Process.clicked.connect(Steel_Process_data)
        self.ui.pushButton_Steel_Process_renum.clicked.connect(Steel_Process_data_with_renumerate)
        self.ui.pushButton_Steel_Process_renum_schedules.clicked.connect(Steel_Process_data_with_enumerate_and_schedules)
        self.ui.pushButton_Steel_help.clicked.connect(lambda: dosyntax("myapp.show_memo('x_help_steel.md')"))
        self.ui.comboBox_Steel_sectgroup.currentIndexChanged.connect(self.comboBox_group_selected)
        self.ui.comboBox_Steel_secttype.currentIndexChanged.connect(self.comboBox_type_selected)
        #---Button clicked events - Command        
        self.ui.pushButton_Command_show.clicked.connect(Command_show)
        self.ui.pushButton_Command_do_all.clicked.connect(Command_do_all)
        self.ui.pushButton_Command_help.clicked.connect(lambda: dosyntax("myapp.show_memo('x_help_command.md')"))
        #---Button clicked events - DS system        
        self.ui.pushButton_Inject_to_file.clicked.connect(Inject_to_file)
        self.ui.pushButton_System_help.clicked.connect(lambda: dosyntax("myapp.show_memo('x_help_system.md')"))
        #---MenuBar events
        self.ui.actionLoad_dxf.triggered.connect(Open)
        self.ui.actionAbout.triggered.connect(lambda: dosyntax("myapp.show_memo('x_about.md')"))
        self.ui.actionLicence.triggered.connect(lambda: dosyntax("myapp.show_memo('x_license.md')"))

    #--method for sys.stdout 
    def write(self, text):
        if text == '\n': return 0
        myapp.ui.textBrowser.append(text)
    
    def show_markdown(self, markdown):
        #---
        prepath = os.path.join(APP_PATH, 'memos/')
        markdown = re.sub(r'!\[(.*)\]\((.*)\)',r'![\1](%s\2)'%prepath, markdown)
        #---
        code_html = mistune.markdown(markdown)
        #---
        self.ui.textBrowser.setHtml(codecs.decode(code_html, 'utf-8'))
        
    def showStartpage(self):
        path = os.path.join(APP_PATH, 'memos/x_startpage.md')
        markdown = open(path, 'r').read()
        self.show_markdown(markdown)
    
    def show_memo(self, memoname = 'x_startpage.md'):
        path = os.path.join(APP_PATH, 'memos', memoname)
        markdown = open(path, 'r').read()
        self.show_markdown(markdown)    
        
    def comboBox_group_selected(self):
        groupselected = str(myapp.ui.comboBox_Steel_sectgroup.currentText())
        id = section_base_report.group_name_id(groupselected)
        myapp.ui.comboBox_Steel_secttype.clear()
        self.ui.comboBox_Steel_secttype.addItems(list(section_base_report.type_for_group(id)))
        self.show_markdown('```\n%s\n```'%section_base_report.report_group(id))

    def comboBox_type_selected(self):
        typeselected = str(myapp.ui.comboBox_Steel_secttype.currentText())
        if typeselected:
            self.show_markdown('```\n%s\n```'%section_base_report.report_type(typeselected))
    
def Open(test=False):
    filename = None
    if not test:
        directory = ''
        if DRAWING.filepath: directory = os.path.dirname(DRAWING.filepath)
        filename = QtGui.QFileDialog.getOpenFileName( caption = 'Load dxf', directory = directory, filter = "DXF (*.dxf)")
        filename = str(filename)
        #---
        progress(30)
    clear_model_data()
    DRAWING.open_file(filename)
    progress(60)
    SCANER.load_data_to_model()
    myapp.setWindowTitle(_appname + ' ' + _version + ' - ' + os.path.basename(DRAWING.filepath))
    progress(100)

#----------------------Ui event action Concrete model--------------------

def Concrete_Check():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    CHECKER.check_concrete()
    #--
    progress(100)

def Concrete_Check_and_save():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    CHECKER.check_concrete()
    save()
    #--
    progress(100)

def Concrete_Show_depndence_and_save():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    CHECKER.show_concrete_depenance()
    save()
    #--
    progress(100)

def Concrete_Process_data():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    CONCRETE_MODEL.selftest()
    CONCRETE_MODEL.procces_data()
    save()
    #--
    progress(100)

def Concrete_Process_data_with_renumerate():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    CONCRETE_MODEL.selftest()
    CONCRETE_MODEL.procces_data()
    CONCRETE_MODEL.renumerate()
    save()
    #--
    progress(100)

def Concrete_Process_data_with_enumerate_and_schedules():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    CONCRETE_MODEL.selftest()
    CONCRETE_MODEL.procces_data()
    CONCRETE_MODEL.renumerate()
    SCHEDULE.draw_concrete_schedule_in_drawing()
    save()
    #--
    progress(100)

#----------------------Ui event action Steel model--------------------

def Steel_Check():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    CHECKER.check_steel()
    #--
    progress(100)

def Steel_Check_and_save():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    CHECKER.check_steel()
    save()
    #--
    progress(100)

def Steel_Show_depndence_and_save():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    CHECKER.show_steel_depenance()
    save()
    #--
    progress(100)

def Steel_Process_data():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    STEEL_MODEL.selftest()
    STEEL_MODEL.procces_data()
    save()
    #--
    progress(100)

def Steel_Process_data_with_renumerate():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    STEEL_MODEL.selftest()
    STEEL_MODEL.procces_data()
    STEEL_MODEL.renumerate()
    save()
    #--
    progress(100)

def Steel_Process_data_with_enumerate_and_schedules():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    STEEL_MODEL.selftest()
    STEEL_MODEL.procces_data()
    STEEL_MODEL.renumerate()
    SCHEDULE.draw_steel_schedule_in_drawing()
    save()
    #--
    progress(100)

#----------------------Ui event action Command--------------------

def Command_show():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    myapp.ui.textBrowser.clear()
    myapp.write(EXECUTOR.get_commands_report())
    #--
    progress(100)

def Command_do_all():
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    reload_file()
    EXECUTOR.ExecuteAll()
    save()
    #--
    progress(100)
    
#----------------------Ui event action DS syetem--------------------
    
def Inject_to_file():
    
    if not DRAWING.filepath: 
        no_data_massage()
        return 0
    myapp.ui.textBrowser.clear()
    #--
    progress(50)
    #---
    CREATOR.inject_DS_system()
    save()
    #--
    progress(100)
    
#---------------------------------------------------------

def reload_file():
    clear_model_data()
    #---
    DRAWING.reload_file()
    SCANER.load_data_to_model()
    
def clear_model_data():
    DRAWING.create_data_fields()
    CONCRETE_MODEL.create_data_fields()
    STEEL_MODEL.create_data_fields()
    EXECUTOR.create_data_fields()

def save():
    message = 'File %s will be changed.'%os.path.basename(DRAWING.filepath)
    reply = QtGui.QMessageBox.question(None, 'Continue?', message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Cancel)
    if reply == QtGui.QMessageBox.Ok:
            DRAWING.save()

def no_data_massage():
    QtGui.QMessageBox.information(None, 'Info', 'Please open dxf file first')
    

def progress(value=0):
        if value:
            myapp.ui.progressBar.setVisible(True)
        myapp.ui.progressBar.setValue(value - 1)
        myapp.ui.progressBar.setValue(value)
        if value == 100:
            myapp.ui.progressBar.setVisible(False)
            myapp.ui.progressBar.setValue(0)

def dosyntax(syntax): #Function used as slot for sending simple action
    exec(syntax)
            
#---------------------------------------------------------

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MAINWINDOW()
    #--
    myapp.setWindowTitle(_appname + ' ' + _version)
    myapp.ui.progressBar.setVisible(False)
    #--
    sys.stdout = myapp
    sys.stderr = myapp
    #--
    myapp.ui.comboBox_Steel_sectgroup.addItems(section_base_report.available_groups_names)
    #--
    #Open(test=True)
    myapp.showStartpage()
    #--
    myapp.show()
    sys.exit(app.exec_())