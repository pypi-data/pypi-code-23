#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import glob
import sip
from PyQt5 import QtCore, QtGui, QtWidgets
import cryio
from cryio.cbfimage import CbfImage


NEGATIVE_THRESHOLD = -3


class Page(QtWidgets.QWizardPage):
    def __init__(self, parent=None, prevPage=None):
        QtWidgets.QWizardPage.__init__(self, parent)
        self.prevPage = prevPage
        self.setupUi()

    def setupUi(self):
        pass


class FilesPage(Page):
    def setupUi(self):
        folderButton = QtWidgets.QPushButton('Choose folder...')
        folderButton.clicked.connect(self.chooseFolder)

        filesButton = QtWidgets.QPushButton('Choose files...')
        filesButton.clicked.connect(self.chooseFiles)

        label = QtWidgets.QLabel('or')

        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(folderButton)
        hlayout.addWidget(label)
        hlayout.addWidget(filesButton)
        hlayout.addStretch()

        self.fileList = QtWidgets.QListWidget()
        self.fileList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        delButton = QtWidgets.QPushButton('Delete items')
        delButton.clicked.connect(self.delItems)

        clearButton = QtWidgets.QPushButton('Clear')
        clearButton.clicked.connect(self.clearItems)

        self.label = QtWidgets.QLabel('Selected files: 0')

        hlayout1 = QtWidgets.QHBoxLayout()
        hlayout1.addWidget(self.label)
        hlayout1.addStretch()
        hlayout1.addWidget(delButton)
        hlayout1.addWidget(clearButton)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self.fileList)
        vlayout.addLayout(hlayout1)
        self.setLayout(vlayout)

    def initializePage(self):
        settings = QtCore.QSettings()
        self.lastFolder = settings.value('Convert/lastFolder', '', str)
        self.files = {}

    @QtCore.pyqtSlot()
    def chooseFolder(self, what='*.cbf *.edf'):
        d = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose the folder with %s files' % what, self.lastFolder)
        if not d:
            return
        self.lastFolder = d
        pd = QtWidgets.QProgressDialog('Reading directories...', 'Cancel', 0, 1, self)
        pd.setAutoClose(False)
        pd.setAutoReset(False)
        pd.setWindowModality(QtCore.Qt.WindowModal)
        counter, files = 1, []
        for dirpath, dirnames, filenames in os.walk(d):
            pd.setMaximum(counter + len(dirnames))
            pd.setValue(counter)
            pd.setLabelText('Reading {}'.format(dirpath))
            counter += len(dirnames)
            if pd.wasCanceled():
                self.files = {}
                return
            QtCore.QCoreApplication.processEvents()
            self.files[dirpath] = []
            for ext in what.split(' '):
                fs = glob.glob(os.path.join(dirpath, ext))
                fs.sort()
                self.files[dirpath] += fs
                files += fs
        pd.close()
        self.openFiles(files)

    @QtCore.pyqtSlot()
    def chooseFiles(self, what='*.cbf *.edf'):
        files = QtWidgets.QFileDialog.getOpenFileNames(self, 'Choose %s files' % what,
                                                       self.lastFolder, 'Pilatus data (%s)' % what)[0]
        if files:
            self.files[os.path.dirname(files[0])] = files
        self.openFiles(files)

    def openFiles(self, files):
        if not files:
            return
        self.fileList.addItems(files)
        self.label.setText('Selected files: %d' % self.fileList.count())

    @QtCore.pyqtSlot()
    def delItems(self):
        for item in self.fileList.selectedItems():
            sip.delete(item)
        self.label.setText('Selected files: %d' % self.fileList.count())

    @QtCore.pyqtSlot()
    def clearItems(self):
        self.fileList.clear()
        self.label.setText('Selected files: %d' % self.fileList.count())

    def validatePage(self):
        settings = QtCore.QSettings()
        settings.setValue('Convert/lastFolder', self.lastFolder)
        return Page.validatePage(self)


