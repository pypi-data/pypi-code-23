# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/satarsa/python/snbltb/SNBLToolBox/ui/ui_wheader.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WHeader(object):
    def setupUi(self, WHeader):
        WHeader.setObjectName("WHeader")
        WHeader.resize(788, 542)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/header"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WHeader.setWindowIcon(icon)
        WHeader.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.valuesList = QtWidgets.QListWidget(WHeader)
        self.valuesList.setGeometry(QtCore.QRect(6, 65, 256, 192))
        self.valuesList.setObjectName("valuesList")
        self.resultTable = QtWidgets.QTableWidget(WHeader)
        self.resultTable.setGeometry(QtCore.QRect(6, 273, 256, 192))
        self.resultTable.setObjectName("resultTable")
        self.resultTable.setColumnCount(0)
        self.resultTable.setRowCount(0)
        self.runProgressBar = QtWidgets.QProgressBar(WHeader)
        self.runProgressBar.setGeometry(QtCore.QRect(471, 486, 123, 45))
        self.runProgressBar.setProperty("value", 0)
        self.runProgressBar.setObjectName("runProgressBar")
        self.copyButton = QtWidgets.QPushButton(WHeader)
        self.copyButton.setGeometry(QtCore.QRect(349, 482, 116, 53))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/copy"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.copyButton.setIcon(icon1)
        self.copyButton.setObjectName("copyButton")
        self.stopButton = QtWidgets.QPushButton(WHeader)
        self.stopButton.setGeometry(QtCore.QRect(116, 482, 110, 53))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/stop"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stopButton.setIcon(icon2)
        self.stopButton.setObjectName("stopButton")
        self.saveButton = QtWidgets.QPushButton(WHeader)
        self.saveButton.setGeometry(QtCore.QRect(232, 482, 111, 53))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/save"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveButton.setIcon(icon3)
        self.saveButton.setObjectName("saveButton")
        self.runButton = QtWidgets.QPushButton(WHeader)
        self.runButton.setGeometry(QtCore.QRect(7, 482, 103, 53))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(":/run"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.runButton.setIcon(icon4)
        self.runButton.setObjectName("runButton")
        self.label = QtWidgets.QLabel(WHeader)
        self.label.setGeometry(QtCore.QRect(7, 7, 38, 37))
        self.label.setObjectName("label")
        self.folderButton = QtWidgets.QToolButton(WHeader)
        self.folderButton.setGeometry(QtCore.QRect(354, 8, 48, 48))
        self.folderButton.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(":/folder"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.folderButton.setIcon(icon5)
        self.folderButton.setObjectName("folderButton")
        self.folderLineEdit = QtWidgets.QLineEdit(WHeader)
        self.folderLineEdit.setGeometry(QtCore.QRect(51, 7, 254, 51))
        self.folderLineEdit.setObjectName("folderLineEdit")

        self.retranslateUi(WHeader)
        QtCore.QMetaObject.connectSlotsByName(WHeader)

    def retranslateUi(self, WHeader):
        _translate = QtCore.QCoreApplication.translate
        WHeader.setWindowTitle(_translate("WHeader", "Header Extractor"))
        self.copyButton.setText(_translate("WHeader", "Copy"))
        self.stopButton.setText(_translate("WHeader", "Stop"))
        self.saveButton.setText(_translate("WHeader", "Save"))
        self.runButton.setText(_translate("WHeader", "Run"))
        self.label.setText(_translate("WHeader", "Dir"))

from . import resources_rc
