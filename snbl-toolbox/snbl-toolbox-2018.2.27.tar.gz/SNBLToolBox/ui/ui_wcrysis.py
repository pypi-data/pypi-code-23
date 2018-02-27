# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/satarsa/python/snbltb/SNBLToolBox/ui/ui_wcrysis.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WCrysis(object):
    def setupUi(self, WCrysis):
        WCrysis.setObjectName("WCrysis")
        WCrysis.resize(566, 131)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/crysis"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WCrysis.setWindowIcon(icon)
        WCrysis.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(WCrysis)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(WCrysis)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.folderLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.folderLineEdit.setObjectName("folderLineEdit")
        self.horizontalLayout.addWidget(self.folderLineEdit)
        self.folderButton = QtWidgets.QPushButton(self.groupBox)
        self.folderButton.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/folder"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.folderButton.setIcon(icon1)
        self.folderButton.setObjectName("folderButton")
        self.horizontalLayout.addWidget(self.folderButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.delAnglesCheckBox = QtWidgets.QCheckBox(self.groupBox)
        self.delAnglesCheckBox.setChecked(True)
        self.delAnglesCheckBox.setObjectName("delAnglesCheckBox")
        self.verticalLayout.addWidget(self.delAnglesCheckBox)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.runButton = QtWidgets.QPushButton(self.groupBox)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/run"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.runButton.setIcon(icon2)
        self.runButton.setObjectName("runButton")
        self.horizontalLayout_3.addWidget(self.runButton)
        self.stopButton = QtWidgets.QPushButton(self.groupBox)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/stop"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stopButton.setIcon(icon3)
        self.stopButton.setObjectName("stopButton")
        self.horizontalLayout_3.addWidget(self.stopButton)
        self.runProgressBar = QtWidgets.QProgressBar(self.groupBox)
        self.runProgressBar.setProperty("value", 0)
        self.runProgressBar.setObjectName("runProgressBar")
        self.horizontalLayout_3.addWidget(self.runProgressBar)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout_3.addWidget(self.groupBox)

        self.retranslateUi(WCrysis)
        QtCore.QMetaObject.connectSlotsByName(WCrysis)

    def retranslateUi(self, WCrysis):
        _translate = QtCore.QCoreApplication.translate
        WCrysis.setWindowTitle(_translate("WCrysis", "Crysis - From Dectris to Oxford"))
        self.groupBox.setTitle(_translate("WCrysis", "Create crysalis files"))
        self.label.setText(_translate("WCrysis", "Walk through subfolders in the folder"))
        self.folderLineEdit.setToolTip(_translate("WCrysis", "<html><head/><body><p>Choose here the folder where there are your data sets</p></body></html>"))
        self.delAnglesCheckBox.setText(_translate("WCrysis", "Delete angles (for single run and crysalis < 37 only)"))
        self.runButton.setText(_translate("WCrysis", "Run"))
        self.stopButton.setText(_translate("WCrysis", "Stop"))

from . import resources_rc
