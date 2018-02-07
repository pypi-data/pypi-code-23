# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files/ConnectDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConnectDialog(object):
    def setupUi(self, ConnectDialog):
        ConnectDialog.setObjectName("ConnectDialog")
        ConnectDialog.resize(320, 210)
        self.label = QtWidgets.QLabel(ConnectDialog)
        self.label.setGeometry(QtCore.QRect(20, 20, 91, 30))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.lineEditLogin = QtWidgets.QLineEdit(ConnectDialog)
        self.lineEditLogin.setGeometry(QtCore.QRect(120, 60, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineEditLogin.setFont(font)
        self.lineEditLogin.setObjectName("lineEditLogin")
        self.lineEditPassword = QtWidgets.QLineEdit(ConnectDialog)
        self.lineEditPassword.setGeometry(QtCore.QRect(120, 100, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineEditPassword.setFont(font)
        self.lineEditPassword.setObjectName("lineEditPassword")
        self.lineEditIP = QtWidgets.QLineEdit(ConnectDialog)
        self.lineEditIP.setGeometry(QtCore.QRect(120, 20, 181, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineEditIP.setFont(font)
        self.lineEditIP.setObjectName("lineEditIP")
        self.label_2 = QtWidgets.QLabel(ConnectDialog)
        self.label_2.setGeometry(QtCore.QRect(20, 60, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(ConnectDialog)
        self.label_3.setGeometry(QtCore.QRect(20, 100, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.pushButtonConnect = QtWidgets.QPushButton(ConnectDialog)
        self.pushButtonConnect.setGeometry(QtCore.QRect(20, 150, 281, 41))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButtonConnect.setFont(font)
        self.pushButtonConnect.setObjectName("pushButtonConnect")

        self.retranslateUi(ConnectDialog)
        QtCore.QMetaObject.connectSlotsByName(ConnectDialog)

    def retranslateUi(self, ConnectDialog):
        _translate = QtCore.QCoreApplication.translate
        ConnectDialog.setWindowTitle(_translate("ConnectDialog", "MyMessenger"))
        self.label.setText(_translate("ConnectDialog", "Сервер"))
        self.lineEditIP.setText(_translate("ConnectDialog", "127.0.0.1:7777"))
        self.label_2.setText(_translate("ConnectDialog", "Логин"))
        self.label_3.setText(_translate("ConnectDialog", "Пароль"))
        self.pushButtonConnect.setText(_translate("ConnectDialog", "Подключиться"))

