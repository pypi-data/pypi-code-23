# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'new_chat.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(402, 467)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(120, 420, 161, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.textEditSearch = QtWidgets.QTextEdit(Dialog)
        self.textEditSearch.setGeometry(QtCore.QRect(20, 40, 341, 51))
        self.textEditSearch.setObjectName("textEditSearch")
        self.listWidgetYourContacts = QtWidgets.QListWidget(Dialog)
        self.listWidgetYourContacts.setGeometry(QtCore.QRect(10, 140, 161, 261))
        self.listWidgetYourContacts.setObjectName("listWidgetYourContacts")
        self.labelChatName = QtWidgets.QLabel(Dialog)
        self.labelChatName.setGeometry(QtCore.QRect(120, 20, 181, 16))
        self.labelChatName.setObjectName("labelChatName")
        self.listWidgetYourContacts_2 = QtWidgets.QListWidget(Dialog)
        self.listWidgetYourContacts_2.setGeometry(QtCore.QRect(220, 140, 161, 261))
        self.listWidgetYourContacts_2.setObjectName("listWidgetYourContacts_2")
        self.labelYourContacts = QtWidgets.QLabel(Dialog)
        self.labelYourContacts.setGeometry(QtCore.QRect(40, 120, 121, 16))
        self.labelYourContacts.setObjectName("labelYourContacts")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(270, 120, 60, 16))
        self.label.setObjectName("label")
        self.pushButtonAdd = QtWidgets.QPushButton(Dialog)
        self.pushButtonAdd.setGeometry(QtCore.QRect(180, 200, 31, 61))
        self.pushButtonAdd.setObjectName("pushButtonAdd")
        self.pushButtonRemove = QtWidgets.QPushButton(Dialog)
        self.pushButtonRemove.setGeometry(QtCore.QRect(180, 280, 31, 61))
        self.pushButtonRemove.setObjectName("pushButtonRemove")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "New Chat"))
        self.labelChatName.setText(_translate("Dialog", "Enter name of new chat"))
        self.labelYourContacts.setText(_translate("Dialog", "Your contacts"))
        self.label.setText(_translate("Dialog", "New chat"))
        self.pushButtonAdd.setText(_translate("Dialog", ">"))
        self.pushButtonRemove.setText(_translate("Dialog", "<"))

