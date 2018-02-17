# -*- coding: utf-8 -*-
"""Notification tab module.

contains PSNotificationTab, a subclass of QWidget
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from puzzlestream.ui.notification import PSNotification


class PSNotificationTab(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.__scroll = QtWidgets.QScrollArea()
        self.__widget = QtWidgets.QWidget()
        self.__scroll.setWidget(self.__widget)
        self.__scrollBox = QtWidgets.QVBoxLayout()
        self.__widget.setLayout(self.__scrollBox)
        self.__scroll.setWidgetResizable(True)

        self.__layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.__layout)

        btnLayout = QtWidgets.QHBoxLayout()
        self.__deleteAllBtn = QtWidgets.QPushButton("Delete all")
        self.__deleteAllBtn.setFixedWidth(100)
        self.__deleteAllBtn.pressed.connect(self.__deleteAll)
        btnLayout.addStretch()
        btnLayout.addWidget(self.__deleteAllBtn)

        self.__layout.addLayout(btnLayout)
        self.__layout.addWidget(self.__scroll)

        self.notifications = []
        self.__numberUpdateMethod = None

    def setNumberUpdateMethod(self, method):
        self.__numberUpdateMethod = method

    def deleteNotification(self, notification):
        if notification in self.notifications:
            self.__scrollBox.removeWidget(notification)
            notification.hide()
            index = self.notifications.index(notification)
            del self.notifications[index]
            del notification
            self.__resize()
            if self.__numberUpdateMethod is not None:
                self.__numberUpdateMethod()

    def __deleteAll(self):
        for n in self.notifications:
            self.__scrollBox.removeWidget(n)
            n.hide()
            del n

        self.notifications = []
        self.__resize()
        if self.__numberUpdateMethod is not None:
            self.__numberUpdateMethod()

    def addNotification(self, message):
        notification = PSNotification(message)
        notification.setDeletionMethod(self.deleteNotification)
        self.__scrollBox.addWidget(notification)
        self.notifications.append(notification)
        self.__resize()
        if self.__numberUpdateMethod is not None:
            self.__numberUpdateMethod()

    def __resize(self):
        self.__widget.setFixedHeight(40 * len(self.notifications))
        self.__scroll.verticalScrollBar().setSliderPosition(
            self.__scroll.verticalScrollBar().maximum())
