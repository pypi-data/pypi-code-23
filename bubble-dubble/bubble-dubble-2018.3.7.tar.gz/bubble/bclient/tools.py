#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PyQt5 import QtCore


def clearButtonSlot(widget: QtCore.QObject):
    button = QtCore.QObject.sender(widget)
    bname = button.objectName()
    end = bname.find('ClearButton')
    widget.__dict__[f'{bname[:end]}LineEdit'].setText('')


def autoLevels(array: np.ndarray) -> tuple:
    return -10, array.mean() + 2 * array.std()