class OptionsPage(Page):
    def setupUi(self):
        self.cbf = QtWidgets.QRadioButton('cbf')
        self.cbf.setChecked(True)
        self.edf = QtWidgets.QRadioButton('edf')

        hrlayout = QtWidgets.QHBoxLayout()
        vrlayout1 = QtWidgets.QVBoxLayout()
        vrlayout1.addWidget(self.cbf)
        vrlayout2 = QtWidgets.QVBoxLayout()
        vrlayout2.addWidget(self.edf)
        hrlayout.addLayout(vrlayout1)
        hrlayout.addLayout(vrlayout2)

        radiosGroupBox = QtWidgets.QGroupBox('Choose the format to convert')
        radiosGroupBox.setLayout(hrlayout)

        self.binningCheckBox = QtWidgets.QCheckBox('Make binning')
        self.binningEveryRadio = QtWidgets.QRadioButton('for every')
        self.binningSpinBox = QtWidgets.QSpinBox()
        self.binningSpinBox.setDisabled(True)
        self.binningSpinBox.setMinimum(2)
        self.binningSpinBox.setMaximum(65535)
        self.binningPeriodRadio = QtWidgets.QRadioButton('periodically')
        filesLabel = QtWidgets.QLabel('files')
        self.binningGroup = QtWidgets.QButtonGroup()
        self.binningGroup.addButton(self.binningEveryRadio)
        self.binningGroup.addButton(self.binningPeriodRadio)

        def toggleBinning(enable=None):
            if enable is None:
                enable = self.binningCheckBox.isChecked()
            self.binningSpinBox.setEnabled(enable)
            self.binningEveryRadio.setEnabled(enable)
            self.binningPeriodRadio.setEnabled(enable)
            filesLabel.setEnabled(enable)

        toggleBinning(False)
        self.binningEveryRadio.setChecked(True)
        self.binningCheckBox.toggled.connect(toggleBinning)
        self.binningPeriodRadio.toggled.connect(
            lambda: self.binningSpinBox.setDisabled(self.binningPeriodRadio.isChecked())
        )

        hlayout1 = QtWidgets.QHBoxLayout()
        hlayout1.addWidget(self.binningCheckBox)
        hlayout1.addWidget(self.binningEveryRadio)
        hlayout1.addWidget(self.binningSpinBox)
        hlayout1.addWidget(filesLabel)
        hlayout1.addWidget(self.binningPeriodRadio)
        hlayout1.addStretch()

        self.negativeCheckBox = QtWidgets.QCheckBox('Set negative intensity as')
        self.negativeSpinBox = QtWidgets.QSpinBox()
        self.negativeSpinBox.setMinimum(-2)
        self.negativeSpinBox.setDisabled(True)
        self.negativeCheckBox.clicked.connect(
            lambda: self.negativeSpinBox.setEnabled(self.negativeCheckBox.isChecked())
        )

        hlayout2 = QtWidgets.QHBoxLayout()
        hlayout2.addWidget(self.negativeCheckBox)
        hlayout2.addWidget(self.negativeSpinBox)
        hlayout2.addStretch()

        self.moveAngleCheckBox = QtWidgets.QCheckBox('Move final angles:')
        self.startingAngleSpinBox = QtWidgets.QDoubleSpinBox()
        self.startingAngleSpinBox.setDecimals(4)
        self.startingAngleSpinBox.setMinimum(-360)
        self.startingAngleSpinBox.setMaximum(360)
        self.angleIncrementSpinBox = QtWidgets.QDoubleSpinBox()
        self.angleIncrementSpinBox.setDecimals(4)
        self.angleIncrementSpinBox.setMinimum(-360)
        self.angleIncrementSpinBox.setMaximum(360)
        startLabel = QtWidgets.QLabel('start')
        incLabel = QtWidgets.QLabel('increment')
        hlayout3 = QtWidgets.QHBoxLayout()
        hlayout3.addWidget(self.moveAngleCheckBox)
        hlayout3.addWidget(startLabel)
        hlayout3.addWidget(self.startingAngleSpinBox)
        hlayout3.addWidget(incLabel)
        hlayout3.addWidget(self.angleIncrementSpinBox)
        hlayout3.addStretch()

        def showAngle(show):
            self.moveAngleCheckBox.setVisible(show)
            self.startingAngleSpinBox.setVisible(show)
            self.angleIncrementSpinBox.setVisible(show)
            startLabel.setVisible(show)
            incLabel.setVisible(show)

        showAngle(True)
        self.cbf.toggled[bool].connect(showAngle)

        def enableAngle(en):
            self.angleIncrementSpinBox.setEnabled(en)
            self.startingAngleSpinBox.setEnabled(en)

        enableAngle(False)
        self.moveAngleCheckBox.toggled[bool].connect(enableAngle)

        self.int32 = QtWidgets.QRadioButton('Int32 (for fit2d)')
        self.int32.setChecked(True)
        self.int16 = QtWidgets.QRadioButton('Int16')
        self.intGroup = QtWidgets.QButtonGroup()
        self.intGroup.addButton(self.int32)
        self.intGroup.addButton(self.int16)
        self.flipCheckBox = QtWidgets.QCheckBox('Flip image (for fit2d)')
        self.flipCheckBox.setChecked(True)
        self.addHeaderCheckBox = QtWidgets.QCheckBox('Add edf header (for fit2d)')
        self.addHeaderCheckBox.setChecked(True)
        hlayout4 = QtWidgets.QHBoxLayout()
        hlayout4.addWidget(self.int32)
        hlayout4.addWidget(self.int16)
        hlayout4.addStretch()
        hlayout5 = QtWidgets.QHBoxLayout()
        hlayout5.addWidget(self.flipCheckBox)
        hlayout5.addStretch()
        hlayout6 = QtWidgets.QHBoxLayout()
        hlayout6.addWidget(self.addHeaderCheckBox)
        hlayout6.addStretch()

        def showEdfOpts(show):
            self.int16.setVisible(show)
            self.int32.setVisible(show)
            self.flipCheckBox.setVisible(show)
            self.addHeaderCheckBox.setVisible(show)

        showEdfOpts(False)
        self.edf.toggled[bool].connect(showEdfOpts)

        vlayout1 = QtWidgets.QVBoxLayout()
        vlayout1.addLayout(hlayout1)
        vlayout1.addLayout(hlayout2)
        vlayout1.addLayout(hlayout3)
        vlayout1.addLayout(hlayout4)
        vlayout1.addLayout(hlayout5)
        vlayout1.addLayout(hlayout6)

        optionsGroupBox = QtWidgets.QGroupBox('Options')
        optionsGroupBox.setLayout(vlayout1)

        vlayout2 = QtWidgets.QVBoxLayout()
        vlayout2.addWidget(radiosGroupBox)
        vlayout2.addWidget(optionsGroupBox)
        self.setLayout(vlayout2)

    def initializePage(self):
        s = QtCore.QSettings()
        self.setRadio(s.value('Convert/format', 'cbf', str), 'edf', 'cbf')
        binning = s.value('Convert/binning', False, bool)
        self.binningCheckBox.setChecked(binning)
        self.binningSpinBox.setValue(s.value('Convert/binning_value', 1, int))
        self.setRadio(s.value('Convert/bintype', 'binningEveryRadio', str), 'binningEveryRadio', 'binningPeriodRadio')
        negative = s.value('Convert/negative', False, bool)
        self.negativeCheckBox.setChecked(negative)
        self.negativeSpinBox.setEnabled(negative)
        self.negativeSpinBox.setValue(s.value('Convert/negative_value', 0, int))
        self.angleIncrementSpinBox.setValue(s.value('Convert/angleIncrement', 0, float))
        self.startingAngleSpinBox.setValue(s.value('Convert/startingAngle', 0, float))
        self.flipCheckBox.setChecked(s.value('Convert/edfFlip', True, bool))
        self.setRadio(s.value('Convert/edfInt', 'int32', str), 'int16', 'int32')
        self.addHeaderCheckBox.setChecked(s.value('Convert/edfAddHeader', True, bool))
        self.moveAngleCheckBox.setChecked(s.value('Convert/move', False, bool))

    def getRadio(self, *radios):
        for item in radios:
            if self.__dict__[item].isChecked():
                return item

    def setRadio(self, value, *radios):
        for item in radios:
            if value == item:
                self.__dict__[item].setChecked(True)
                return

    def validatePage(self):
        s = QtCore.QSettings()
        s.setValue('Convert/format', self.getRadio('cbf', 'edf'))
        s.setValue('Convert/binning', self.binningCheckBox.isChecked())
        s.setValue('Convert/bintype', self.getRadio('binningEveryRadio', 'binningPeriodRadio'))
        s.setValue('Convert/binning_value', self.binningSpinBox.value())
        s.setValue('Convert/negative', self.negativeCheckBox.isChecked())
        s.setValue('Convert/negative_value', self.negativeSpinBox.value())
        s.setValue('Convert/startingAngle', self.startingAngleSpinBox.value())
        s.setValue('Convert/angleIncrement', self.angleIncrementSpinBox.value())
        s.setValue('Convert/edfInt', self.getRadio('int16', 'int32'))
        s.setValue('Convert/edfFlip', self.flipCheckBox.isChecked())
        s.setValue('Convert/edfAddHeader', self.addHeaderCheckBox.isChecked())
        s.setValue('Convert/move', self.moveAngleCheckBox.isChecked())
        return Page.validatePage(self)


