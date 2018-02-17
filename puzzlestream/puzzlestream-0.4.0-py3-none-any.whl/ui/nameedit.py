# -*- coding: utf-8 -*-
"""Name edit module.

contains PSNameEdit, a subclass of QLineEdit
"""

from PyQt5 import QtCore, QtWidgets


class PSNameEdit(QtWidgets.QLineEdit):

    nameChanged = QtCore.pyqtSignal(object)

    def __init__(self, text, inactiveColor, parent=None):
        super().__init__(text, parent)
        self.returnPressed.connect(self.__leaveEdit)
        self.__activeColor = self.palette().color(self.backgroundRole())
        self.__inactiveColor = inactiveColor
        self.__setInactiveColors()

    def mouseDoubleClickEvent(self, *args):
        self.setReadOnly(False)
        self.setClearButtonEnabled(True)
        self.__setActiveColors()
        super().mouseDoubleClickEvent(*args)

    def setReadOnly(self, readonly):
        super().setReadOnly(readonly)

    def __leaveEdit(self):
        self.setReadOnly(True)
        self.clearFocus()
        self.__setInactiveColors()
        self.setClearButtonEnabled(False)
        self.nameChanged.emit(self.text())

    def __setInactiveColors(self):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), self.__inactiveColor)
        self.setPalette(palette)

    def __setActiveColors(self):
        palette = self.palette()
        palette.setColor(self.backgroundRole(), self.__activeColor)
        self.setPalette(palette)

    def focusOutEvent(self, event):
        self.__leaveEdit()
        super().focusOutEvent(event)
