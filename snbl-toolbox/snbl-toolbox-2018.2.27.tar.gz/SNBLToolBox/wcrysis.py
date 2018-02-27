#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import glob
import collections
from datetime import datetime
from PyQt5 import QtCore, QtWidgets
from cryio import cbfimage, crysalis
from .ui.ui_wcrysis import Ui_WCrysis


TIME_XY_SWITCH = 1503489417  # August 23, 2017 we switched BeamX and BeamY convention


Scan = collections.namedtuple('Scan', ['kappa', 'omegaphi', 'type'])


class WorkerSignals(QtCore.QObject):
    errorSignal = QtCore.pyqtSignal(str)
    progressSignal = QtCore.pyqtSignal()
    stopSignal = QtCore.pyqtSignal()
    finishedSignal = QtCore.pyqtSignal(object)


class Worker(QtCore.QRunnable):
    corruptKeys = 'Omega', 'Phi', 'Kappa', 'Oscillation_axis', 'Phi_increment', 'Omega_increment'

    def __init__(self, folder, deleteAngles):
        super().__init__()
        self.stop = False
        self.folder = folder
        self.deleteAngles = deleteAngles
        self.signals = WorkerSignals()
        self.signals.stopSignal.connect(self.stopIt)

    def stopIt(self):
        self.stop = True

    def run(self):
        self.basename = os.path.basename(self.folder)
        self.runname = os.path.join(self.folder, self.basename)
        self.cbflist = sorted(glob.glob(os.path.join(self.folder, '*.cbf')))
        self.ncbf = len(self.cbflist)
        self.scans = collections.OrderedDict()
        try:
            self.readFiles()
            self.createRunFiles()
        except OSError as err:
            self.signals.errorSignal.emit(f'Error in {self.folder}: {err}')
        self.stopIt()
        self.signals.finishedSignal.emit(self)

    def readFiles(self):
        header, i = None, 0
        for i, cbf in enumerate(self.cbflist, 1):
            QtCore.QCoreApplication.processEvents()
            if self.stop:
                return
            try:
                header = cbfimage.CbfHeader(cbf)
            except cbfimage.CbfError:
                self.signals.errorSignal.emit('File {} is corrupted. Cannot proceed further'.format(cbf))
                self.stopIt()
                return
            if 'Oscillation_axis' not in header.header_dict:
                if 'Start_angle' in header.header_dict and 'Angle_increment' in header.header_dict:
                    header.header_dict['Oscillation_axis'] = 'OMEGA'
                    header.header_dict['Kappa'] = 0
                    header.header_dict['Phi'] = 0
                else:
                    self.signals.errorSignal.emit(self.folder)
                    self.stopIt()
                    return
            header.header_dict['cbf'] = os.path.basename(cbf)
            axis = header.header_dict['Oscillation_axis'].upper()
            scan = Scan(header['Kappa'], header['Phi' if axis == 'OMEGA' else 'Omega'], axis)
            if scan not in self.scans:
                self.scans[scan] = []
            self.scans[scan].append(header.header_dict)
            if i == 1:
                self.wavelength = header['Wavelength']
                self.dist = header['Detector_distance'] * 1000
                x, y = header['Beam_xy']
                if header.get_timestamp() < TIME_XY_SWITCH:
                    self.center_x, self.center_y = x, y
                else:
                    self.center_y = x
                    self.center_x = header.binary_header_dict['X-Binary-Size-Second-Dimension'] - y
            if self.deleteAngles:
                self.removeCorruptKeys(header, cbf)
            self.signals.progressSignal.emit()
        if header:
            try:
                self.shape = (header.binary_header_dict['X-Binary-Size-Second-Dimension'],
                              header.binary_header_dict['X-Binary-Size-Fastest-Dimension'])
            except KeyError:
                self.shape = None

    def removeCorruptKeys(self, header, name):
        for key in self.corruptKeys:
            if key in header.header_dict:
                del header.header_dict[key]
        header.save_cbf(name)

    def createRunFiles(self):
        if self.stop or not len(self.scans):
            return
        runFile = []
        for i, scan in enumerate(self.scans):
            scanset = self.scans[scan]
            scanset.sort(key=lambda k: k['Start_angle'])
            dscr = crysalis.RunDscr(i)
            dscr.axis = crysalis.SCAN_AXIS[scan.type]
            dscr.kappa = scan.kappa
            dscr.omegaphi = scan.omegaphi
            dscr.start = scanset[0]['Start_angle']
            dscr.end = scanset[-1]['Start_angle']
            dscr.width = scanset[0]['Angle_increment']
            dscr.todo = dscr.done = len(scanset)
            dscr.exposure = scanset[0]['Exposure_time']
            runFile.append(dscr)
        runHeader = crysalis.RunHeader(self.basename.encode(), self.folder.encode(), len(self.scans))
        crysalis.saveRun(self.runname, runHeader, runFile)
        if self.shape is None:
            crysalis.saveSet(self.runname)
            crysalis.saveCcd(self.runname)
            crysalis.saveSel(self.runname)
        elif self.shape == cbfimage.PILATUS2M:
            crysalis.saveSet(self.runname, '2M')
            crysalis.saveCcd(self.runname)
            crysalis.saveSel(self.runname)
        elif self.shape == cbfimage.PILATUS6M:
            crysalis.saveSet(self.runname, '6M')
            crysalis.saveCcd(self.runname, '6M')
            crysalis.saveSel(self.runname, 'esperanto')
        elif self.shape == cbfimage.PILATUS300K:
            crysalis.saveSet(self.runname, '300K')
            crysalis.saveCcd(self.runname)
            crysalis.saveSel(self.runname)
        elif self.shape == cbfimage.PILATUS1M:
            crysalis.saveSet(self.runname, '1M')
            crysalis.saveCcd(self.runname, '1M')
            crysalis.saveSel(self.runname, 'esperanto')
        crysalis.savePar(self.runname, {'wavelength': self.wavelength, 'path': self.folder, 'center_y': self.center_y,
                                        'center_x': self.center_x, 'basename': self.basename, 'dist': self.dist,
                                        'date': datetime.now().strftime(u'%Y-%m-%d %H:%M:%S'),
                                        'chip': True, 'chip1': self.shape[0], 'chip2': self.shape[1]},)
        crysalis.saveAliases(self.folder, {'scans': self.scans, 'basename': self.basename, 'crysis': True})
        crysalis.saveCrysalisExpSettings(self.folder)


