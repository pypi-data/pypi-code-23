# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/sub/password_input/password_input.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PasswordInputWidget(object):
    def setupUi(self, PasswordInputWidget):
        PasswordInputWidget.setObjectName("PasswordInputWidget")
        PasswordInputWidget.resize(400, 106)
        self.verticalLayout = QtWidgets.QVBoxLayout(PasswordInputWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.edit_secret_key = QtWidgets.QLineEdit(PasswordInputWidget)
        self.edit_secret_key.setEchoMode(QtWidgets.QLineEdit.Password)
        self.edit_secret_key.setObjectName("edit_secret_key")
        self.verticalLayout.addWidget(self.edit_secret_key)
        self.edit_password = QtWidgets.QLineEdit(PasswordInputWidget)
        self.edit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.edit_password.setObjectName("edit_password")
        self.verticalLayout.addWidget(self.edit_password)
        self.label_info = QtWidgets.QLabel(PasswordInputWidget)
        self.label_info.setText("")
        self.label_info.setObjectName("label_info")
        self.verticalLayout.addWidget(self.label_info)

        self.retranslateUi(PasswordInputWidget)
        QtCore.QMetaObject.connectSlotsByName(PasswordInputWidget)

    def retranslateUi(self, PasswordInputWidget):
        _translate = QtCore.QCoreApplication.translate
        PasswordInputWidget.setWindowTitle(_translate("PasswordInputWidget", "Please enter your password"))
        self.edit_secret_key.setPlaceholderText(_translate("PasswordInputWidget", "Please enter your secret key"))
        self.edit_password.setPlaceholderText(_translate("PasswordInputWidget", "Please enter your password"))

