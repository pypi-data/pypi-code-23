# -*- coding: utf-8 -*-
"""Notification module.

contains PSNotification, a subclass of QWidget
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
import time


class PSNotification(QtWidgets.QWidget):

    def __init__(self, message, *args):
        super().__init__(*args)
        self.__layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.__layout)
        self.setFixedHeight(40)
        self.__timeLabel = QtWidgets.QLabel(time.strftime("%H:%M:%S"))
        self.__label = QtWidgets.QLabel(message)
        self.__closeButton = QtWidgets.QPushButton("x")

        self.__timeLabel.setFixedWidth(100)
        self.__closeButton.setFixedWidth(20)
        self.__layout.addWidget(self.__timeLabel)
        self.__layout.addWidget(self.__label)
        self.__layout.addWidget(self.__closeButton)

    def setDeletionMethod(self, method):
        self.__closeButton.pressed.connect(lambda: method(self))
