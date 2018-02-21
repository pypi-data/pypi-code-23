# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/sub/search_user/search_user.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SearchUserWidget(object):
    def setupUi(self, SearchUserWidget):
        SearchUserWidget.setObjectName("SearchUserWidget")
        SearchUserWidget.resize(400, 44)
        self.horizontalLayout = QtWidgets.QHBoxLayout(SearchUserWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.combobox_search = QtWidgets.QComboBox(SearchUserWidget)
        self.combobox_search.setEditable(True)
        self.combobox_search.setObjectName("combobox_search")
        self.horizontalLayout.addWidget(self.combobox_search)
        self.button_reset = QtWidgets.QPushButton(SearchUserWidget)
        self.button_reset.setMaximumSize(QtCore.QSize(85, 27))
        self.button_reset.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/home_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_reset.setIcon(icon)
        self.button_reset.setObjectName("button_reset")
        self.horizontalLayout.addWidget(self.button_reset)

        self.retranslateUi(SearchUserWidget)
        QtCore.QMetaObject.connectSlotsByName(SearchUserWidget)

    def retranslateUi(self, SearchUserWidget):
        _translate = QtCore.QCoreApplication.translate
        SearchUserWidget.setWindowTitle(_translate("SearchUserWidget", "Form"))
        self.button_reset.setToolTip(_translate("SearchUserWidget", "Center the view on me"))

import sakia.icons_rc
