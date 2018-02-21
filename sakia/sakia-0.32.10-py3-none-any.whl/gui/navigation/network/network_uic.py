# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/navigation/network/network.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NetworkWidget(object):
    def setupUi(self, NetworkWidget):
        NetworkWidget.setObjectName("NetworkWidget")
        NetworkWidget.resize(400, 300)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(NetworkWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 6, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.button_manual_refresh = QtWidgets.QPushButton(NetworkWidget)
        self.button_manual_refresh.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/refresh_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_manual_refresh.setIcon(icon)
        self.button_manual_refresh.setIconSize(QtCore.QSize(16, 16))
        self.button_manual_refresh.setObjectName("button_manual_refresh")
        self.horizontalLayout_2.addWidget(self.button_manual_refresh)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.table_network = QtWidgets.QTableView(NetworkWidget)
        self.table_network.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table_network.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.table_network.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.table_network.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_network.setSortingEnabled(True)
        self.table_network.setObjectName("table_network")
        self.table_network.horizontalHeader().setSortIndicatorShown(True)
        self.table_network.horizontalHeader().setStretchLastSection(True)
        self.table_network.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.table_network)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(NetworkWidget)
        self.button_manual_refresh.clicked.connect(NetworkWidget.manual_nodes_refresh)
        QtCore.QMetaObject.connectSlotsByName(NetworkWidget)

    def retranslateUi(self, NetworkWidget):
        _translate = QtCore.QCoreApplication.translate
        NetworkWidget.setWindowTitle(_translate("NetworkWidget", "Form"))

import sakia.icons_rc
