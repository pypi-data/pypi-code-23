# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plover/gui_qt/config_keyboard_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_KeyboardWidget(object):
    def setupUi(self, KeyboardWidget):
        KeyboardWidget.setObjectName("KeyboardWidget")
        KeyboardWidget.resize(117, 38)
        self.gridLayout = QtWidgets.QGridLayout(KeyboardWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.arpeggiate = QtWidgets.QCheckBox(KeyboardWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.arpeggiate.sizePolicy().hasHeightForWidth())
        self.arpeggiate.setSizePolicy(sizePolicy)
        self.arpeggiate.setObjectName("arpeggiate")
        self.gridLayout.addWidget(self.arpeggiate, 0, 0, 1, 1)

        self.retranslateUi(KeyboardWidget)
        self.arpeggiate.clicked['bool'].connect(KeyboardWidget.on_arpeggiate_changed)
        QtCore.QMetaObject.connectSlotsByName(KeyboardWidget)

    def retranslateUi(self, KeyboardWidget):

        KeyboardWidget.setWindowTitle(_("Form"))
        self.arpeggiate.setText(_("Arpeggiate"))