class ConvertPage(Page):
    def setupUi(self):
        self.progress = QtWidgets.QProgressBar()
        self.progress.setMaximum(100)
        self.log = QtWidgets.QListWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.progress)
        layout.addWidget(self.log)
        self.setLayout(layout)

    def isComplete(self):
        return self.wizard().stopped


class ConvertWizard(QtWidgets.QWizard):
    terminateSignal = QtCore.pyqtSignal()

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Escape:
            pass
        else:
            QtWidgets.QDialog.keyPressEvent(self, event)

    def __init__(self, parent=None):
        QtWidgets.QWizard.__init__(self, parent)
        self.addPage(FilesPage())
        self.addPage(OptionsPage())
        self.addPage(ConvertPage())
        self.setWindowTitle('Pylatus image converter')
        self.setOptions(QtWidgets.QWizard.NoBackButtonOnLastPage)
        self.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        matrix = QtGui.QTransform().rotate(-90)
        pixmap = QtGui.QPixmap(':/snbl').scaled(281, 151, QtCore.Qt.KeepAspectRatio,
                                                QtCore.Qt.SmoothTransformation).transformed(matrix)
        self.setPixmap(QtWidgets.QWizard.WatermarkPixmap, pixmap)
        self.setWindowIcon(QtGui.QIcon(':/convert'))
        self.currentIdChanged[int].connect(self.checkPage)
        self.stopped = False
        self.workerThread = QtCore.QThread()
        self.rejected.connect(self.terminate)

    def terminate(self):
        self.terminateSignal.emit()
        self.finished()

    def checkPage(self, page):
        if page == 2:
            self.convert()

    def closeEvent(self, event):
        self.terminate()
        event.accept()

    def loadSettings(self):
        settings = QtCore.QSettings()
        self.restoreGeometry(settings.value('Convert/Geometry', b''))

    def saveSettings(self):
        settings = QtCore.QSettings()
        settings.setValue('Convert/Geometry', self.saveGeometry())

    def showProgress(self, images, converted, queueLength):
        self.log.addItem(images)
        self.log.scrollToBottom()
        self.progress.setValue(100.0 * converted / queueLength)

    def finished(self, p_int=0):
        self.stopped = True
        if hasattr(self, 'page2'):
            self.page2.completeChanged.emit()
        self.workerThread.quit()
        self.workerThread.wait()

    def convert(self):
        self.page2 = self.page(2)
        self.progress = self.page2.progress
        self.log = self.page2.log

        page1 = self.page(1)
        if page1.negativeCheckBox.isChecked():
            negative = page1.negativeSpinBox.value()
        else:
            negative = NEGATIVE_THRESHOLD

        self.format = page1.getRadio('cbf', 'edf')
        if page1.moveAngleCheckBox.isChecked():
            move = [page1.startingAngleSpinBox.value(), page1.angleIncrementSpinBox.value()]
        else:
            move = []

        images = self.page(0).files
        binning = page1.binningCheckBox.isChecked()
        binnum = page1.binningSpinBox.value() if page1.binningSpinBox.isEnabled() else 0
        opts = {
            'format': self.format,
            'negative': negative,
            'move': move,
            'edfInt': page1.getRadio('int16', 'int32'),
            'edfFlip': page1.flipCheckBox.isChecked(),
            'edfHeader': page1.addHeaderCheckBox.isChecked(),
        }
        self.workerManager = CbfConverterManager(images, binning, binnum, opts)
        self.workerManager.moveToThread(self.workerThread)
        self.workerThread.started.connect(self.workerManager.convert)
        self.workerManager.progressSignal.connect(self.showProgress)
        self.workerManager.finishedSignal.connect(self.workerFinished)
        self.terminateSignal.connect(self.workerManager.terminateAll)
        self.workerThread.start()

    def workerFinished(self, errors):
        if errors:
            QtWidgets.QMessageBox.critical(self, 'Errors', '\n'.join(e for e in errors))
        self.finished()


