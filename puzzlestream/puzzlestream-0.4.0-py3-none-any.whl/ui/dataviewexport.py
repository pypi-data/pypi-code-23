# -*- coding: utf-8 -*-
"""Data view export dialog module.

contains PSTableExportDialog
"""

import os
from collections import OrderedDict
from io import BytesIO

import numpy as np
from PyQt5 import QtCore, QtWidgets
from tabulate import tabulate


class PSTableExportDialog(QtWidgets.QDialog):

    def __init__(self, data, config, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 200)

        self.__data = data
        self.__config = config
        self.vbox = QtWidgets.QVBoxLayout()
        self.setLayout(self.vbox)

        self.groupBox = QtWidgets.QGroupBox("Please choose an export format")
        self.groupBoxLayout = QtWidgets.QVBoxLayout()
        self.groupBox.setLayout(self.groupBoxLayout)
        self.vbox.addWidget(self.groupBox)

        self.radioButtons = OrderedDict([
            ("txt", QtWidgets.QRadioButton("Plain text")),
            ("csv", QtWidgets.QRadioButton("Comma separated (csv)")),
            ("tex", QtWidgets.QRadioButton("Latex"))
        ])

        self.radioButtons["txt"].setChecked(True)

        for btn in self.radioButtons.values():
            self.groupBoxLayout.addWidget(btn)

        self.saveBtn = QtWidgets.QPushButton("Save")
        self.clipboardBtn = QtWidgets.QPushButton("Copy to clipboard")
        self.cancelBtn = QtWidgets.QPushButton("Cancel")

        self.saveBtn.clicked.connect(self.__save)
        self.clipboardBtn.clicked.connect(self.__toClipboard)
        self.cancelBtn.clicked.connect(self.close)

        self.btnHBox = QtWidgets.QHBoxLayout()
        self.btnHBox.setAlignment(QtCore.Qt.AlignRight)
        self.btnHBox.addWidget(self.saveBtn)
        self.btnHBox.addWidget(self.clipboardBtn)
        self.btnHBox.addWidget(self.cancelBtn)
        self.vbox.addLayout(self.btnHBox)

        self.show()

    def __getSelectedType(self):
        for key in self.radioButtons:
            if self.radioButtons[key].isChecked():
                return key

    def __getExport(self, selected):
        if selected == "txt":
            return tabulate(self.__data)
        elif selected == "tex":
            return tabulate(self.__data, tablefmt="latex")

    def __save(self):
        selected = self.__getSelectedType()
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                        filter="*." + selected)

        if path != "":
            export = self.__getExport(selected)

            if export is not None:
                with open(path, "w") as f:
                    f.write(export)
            elif selected == "csv":
                np.savetxt(path, self.__data, delimiter=",")
            self.close()

    def __toClipboard(self):
        selected = self.__getSelectedType()
        export = self.__getExport(selected)
        clipboard = QtWidgets.QApplication.clipboard()

        if export is not None:
            clipboard.setText(self.__getExport(selected))
        elif selected == "csv":
            s = BytesIO()
            np.savetxt(s, self.__data, delimiter=",")
            clipboard.setText(s.getvalue().decode("utf-8"))
