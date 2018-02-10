#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore


def qdelay(msec):
    dieTime = QtCore.QTime.currentTime().addMSecs(msec)
    while QtCore.QTime.currentTime() < dieTime:
        QtCore.QCoreApplication.processEvents()
