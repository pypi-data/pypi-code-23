# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(616, 597)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(134, 153, 181))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(134, 153, 181))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(134, 153, 181))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(134, 153, 181))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        MainWindow.setPalette(palette)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setToolTipDuration(1)
        MainWindow.setStyleSheet("\n"
"\n"
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
"\n"
"QListWidget {\n"
"    border: none;\n"
"}\n"
"QListWidget QWidget {\n"
"    margin: 0;\n"
"    padding: 0;\n"
"}\n"
"\n"
"QListWidget QPushButton {\n"
"    width: 16px;\n"
"    height: 16px;\n"
"    margin: 0;\n"
"    padding: 3px;\n"
"    background-color: #fff;\n"
"    border: none;\n"
"    color: orange;\n"
"}\n"
"QListWidget QPushButton:hover {\n"
"    background-color: orange;\n"
"    color: white;\n"
"}\n"
"\n"
"QTextEdit {\n"
"        border: 1px solid #8699B5;\n"
"    border-radius: 4px;\n"
"}\n"
"QTextEdit:focus {\n"
"    border: 3px solid #8699B5;\n"
"}\n"
"\n"
"QListView::item:alternate {\n"
"    background: #EEEEEE;\n"
"}\n"
"\n"
"QListView::item:selected {\n"
"    border: 1px solid #8699B5;\n"
"    color: #000;\n"
"    font-weight: 800;\n"
"    background-color: #fff;\n"
"}\n"
"\n"
"QListView::item:selected:!active {\n"
"    border: 1px solid lightgrey;\n"
"}\n"
"\n"
"QListView::item:hover {\n"
"    border: 1px solid lightgrey;\n"
"}\n"
"\n"
"QLineEdit {\n"
"    border: 1px solid #66BB6A;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"QLineEdit[echoMode=\"2\"] {\n"
"    lineedit-password-character: 9679;\n"
"}\n"
"\n"
"QLineEdit:focus {\n"
"    border: 2px solid #8699B5;\n"
"}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(420, 350, 151, 111))
        self.groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.setFlat(True)
        self.groupBox.setObjectName("groupBox")
        self.textEditUsername = QtWidgets.QTextEdit(self.groupBox)
        self.textEditUsername.setGeometry(QtCore.QRect(10, 30, 131, 31))
        self.textEditUsername.setAcceptRichText(True)
        self.textEditUsername.setObjectName("textEditUsername")
        self.pushButtonAddContact = QtWidgets.QPushButton(self.groupBox)
        self.pushButtonAddContact.setGeometry(QtCore.QRect(30, 70, 81, 31))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("../../../../../Downloads/icons8-plus.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonAddContact.setIcon(icon1)
        self.pushButtonAddContact.setObjectName("pushButtonAddContact")
        self.groupBox_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_2.setGeometry(QtCore.QRect(420, 70, 151, 271))
        self.groupBox_2.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_2.setFlat(True)
        self.groupBox_2.setCheckable(False)
        self.groupBox_2.setObjectName("groupBox_2")
        self.listWidgetContacts = QtWidgets.QListWidget(self.groupBox_2)
        self.listWidgetContacts.setGeometry(QtCore.QRect(10, 30, 131, 231))
        self.listWidgetContacts.setObjectName("listWidgetContacts")
        self.groupBox_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_3.setGeometry(QtCore.QRect(20, 10, 391, 211))
        self.groupBox_3.setFlat(True)
        self.groupBox_3.setObjectName("groupBox_3")
        self.listWidgetMessages = QtWidgets.QListWidget(self.groupBox_3)
        self.listWidgetMessages.setGeometry(QtCore.QRect(10, 30, 371, 181))
        self.listWidgetMessages.setObjectName("listWidgetMessages")
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(20, 440, 391, 101))
        self.groupBox_4.setFlat(True)
        self.groupBox_4.setObjectName("groupBox_4")
        self.textEditMessage = QtWidgets.QTextEdit(self.groupBox_4)
        self.textEditMessage.setGeometry(QtCore.QRect(10, 30, 371, 61))
        self.textEditMessage.setLineWidth(1)
        self.textEditMessage.setObjectName("textEditMessage")
        self.groupBox_6 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_6.setGeometry(QtCore.QRect(20, 240, 391, 191))
        self.groupBox_6.setFlat(True)
        self.groupBox_6.setObjectName("groupBox_6")
        self.listWidgetHistory = QtWidgets.QListWidget(self.groupBox_6)
        self.listWidgetHistory.setGeometry(QtCore.QRect(10, 30, 371, 151))
        self.listWidgetHistory.setObjectName("listWidgetHistory")
        self.labelAvatar = QtWidgets.QLabel(self.centralwidget)
        self.labelAvatar.setGeometry(QtCore.QRect(470, 10, 60, 60))
        self.labelAvatar.setText("")
        self.labelAvatar.setPixmap(QtGui.QPixmap("generic-avatar.png"))
        self.labelAvatar.setScaledContents(True)
        self.labelAvatar.setAlignment(QtCore.Qt.AlignCenter)
        self.labelAvatar.setWordWrap(False)
        self.labelAvatar.setObjectName("labelAvatar")
        self.PushButtonSend = QtWidgets.QPushButton(self.centralwidget)
        self.PushButtonSend.setGeometry(QtCore.QRect(440, 480, 111, 41))
        self.PushButtonSend.setIcon(icon)
        self.PushButtonSend.setObjectName("PushButtonSend")
        self.groupBox.raise_()
        self.groupBox_2.raise_()
        self.groupBox_3.raise_()
        self.groupBox_4.raise_()
        self.groupBox_6.raise_()
        self.labelAvatar.raise_()
        self.textEditMessage.raise_()
        self.PushButtonSend.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 616, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MyOwnMessenger"))
        self.groupBox.setTitle(_translate("MainWindow", "Change contact list"))
        self.pushButtonAddContact.setText(_translate("MainWindow", "Add"))
        self.groupBox_2.setTitle(_translate("MainWindow", "Contact list"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Current chat"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Enter your message"))
        self.groupBox_6.setTitle(_translate("MainWindow", "History"))
        self.PushButtonSend.setText(_translate("MainWindow", "Send"))

