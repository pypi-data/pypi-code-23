# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plover/gui_qt/suggestions_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SuggestionsDialog(object):
    def setupUi(self, SuggestionsDialog):
        SuggestionsDialog.setObjectName("SuggestionsDialog")
        SuggestionsDialog.resize(247, 430)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        SuggestionsDialog.setFont(font)
        SuggestionsDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(SuggestionsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.suggestions = SuggestionsWidget(SuggestionsDialog)
        self.suggestions.setObjectName("suggestions")
        self.verticalLayout.addWidget(self.suggestions)
        self.action_Clear = QtWidgets.QAction(SuggestionsDialog)
        icon = QtGui.QIcon()
        icon.addFile(":/trash.svg", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Clear.setIcon(icon)
        self.action_Clear.setObjectName("action_Clear")
        self.action_ToggleOnTop = QtWidgets.QAction(SuggestionsDialog)
        self.action_ToggleOnTop.setCheckable(True)
        icon1 = QtGui.QIcon()
        icon1.addFile(":/pin.svg", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_ToggleOnTop.setIcon(icon1)
        self.action_ToggleOnTop.setObjectName("action_ToggleOnTop")
        self.action_SelectFont = QtWidgets.QAction(SuggestionsDialog)
        icon2 = QtGui.QIcon()
        icon2.addFile(":/font_selector.svg", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_SelectFont.setIcon(icon2)
        self.action_SelectFont.setObjectName("action_SelectFont")

        self.retranslateUi(SuggestionsDialog)
        self.action_Clear.triggered.connect(SuggestionsDialog.on_clear)
        self.action_ToggleOnTop.triggered['bool'].connect(SuggestionsDialog.on_toggle_ontop)
        self.action_SelectFont.triggered.connect(SuggestionsDialog.on_select_font)
        QtCore.QMetaObject.connectSlotsByName(SuggestionsDialog)

    def retranslateUi(self, SuggestionsDialog):

        SuggestionsDialog.setWindowTitle(_("Plover: Suggestions"))
        self.action_Clear.setText(_("&Clear"))
        self.action_Clear.setToolTip(_("Clear paper tape"))
        self.action_Clear.setShortcut(_("Ctrl+L"))
        self.action_ToggleOnTop.setText(_("&Toggle \"always on top\""))
        self.action_ToggleOnTop.setToolTip(_("Toggle \"always on top\""))
        self.action_ToggleOnTop.setShortcut(_("Ctrl+T"))
        self.action_SelectFont.setText(_("Select &font"))
        self.action_SelectFont.setToolTip(_("Open font selection dialog"))

from plover.gui_qt.suggestions_widget import SuggestionsWidget
from . import resources_rc