class Signals(QtCore.QObject):
    progressSignal = QtCore.pyqtSignal(str)
    errorSignal = QtCore.pyqtSignal(str)
    finishedSignal = QtCore.pyqtSignal(object)
    stopSignal = QtCore.pyqtSignal()


class CbfConverterWorker(QtCore.QRunnable):
    def __init__(self, opts):
        super().__init__()
        self.opts = opts
        self.stopped = False
        self.signals = Signals()
        self.signals.stopSignal.connect(self.stop)

    def run(self):
        try:
            self.convert()
        except OSError as e:
            self.signals.errorSignal.emit(str(e))
        self.stopped = True
        self.signals.finishedSignal.emit(self)

    def stop(self):
        self.stopped = True

    def convert(self):
        if self.stopped:
            return
        folder = os.path.join(os.path.dirname(self.opts['images'][0]), self.opts['format'])
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass
        img = cryio.openImage(self.opts['images'][0])
        oi = img.header.get('Omega_increment')
        pi = img.header.get('Phi_increment')
        ai = img.header.get('Angle_increment')
        for image in self.opts['images'][1:]:
            if self.stopped:
                return
            img += cryio.openImage(image)
        if self.opts['negative'] > NEGATIVE_THRESHOLD:
            img.array[img.array < 0] = self.opts['negative']
        if self.opts['move'] and isinstance(img, CbfImage):
            img.header['Start_angle'], img.header['Angle_increment'] = self.opts['move']
            if 'Oscillation_axis' in img.header:
                axis = img.header['Oscillation_axis'].upper()
                if axis == 'OMEGA':
                    img.header['Omega'], img.header['Omega_increment'] = self.opts['move']
                elif axis == 'PHI':
                    img.header['Phi'], img.header['Phi_increment'] = self.opts['move']
        if self.opts['binperiods']:
            if oi is not None:
                img.header['Omega_increment'] = oi
            if pi is not None:
                img.header['Phi_increment'] = pi
            if ai is not None:
                img.header['Angle_increment'] = ai
        self.opts.update(img.header)
        newImg = os.path.join(folder, self.opts['name'])
        img.save(newImg, self.opts['format'], **self.opts)
        self.signals.progressSignal.emit(newImg)


