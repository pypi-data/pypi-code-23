# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/navigation/homescreen/homescreen.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HomescreenWidget(object):
    def setupUi(self, HomescreenWidget):
        HomescreenWidget.setObjectName("HomescreenWidget")
        HomescreenWidget.resize(648, 472)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(HomescreenWidget.sizePolicy().hasHeightForWidth())
        HomescreenWidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(HomescreenWidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.retranslateUi(HomescreenWidget)
        QtCore.QMetaObject.connectSlotsByName(HomescreenWidget)

    def retranslateUi(self, HomescreenWidget):
        _translate = QtCore.QCoreApplication.translate
        HomescreenWidget.setWindowTitle(_translate("HomescreenWidget", "Form"))

import sakia.icons_rc
