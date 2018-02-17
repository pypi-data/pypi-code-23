# -*- coding: utf-8 -*-
"""Tree model module.

contains PSTreeModel
"""

from PyQt5 import QtGui


class PSTreeModel(QtGui.QStandardItemModel):
    """Tree model class, used in data view.

    Model that displays standard keys, numpy keys, ... in different sub-trees.
    """

    def __init__(self, standardKeys, numpy2DKeys,
                 mplKeys, otherKeys, checkStates, parent=None):
        """Tree model init.

        standardKeys (list): Numpy 1D array keys.
        numpy2DKeys (list): Numpy 2D array keys.
        mplKeys (list): Matplotlib figure keys.
        otherKeys (list): Keys of all other items.
        checkStates (list): Initial states of the standard item check boxes.
        """
        self.__standardKeys = standardKeys
        self.__checkStates = checkStates
        self.__numpy2DKeys = numpy2DKeys
        self.__mplKeys = mplKeys
        self.__otherKeys = otherKeys
        super().__init__(parent)
        self.keyUpdate()

    def keyUpdate(self):
        """Update model from lists."""
        self.clear()
        standardItem = QtGui.QStandardItem("1D items")
        twoDItem = QtGui.QStandardItem("2D items")
        plotItem = QtGui.QStandardItem("Plot items")
        otherItem = QtGui.QStandardItem("Other items")

        for key in self.__standardKeys:
            item = QtGui.QStandardItem(key)
            item.setCheckable(True)

            if key not in self.__checkStates:
                    self.__checkStates[key] = True

            if self.__checkStates[key]:
                item.setCheckState(2)
            else:
                item.setCheckState(0)

            standardItem.appendRow(item)

        for key in self.__numpy2DKeys:
            twoDItem.appendRow(QtGui.QStandardItem(key))

        for key in self.__mplKeys:
            plotItem.appendRow(QtGui.QStandardItem(key))

        for key in self.__otherKeys:
            otherItem.appendRow(QtGui.QStandardItem(key))

        for item in (standardItem, twoDItem, plotItem, otherItem):
            self.appendRow(item)
