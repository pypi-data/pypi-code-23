# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/dialogs/connection_cfg/congratulation.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CongratulationPopup(object):
    def setupUi(self, CongratulationPopup):
        CongratulationPopup.setObjectName("CongratulationPopup")
        CongratulationPopup.resize(350, 198)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(CongratulationPopup.sizePolicy().hasHeightForWidth())
        CongratulationPopup.setSizePolicy(sizePolicy)
        CongratulationPopup.setMaximumSize(QtCore.QSize(350, 16777215))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(CongratulationPopup)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(CongratulationPopup)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignTop)
        self.label.setOpenExternalLinks(True)
        self.label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.buttonBox = QtWidgets.QDialogButtonBox(CongratulationPopup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(CongratulationPopup)
        self.buttonBox.accepted.connect(CongratulationPopup.accept)
        QtCore.QMetaObject.connectSlotsByName(CongratulationPopup)

    def retranslateUi(self, CongratulationPopup):
        _translate = QtCore.QCoreApplication.translate
        CongratulationPopup.setWindowTitle(_translate("CongratulationPopup", "Congratulation"))
        self.label.setText(_translate("CongratulationPopup", "label"))

