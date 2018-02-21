# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/main_window/toolbar/about_money.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutMoney(object):
    def setupUi(self, AboutMoney):
        AboutMoney.setObjectName("AboutMoney")
        AboutMoney.resize(509, 406)
        self.verticalLayout = QtWidgets.QVBoxLayout(AboutMoney)
        self.verticalLayout.setObjectName("verticalLayout")
        self.group_general = QtWidgets.QGroupBox(AboutMoney)
        self.group_general.setStyleSheet("")
        self.group_general.setFlat(False)
        self.group_general.setObjectName("group_general")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.group_general)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_general = QtWidgets.QLabel(self.group_general)
        self.label_general.setText("")
        self.label_general.setScaledContents(False)
        self.label_general.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_general.setObjectName("label_general")
        self.verticalLayout_2.addWidget(self.label_general)
        self.verticalLayout.addWidget(self.group_general)
        self.group_rules = QtWidgets.QGroupBox(AboutMoney)
        self.group_rules.setObjectName("group_rules")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.group_rules)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_rules = QtWidgets.QLabel(self.group_rules)
        self.label_rules.setText("")
        self.label_rules.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_rules.setObjectName("label_rules")
        self.verticalLayout_6.addWidget(self.label_rules)
        self.verticalLayout.addWidget(self.group_rules)
        self.group_money = QtWidgets.QGroupBox(AboutMoney)
        self.group_money.setObjectName("group_money")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.group_money)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_money = QtWidgets.QLabel(self.group_money)
        self.label_money.setText("")
        self.label_money.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_money.setObjectName("label_money")
        self.verticalLayout_3.addWidget(self.label_money)
        self.verticalLayout.addWidget(self.group_money)

        self.retranslateUi(AboutMoney)
        QtCore.QMetaObject.connectSlotsByName(AboutMoney)

    def retranslateUi(self, AboutMoney):
        _translate = QtCore.QCoreApplication.translate
        AboutMoney.setWindowTitle(_translate("AboutMoney", "Form"))
        self.group_general.setTitle(_translate("AboutMoney", "General"))
        self.group_rules.setTitle(_translate("AboutMoney", "Rules"))
        self.group_money.setTitle(_translate("AboutMoney", "Money"))

