# -*- coding: utf-8 -*-
"""About window module.

contains PSAboutWindow
"""

import os
from PyQt5 import QtGui, QtWidgets


class PSAboutWindow(QtWidgets.QMainWindow):
    """Window that shows some information about Puzzle Stream."""

    def __init__(self, parent=None):
        """Window init.

        Args:
            parent: Qt parent
        """
        super().__init__(parent)
        self.label = QtWidgets.QLabel()
        currentDir = os.path.dirname(__file__)
        self.label.setPixmap(QtGui.QPixmap(
            os.path.join(currentDir, "../icons/PuzzleStream.png")))
        self.setCentralWidget(self.label)
        self.show()

    def closeEvent(self, event):
        """Set parent to None on exit to free RAM."""
        self.setParent(None)
        event.accept()
