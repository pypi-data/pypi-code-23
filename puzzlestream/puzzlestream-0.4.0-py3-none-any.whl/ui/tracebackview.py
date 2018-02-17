# -*- coding: utf-8 -*-
"""Traceback view module.

contains PSTracebackView, a subclass of QMainWindow
"""

from PyQt5 import QtWidgets
from puzzlestream.backend.tracebackmodel import PSTracebackModel


class PSTracebackView(QtWidgets.QMainWindow):

    def __init__(self, key, userKey, stream, modules, parent=None):
        super().__init__(parent)
        self.__widget = QtWidgets.QWidget()
        self.__layout = QtWidgets.QGridLayout()

        model = PSTracebackModel(key, stream, modules)

        self.__listView = QtWidgets.QListView(self.__widget)
        self.__listView.setModel(model)
        self.__listView.setSelectionMode(
            QtWidgets.QListView.NoSelection)
        self.__layout.addWidget(self.__listView)
        self.__widget.setLayout(self.__layout)
        self.setCentralWidget(self.__widget)

        self.setWindowTitle("Traceback - " + userKey)
        self.resize(400, 800)
        self.show()