class CrysisWorker(QtCore.QObject):
    progressSignal = QtCore.pyqtSignal(int)
    finishedSignal = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.pool = QtCore.QThreadPool.globalInstance()
        self.workers, self.errors = [], []

    def run(self, folder, deleteAngles):
        self.files = self.done = 0
        self.workers, self.errors = [], []
        for dirpath, dirnames, filenames in os.walk(folder):
            self.files += len(filenames)
            worker = Worker(dirpath, deleteAngles)
            worker.signals.errorSignal.connect(self.workerError)
            worker.signals.progressSignal.connect(self.workerProgress)
            worker.signals.finishedSignal.connect(self.workerFinished)
            self.workers.append(worker)
        self.progressSignal.emit(0)
        for worker in self.workers:
            self.pool.start(worker)

    def stopIt(self):
        for worker in self.workers:
            worker.signals.stopSignal.emit()

    def workerProgress(self):
        self.done += 1
        done = 100.0 * self.done / self.files
        self.progressSignal.emit(done)

    def workerError(self, folder):
        self.errors.append(folder)

    def workerFinished(self, worker):
        self.workers.remove(worker)
        if not self.workers:
            self.progressSignal.emit(100)
            self.finishedSignal.emit(self.errors)


class WCrysis(QtWidgets.QDialog, Ui_WCrysis):
    stopWorkerSignal = QtCore.pyqtSignal()
    runWorkerSignal = QtCore.pyqtSignal(str, bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.stopButton.setVisible(False)
        self.workerThread = QtCore.QThread()
        self.worker = CrysisWorker()
        self.worker.moveToThread(self.workerThread)
        self.worker.progressSignal.connect(self.showProgress)
        self.worker.finishedSignal.connect(self.workerFinished)
        self.stopWorkerSignal.connect(self.worker.stopIt)
        self.runWorkerSignal.connect(self.worker.run)
        self.workerThread.start()

    def showError(self, errors):
        QtWidgets.QMessageBox.critical(self, 'Crysis error', '\n'.join(errors))

    def showProgress(self, value):
        self.runProgressBar.setFormat('{0}: %p%'.format('Reading files'))
        self.runProgressBar.setValue(value)

    def closeEvent(self, event):
        self.saveSettings()
        self.stopWorkerSignal.emit()
        self.hide()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            pass
        else:
            QtWidgets.QDialog.keyPressEvent(self, event)

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WCrysis/Geometry', self.saveGeometry())
        s.setValue('WCrysis/lastFolder', self.lastFolder)
        s.setValue('WCrysis/folder', self.folderLineEdit.text())
        s.setValue('WCrysis/delAngles', self.delAnglesCheckBox.isChecked())

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WCrysis/Geometry', b''))
        self.lastFolder = s.value('WCrysis/lastFolder', '', str)
        self.folderLineEdit.setText(s.value('WCrysis/folder', '', str))
        self.delAnglesCheckBox.setChecked(s.value('WCrysis/delAngles', True, bool))

    @QtCore.pyqtSlot()
    def on_runButton_clicked(self):
        folder = self.folderLineEdit.text()
        if not folder or not os.path.exists(folder):
            return
        self.runButton.setVisible(False)
        self.stopButton.setVisible(True)
        self.runWorkerSignal.emit(folder, self.delAnglesCheckBox.isChecked())

    def workerFinished(self, errors):
        self.runButton.setVisible(True)
        self.stopButton.setVisible(False)
        if errors:
            self.showError(errors)

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        self.stopWorkerSignal.emit()

    @QtCore.pyqtSlot()
    def on_folderButton_clicked(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory', self.lastFolder)
        if not folder:
            return
        self.folderLineEdit.setText(folder)
        self.lastFolder = folder
