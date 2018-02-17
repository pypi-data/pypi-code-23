# -*- coding: utf-8 -*-
"""Puzzle Stream module widget module.

contains PSModuleWidget, a subclass of QGraphicsProxyWidget
"""

import os

from PyQt5 import QtCore, QtGui, QtWidgets

from puzzlestream.ui.nameedit import PSNameEdit


class PSModuleWidget(QtWidgets.QGraphicsProxyWidget):

    def __init__(self, initx, inity, width, height, name, parent=None):

        super().__init__(parent=parent)

        self.__width = width
        self.__height = height
        size = QtCore.QSizeF(self.__width, self.__height)
        self.__widget = QtWidgets.QWidget()
        # print(os.getcwd())
        # with open("./puzzlestream/ui/style/module_sheet.qss", "r") as style:
        #    self.__widget.setStyleSheet(style.read())
        self.__centralgrid = QtWidgets.QGridLayout(self.__widget)
        self.__widget.setLayout(self.__centralgrid)
        self.__playpauseButton = QtWidgets.QPushButton(self.__widget)
        self.__stopButton = QtWidgets.QPushButton(self.__widget)

        self.__centralgrid.setColumnMinimumWidth(0, self.__width * 0.62)
        self.__centralgrid.setColumnMinimumWidth(1, self.__width * 0.38)

        for button in [self.__playpauseButton, self.__stopButton]:
            buttonsize = None
            buttonstring = None
            if button == self.__playpauseButton:
                buttonsize = 50
                buttonstring = "play_blue_out"
            else:
                buttonsize = 40
                buttonstring = "stop_blue_out"

            button.setFixedHeight(buttonsize)
            button.setFixedWidth(buttonsize)

            buttonBoundingRect = QtCore.QRect(
                1, 1, buttonsize - 2, buttonsize - 2)

            ellipseregion = QtGui.QRegion(buttonBoundingRect,
                                          QtGui.QRegion.Ellipse)
            button.setMask(ellipseregion)
            button.setIcon(
                QtGui.QIcon(
                    os.path.join(os.path.dirname(__file__),
                                 "../icons//" + buttonstring + ".png")
                )
            )

            button.setIconSize(QtCore.QSize(round(buttonsize * 0.75),
                                            round(buttonsize * 0.75)))

        self.nameEdit = PSNameEdit(
            name,
            self.__widget.palette().color(self.__widget.backgroundRole()),
            self.__widget
        )
        self.nameEdit.setReadOnly(True)

        self.progressBar = QtWidgets.QProgressBar(self.__widget)
        self.progressBar.setFixedHeight(4)
        self.progressBar.setTextVisible(False)
        self.progressBar.hide()

        self.__centralgrid.addWidget(self.nameEdit, 0, 0, 1, 2)
        self.__centralgrid.addWidget(self.__playpauseButton, 1, 0)
        self.__centralgrid.addWidget(self.__stopButton, 1, 1)
        self.__centralgrid.addWidget(self.progressBar, 2, 0, 1, 2)
        self.__centralgrid.setAlignment(self.__playpauseButton,
                                        QtCore.Qt.AlignRight)
        self.__centralgrid.setAlignment(self.progressBar,
                                        QtCore.Qt.AlignBottom)
        self.__stopButton.setEnabled(False)

        self.__widget.setGeometry(initx, inity, self.__width, self.__height)
        self.__widget.setFixedSize(self.__width, self.__height)

        self.setWidget(self.__widget)

    def setPlayPauseButtonAction(self, action):
        self.__playpauseButton.clicked.connect(action)

    def setStopButtonAction(self, action):
        self.__stopButton.clicked.connect(action)

    def togglePlayPauseEnabled(self):
        self.__playPauseButton.setEnabled(
            not self.__playPauseButton.isEnabled())

    def toggleStopEnabled(self):
        self.__stopButton.setEnabled(not self.__stopButton.isEnabled())

    def updateIcons(self, module):
        if module.status == "running":
            self.__playpauseButton.setIcon(
                QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                         "../icons//pause_blue_out.png")))
            self.__stopButton.setEnabled(True)
        elif module.status == "paused":
            self.__playpauseButton.setIcon(
                QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                         "../icons//play_blue_out.png")))
            self.__stopButton.setEnabled(True)
        else:
            self.__playpauseButton.setIcon(
                QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                         "../icons//play_blue_out.png")))
            self.__stopButton.setEnabled(False)
