# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/main_window/toolbar/about_wot.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutWot(object):
    def setupUi(self, AboutWot):
        AboutWot.setObjectName("AboutWot")
        AboutWot.resize(509, 406)
        self.verticalLayout = QtWidgets.QVBoxLayout(AboutWot)
        self.verticalLayout.setObjectName("verticalLayout")
        self.group_wot = QtWidgets.QGroupBox(AboutWot)
        self.group_wot.setObjectName("group_wot")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.group_wot)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_wot = QtWidgets.QLabel(self.group_wot)
        self.label_wot.setText("")
        self.label_wot.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_wot.setObjectName("label_wot")
        self.verticalLayout_4.addWidget(self.label_wot)
        self.verticalLayout.addWidget(self.group_wot)

        self.retranslateUi(AboutWot)
        QtCore.QMetaObject.connectSlotsByName(AboutWot)

    def retranslateUi(self, AboutWot):
        _translate = QtCore.QCoreApplication.translate
        AboutWot.setWindowTitle(_translate("AboutWot", "Form"))
        self.group_wot.setTitle(_translate("AboutWot", "WoT"))

