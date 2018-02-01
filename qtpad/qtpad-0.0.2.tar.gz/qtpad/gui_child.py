# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qtpad/gui_child.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(279, 231)
        Form.setAutoFillBackground(False)
        Form.setStyleSheet("QWidget.QPlainTextEdit, QWidget.QTextEdit\n"
"{\n"
"    border: none;\n"
"}\n"
"\n"
"QWidget.QLineEdit\n"
"{\n"
"    border: 1px solid black;\n"
"    margin: 6px;\n"
"}\n"
"\n"
"QWidget.QLabel#renameLabel\n"
"{\n"
"    padding-top: 3px;\n"
"    padding-left: 4px;\n"
"}\n"
"\n"
"QWidget.QScrollBar\n"
"{\n"
"    width: 18px;\n"
"    color: black;\n"
"    background-color: lightgray\n"
"}\n"
"\n"
"")
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.iconLabel = QtWidgets.QLabel(Form)
        self.iconLabel.setMinimumSize(QtCore.QSize(30, 0))
        self.iconLabel.setMaximumSize(QtCore.QSize(30, 16777215))
        self.iconLabel.setText("")
        self.iconLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.iconLabel.setObjectName("iconLabel")
        self.gridLayout.addWidget(self.iconLabel, 0, 0, 1, 1)
        self.closeButton = QtWidgets.QPushButton(Form)
        self.closeButton.setMinimumSize(QtCore.QSize(30, 0))
        self.closeButton.setMaximumSize(QtCore.QSize(30, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.closeButton.setFont(font)
        self.closeButton.setObjectName("closeButton")
        self.gridLayout.addWidget(self.closeButton, 0, 2, 1, 1)
        self.textEdit = QtWidgets.QPlainTextEdit(Form)
        self.textEdit.setPlainText("")
        self.textEdit.setObjectName("textEdit")
        self.gridLayout.addWidget(self.textEdit, 2, 0, 1, 3)
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 0, 1, 3)
        self.renameText = QtWidgets.QLineEdit(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.renameText.sizePolicy().hasHeightForWidth())
        self.renameText.setSizePolicy(sizePolicy)
        self.renameText.setAcceptDrops(False)
        self.renameText.setFrame(True)
        self.renameText.setObjectName("renameText")
        self.gridLayout.addWidget(self.renameText, 5, 0, 1, 3)
        self.titleLabel = QtWidgets.QLabel(Form)
        self.titleLabel.setMinimumSize(QtCore.QSize(0, 24))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.titleLabel.setFont(font)
        self.titleLabel.setToolTipDuration(0)
        self.titleLabel.setAutoFillBackground(True)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setObjectName("titleLabel")
        self.gridLayout.addWidget(self.titleLabel, 0, 1, 1, 1)
        self.renameLabel = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.renameLabel.sizePolicy().hasHeightForWidth())
        self.renameLabel.setSizePolicy(sizePolicy)
        self.renameLabel.setObjectName("renameLabel")
        self.gridLayout.addWidget(self.renameLabel, 4, 0, 1, 3)
        self.bottomLayout = QtWidgets.QHBoxLayout()
        self.bottomLayout.setObjectName("bottomLayout")
        self.gridLayout.addLayout(self.bottomLayout, 6, 0, 1, 3)
        self.imageLabel = QtWidgets.QLabel(Form)
        self.imageLabel.setText("")
        self.imageLabel.setObjectName("imageLabel")
        self.gridLayout.addWidget(self.imageLabel, 1, 0, 1, 3)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.closeButton.setText(_translate("Form", "x"))
        self.titleLabel.setText(_translate("Form", "Title"))
        self.renameLabel.setText(_translate("Form", "Enter new name:"))

