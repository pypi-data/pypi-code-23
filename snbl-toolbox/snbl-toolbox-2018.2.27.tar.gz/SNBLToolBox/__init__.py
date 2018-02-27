#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtWidgets
from .wsnbltb import WSnblTB


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setOrganizationName('SNBL')
    app.setOrganizationDomain('snbl.eu')
    app.setApplicationName('pylatus')
    wsnbl = WSnblTB()
    wsnbl.loadSettings()
    wsnbl.show()
    sys.exit(app.exec())
