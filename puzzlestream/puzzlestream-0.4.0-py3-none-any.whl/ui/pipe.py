# -*- coding: utf-8 -*-
"""Puzzle Stream pipe module.

contains PSPipe, a subclass of PSPuzzleItem
"""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QBrush, QColor, QPalette, QPen

import puzzlestream.backend
from puzzlestream.ui.module import PSModule
from puzzlestream.ui.puzzleitem import PSPuzzleItem
from puzzlestream.ui.valve import PSValve
from puzzlestream.ui import colors


class PSPipe(PSPuzzleItem):

    def __init__(self, pipeID, x, y, orientation="vertical"):
        """
        =======================================================================
            Define GUI appearence: geometry and position
        """

        self.__width = 40
        self.__length = 100
        self.__buttonsize = 20
        self.__bodycolor = colors.get("standard-blue")
        self.__framecolor = "black"
        self.__name = "Pipe_" + str(pipeID)

        self.__initposx, self.__initposy = 0, 0
        self._radius = self.__length / 2

        super().__init__(pipeID)

        self.setTransformOriginPoint(
            self.__initposx + self.__width / 2,
            self.__initposy + self.__length / 2)

        self.__body = QtWidgets.QGraphicsRectItem(
            self.boundingRect(), parent=self)
        self.__bodyBrush = QBrush(QColor(self.__bodycolor))
        self.__framePen = QPen(QColor(self.__framecolor))

        self.__body.setBrush(self.__bodyBrush)
        self.__body.setPen(self.__framePen)

        widgetGeoRect = QtCore.QRect(
            self.__initposx + self.__width / 2 - self.__buttonsize / 2,
            self.__initposy + self.__length / 2 - self.__buttonsize / 2,
            self.__buttonsize, self.__buttonsize
        )
        widgetGeoRectF = QtCore.QRectF(widgetGeoRect)

        self.__proxyWidgetBox = QtWidgets.QGraphicsProxyWidget(parent=self)
        self.__proxyWidgetBox.setGeometry(widgetGeoRectF)
        self.__changeOrientationButton = QtWidgets.QPushButton()
        self.__changeOrientationButton.setAutoFillBackground(False)
        self.__changeOrientationButton.setAttribute(
            QtCore.Qt.WA_NoSystemBackground)
        self.__changeOrientationButton.setGeometry(widgetGeoRect)
        self.__changeOrientationButton.clicked.connect(self.changeOrientation)
        self.__proxyWidgetBox.setWidget(self.__changeOrientationButton)

        """
        =======================================================================
            Initialisation of backendstructure
        """

        self.__inputItem = None
        self.hasOutput = False

        self.setOrientation(orientation)
        self.setCenterPos(QtCore.QPointF(x, y))
        self.__updateButtonEnabled()

    def __str__(self):
        return self.__name

    def __repr__(self):
        return self.__name

    def __updateButtonEnabled(self):
        self.__changeOrientationButton.setEnabled(
            not (self.hasInput or self.hasOutput))

    @property
    def orientation(self):
        if int(round(self.rotation())) == 90:
            return "horizontal"
        return "vertical"

    def changeOrientation(self):
        if self.orientation == "horizontal":
            self.setOrientation("vertical")
        elif self.orientation == "vertical":
            self.setOrientation("horizontal")

    def setOrientation(self, orientation):
        if orientation == "horizontal":
            self.setRotation(90)
            blockCPoints = ["top", "bottom"]
            freeCPoints = ["left", "right"]
        elif orientation == "vertical":
            self.setRotation(0)
            blockCPoints = ["left", "right"]
            freeCPoints = ["top", "bottom"]

        for cPoint in blockCPoints:
            self._connections[self._positionIndex[cPoint]] = "not available"

        for cPoint in freeCPoints:
            self._connections[self._positionIndex[cPoint]] = "disconnected"

    def boundingRect(self):
        return QtCore.QRectF(self.__initposx, self.__initposy,
                             self.__width, self.__length)

    @property
    def width(self):
        return self.__width

    @property
    def __shift(self):
        return QtCore.QPointF(self.__width / 2, self.__length / 2)

    def centerPos(self):
        return self.pos() + self.__shift

    def setCenterPos(self, point):
        p = point - self.__shift
        self.setPos(point - self.__shift)

    @property
    def saveProperties(self):
        props = {"orientation": self.orientation}

        if self.__inputItem is not None:
            props["inItemID"] = self.__inputItem.id

        props.update(super().saveProperties)
        return props

    def restoreProperties(self, props, stream):
        if "orientation" in props:
            self.setOrientation(props["orientation"])
        super().restoreProperties(props, stream)
        self.__updatePattern()

    def toggleOpenClosed(self):
        if self.autopass:
            self.autopass = False
        else:
            self.autopass = True
        self.__updatePattern()

    def __updatePattern(self):
        if self.autopass:
            self.__bodyBrush.setColor(QColor(colors.get("standard-blue")))
            self.__bodyBrush.setStyle(QtCore.Qt.SolidPattern)
        else:
            self.__bodyBrush.setColor(QColor(colors.get("light-blue")))
            self.__bodyBrush.setStyle(QtCore.Qt.BDiagPattern)
        self.__body.setBrush(self.__bodyBrush)

    @property
    def inputItem(self):
        return self.__inputItem

    @property
    def inputItems(self):
        if self.__inputItem is None:
            return []
        return [self.__inputItem]

    @property
    def hasInput(self):
        return self.inputItem is not None

    def inputUpdate(self, puzzleItem):
        self.stopHere = puzzleItem.stopHere

        if (puzzleItem.status == "test failed" or
                puzzleItem.status == "paused" or
                puzzleItem.status == "running"):
            self.status = "paused"
        else:
            self.streamSection = puzzleItem.streamSection.copy(self.id)
            self.status = "finished"

    def __setInputItem(self, puzzleItem):
        self.__inputItem = puzzleItem

        if (isinstance(puzzleItem, PSModule) or
                isinstance(puzzleItem, PSPipe)):
            self.__inputItem.hasOutput = True
        else:
            self.__inputItem.numberOfOutputs += 1

        self.__inputItem.statusChanged.connect(self.inputUpdate)

    def __disconnectInputItem(self):
        if (isinstance(self.__inputItem, PSModule) or
                isinstance(self.__inputItem, PSPipe)):
            self.__inputItem.hasOutput = False
        else:
            self.__inputItem.numberOfOutputs -= 1

        self.__inputItem.statusChanged.disconnect(self.inputUpdate)
        self.__inputItem = None

    def establishConnection(self, otherItem, silent=False):
        self.__setInputItem(otherItem)
        self.__updateButtonEnabled()

        if not silent and otherItem.streamSection is not None:
            self.streamSection = self.__inputItem.streamSection.copy(self.id)
        return super().establishConnection(otherItem)

    def removeConnection(self, otherItem):
        self.__disconnectInputItem()
        self.__updateButtonEnabled()
        super().removeConnection(otherItem)

    def freeConnectionPoint(self, position):
        super().freeConnectionPoint(position)
        self.__updateButtonEnabled()

    def blockConnectionPoint(self, position):
        super().blockConnectionPoint(position)
        self.__updateButtonEnabled()
