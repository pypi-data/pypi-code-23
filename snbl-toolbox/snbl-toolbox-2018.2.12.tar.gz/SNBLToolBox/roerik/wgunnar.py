#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets
from cryio.parparser import ParParser
from ..ui.ui_wgunnar import Ui_WGunnar
from . import neighbors


class WGunnar(QtWidgets.QDialog, Ui_WGunnar):
    def __init__(self, parent):
        super(WGunnar, self).__init__(parent)
        self.setupUi(self)
        self._parent = parent
        doubbleValidator = QtGui.QDoubleValidator()
        for name, obj in self.interEdit():
            obj.setValidator(doubbleValidator)
        self.resTable.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.resTable.verticalHeader().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WRoerik/Geometry', self.saveGeometry())
        for name, obj in self.interEdit():
            s.setValue('WRoerik/{}'.format(name), obj.text())
        s.setValue('WRoerik/ubm', self.ubmText.toPlainText())
        s.setValue('WRoerik/folder', self.folder)

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WRoerik/Geometry', QtCore.QByteArray()))
        for name, obj in self.interEdit():
            obj.setText(s.value('WRoerik/{}'.format(name), '0'))
        self.ubmText.setPlainText(s.value('WRoerik/ubm', ''))
        self.folder = s.value('WRoerik/folder', '')

    def closeEvent(self, event):
        self.saveSettings()
        self.hide()

    def interEdit(self):
        for name in self.__dict__:
            if name.endswith('Edit'):
                yield name, self.__dict__[name]

    @QtCore.pyqtSlot()
    def on_parButton_clicked(self):
        # noinspection PyCallByClass,PyTypeChecker
        par = QtWidgets.QFileDialog.getOpenFileName(self, 'Open .par file', self.folder, 'Crysalis par (*.par)')[0]
        if par:
            self.folder = os.path.dirname(par)
            self.parsePar(par)

    def parsePar(self, par):
        par = ParParser(par)
        self.alphaEdit.setText(str(par.alpha))
        self.betaEdit.setText(str(par.beta))
        self.lambdaEdit.setText(str(par.wavelength))
        self.d0Edit.setText(str(par.dist))
        self.phixEdit.setText(str(par.phix))
        self.phiyEdit.setText(str(par.phiy))
        self.ubmText.setPlainText(' '.join([str(i) for i in par.ub]))
        self.x0Edit.setText(str(par.xc))
        self.y0Edit.setText(str(par.yc))

    # noinspection PyArgumentList
    @QtCore.pyqtSlot(str, name='on_alphaEdit_textChanged')
    @QtCore.pyqtSlot(str, name='on_betaEdit_textChanged')
    @QtCore.pyqtSlot(str, name='on_lambdaEdit_textChanged')
    @QtCore.pyqtSlot(str, name='on_d0Edit_textChanged')
    @QtCore.pyqtSlot(str, name='on_phixEdit_textChanged')
    @QtCore.pyqtSlot(str, name='on_phiyEdit_textChanged')
    @QtCore.pyqtSlot(str, name='on_x0Edit_textChanged')
    @QtCore.pyqtSlot(str, name='on_y0Edit_textChanged')
    @QtCore.pyqtSlot(name='on_ubmText_textChanged')
    @QtCore.pyqtSlot(str, name='on_y0Edit_textChanged')
    @QtCore.pyqtSlot(str, name='on_deltaEdit_textChanged')
    @QtCore.pyqtSlot(str, name='on_omegaEdit_textChanged')
    @QtCore.pyqtSlot(str, name='on_kappaEdit_textChanged')
    @QtCore.pyqtSlot(str, name='on_phiEdit_textChanged')
    def calculateVectors(self, text=None):
        self.resTable.clear()
        self.resTable.setRowCount(3)
        self.resTable.setHorizontalHeaderLabels(['(h,k,l)', '(x,y)', 'alpha_h'])
        try:
            ubm = np.fromstring(self.ubmText.toPlainText(), dtype=float, count=9, sep=' ').reshape((3, 3))
            wavelength = float(self.lambdaEdit.text())
            delta = float(self.deltaEdit.text())
            alpha = float(self.alphaEdit.text())
            beta = float(self.betaEdit.text())
            omega = float(self.omegaEdit.text())
            kappa = float(self.kappaEdit.text())
            phi = float(self.phiEdit.text())
            phix = float(self.phixEdit.text())
            phiy = float(self.phiyEdit.text())
            y0 = float(self.x0Edit.text())
            x0 = float(self.y0Edit.text())
            d0 = float(self.d0Edit.text())
        except ValueError:
            return
        res = neighbors.neighbors(ubm, wavelength, delta, alpha, beta, omega, kappa, phi, phix, phiy, x0, y0, d0)
        if not res:
            return
        self.resTable.setRowCount(len(res))
        for i, item in enumerate(res):
            for j, value in enumerate(item):
                self.resTable.setItem(i, j, QtWidgets.QTableWidgetItem(str(value)))

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            pass
        else:
            QtWidgets.QDialog.keyPressEvent(self, event)

