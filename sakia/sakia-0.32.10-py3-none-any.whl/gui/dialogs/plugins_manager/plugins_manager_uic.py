# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/inso/code/sakia/src/sakia/gui/dialogs/plugins_manager/plugins_manager.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PluginDialog(object):
    def setupUi(self, PluginDialog):
        PluginDialog.setObjectName("PluginDialog")
        PluginDialog.resize(629, 316)
        self.verticalLayout = QtWidgets.QVBoxLayout(PluginDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(PluginDialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.table_plugins = QtWidgets.QTableView(self.groupBox_2)
        self.table_plugins.setObjectName("table_plugins")
        self.table_plugins.horizontalHeader().setStretchLastSection(True)
        self.table_plugins.verticalHeader().setStretchLastSection(True)
        self.verticalLayout_3.addWidget(self.table_plugins)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(-1, 6, -1, -1)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.button_install = QtWidgets.QPushButton(self.groupBox_2)
        self.button_install.setIconSize(QtCore.QSize(16, 16))
        self.button_install.setObjectName("button_install")
        self.horizontalLayout_5.addWidget(self.button_install)
        self.button_delete = QtWidgets.QPushButton(self.groupBox_2)
        self.button_delete.setObjectName("button_delete")
        self.horizontalLayout_5.addWidget(self.button_delete)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.button_box = QtWidgets.QDialogButtonBox(PluginDialog)
        self.button_box.setEnabled(True)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.button_box.setObjectName("button_box")
        self.verticalLayout.addWidget(self.button_box)

        self.retranslateUi(PluginDialog)
        QtCore.QMetaObject.connectSlotsByName(PluginDialog)

    def retranslateUi(self, PluginDialog):
        _translate = QtCore.QCoreApplication.translate
        PluginDialog.setWindowTitle(_translate("PluginDialog", "Plugins manager"))
        self.groupBox_2.setTitle(_translate("PluginDialog", "Installed plugins list"))
        self.button_install.setText(_translate("PluginDialog", "Install a new plugin"))
        self.button_delete.setText(_translate("PluginDialog", "Uninstall selected plugin"))

import sakia.icons_rc
