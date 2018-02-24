# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plover/gui_qt/add_translation_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AddTranslationDialog(object):
    def setupUi(self, AddTranslationDialog):
        AddTranslationDialog.setObjectName("AddTranslationDialog")
        AddTranslationDialog.resize(299, 255)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AddTranslationDialog.sizePolicy().hasHeightForWidth())
        AddTranslationDialog.setSizePolicy(sizePolicy)
        AddTranslationDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddTranslationDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.add_translation = AddTranslationWidget(AddTranslationDialog)
        self.add_translation.setObjectName("add_translation")
        self.verticalLayout.addWidget(self.add_translation)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddTranslationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AddTranslationDialog)
        self.buttonBox.accepted.connect(AddTranslationDialog.accept)
        self.buttonBox.rejected.connect(AddTranslationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddTranslationDialog)

    def retranslateUi(self, AddTranslationDialog):

        AddTranslationDialog.setWindowTitle(_("Plover: Add Translation"))

from plover.gui_qt.add_translation_widget import AddTranslationWidget
