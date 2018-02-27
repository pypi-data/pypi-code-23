#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import glob
import concurrent.futures
from PyQt5 import QtCore, QtGui, QtWidgets
from cryio import parparser, cbfimage, ImageError
from crymon import reconstruct
from .ui.ui_wdarth import Ui_WDarth


class WorkerSignals(QtCore.QObject):
    errorSignal = QtCore.pyqtSignal(str)
    progressSignal = QtCore.pyqtSignal(str)
    stopSignal = QtCore.pyqtSignal()
    finishedSignal = QtCore.pyqtSignal(object)
    nFilesSignal = QtCore.pyqtSignal(int)


class Worker(QtCore.QRunnable):
    def __init__(self, params: dict):
        super().__init__()
        self.stop = False
        dirpath = params['dir']
        self.dirpath = dirpath[:-1] if dirpath[-1] == '/' or dirpath[-1] == '\\' else dirpath
        self.params = params
        self.r = []
        self.signals = WorkerSignals()
        self.signals.stopSignal.connect(self.stopIt)

    def stopIt(self):
        self.stop = True

    def makeSlices(self):
        bn = os.path.basename(self.dirpath)
        ld = os.path.join(self.dirpath, 'layers')
        try:
            os.mkdir(ld)
        except OSError:
            if not os.path.isdir(ld):
                self.stopIt()
                return
        if self.params['volume']:
            s = reconstruct.Slice()
            s.downsample = self.params['downsample']
            s.lorentz = self.params['lorentz']
            s.scale = self.params['scale']
            s.dQ = self.params['dQ']
            s.x = self.params['x']
            s.y = self.params['y']
            s.z = self.params['z']
            s.p0.h, s.p0.k, s.p0.l = 1, 0, 0
            s.p1.h, s.p1.k, s.p1.l = 0, 1, 0
            s.pc.h, s.pc.k, s.pc.l = 0, 0, 0
            r = reconstruct.Volume(s)
            r.set_par(self.par)
            r.name = os.path.join(ld, f'{bn}.ccp4')
            self.r.append(r)
        for l in self.params['layers']:
            s = reconstruct.Slice()
            s.downsample = self.params['downsample']
            s.lorentz = self.params['lorentz']
            s.scale = self.params['scale']
            s.p0.h, s.p0.k, s.p0.l = l['hkl1']
            s.p1.h, s.p1.k, s.p1.l = l['hkl2']
            s.pc.h, s.pc.k, s.pc.l = l['center']
            s.qmax = l['qmax']
            s.voxels = l['size']
            s.thickness = l['thickness']
            r = reconstruct.Layer(s)
            r.set_par(self.par)
            n = f"{bn}__{l['hkl1']}__{l['hkl2']}__{l['center']}.cbf".replace(' ', '_')
            r.name = os.path.join(ld, re.sub('[\[\],]', '', n))
            self.r.append(r)

    def waitForResults(self, tasks: list) -> cbfimage.CbfImage or None:
        res = None
        for future in concurrent.futures.as_completed(tasks):
            if self.stop:
                return None
            result = future.result()
            if result is not None:
                res = result
        return res

    def submit(self, executor: concurrent.futures.ThreadPoolExecutor, i: cbfimage.CbfImage, cbf: str = '') -> list:
        tasks = [executor.submit(r.add, i.array, i.header['Start_angle'], i.header['Angle_increment']) for r in self.r]
        if cbf:
            tasks.append(executor.submit(lambda: cbfimage.CbfImage(cbf)))
        return tasks

    def makemap(self):
        if self.cbflist:
            image = cbfimage.CbfImage(self.cbflist[0])
            with concurrent.futures.ThreadPoolExecutor(os.cpu_count()) as executor:
                for cbf in self.cbflist[1:]:
                    if self.stop:
                        break
                    image = self.waitForResults(self.submit(executor, image, cbf))
                    self.signals.progressSignal.emit('Reading files')
                if not self.stop:
                    self.waitForResults(self.submit(executor, image))
                    self.signals.progressSignal.emit('Calculating CCP4')
                    self.waitForResults([executor.submit(r.save, r.name) for r in self.r])
        self.signals.progressSignal.emit('Finished')

    def run(self):
        try:
            self.cbflist = glob.glob(os.path.join(self.dirpath, '*.cbf'))
            self.signals.nFilesSignal.emit(len(self.cbflist))
            self.par = parparser.ParParser(self.params['par'])
            self.makeSlices()
            self.makemap()
        except (OSError, ImageError, reconstruct.ReconstructionError, parparser.ParError) as err:
            self.signals.errorSignal.emit(f'{self.dirpath}: {err}')
        self.stopIt()
        self.signals.finishedSignal.emit(self)


