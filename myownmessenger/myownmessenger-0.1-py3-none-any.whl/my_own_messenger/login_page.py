# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login_page.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!
import os
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(646, 528)
        MainWindow.setStyleSheet("\n"
"QPushButton {\n"
"    background-color: #39424f;\n"
"    border: 1px solid #39424f;\n"
"    border-radius: 4px;\n"
"    color: #fafafa;\n"
"    padding: 8px 24px;\n"
"\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: #BBC7DA;\n"
"}\n"
"QPushButton:focus {\n"
"    outline: none;\n"
"    border: 1px solid #8699B5;\n"
"    text-decoration: underline;\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #8699B5;\n"
"}\n"
"")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(140, 20, 371, 191))
        self.label.setText("")
        parent_dir_name = (os.path.dirname(os.path.realpath(__file__))+'/')
        self.label.setPixmap(QtGui.QPixmap("{}MyOwn.png".format(parent_dir_name)))
        self.label.setObjectName("label")
        self.PasswordPlainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.PasswordPlainTextEdit.setGeometry(QtCore.QRect(180, 327, 311, 71))
        self.PasswordPlainTextEdit.setObjectName("PasswordPlainTextEdit")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(180, 190, 161, 31))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(180, 300, 68, 17))
        self.label_3.setObjectName("label_3")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(240, 420, 201, 51))
        self.pushButton.setObjectName("pushButton")
        self.LoginPlainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.LoginPlainTextEdit.setGeometry(QtCore.QRect(180, 220, 311, 78))
        self.LoginPlainTextEdit.setObjectName("LoginPlainTextEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 646, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_2.setText(_translate("MainWindow", "Login"))
        self.label_3.setText(_translate("MainWindow", "Password"))
        self.pushButton.setText(_translate("MainWindow", "Let\'s Chat!"))

