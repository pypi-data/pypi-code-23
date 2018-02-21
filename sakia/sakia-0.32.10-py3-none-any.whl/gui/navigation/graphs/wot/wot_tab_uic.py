# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/navigation/graphs/wot/wot_tab.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WotWidget(object):
    def setupUi(self, WotWidget):
        WotWidget.setObjectName("WotWidget")
        WotWidget.resize(522, 442)
        self.verticalLayout = QtWidgets.QVBoxLayout(WotWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphics_view = WotGraphicsView(WotWidget)
        self.graphics_view.setViewportUpdateMode(QtWidgets.QGraphicsView.BoundingRectViewportUpdate)
        self.graphics_view.setObjectName("graphics_view")
        self.verticalLayout.addWidget(self.graphics_view)

        self.retranslateUi(WotWidget)
        QtCore.QMetaObject.connectSlotsByName(WotWidget)

    def retranslateUi(self, WotWidget):
        _translate = QtCore.QCoreApplication.translate
        WotWidget.setWindowTitle(_translate("WotWidget", "Form"))

from sakia.gui.navigation.graphs.wot.graphics_view import WotGraphicsView
import sakia.icons_rc
