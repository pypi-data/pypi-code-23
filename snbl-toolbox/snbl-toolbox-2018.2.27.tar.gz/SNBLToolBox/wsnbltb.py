#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import qtsnbl.widgets
import qtsnbl.version
from .ui.ui_snbltb import Ui_WSnblToolBox
from .ui.ui_wsnbltbabout import Ui_WSnblAbout
from .wcrysis import WCrysis
from .convert import ConvertWizard
from .wheader import WHeader
from .wsleuth import WSleuth
from .roerik.wgunnar import WGunnar
from .wdarth import WDarth
try:
    from . import frozen
except ImportError:
    frozen = False


class WAboutSnblTB(QtWidgets.QDialog, Ui_WSnblAbout, qtsnbl.widgets.FixedWidget):
    def __init__(self, parent, hghash, string):
        super().__init__(parent)
        self.setupUi(self)
        self.aboutLabel.setText(self.aboutLabel.text().replace('@', hghash).replace('#', string))
        self.setWindowIcon(QtGui.QIcon(':/swiss'))
        self.closeButton.clicked.connect(self.close)
        self.aboutQtButton.clicked.connect(lambda: QtWidgets.QMessageBox.aboutQt(self))
        self.fixWindow()


class WSnblTB(QtWidgets.QDialog, Ui_WSnblToolBox, qtsnbl.widgets.FixedWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.wcrysis = WCrysis(self)
        self.wconvert = ConvertWizard(self)
        version = qtsnbl.version.Version(frozen)
        self.wupdates = qtsnbl.widgets.WUpdates(self, version)
        self.wabout = WAboutSnblTB(self, version.hash, version.string)
        self.wabout.buttonUpdates.clicked.connect(self.wupdates.checkNewVersionByUser)
        self.wheader = WHeader(self)
        self.wsleuth = WSleuth(self)
        self.wroerik = WGunnar(self)
        self.wdarth = WDarth(self)
        if QtWidgets.QApplication.screens()[0].logicalDotsPerInch() > 120:  # Hack for HiDPI displays
            size = QtCore.QSize(146, 146)
            self.roerikButton.setIconSize(size)
            self.crysisButton.setIconSize(size)
            self.convertButton.setIconSize(size)
            self.infoButton.setIconSize(size)
            self.headExButton.setIconSize(size)
            self.darthButton.setIconSize(size)
            self.sleuthButton.setIconSize(size)
            self.sigmasButton.setIconSize(size)
        self.fixWindow()

    def showEvent(self, event: QtGui.QShowEvent):
        self.wupdates.checkNewVersion()

    def closeEvent(self, event):
        self.saveSettings()
        self.wcrysis.close()
        self.wconvert.close()
        self.wabout.close()
        self.wheader.close()
        self.wsleuth.close()
        self.wroerik.close()
        self.wdarth.close()

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WSNBLToolBox/Geometry', self.saveGeometry())
        self.wupdates.saveSettings()
        self.wcrysis.saveSettings()
        self.wconvert.saveSettings()
        self.wheader.saveSettings()
        self.wsleuth.saveSettings()
        self.wroerik.saveSettings()
        self.wdarth.saveSettings()

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WSNBLToolBox/Geometry', b''))
        self.wupdates.loadSettings()
        self.wcrysis.loadSettings()
        self.wconvert.loadSettings()
        self.wheader.loadSettings()
        self.wsleuth.loadSettings()
        self.wroerik.loadSettings()
        self.wdarth.loadSettings()

    @QtCore.pyqtSlot()
    def on_crysisButton_clicked(self):
        self.wcrysis.show()

    @QtCore.pyqtSlot()
    def on_convertButton_clicked(self):
        if self.wconvert.stopped:
            self.wconvert = ConvertWizard(self)
        self.wconvert.show()

    @QtCore.pyqtSlot()
    def on_sigmasButton_clicked(self):
        QtWidgets.QMessageBox.question(self, 'Fit2D?!', 'Fit2D?! In 2016?! Seriously?! No way!',
                                       QtWidgets.QMessageBox.No)

    @QtCore.pyqtSlot()
    def on_infoButton_clicked(self):
        self.wabout.show()

    @QtCore.pyqtSlot()
    def on_headExButton_clicked(self):
        self.wheader.show()

    @QtCore.pyqtSlot()
    def on_sleuthButton_clicked(self):
        self.wsleuth.show()

    @QtCore.pyqtSlot()
    def on_darthButton_clicked(self):
        self.wdarth.show()

    @QtCore.pyqtSlot()
    def on_roerikButton_clicked(self):
        self.wroerik.show()
