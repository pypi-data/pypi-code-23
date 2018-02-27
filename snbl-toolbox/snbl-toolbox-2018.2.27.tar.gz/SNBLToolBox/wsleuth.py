#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
from PyQt5 import QtCore, QtGui, QtWidgets
from cryio.cbfimage import CbfImage
from .ui.ui_wsleuth import Ui_WSleuth


class SleuthWalker(QtCore.QObject):
    progressSignal = QtCore.pyqtSignal(object, float, int, float)
    finishedSignal = QtCore.pyqtSignal()

    def __init__(self, dire, frame, frame_pm, roi, reg, psi):
        QtCore.QObject.__init__(self)
        self.dir = dire
        self.roi = roi
        self.frame = frame
        self.frame_pm = frame_pm
        self.reg = reg
        self.psi = psi
        self.stop()

    def stop(self):
        self.stopped = True

    def run(self):
        self.stopped = False
        if self.frame == -1:
            self.listDir()
        elif self.psi:
            self.psiScan()
        else:
            self.walk()
        self.finishedSignal.emit()
        self.stop()

    def psiScan(self):
        files = {}
        for fcbf in sorted(os.listdir(self.dir)):
            if not fcbf.endswith('.cbf'):
                continue
            QtCore.QCoreApplication.processEvents()
            if self.stopped:
                return
            nums = re.split(r'^psi_([-+]?[0-9]*\.?[0-9]+)_\d+p_(\d+)\.cbf$', fcbf)
            frame = int(nums[2])
            psi = float(nums[1])
            if self.frame - self.frame_pm <= frame <= self.frame + self.frame_pm:
                if psi not in files:
                    files[psi] = []
                files[psi].append(fcbf)
        for psi in sorted(files):
            self.readIntensity(self.dir, files[psi], psi)

    def walk(self):
        params = []
        for dirpath, dirnames, filenames in sorted(os.walk(self.dir)):
            QtCore.QCoreApplication.processEvents()
            if self.stopped:
                return
            if not filenames:
                continue
            match = re.search(self.reg, os.path.basename(dirpath))
            if match:
                try:
                    params.append((dirpath, self.listDirForFrames(filenames), match.group(1)))
                except (ValueError, IndexError):
                    continue

        def sp(key):
            d, f, m = key
            try:
                return float(d)
            except ValueError:
                return d
        params.sort(key=sp)
        for p in params:
            self.readIntensity(*p)

    def listDir(self):
        i = 0
        for fcbf in sorted(os.listdir(self.dir)):
            if not fcbf.endswith('.cbf'):
                continue
            # noinspection PyArgumentList
            QtCore.QCoreApplication.processEvents()
            if self.stopped:
                return
            try:
                frame = int(re.split(r'.+_\d+p_(\d+)\.cbf$', fcbf)[1])
            except IndexError:
                frame_re = re.split(r'.+_(\d+)p\.cbf$', fcbf)
                if len(frame_re) > 1:
                    frame = int(frame_re[1])
                else:
                    frame = i
                    i += 1
            self.readIntensity(self.dir, [fcbf], frame)

    def readIntensity(self, dire, fcbfs, param):
        roi_sum = flux = 0
        for fcbf in fcbfs:
            if not fcbf.endswith('.cbf'):
                continue
            # noinspection PyArgumentList
            QtCore.QCoreApplication.processEvents()
            if self.stopped:
                return
            x1, x2, y1, y2 = self.roi
            cbf = CbfImage(os.path.join(dire, fcbf))
            if 'Flux' not in cbf.header_dict:
                return
            roi = cbf.array[y1:y2, x1:x2]
            roi_sum += roi.sum()
            flux += cbf.header_dict['Flux']
        roi_sum = float(roi_sum)
        try:
            roi_norm = roi_sum / flux
        except ZeroDivisionError:
            roi_norm = 0
        self.progressSignal.emit(param, roi_sum, flux, roi_norm)

    def listDirForFrames(self, filenames):
        start = self.frame - self.frame_pm
        stop = self.frame + self.frame_pm + 1
        # format: base_XXXXXXp_frames.cbf
        rexp = r'.+_\d+p_(%s)\.cbf$' % '|'.join('%05d' % n for n in range(start, stop))
        for fname in sorted(filenames):
            if re.search(rexp, fname):
                yield fname


