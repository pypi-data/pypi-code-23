# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class MainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName("mainWindow")
        mainWindow.resize(730, 527)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(mainWindow)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.chatGroup = QtWidgets.QGroupBox(mainWindow)
        self.chatGroup.setObjectName("chatGroup")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.chatGroup)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.chatArea = QtWidgets.QListWidget(self.chatGroup)
        self.chatArea.setObjectName("chatArea")
        self.verticalLayout_2.addWidget(self.chatArea)
        self.messageGroup = QtWidgets.QGroupBox(self.chatGroup)
        self.messageGroup.setObjectName("messageGroup")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.messageGroup)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.messageInput = QtWidgets.QTextEdit(self.messageGroup)
        self.messageInput.setObjectName("messageInput")
        self.horizontalLayout.addWidget(self.messageInput, 0, QtCore.Qt.AlignBottom)
        self.sendButton = QtWidgets.QPushButton(self.messageGroup)
        self.sendButton.setObjectName("sendButton")
        self.horizontalLayout.addWidget(self.sendButton)
        self.verticalLayout_2.addWidget(self.messageGroup)
        self.horizontalLayout_3.addWidget(self.chatGroup)
        self.contactsGroup = QtWidgets.QGroupBox(mainWindow)
        self.contactsGroup.setMaximumSize(QtCore.QSize(345, 16777215))
        self.contactsGroup.setObjectName("contactsGroup")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.contactsGroup)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.deleteContactButton = QtWidgets.QPushButton(self.contactsGroup)
        self.deleteContactButton.setObjectName("deleteContactButton")
        self.verticalLayout_3.addWidget(self.deleteContactButton, 0, QtCore.Qt.AlignRight)
        self.contactList = QtWidgets.QListWidget(self.contactsGroup)
        self.contactList.setObjectName("contactList")
        self.verticalLayout_3.addWidget(self.contactList)
        self.newContactGroup = QtWidgets.QGroupBox(self.contactsGroup)
        self.newContactGroup.setObjectName("newContactGroup")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.newContactGroup)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.newContactInput = QtWidgets.QLineEdit(self.newContactGroup)
        self.newContactInput.setObjectName("newContactInput")
        self.horizontalLayout_4.addWidget(self.newContactInput)
        self.newContactButton = QtWidgets.QPushButton(self.newContactGroup)
        self.newContactButton.setObjectName("newContactButton")
        self.horizontalLayout_4.addWidget(self.newContactButton)
        self.verticalLayout_3.addWidget(self.newContactGroup)
        self.horizontalLayout_3.addWidget(self.contactsGroup)

        self.retranslateUi(mainWindow)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def retranslateUi(self, mainWindow):
        _translate = QtCore.QCoreApplication.translate
        mainWindow.setWindowTitle(_translate("mainWindow", "Echo"))
        self.chatGroup.setTitle(_translate("mainWindow", "Chat"))
        self.messageGroup.setTitle(_translate("mainWindow", "Message"))
        self.sendButton.setText(_translate("mainWindow", "Send"))
        self.contactsGroup.setTitle(_translate("mainWindow", "Contact list"))
        self.deleteContactButton.setText(_translate("mainWindow", "X"))
        self.newContactGroup.setTitle(_translate("mainWindow", "New contact"))
        self.newContactButton.setText(_translate("mainWindow", "Add"))

