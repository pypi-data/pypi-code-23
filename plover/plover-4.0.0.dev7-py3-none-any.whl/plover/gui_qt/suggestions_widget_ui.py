# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plover/gui_qt/suggestions_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SuggestionsWidget(object):
    def setupUi(self, SuggestionsWidget):
        SuggestionsWidget.setObjectName("SuggestionsWidget")
        SuggestionsWidget.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(SuggestionsWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.suggestions = QtWidgets.QTextEdit(SuggestionsWidget)
        self.suggestions.setFrameShape(QtWidgets.QFrame.Box)
        self.suggestions.setUndoRedoEnabled(False)
        self.suggestions.setReadOnly(True)
        self.suggestions.setObjectName("suggestions")
        self.gridLayout.addWidget(self.suggestions, 0, 0, 1, 1)

        self.retranslateUi(SuggestionsWidget)
        QtCore.QMetaObject.connectSlotsByName(SuggestionsWidget)

    def retranslateUi(self, SuggestionsWidget):

        SuggestionsWidget.setWindowTitle(_("Form"))

