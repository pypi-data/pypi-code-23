# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plover_wpm_meter/wpm_meter.ui'
#
# Created by: PyQt5 UI code generator 5.8
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WpmMeter(object):
    def setupUi(self, WpmMeter):
        WpmMeter.setObjectName("WpmMeter")
        WpmMeter.resize(180, 151)
        self.layoutWidget = QtWidgets.QWidget(WpmMeter)
        self.layoutWidget.setGeometry(QtCore.QRect(0, 30, 181, 121))
        self.layoutWidget.setObjectName("layoutWidget")
        self.wpm_meter = QtWidgets.QGridLayout(self.layoutWidget)
        self.wpm_meter.setContentsMargins(0, 0, 0, 0)
        self.wpm_meter.setSpacing(0)
        self.wpm_meter.setObjectName("wpm_meter")
        self.wpm1 = QtWidgets.QLCDNumber(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wpm1.sizePolicy().hasHeightForWidth())
        self.wpm1.setSizePolicy(sizePolicy)
        self.wpm1.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.wpm1.setProperty("value", 0.0)
        self.wpm1.setObjectName("wpm1")
        self.wpm_meter.addWidget(self.wpm1, 0, 0, 1, 1)
        self.wpm1_label = QtWidgets.QLabel(self.layoutWidget)
        self.wpm1_label.setAlignment(QtCore.Qt.AlignCenter)
        self.wpm1_label.setObjectName("wpm1_label")
        self.wpm_meter.addWidget(self.wpm1_label, 0, 1, 1, 1)
        self.wpm2 = QtWidgets.QLCDNumber(self.layoutWidget)
        self.wpm2.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.wpm2.setProperty("value", 0.0)
        self.wpm2.setObjectName("wpm2")
        self.wpm_meter.addWidget(self.wpm2, 1, 0, 1, 1)
        self.wpm2_label = QtWidgets.QLabel(self.layoutWidget)
        self.wpm2_label.setAlignment(QtCore.Qt.AlignCenter)
        self.wpm2_label.setObjectName("wpm2_label")
        self.wpm_meter.addWidget(self.wpm2_label, 1, 1, 1, 1)
        self.wpm_meter.setColumnStretch(0, 2)
        self.wpm_meter.setColumnStretch(1, 1)
        self.layoutWidget1 = QtWidgets.QWidget(WpmMeter)
        self.layoutWidget1.setGeometry(QtCore.QRect(0, 0, 181, 27))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.wpm_controls = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.wpm_controls.setContentsMargins(0, 0, 0, 0)
        self.wpm_controls.setObjectName("wpm_controls")
        self.wpm_method = QtWidgets.QComboBox(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wpm_method.sizePolicy().hasHeightForWidth())
        self.wpm_method.setSizePolicy(sizePolicy)
        self.wpm_method.setObjectName("wpm_method")
        self.wpm_controls.addWidget(self.wpm_method)
        spacerItem = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.wpm_controls.addItem(spacerItem)
        self.is_pinned_checkbox = QtWidgets.QCheckBox(self.layoutWidget1)
        self.is_pinned_checkbox.setChecked(True)
        self.is_pinned_checkbox.setObjectName("is_pinned_checkbox")
        self.wpm_controls.addWidget(self.is_pinned_checkbox)

        self.retranslateUi(WpmMeter)
        QtCore.QMetaObject.connectSlotsByName(WpmMeter)

    def retranslateUi(self, WpmMeter):
        _translate = QtCore.QCoreApplication.translate
        WpmMeter.setWindowTitle(_translate("WpmMeter", "WPM Meter"))
        self.wpm1_label.setText(_translate("WpmMeter", "last 10s"))
        self.wpm2_label.setText(_translate("WpmMeter", "last 1m"))
        self.is_pinned_checkbox.setText(_translate("WpmMeter", "📌"))

from . import resources_rc
