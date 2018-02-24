# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plover/gui_qt/config_file_widget.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FileWidget(object):
    def setupUi(self, FileWidget):
        FileWidget.setObjectName("FileWidget")
        FileWidget.resize(166, 78)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(FileWidget.sizePolicy().hasHeightForWidth())
        FileWidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(FileWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.path = QtWidgets.QLineEdit(FileWidget)
        self.path.setObjectName("path")
        self.verticalLayout.addWidget(self.path)
        self.pushButton = QtWidgets.QPushButton(FileWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(FileWidget)
        self.pushButton.clicked.connect(FileWidget.on_browse)
        self.path.editingFinished.connect(FileWidget.on_path_edited)
        QtCore.QMetaObject.connectSlotsByName(FileWidget)

    def retranslateUi(self, FileWidget):

        FileWidget.setWindowTitle(_("Form"))
        self.pushButton.setText(_("Browse"))

