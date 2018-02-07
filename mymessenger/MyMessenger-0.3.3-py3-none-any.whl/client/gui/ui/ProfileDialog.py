# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files/ProfileDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ProfileDialog(object):
    def setupUi(self, ProfileDialog):
        ProfileDialog.setObjectName("ProfileDialog")
        ProfileDialog.resize(300, 300)
        self.groupBox = QtWidgets.QGroupBox(ProfileDialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 281, 151))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.pushButtonBrowse = QtWidgets.QPushButton(self.groupBox)
        self.pushButtonBrowse.setGeometry(QtCore.QRect(140, 40, 85, 27))
        self.pushButtonBrowse.setObjectName("pushButtonBrowse")
        self.labelAvatarImage = QtWidgets.QLabel(self.groupBox)
        self.labelAvatarImage.setGeometry(QtCore.QRect(10, 40, 100, 100))
        self.labelAvatarImage.setText("")
        self.labelAvatarImage.setObjectName("labelAvatarImage")
        self.lineEditLogin = QtWidgets.QLineEdit(ProfileDialog)
        self.lineEditLogin.setGeometry(QtCore.QRect(50, 200, 113, 27))
        self.lineEditLogin.setObjectName("lineEditLogin")
        self.lineEditPassword = QtWidgets.QLineEdit(ProfileDialog)
        self.lineEditPassword.setGeometry(QtCore.QRect(50, 260, 113, 27))
        self.lineEditPassword.setObjectName("lineEditPassword")
        self.labelLogin = QtWidgets.QLabel(ProfileDialog)
        self.labelLogin.setGeometry(QtCore.QRect(20, 170, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelLogin.setFont(font)
        self.labelLogin.setObjectName("labelLogin")
        self.labelPassword = QtWidgets.QLabel(ProfileDialog)
        self.labelPassword.setGeometry(QtCore.QRect(20, 230, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelPassword.setFont(font)
        self.labelPassword.setObjectName("labelPassword")
        self.pushButtonSave = QtWidgets.QPushButton(ProfileDialog)
        self.pushButtonSave.setGeometry(QtCore.QRect(200, 260, 85, 27))
        self.pushButtonSave.setObjectName("pushButtonSave")

        self.retranslateUi(ProfileDialog)
        QtCore.QMetaObject.connectSlotsByName(ProfileDialog)

    def retranslateUi(self, ProfileDialog):
        _translate = QtCore.QCoreApplication.translate
        ProfileDialog.setWindowTitle(_translate("ProfileDialog", "Profile"))
        self.groupBox.setTitle(_translate("ProfileDialog", "Аватар"))
        self.pushButtonBrowse.setText(_translate("ProfileDialog", "Обзор..."))
        self.labelLogin.setText(_translate("ProfileDialog", "Логин"))
        self.labelPassword.setText(_translate("ProfileDialog", "Пароль"))
        self.pushButtonSave.setText(_translate("ProfileDialog", "Сохранить"))

