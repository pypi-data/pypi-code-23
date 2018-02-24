# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plover/gui_qt/config_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ConfigWindow(object):
    def setupUi(self, ConfigWindow):
        ConfigWindow.setObjectName("ConfigWindow")
        ConfigWindow.resize(471, 480)
        icon = QtGui.QIcon()
        icon.addFile(":/plover.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ConfigWindow.setWindowIcon(icon)
        ConfigWindow.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(ConfigWindow)
        self.gridLayout.setContentsMargins(8, 8, 8, 8)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.tabs = QtWidgets.QTabWidget(ConfigWindow)
        self.tabs.setObjectName("tabs")
        self.gridLayout.addWidget(self.tabs, 0, 0, 1, 1)
        self.buttons = QtWidgets.QDialogButtonBox(ConfigWindow)
        self.buttons.setOrientation(QtCore.Qt.Horizontal)
        self.buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttons.setObjectName("buttons")
        self.gridLayout.addWidget(self.buttons, 1, 0, 1, 1)

        self.retranslateUi(ConfigWindow)
        self.tabs.setCurrentIndex(-1)
        self.buttons.accepted.connect(ConfigWindow.accept)
        self.buttons.rejected.connect(ConfigWindow.reject)
        QtCore.QMetaObject.connectSlotsByName(ConfigWindow)

    def retranslateUi(self, ConfigWindow):

        ConfigWindow.setWindowTitle(_("Plover: Configuration"))

from . import resources_rc
