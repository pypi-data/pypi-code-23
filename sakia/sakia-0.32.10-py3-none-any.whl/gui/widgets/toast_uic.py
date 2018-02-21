# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/widgets/toast.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Toast(object):
    def setupUi(self, Toast):
        Toast.setObjectName("Toast")
        Toast.resize(358, 87)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/cutecoin_logo"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Toast.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(Toast)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.display = QtWidgets.QLabel(self.centralwidget)
        self.display.setStyleSheet("")
        self.display.setText("")
        self.display.setTextFormat(QtCore.Qt.RichText)
        self.display.setAlignment(QtCore.Qt.AlignCenter)
        self.display.setObjectName("display")
        self.verticalLayout.addWidget(self.display)
        Toast.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(Toast)
        self.statusbar.setObjectName("statusbar")
        Toast.setStatusBar(self.statusbar)

        self.retranslateUi(Toast)
        QtCore.QMetaObject.connectSlotsByName(Toast)

    def retranslateUi(self, Toast):
        _translate = QtCore.QCoreApplication.translate
        Toast.setWindowTitle(_translate("Toast", "MainWindow"))

import sakia.icons_rc
