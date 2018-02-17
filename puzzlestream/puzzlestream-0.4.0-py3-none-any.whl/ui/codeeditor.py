# -*- coding: utf-8 -*-
"""Code editor module.

contains PSCodeEdit, a subclass of PyCodeEdit
"""

from pyqode.python.widgets import PyCodeEdit
from pyqode.core.api import ColorScheme
from pyqode.core.modes import RightMarginMode
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence, QColor
from puzzlestream.ui.codestyle import PSCodeStyleDark, PSCodeStyleLight


class PSCodeEdit(PyCodeEdit):
    """PyCodeEdit with some added functionality."""

    def __init__(self, server_script=None, args=None):
        """Editor init.

        Args:
            server_script: Location of the PyCodeEdit server script file (.py).
            args (list): Additional args to be passed to the server.
        """
        super().__init__(server_script=server_script, args=args)

        # shortcuts
        self.__shortcuts = {}

        # set default colors
        self.setRightMarginColor()

    def setRightMarginColor(self, color=QColor(42, 92, 129)):
        """Set colour of right margin line to color,"""
        self._modes.get(RightMarginMode).color = color

    def setCurrentLineColor(self, color=QColor(42, 92, 129)):
        """Set colour of current active line to color,"""
        self._modes.get("CaretLineHighlighterMode").background = color

    def setSyntaxColorScheme(self, scheme="dark"):
        """Set syntax colour scheme to scheme (str, dark or light)."""
        if scheme == "dark":
            style = PSCodeStyleDark
        elif scheme == "light":
            style = PSCodeStyleLight
        else:
            return

        colorScheme = self.syntax_highlighter.color_scheme
        colorScheme._load_formats_from_style(style)
        self.syntax_highlighter.color_scheme = colorScheme
        self.syntax_highlighter.refresh_editor(colorScheme)
        self.syntax_highlighter.rehighlight()

    def addShortcut(self, sequence, target):
        """Add shortcut to the editor.

        Args:
            sequence (str): Key sequence.
            target: Method to be executed when sequence is entered.
        """
        sc = QShortcut(QKeySequence(sequence), self)
        sc.activated.connect(target)
        self.__shortcuts[sequence] = sc