class WSleuth(QtWidgets.QDialog, Ui_WSleuth):
    stopWalkSignal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self._parent = parent
        self.setupUi(self)
        self.stopButton.hide()
        self.walkThread = QtCore.QThread()
        self.createContextMenu()
        self.intTable.keyPressEvent = self.resultTableKeyPressEvent
        self.intTable.contextMenuEvent = self.resultTableContextMenuEvent
        self.onlineCheckBox.setText('Psi scan')

    def createContextMenu(self):
        copyMenuAction = QtWidgets.QAction('&Copy', self.intTable)
        copyMenuAction.setShortcut(QtGui.QKeySequence.Copy)
        # noinspection PyUnresolvedReferences
        copyMenuAction.triggered.connect(self.copyToClipboard)
        saveTextAction = QtWidgets.QAction('&Save as text', self.intTable)
        saveTextAction.setShortcut(QtGui.QKeySequence.Save)
        # noinspection PyUnresolvedReferences
        saveTextAction.triggered.connect(self.on_saveButton_clicked)
        self.contextMenu = QtWidgets.QMenu()
        self.contextMenu.addAction(copyMenuAction)
        self.contextMenu.addAction(saveTextAction)

    def resultTableContextMenuEvent(self, event):
        self.contextMenu.exec_(event.globalPos())

    @QtCore.pyqtSlot()
    def copyToClipboard(self):
        selectedItems = self.intTable.selectedItems()
        toClipboard = u''
        for i in range(self.intTable.rowCount()):
            setNewLine = u''
            for j in range(self.intTable.columnCount()):
                item = self.intTable.item(i, j)
                if selectedItems:
                    if item in selectedItems:
                        toClipboard += item.text() + u'\t'
                        setNewLine = u'\n'
                elif item:
                    toClipboard += item.text() + u'\t'
                    setNewLine = u'\n'
            toClipboard += setNewLine
        QtWidgets.QApplication.clipboard().setText(toClipboard)

    def resultTableKeyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C and event.modifiers() == QtCore.Qt.ControlModifier:
            self.copyToClipboard()

    def dataReceived(self, x, y, flux, y_norm):
        self.tx += 1
        self.intTable.setRowCount(self.tx)
        self.intTable.setItem(self.tx - 1, 0, QtWidgets.QTableWidgetItem(str(x)))
        self.intTable.setItem(self.tx - 1, 1, QtWidgets.QTableWidgetItem(str(y)))
        self.intTable.setItem(self.tx - 1, 2, QtWidgets.QTableWidgetItem(str(flux)))
        self.intTable.setItem(self.tx - 1, 3, QtWidgets.QTableWidgetItem(str(y_norm)))
        self.y.append(y)
        self.y_norm.append(y_norm)
        self.flux.append(flux)
        try:
            x = float(x)
        except ValueError:
            pass
        else:
            self.x.append(x)
            self.plotView.plot(self.x, self.y_norm, pen='g', clear=True)

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WSleuth/Geometry', self.saveGeometry())
        s.setValue('WSleuth/lastFolder', self.lastDir)
        s.setValue('WSleuth/x1', self.x1SpinBox.value())
        s.setValue('WSleuth/x2', self.x2SpinBox.value())
        s.setValue('WSleuth/y1', self.y1SpinBox.value())
        s.setValue('WSleuth/y2', self.y2SpinBox.value())
        s.setValue('WSleuth/frame', self.frameSpinBox.value())
        s.setValue('WSleuth/pm', self.pmSpinBox.value())
        s.setValue('WSleuth/online', self.onlineCheckBox.isChecked())
        s.setValue('WSleuth/folder', self.dirLineEdit.text())
        s.setValue('WSleuth/re', self.reLineEdit.text())

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WSleuth/Geometry', b''))
        self.lastDir = s.value('WSleuth/lastFolder', '', str)
        self.dirLineEdit.setText(s.value('WSleuth/folder', '', str))
        self.x1SpinBox.setValue(s.value('WSleuth/x1', 0, float))
        self.x2SpinBox.setValue(s.value('WSleuth/x2', 0, float))
        self.y1SpinBox.setValue(s.value('WSleuth/y1', 0, float))
        self.y2SpinBox.setValue(s.value('WSleuth/y2', 0, float))
        self.frameSpinBox.setValue(s.value('WSleuth/frame', 0, float))
        self.pmSpinBox.setValue(s.value('WSleuth/pm', 0, float))
        self.onlineCheckBox.setChecked(s.value('WSleuth/online', False, bool))
        self.reLineEdit.setText(s.value('WSleuth/re', '', str))

    def closeEvent(self, event):
        self.saveSettings()
        self.stopWalkSignal.emit()
        self.hide()
        self.walkThread.quit()
        self.walkThread.wait()

    @QtCore.pyqtSlot()
    def on_runButton_clicked(self):
        dire = self.dirLineEdit.text()
        if not dire or not os.path.exists(dire):
            return
        self.intTable.setColumnCount(4)
        self.intTable.setHorizontalHeaderLabels(['P', 'I', 'Flux', 'Inorm'])
        self.tx = 0
        self.stopButton.show()
        self.runButton.hide()
        self.walk(dire)

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        self.stopButton.hide()
        self.runButton.show()
        self.stopWalkSignal.emit()

    @QtCore.pyqtSlot()
    def on_dirButton_clicked(self):
        # noinspection PyCallByClass,PyTypeChecker
        dire = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select directory', self.lastDir)
        if not dire:
            return
        self.dirLineEdit.setText(dire)
        self.lastDir = dire

    @QtCore.pyqtSlot()
    def on_exitButton_clicked(self):
        self.close()

    def walk(self, dire):
        self.x, self.y, self.flux, self.y_norm = [], [], [], []
        x1 = self.x1SpinBox.value()
        x2 = self.x2SpinBox.value()
        y1 = self.y1SpinBox.value()
        y2 = self.y2SpinBox.value()
        frame = self.frameSpinBox.value()
        frame_pm = self.pmSpinBox.value()
        reg = self.reLineEdit.text()
        psi = self.onlineCheckBox.isChecked()
        self.worker = SleuthWalker(dire, frame, frame_pm, (x1, x2, y1, y2), reg, psi)
        self.worker.moveToThread(self.walkThread)
        # noinspection PyUnresolvedReferences
        self.walkThread.started.connect(self.worker.run)
        self.worker.finishedSignal.connect(self.on_stopButton_clicked)
        self.worker.finishedSignal.connect(self.walkThread.quit)
        self.worker.progressSignal.connect(self.dataReceived)
        self.stopWalkSignal.connect(self.worker.stop)
        self.walkThread.start()

    @QtCore.pyqtSlot()
    def on_saveButton_clicked(self):
        datName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file as a text', self.lastDir)[0]
        if not datName:
            return
        res = u''
        for i in range(self.intTable.rowCount()):
            for j in range(self.intTable.columnCount()):
                res += u'%s ' % self.intTable.item(i, j).text()
            res += u'\n'
        open(datName, 'w').write(res)

    @QtCore.pyqtSlot()
    def on_copyButton_clicked(self):
        self.intTable.selectAll()
        self.copyToClipboard()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            pass
        else:
            super().keyPressEvent(event)