class WorkerPool(QtCore.QObject):
    progressSignal = QtCore.pyqtSignal(str, int)
    finishedSignal = QtCore.pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.pool = QtCore.QThreadPool.globalInstance()
        self.workers, self.errors = [], []

    def run(self, params: dict):
        folder = params['folder']
        self.jobs = len(params['layers']) + ('volume' in params)
        self.files = self.done = 0
        self.workers, self.errors = [], []
        for dirpath, dirnames, filenames in os.walk(folder):
            pars = glob.glob(os.path.join(dirpath, '*.par'))
            if not pars:
                continue
            for p in pars:
                if 'cracker' in p:
                    par = p
                    break
            else:
                par = pars[0]
            p = params.copy()
            p.update({'par': par, 'dir': dirpath})
            self.startWorker(p)
        self.workerFinished()

    def startWorker(self, p: dict):
        worker = Worker(p)
        worker.signals.errorSignal.connect(self.workerError)
        worker.signals.progressSignal.connect(self.workerProgress)
        worker.signals.finishedSignal.connect(self.workerFinished)
        worker.signals.nFilesSignal.connect(self.addNFiles)
        self.workers.append(worker)
        self.pool.start(worker)

    def addNFiles(self, n: int):
        self.files += n * self.jobs

    def stopIt(self):
        for worker in self.workers:
            worker.signals.stopSignal.emit()

    def workerProgress(self, info: str):
        self.done += self.jobs
        done = 100.0 * self.done / self.files
        self.progressSignal.emit(info, done)

    def workerError(self, folder: str):
        self.errors.append(folder)

    def workerFinished(self, worker: Worker = None):
        if worker:
            self.workers.remove(worker)
        if not self.workers:
            self.progressSignal.emit('Finished', 100)
            self.finishedSignal.emit(self.errors)


class WDarth(QtWidgets.QDialog, Ui_WDarth):
    stopWorkerSignal = QtCore.pyqtSignal()
    runWorkerSignal = QtCore.pyqtSignal(dict)

    def __init__(self, parent):
        super().__init__(parent)
        self.setUI()
        self.setPool()
        self.connectSignals()
        self.workerThread.start()

    def connectSignals(self):
        self.stopWorkerSignal.connect(self.pool.stopIt)
        self.runWorkerSignal.connect(self.pool.run)

    def setPool(self):
        self.workerThread = QtCore.QThread()
        self.pool = WorkerPool()
        self.pool.moveToThread(self.workerThread)
        self.pool.progressSignal.connect(self.showProgress)
        self.pool.finishedSignal.connect(self.workerFinished)

    def setUI(self):
        self.setupUi(self)
        intValidator = QtGui.QIntValidator()
        intValidator.setBottom(1)
        floatValidator = QtGui.QDoubleValidator()
        floatValidator.setBottom(1e-3)
        self.xLineEdit.setValidator(intValidator)
        self.yLineEdit.setValidator(intValidator)
        self.zLineEdit.setValidator(intValidator)
        self.editDownsample.setValidator(intValidator)
        self.editScale.setValidator(intValidator)
        self.dQLineEdit.setValidator(floatValidator)
        self.stopButton.setVisible(False)

    def showError(self, errors):
        QtWidgets.QMessageBox.critical(self, '3DV errors', '\n'.join(errors))

    def showProgress(self, info, value):
        self.runProgressBar.setFormat('{0}: %p%'.format(info))
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
        s.setValue('WDarth/Geometry', self.saveGeometry())
        s.setValue('WDarth/lastFolder', self.lastFolder)
        s.setValue('WDarth/folder', self.folderLineEdit.text())
        s.setValue('WDarth/x', self.xLineEdit.text())
        s.setValue('WDarth/y', self.yLineEdit.text())
        s.setValue('WDarth/z', self.zLineEdit.text())
        s.setValue('WDarth/dQ', self.dQLineEdit.text())
        s.setValue('WDarth/lorentz', self.lorentzCheckBox.isChecked())
        s.setValue('WDarth/treeLayersState', self.treeLayers.header().saveState())
        s.setValue('WDarth/downsample', self.editDownsample.text())
        s.setValue('WDarth/scale', self.editScale.text())
        s.setValue('WDarth/volume', self.volumeCheckBox.isChecked())

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WDarth/Geometry', b''))
        self.lastFolder = s.value('WDarth/lastFolder', '', str)
        self.folderLineEdit.setText(s.value('WDarth/folder', '', str))
        self.xLineEdit.setText(s.value('WDarth/x', '256', str))
        self.yLineEdit.setText(s.value('WDarth/y', '256', str))
        self.zLineEdit.setText(s.value('WDarth/z', '256', str))
        self.dQLineEdit.setText(s.value('WDarth/dQ', '0.6', str))
        self.lorentzCheckBox.setChecked(s.value('WDarth/lorentz', False, bool))
        self.treeLayers.header().restoreState(s.value('WDarth/treeLayersState', b''))
        self.editDownsample.setText(s.value('WDarth/downsample', '1', str))
        self.editScale.setText(s.value('WDarth/scale', '1', str))
        self.volumeCheckBox.setChecked(s.value('WDarth/volume', True, bool))

    @QtCore.pyqtSlot()
    def on_runButton_clicked(self):
        folder = self.folderLineEdit.text()
        if not folder or not os.path.exists(folder):
            return
        self.runButton.setVisible(False)
        self.stopButton.setVisible(True)
        params = {
            'folder': folder,
            'x': int(self.xLineEdit.text()),
            'y': int(self.yLineEdit.text()),
            'z': int(self.zLineEdit.text()),
            'dQ': float(self.dQLineEdit.text()),
            'lorentz': int(self.lorentzCheckBox.isChecked()),
            'scale': int(self.editScale.text()),
            'volume': self.volumeCheckBox.isChecked(),
            'layers': self.treeLayers.getLayers(),
            'downsample': int(self.editDownsample.text()),
        }
        self.runWorkerSignal.emit(params)

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
