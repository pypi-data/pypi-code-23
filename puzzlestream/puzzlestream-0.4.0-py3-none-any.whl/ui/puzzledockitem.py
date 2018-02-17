# -*- coding: utf-8 -*-
"""Puzzle dock item module.

contains PSPuzzleDockItem, a subclass of PSPuzzleItem
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import QPointF, QRectF

from puzzlestream.ui.puzzleitem import PSPuzzleItem
from puzzlestream.ui.dock import PSDock

import numpy as np


class PSPuzzleDockItem(PSPuzzleItem):

    # Defined by child classes:
    # -------------------------------------------------------------------------
    # PSModule / PSValve :
    _width = None
    _height = None

    def __init__(self, dockItemID):

        super().__init__(dockItemID)

        self._dockWidth = 60
        self._dockHeight = 25
        self.__createDocks()
        self._connPreferences = np.array(["output"] * 4, dtype=str)
        self.hideDocksWithState("disconnected")
        self.setAcceptHoverEvents(True)

    """
    ===========================================================================
        Initialisation
    """

    def __createDocks(self):
        self._docks = []
        dockwidth = self._dockWidth
        dockheight = self._dockHeight

        for i in range(4):
            self._docks.append(PSDock(dockwidth, dockheight, parent=self))

        topDock = self._docks[self._positionIndex["top"]]
        topposition = QPointF(
            self.centerPos().x(),
            self.centerPos().y() - self._height / 2 - dockheight / 2
        )
        topDock.setCenterPos(topposition)
        topDock.setRotation(0)
        topDock.setDoubleClickReaction(
            lambda: self.changeConnectionPreference("top"))

        leftDock = self._docks[self._positionIndex["left"]]
        leftposition = QPointF(
            self.centerPos().x() - self._width / 2 - dockheight / 2,
            self.centerPos().y()
        )
        leftDock.setCenterPos(leftposition)
        leftDock.setRotation(270)
        leftDock.setDoubleClickReaction(
            lambda: self.changeConnectionPreference("left"))

        bottomDock = self._docks[self._positionIndex["bottom"]]
        bottomposition = QPointF(
            self.centerPos().x(),
            self.centerPos().y() + self._height / 2 + dockheight / 2
        )
        bottomDock.setCenterPos(bottomposition)
        bottomDock.setRotation(180)
        bottomDock.setDoubleClickReaction(
            lambda: self.changeConnectionPreference("bottom"))

        rightDock = self._docks[self._positionIndex["right"]]
        rightposition = QPointF(
            self.centerPos().x() + self._width / 2 + dockheight / 2,
            self.centerPos().y()
        )
        rightDock.setCenterPos(rightposition)
        rightDock.setRotation(90)
        rightDock.setDoubleClickReaction(
            lambda: self.changeConnectionPreference("right"))

        for i in range(4):
            self._docks[i].setColor("output")
            self._docks[i].hide()

    def __showAsInput(self, position):
        dock = self._docks[self._positionIndex[position]]
        if position == "top":
            dock.setRotation(180)
        elif position == "left":
            dock.setRotation(90)
        elif position == "bottom":
            dock.setRotation(0)
        elif position == "right":
            dock.setRotation(270)
        dock.setColor("input")
        self._showPosition(position)

    def __showAsOutput(self, position):
        dock = self._docks[self._positionIndex[position]]
        if position == "top":
            dock.setRotation(0)
        elif position == "left":
            dock.setRotation(270)
        elif position == "bottom":
            dock.setRotation(180)
        elif position == "right":
            dock.setRotation(90)
        dock.setColor("output")
        self._showPosition(position)

    def changeConnectionPreference(self, position):
        index = self._positionIndex[position]
        if self._connPreferences[index] != "output":
            self._connPreferences[index] = "output"
            self.__showAsOutput(position)
        else:
            self._connPreferences[index] = "input"
            self.__showAsInput(position)

    def showDocksWithState(self, state):
        """Show all docks with given state and return their indices."""
        shownDocks = []
        for position in self._positionIndex:
            i = self._positionIndex[position]
            if self._connections[i] == state:
                self._showPosition(position)
                shownDocks.append(i)
        return shownDocks

    def hideDocksWithState(self, state):
        """Hide all docks with given state and return their indices."""
        hiddenDocks = []
        for position in self._positionIndex:
            i = self._positionIndex[position]
            if self._connections[i] == state:
                self._hidePosition(position)
                hiddenDocks.append(i)
        return hiddenDocks

    def preConnect(self, otherItem):
        connectionPossible = super().preConnect(otherItem)
        if connectionPossible:
            # hide and disconnect old preconnection candidate
            for i in self.hideDocksWithState("preconnected"):
                self._connections[i] = "disconnected"
            # preconnect new candidate and show it
            self._connections[self._positionIndex[
                self._preConnectionDirection[0]
            ]] = "preconnected"
            self.__showAsInput(self._preConnectionDirection[0])
        return connectionPossible

    def preblockOutputConnectionPoint(self, position):
        # hide and disconnect old preconnection candidate
        for i in self.hideDocksWithState("preconnected"):
            self._connections[i] = "disconnected"
        # preconnect new candidate and show it
        self._connections[self._positionIndex[position]] = "preconnected"
        self.__showAsOutput(position)

    def freeConnectionPoint(self, position):
        self._hidePosition(position)
        dock = self._docks[self._positionIndex[position]]
        dock.showOnMouseOver = True
        super().freeConnectionPoint(position)

    def blockConnectionPoint(self, position):
        self._docks[self._positionIndex[position]].showOnMouseOver = False
        super().blockConnectionPoint(position)

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def _hidePosition(self, position):
        dock = self._docks[self._positionIndex[position]]
        dock.hide()

    def _showPosition(self, position):
        dock = self._docks[self._positionIndex[position]]
        dock.show()

    def connectionPreference(self, position):
        return self._connPreferences[self._positionIndex[position]]

    """
    ===========================================================================
    Show / hide docks on mouse over
    """

    def hoverEnterEvent(self, event):
        self.showDocksWithState("disconnected")
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.hideDocksWithState("disconnected")
        super().hoverLeaveEvent(event)

    @property
    def width(self):
        return self._width
