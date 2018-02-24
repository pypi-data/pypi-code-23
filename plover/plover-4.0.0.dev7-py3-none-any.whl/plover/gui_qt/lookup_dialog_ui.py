# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plover/gui_qt/lookup_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LookupDialog(object):
    def setupUi(self, LookupDialog):
        LookupDialog.setObjectName("LookupDialog")
        LookupDialog.resize(274, 272)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LookupDialog.sizePolicy().hasHeightForWidth())
        LookupDialog.setSizePolicy(sizePolicy)
        LookupDialog.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(LookupDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(LookupDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
        self.pattern = QtWidgets.QLineEdit(LookupDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pattern.sizePolicy().hasHeightForWidth())
        self.pattern.setSizePolicy(sizePolicy)
        self.pattern.setObjectName("pattern")
        self.gridLayout.addWidget(self.pattern, 0, 0, 1, 1)
        self.suggestions = SuggestionsWidget(LookupDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.suggestions.sizePolicy().hasHeightForWidth())
        self.suggestions.setSizePolicy(sizePolicy)
        self.suggestions.setObjectName("suggestions")
        self.gridLayout.addWidget(self.suggestions, 1, 0, 1, 1)

        self.retranslateUi(LookupDialog)
        self.buttonBox.accepted.connect(LookupDialog.accept)
        self.buttonBox.rejected.connect(LookupDialog.reject)
        self.pattern.textEdited['QString'].connect(LookupDialog.on_lookup)
        QtCore.QMetaObject.connectSlotsByName(LookupDialog)

    def retranslateUi(self, LookupDialog):

        LookupDialog.setWindowTitle(_("Plover: Dictionary Lookup"))

from plover.gui_qt.suggestions_widget import SuggestionsWidget
