#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import io
import glob
from PyQt5 import QtCore, QtGui, QtWidgets
from cryio import cbfimage
from .ui.ui_wheader import Ui_WHeader


class WHeader(QtWidgets.QDialog, Ui_WHeader):
    sigStopWorker = QtCore.pyqtSignal()
    sigRunWorker = QtCore.pyqtSignal(str, list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setUI()
        self.createWorker()

    def setUI(self):
        self.setupUi(self)
        self.valuesList.addItems(sorted(list(cbfimage.ALL_KEYWORDS.keys()) + list(cbfimage.PSEUDO_KEYS)))
        self.stopButton.setVisible(False)
        self.createContextMenu()
        self.resultTable.keyPressEvent = self.resultTableKeyPressEvent
        self.resultTable.contextMenuEvent = self.resultTableContextMenuEvent
        layoutDir = QtWidgets.QHBoxLayout()
        layoutDir.addWidget(self.label)
        layoutDir.addWidget(self.folderLineEdit)
        layoutDir.addWidget(self.folderButton)
        layoutButtons = QtWidgets.QHBoxLayout()
        layoutButtons.addWidget(self.runButton)
        layoutButtons.addWidget(self.stopButton)
        layoutButtons.addWidget(self.saveButton)
        layoutButtons.addWidget(self.copyButton)
        layoutButtons.addWidget(self.runProgressBar)
        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.valuesList)
        self.splitter.addWidget(self.resultTable)
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(layoutDir)
        layout.addWidget(self.splitter)
        layout.addLayout(layoutButtons)
        self.setLayout(layout)

    def createWorker(self):
        self.workerThread = QtCore.QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.workerThread)
        self.worker.sigFiles.connect(self.setResultTable)
        _signals.sigResult.connect(self.showProgress)
        self.sigStopWorker.connect(self.worker.stop)
        self.sigRunWorker.connect(self.worker.run)
        # noinspection PyUnresolvedReferences
        self.workerThread.started.connect(self.worker.started)
        # noinspection PyUnresolvedReferences
        self.workerThread.finished.connect(self.worker.finished)

    def createContextMenu(self):
        copyMenuAction = QtWidgets.QAction('&Copy', self.resultTable)
        copyMenuAction.setShortcut(QtGui.QKeySequence.Copy)
        # noinspection PyUnresolvedReferences
        copyMenuAction.triggered.connect(self.copyToClipboard)
        saveTextAction = QtWidgets.QAction('&Save as text', self.resultTable)
        saveTextAction.setShortcut(QtGui.QKeySequence.Save)
        # noinspection PyUnresolvedReferences
        saveTextAction.triggered.connect(self.on_saveButton_clicked)
        self.contextMenu = QtWidgets.QMenu()
        self.contextMenu.addAction(copyMenuAction)
        self.contextMenu.addAction(saveTextAction)

    def resultTableContextMenuEvent(self, event):
        self.contextMenu.exec_(event.globalPos())

    @QtCore.pyqtSlot()
    def on_copyButton_clicked(self):
        self.copyToClipboard()

    def copyToClipboard(self):
        buf = io.StringIO()
        self.saveText(buf)
        QtWidgets.QApplication.clipboard().setText(buf.getvalue())

    def resultTableKeyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_C and event.modifiers() == QtCore.Qt.ControlModifier:
            self.copyToClipboard()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            pass
        else:
            super().keyPressEvent(event)

    def checkedHeaderValues(self):
        checked = []
        for i in range(self.valuesList.count()):
            item = self.valuesList.item(i)
            if item.checkState():
                checked.append(item.text())
        return checked

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WHeader/Geometry', self.saveGeometry())
        s.setValue('WHeader/SplitterGeometry', self.splitter.saveGeometry())
        s.setValue('WHeader/SplitterState', self.splitter.saveState())
        s.setValue('WHeader/checked', self.checkedHeaderValues())
        s.setValue('WHeader/lastFolder', self.lastFolder)

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WHeader/Geometry', b''))
        self.splitter.restoreGeometry(s.value('WHeader/SplitterGeometry', b''))
        self.splitter.restoreState(s.value('WHeader/SplitterState', b''))
        self.lastFolder = s.value('WHeader/lastFolder', '', str)
        self.folderLineEdit.setText(self.lastFolder)
        checked = s.value('WHeader/checked', [], list)
        for i in range(self.valuesList.count()):
            item = self.valuesList.item(i)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked if item.text() in checked else QtCore.Qt.Unchecked)
        self.on_valuesList_itemClicked()

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def on_valuesList_itemClicked(self):
        self.resultTable.clear()
        self.resultTable.setRowCount(0)
        checked = self.checkedHeaderValues()
        self.resultTable.setColumnCount(len(checked))
        self.resultTable.setHorizontalHeaderLabels(checked)

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        self.sigStopWorker.emit()
        self.workerFinished()

    def workerFinished(self):
        self.runProgressBar.setValue(100)
        self.runButton.setVisible(True)
        self.stopButton.setVisible(False)

    @QtCore.pyqtSlot()
    def on_runButton_clicked(self):
        self.runButton.setVisible(False)
        self.stopButton.setVisible(True)
        self.on_valuesList_itemClicked()
        folder = self.folderLineEdit.text()
        self.lastFolder = folder
        checked = self.checkedHeaderValues()
        if folder and checked:
            self.sigRunWorker.emit(folder, checked)

    def saveText(self, file):
        s = '\t'.join(self.checkedHeaderValues())
        file.write(f'{s}\n')
        for i in range(self.resultTable.rowCount()):
            s = '\t'.join(self.resultTable.item(i, j).text() for j in range(self.resultTable.columnCount()))
            file.write(f'{s}\n')

    @QtCore.pyqtSlot()
    def on_saveButton_clicked(self):
        datName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file as a text', self.lastFolder)[0]
        if datName:
            try:
                with open(datName, 'w') as file:
                    self.saveText(file)
            except OSError as err:
                QtWidgets.QMessageBox.critical(self, 'Error', f'Could not save file {datName}: {err}')

    def showProgress(self, i, total, values):
        for j, value in enumerate(values):
            item = QtWidgets.QTableWidgetItem(str(value))
            self.resultTable.setItem(i, j, item)
        self.runProgressBar.setValue(100 * i / total)
        if i == total:
            self.workerFinished()

    def setResultTable(self, n):
        self.resultTable.setRowCount(n)

    @QtCore.pyqtSlot()
    def on_folderButton_clicked(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose folder with cbf files', self.lastFolder)
        if folder:
            self.folderLineEdit.setText(folder)
            self.lastFolder = folder

    @QtCore.pyqtSlot()
    def on_copyButton_clicked(self):
        self.resultTable.selectAll()
        self.copyToClipboard()

    def showEvent(self, event: QtGui.QShowEvent):
        event.accept()
        self.workerThread.start()

    def hideEvent(self, event: QtGui.QHideEvent):
        self.on_stopButton_clicked()
        self.saveSettings()
        self.sigStopWorker.emit()
        self.workerThread.quit()
        self.workerThread.wait()
        event.accept()


class Worker(QtCore.QObject):
    sigFiles = QtCore.pyqtSignal(int)
    sigResult = QtCore.pyqtSignal(int, int, list)

    def __init__(self):
        super().__init__()
        self.pool = None

    def stop(self):
        if self.pool:
            self.pool.clear()

    def started(self):
        self.pool = QtCore.QThreadPool()

    def finished(self):
        self.pool.clear()
        self.pool = None

    def run(self, folder: str, checked: list):
        if checked and os.path.isdir(folder):
            files = glob.glob(os.path.join(folder, '*.cbf'))
            self.sigFiles.emit(len(files))
            total = len(files) - 1
            files.sort()
            for i, name in enumerate(files):
                self.pool.start(Reader(i, total, name, checked))


class Reader(QtCore.QRunnable):
    def __init__(self, num: int, total: int, name: str, keys: list):
        super().__init__()
        self.setAutoDelete(True)
        self.name = name
        self.keys = keys
        self.num = num
        self.total = total

    def run(self):
        try:
            hdr = cbfimage.CbfHeader(self.name)
        except (cbfimage.CbfError, OSError) as err:
            QtCore.qWarning(f'Error: {err}')
            values = [0] * len(self.keys)
            if '!File name' in self.keys and values:
                values[0] = os.path.basename(self.name)
        else:
            values = ((hdr[key] if key in hdr else 0) for key in self.keys)
        _signals.sigResult.emit(self.num, self.total, values)


class Signals(QtCore.QObject):
    sigResult = QtCore.pyqtSignal(int, int, object)


_signals = Signals()