class CbfConverterManager(QtCore.QObject):
    progressSignal = QtCore.pyqtSignal(str, int, int)
    finishedSignal = QtCore.pyqtSignal(list)

    def __init__(self, images, binning, binnum, opts):
        super().__init__()
        self.stopped = True
        self.images = images
        self.opts = opts
        self.binning = binning
        self.binnum = binnum
        self.binperiods = self.binnum == 0
        self.opts['binperiods'] = self.binperiods
        self.pool = QtCore.QThreadPool.globalInstance()
        self.workers, self.errors = [], []
        self.startAngle = None
        self.angleInc = None

    def terminateAll(self):
        self.stopped = True
        for worker in self.workers:
            worker.signals.stopSignal.emit()
        self.workers = []

    def simpleConversion(self):
        for dirpath in self.images:
            for cbf in self.images[dirpath]:
                name = '{}.{[format]}'.format(os.path.basename(cbf)[:-4], self.opts)
                args = self.opts.copy()
                args.update({'images': (cbf,), 'name': name})
                yield self.moveAngle(args)

    def moveAngle(self, args):
        if args['move']:
            if self.startAngle is None and self.angleInc is None:
                self.startAngle, self.angleInc = args['move']
            else:
                self.startAngle += self.angleInc
                args['move'] = self.startAngle, self.angleInc
        return args

    def makeChunk(self, i, images):
        args = self.opts.copy()
        name = '{}_{:05d}.{[format]}'.format('_'.join(os.path.basename(images[0])[:-4].split('_')[:-1]), i, self.opts)
        args.update({'images': images, 'name': name})
        return self.moveAngle(args)

    def sort_periods(self, name):
        pattern = re.compile(r'.+_(\d+)p_(\d+)\.cbf$')
        try:
            period, frame = [int(i) for i in pattern.split(name)[1:3]]
        except IndexError:
            return name
        if period > self.binnum:
            self.binnum = period
        return frame, period

    def binFrames(self):
        for dirpath in self.images:
            self.startAngle = None
            self.angleInc = None
            i = 0
            images = []
            if self.binperiods:
                self.binnum = 0
            self.images[dirpath].sort(key=self.sort_periods if self.binperiods else None)
            for cbf in self.images[dirpath]:
                images.append(cbf)
                if len(images) == self.binnum:
                    yield self.makeChunk(i, images)
                    images = []
                    i += 1
            converted = i * self.binnum
            if converted < len(self.images[dirpath]):
                yield self.makeChunk(i, self.images[dirpath][converted:])

    def convert(self):
        self.stopped = False
        self.chunks = self.chunkDone = 0
        if self.binning:
            images = self.binFrames()
        else:
            images = self.simpleConversion()
        for chunk in images:
            QtCore.QCoreApplication.processEvents()
            if self.stopped:
                return
            self.chunks += 1
            worker = CbfConverterWorker(chunk)
            worker.signals.progressSignal.connect(self.showProgress)
            worker.signals.errorSignal.connect(self.showError)
            worker.signals.finishedSignal.connect(self.workerFinished)
            self.workers.append(worker)
            self.pool.start(worker)

    def showError(self, err):
        if err not in self.errors:
            self.errors.append(err)

    def showProgress(self, fname):
        self.chunkDone += 1
        self.progressSignal.emit(fname, self.chunkDone, self.chunks)

    def workerFinished(self, worker):
        if worker in self.workers:
            self.workers.remove(worker)
        if not self.workers:
            self.stopped = True
            self.finishedSignal.emit(self.errors)
