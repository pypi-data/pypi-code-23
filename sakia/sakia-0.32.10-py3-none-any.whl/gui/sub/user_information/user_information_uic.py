# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/sub/user_information/user_information.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_UserInformationWidget(object):
    def setupUi(self, UserInformationWidget):
        UserInformationWidget.setObjectName("UserInformationWidget")
        UserInformationWidget.resize(392, 251)
        self.verticalLayout = QtWidgets.QVBoxLayout(UserInformationWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupbox_user = QtWidgets.QGroupBox(UserInformationWidget)
        self.groupbox_user.setStyleSheet("QGroupBox {\n"
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
        self.groupbox_user.setObjectName("groupbox_user")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupbox_user)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scrollArea = QtWidgets.QScrollArea(self.groupbox_user)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 362, 212))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_path = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_path.setText("")
        self.label_path.setObjectName("label_path")
        self.gridLayout_2.addWidget(self.label_path, 5, 0, 1, 1)
        self.label_properties = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_properties.setText("")
        self.label_properties.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_properties.setObjectName("label_properties")
        self.gridLayout_2.addWidget(self.label_properties, 4, 0, 1, 1)
        self.label_icon = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_icon.sizePolicy().hasHeightForWidth())
        self.label_icon.setSizePolicy(sizePolicy)
        self.label_icon.setMaximumSize(QtCore.QSize(81, 71))
        self.label_icon.setText("")
        self.label_icon.setPixmap(QtGui.QPixmap(":/icons/member_icon"))
        self.label_icon.setScaledContents(True)
        self.label_icon.setObjectName("label_icon")
        self.gridLayout_2.addWidget(self.label_icon, 1, 0, 1, 1)
        self.label_uid = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.label_uid.setMaximumSize(QtCore.QSize(471, 51))
        self.label_uid.setText("")
        self.label_uid.setObjectName("label_uid")
        self.gridLayout_2.addWidget(self.label_uid, 1, 1, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.groupbox_user)

        self.retranslateUi(UserInformationWidget)
        QtCore.QMetaObject.connectSlotsByName(UserInformationWidget)

    def retranslateUi(self, UserInformationWidget):
        _translate = QtCore.QCoreApplication.translate
        UserInformationWidget.setWindowTitle(_translate("UserInformationWidget", "Member informations"))
        self.groupbox_user.setTitle(_translate("UserInformationWidget", "User"))

import sakia.icons_rc
