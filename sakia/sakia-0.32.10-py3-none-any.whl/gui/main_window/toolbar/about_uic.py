# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/main_window/toolbar/about.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutPopup(object):
    def setupUi(self, AboutPopup):
        AboutPopup.setObjectName("AboutPopup")
        AboutPopup.resize(297, 264)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(AboutPopup)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(AboutPopup)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setOpenExternalLinks(True)
        self.label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.buttonBox = QtWidgets.QDialogButtonBox(AboutPopup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(AboutPopup)
        self.buttonBox.accepted.connect(AboutPopup.accept)
        QtCore.QMetaObject.connectSlotsByName(AboutPopup)

    def retranslateUi(self, AboutPopup):
        _translate = QtCore.QCoreApplication.translate
        AboutPopup.setWindowTitle(_translate("AboutPopup", "About"))
        self.label.setText(_translate("AboutPopup", "label"))

