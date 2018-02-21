# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/navigation/navigation.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Navigation(object):
    def setupUi(self, Navigation):
        Navigation.setObjectName("Navigation")
        Navigation.resize(685, 477)
        Navigation.setFrameShape(QtWidgets.QFrame.StyledPanel)
        Navigation.setFrameShadow(QtWidgets.QFrame.Raised)
        self.verticalLayout = QtWidgets.QVBoxLayout(Navigation)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(Navigation)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.tree_view = QtWidgets.QTreeView(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tree_view.sizePolicy().hasHeightForWidth())
        self.tree_view.setSizePolicy(sizePolicy)
        self.tree_view.setMinimumSize(QtCore.QSize(150, 0))
        self.tree_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tree_view.setProperty("showDropIndicator", False)
        self.tree_view.setItemsExpandable(True)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setObjectName("tree_view")
        self.stacked_widget = QtWidgets.QStackedWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stacked_widget.sizePolicy().hasHeightForWidth())
        self.stacked_widget.setSizePolicy(sizePolicy)
        self.stacked_widget.setObjectName("stacked_widget")
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(Navigation)
        QtCore.QMetaObject.connectSlotsByName(Navigation)

    def retranslateUi(self, Navigation):
        _translate = QtCore.QCoreApplication.translate
        Navigation.setWindowTitle(_translate("Navigation", "Frame"))

