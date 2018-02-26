#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import qtsnbl.widgets
from .ui.ui_wabout import Ui_WBubbleAbout


class WAboutBubble(QtWidgets.QDialog, Ui_WBubbleAbout, qtsnbl.widgets.FixedWidget):
    def __init__(self, parent, vhash, vversion):
        super().__init__(parent=parent)
        self.setupUi(self)
        lt = self.aboutLabel.text()
        lt = lt.replace('@', vhash).replace('#', vversion)
        self.aboutLabel.setText(lt)
        self.setWindowIcon(QtGui.QIcon(':/swiss'))
        self.fixWindow()

    @QtCore.pyqtSlot()
    def on_closeButton_clicked(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_aboutQtButton_clicked(self):
        QtWidgets.QMessageBox.aboutQt(self)
