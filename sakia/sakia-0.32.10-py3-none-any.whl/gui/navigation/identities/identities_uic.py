# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/navigation/identities/identities.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IdentitiesWidget(object):
    def setupUi(self, IdentitiesWidget):
        IdentitiesWidget.setObjectName("IdentitiesWidget")
        IdentitiesWidget.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(IdentitiesWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.edit_textsearch = QtWidgets.QLineEdit(IdentitiesWidget)
        self.edit_textsearch.setObjectName("edit_textsearch")
        self.horizontalLayout_3.addWidget(self.edit_textsearch)
        self.button_search = QtWidgets.QToolButton(IdentitiesWidget)
        self.button_search.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)
        self.button_search.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.button_search.setObjectName("button_search")
        self.horizontalLayout_3.addWidget(self.button_search)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.table_identities = QtWidgets.QTableView(IdentitiesWidget)
        self.table_identities.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table_identities.setAlternatingRowColors(True)
        self.table_identities.setSortingEnabled(True)
        self.table_identities.setObjectName("table_identities")
        self.table_identities.horizontalHeader().setSortIndicatorShown(True)
        self.table_identities.horizontalHeader().setStretchLastSection(True)
        self.table_identities.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.table_identities)
        self.busy = Busy(IdentitiesWidget)
        self.busy.setObjectName("busy")
        self.verticalLayout.addWidget(self.busy)

        self.retranslateUi(IdentitiesWidget)
        QtCore.QMetaObject.connectSlotsByName(IdentitiesWidget)

    def retranslateUi(self, IdentitiesWidget):
        _translate = QtCore.QCoreApplication.translate
        IdentitiesWidget.setWindowTitle(_translate("IdentitiesWidget", "Form"))
        self.edit_textsearch.setPlaceholderText(_translate("IdentitiesWidget", "Research a pubkey, an uid..."))
        self.button_search.setText(_translate("IdentitiesWidget", "Search"))

from sakia.gui.widgets.busy import Busy
