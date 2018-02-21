# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/navigation/identity/identity.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IdentityWidget(object):
    def setupUi(self, IdentityWidget):
        IdentityWidget.setObjectName("IdentityWidget")
        IdentityWidget.resize(538, 737)
        IdentityWidget.setStyleSheet("QGroupBox {\n"
"    border: 1px solid gray;\n"
"    border-radius: 9px;\n"
"    margin-top: 0.5em;\n"
"}\n"
"\n"
"QGroupBox::title {\n"
"    subcontrol-origin: margin;\n"
"    left: 10px;\n"
"    padding: 0 3px 0 3px;\n"
"    font-weight: bold;\n"
"}")
        self.gridLayout = QtWidgets.QGridLayout(IdentityWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.stacked_widget = QtWidgets.QStackedWidget(IdentityWidget)
        self.stacked_widget.setObjectName("stacked_widget")
        self.page_empty = QtWidgets.QWidget()
        self.page_empty.setObjectName("page_empty")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.page_empty)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.table_certifiers = QtWidgets.QTableView(self.page_empty)
        self.table_certifiers.setObjectName("table_certifiers")
        self.table_certifiers.horizontalHeader().setSortIndicatorShown(True)
        self.table_certifiers.horizontalHeader().setStretchLastSection(True)
        self.table_certifiers.verticalHeader().setVisible(False)
        self.verticalLayout_3.addWidget(self.table_certifiers)
        self.stacked_widget.addWidget(self.page_empty)
        self.gridLayout.addWidget(self.stacked_widget, 2, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 6, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.button_certify = QtWidgets.QPushButton(IdentityWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/certification_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_certify.setIcon(icon)
        self.button_certify.setObjectName("button_certify")
        self.horizontalLayout.addWidget(self.button_certify)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.group_uid_state = QtWidgets.QGroupBox(IdentityWidget)
        self.group_uid_state.setObjectName("group_uid_state")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.group_uid_state)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_written = QtWidgets.QLabel(self.group_uid_state)
        self.label_written.setText("")
        self.label_written.setObjectName("label_written")
        self.horizontalLayout_3.addWidget(self.label_written)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.button_refresh = QtWidgets.QPushButton(self.group_uid_state)
        self.button_refresh.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/refresh_icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_refresh.setIcon(icon1)
        self.button_refresh.setObjectName("button_refresh")
        self.horizontalLayout_3.addWidget(self.button_refresh)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.label_identity = QtWidgets.QLabel(self.group_uid_state)
        self.label_identity.setText("")
        self.label_identity.setObjectName("label_identity")
        self.verticalLayout.addWidget(self.label_identity)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 6, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_membership = QtWidgets.QLabel(self.group_uid_state)
        self.label_membership.setText("")
        self.label_membership.setObjectName("label_membership")
        self.horizontalLayout_2.addWidget(self.label_membership)
        self.button_membership = QtWidgets.QPushButton(self.group_uid_state)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_membership.sizePolicy().hasHeightForWidth())
        self.button_membership.setSizePolicy(sizePolicy)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/renew_membership"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.button_membership.setIcon(icon2)
        self.button_membership.setIconSize(QtCore.QSize(20, 20))
        self.button_membership.setObjectName("button_membership")
        self.horizontalLayout_2.addWidget(self.button_membership)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addWidget(self.group_uid_state, 0, 0, 1, 1)

        self.retranslateUi(IdentityWidget)
        self.stacked_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(IdentityWidget)

    def retranslateUi(self, IdentityWidget):
        _translate = QtCore.QCoreApplication.translate
        IdentityWidget.setWindowTitle(_translate("IdentityWidget", "Form"))
        self.button_certify.setText(_translate("IdentityWidget", "Certify an identity"))
        self.group_uid_state.setTitle(_translate("IdentityWidget", "Membership status"))
        self.button_membership.setText(_translate("IdentityWidget", "Renew membership"))

import sakia.icons_rc
