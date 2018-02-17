# -*- coding: utf-8 -*-
"""Puzzle Stream module module.

contains PSModule, a subclass of PSPuzzleDockItem
"""

import os
from time import time

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QBrush, QColor, QPen

from puzzlestream.ui.puzzledockitem import PSPuzzleDockItem

from puzzlestream.backend.signal import PSSignal
from puzzlestream.backend.worker import PSWorker
from puzzlestream.ui.moduleheader import PSModuleHeader
from puzzlestream.ui.modulestatusbar import PSModuleStatusbar
from puzzlestream.ui.modulewidget import PSModuleWidget
from puzzlestream.ui import colors


class PSModule(PSPuzzleDockItem):

    def __init__(self, moduleID, x, y, path, name,
                 streamSectionSupplier, workerRegistrationFunction,
                 startTimerFunction, libs):
        """
        =======================================================================
            Object Initialisation and GUI Appearence
        """
        # Full PSModule geometry (header and statusbar inclusive)
        self._width = 150
        self._height = 150

        # PuzzleDockItem -> PuzzleItem -> QGraphicsItem
        super().__init__(moduleID)

        # Detailed geometry
        self.__headerDepth = 20
        self.__statusbarDepth = 20
        self.__widgetDepth = (
            self._height - self.__headerDepth - self.__statusbarDepth
        )
        self._radius = self._width / 2 + self._dockHeight

        """
        =======================================================================
            Initialisation of backendstructure
        """
        self.__inputPipe = None
        self.hasOutput = False
        self.__path, self.__name = path, name
        self.__newStreamSection = streamSectionSupplier
        self.__libs = libs
        self.__inittime, self.__runtime, self.__savetime = 0, 0, 0
        self.__testResults = {}

        self.__stdout = ""
        self.__status = "incomplete"
        self.__errorMessage = ""

        self.__pathChanged = PSSignal()
        self.__nameChanged = PSSignal()
        self.__stdoutChanged = PSSignal()
        self.__progressChanged = PSSignal()

        self.__worker = PSWorker(workerRegistrationFunction,
                                 startTimerFunction)
        self.worker.finished.connect(self.__finish)
        self.worker.newStdout.connect(self.addStdout)
        self.worker.progressUpdate.connect(self.updateProgress)

        """
        =======================================================================
            Initialise GUI module components:
                - Colored Header
                - Centralwidget with module name, run- and stop-button
                - Colored footer with statusbar
                - Docking slots for pipeline connection
        """

        # Header
        self.__header = PSModuleHeader(
            0, 0,
            self._width, self.__headerDepth,
            colors.get("standard-blue"), parent=self
        )

        self.__widget = PSModuleWidget(
            1, 0 + self.__headerDepth,
            self._width - 2,
            self._height - self.__headerDepth - self.__statusbarDepth,
            self.name, parent=self
        )

        def _nameChanged(name):
            self.name = name
        self.__widget.nameEdit.nameChanged.connect(_nameChanged)

        self.__widget.setPlayPauseButtonAction(self.__playPauseClicked)
        self.__widget.setStopButtonAction(self.__stopClicked)
        self.statusChanged.connect(self.__widget.updateIcons)

        self.__statusbar = PSModuleStatusbar(
            0,
            0 + self.__headerDepth + self.__widgetDepth,
            self._width, self.__statusbarDepth,
            colors.get("standard-blue"), parent=self
        )

        self.__statusbar.text = self.status

        self.setCenterPos(QtCore.QPointF(x, y))

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __getstate__(self):
        return (self.id, self.centerPos().x(), self.centerPos().y(), self.path,
                self.name, self.__newStreamSection, self.__libs)

    def __setstate__(self, state):
        self.__id, self.__path, self.__name = state[0], state[3], state[4]
        self.__newStreamSection, self.__libs = state[5], state[6]
        self.setPos(state[1], state[2])

    @property
    def saveProperties(self):
        props = {"name": self.name,
                 "path": self.path,
                 "stdout": self.stdout,
                 "errorMessage": self.errorMessage,
                 "inittime": self.inittime,
                 "runtime": self.runtime,
                 "savetime": self.savetime,
                 "testResults": self.testResults
                 }
        props.update(super().saveProperties)

        if self.__inputPipe is not None:
            props["inPipeID"] = self.__inputPipe.id

        return props

    def restoreProperties(self, props, stream):
        super().restoreProperties(props, stream)
        if "stdout" in props:
            self.__stdout = props["stdout"]
        if "errorMessage" in props:
            self.__errorMessage = props["errorMessage"]
        if "inittime" in props:
            self.__inittime = props["inittime"]
        if "runtime" in props:
            self.__runtime = props["runtime"]
        if "testResults" in props:
            self.__testResults = props["testResults"]
        if "savetime" in props:
            self.__savetime = props["savetime"]

    @property
    def __shift(self):
        return QtCore.QPointF(self._width / 2, self._height / 2)

    @property
    def hasInput(self):
        return self.__inputPipe is not None

    def centerPos(self):
        return self.pos() + self.__shift

    def setCenterPos(self, point):
        self.setPos(point - self.__shift)

    def __playPauseClicked(self):
        if self.status == "running":
            self.pause()
        elif self.status == "paused":
            self.resume()
        else:
            self.run()

    def __stopClicked(self):
        self.stop()

    def visualStatusUpdate(self, module):
        if module == self:
            if self.status == "error":
                color = colors.get("error")
            elif self.status == "test failed":
                color = colors.get("test-failed")
            elif self.status == "running":
                color = colors.get("running")
            elif self.status == "paused":
                color = colors.get("paused")
            else:
                color = colors.get("standard-blue")

            self.__header.bgColor = color
            self.__statusbar.bgColor = color
            self.__statusbar.text = self.status

    """
        properties
    """

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        self.__path = path
        self.pathChanged.emit()

    @property
    def filePath(self):
        return self.__path + "/" + self.__name + ".py"

    @filePath.setter
    def filePath(self, path):
        basepath, name = os.path.split(path)

        if name[-3:] == ".py":
            name = name[:-3]
            os.rename(self.filePath, path)
            self.__name = name
            self.__widget.nameEdit.setText(name)
            self.nameChanged.emit(self)
            self.path = basepath

    def outsource(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName()

        if path != "":
            self.filePath = path

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        os.rename(self.filePath, self.path + "/" + name + ".py")
        self.__name = name
        self.nameChanged.emit(self)

    @property
    def worker(self):
        return self.__worker

    @property
    def stdout(self):
        return self.__stdout

    def resetStdout(self):
        self.__stdout = ""
        self.stdoutChanged.emit(self, None)

    def addStdout(self, value):
        self.__stdout += value
        self.stdoutChanged.emit(self, value)

    @property
    def errorMessage(self):
        return self.__errorMessage

    @property
    def progress(self):
        return self.__progress

    def updateProgress(self, value):
        self.__progress = value
        self.__widget.progressBar.show()
        self.__widget.progressBar.setValue(int(round(value * 100)))
        self.progressChanged.emit(self)

    @property
    def inittime(self):
        return self.__inittime

    @property
    def inittimeHHMMSS(self):
        m, s = divmod(self.__inittime, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d.%003d" % (h, m, s, self.__inittime * 1000)

    @property
    def runtime(self):
        return self.__runtime

    @property
    def runtimeHHMMSS(self):
        m, s = divmod(self.__runtime, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d.%003d" % (h, m, s, self.__runtime * 1000)

    @property
    def savetime(self):
        return self.__savetime

    @property
    def savetimeHHMMSS(self):
        m, s = divmod(self.__savetime, 60)
        h, m = divmod(m, 60)
        return "%02d:%02d:%02d.%003d" % (h, m, s, self.__savetime * 1000)

    @property
    def testResults(self):
        return self.__testResults

    @property
    def statistics(self):
        text = "Run time: %s<br>" % (self.runtimeHHMMSS)
        text += "Save time: %d ms<br><br>" % (self.savetime * 1000)

        if len(self.testResults) > 0:
            text += "Test report:<br>"

            for test in sorted(self.testResults):
                text += test + ": "
                if self.testResults[test]:
                    text += "<font color=\"green\">SUCCESSFULL</font><br>"
                else:
                    text += "<font color=\"red\">FAILED</font><br>"
        return text

    @property
    def pathChanged(self):
        return self.__pathChanged

    @property
    def nameChanged(self):
        return self.__nameChanged

    @property
    def stdoutChanged(self):
        return self.__stdoutChanged

    @property
    def progressChanged(self):
        return self.__progressChanged

    @property
    def header(self):
        return self.__header
    """
        Connection stuff
    """

    @property
    def inputPipe(self):
        return self.__inputPipe

    @property
    def inputItems(self):
        if self.__inputPipe is None:
            return []
        return [self.__inputPipe]

    def establishConnection(self, otherItem, silent=False):
        self.__setInputPipe(otherItem)
        return super().establishConnection(otherItem)

    def removeConnection(self, otherItem):
        self.__disconnectInputPipe()
        super().removeConnection(otherItem)

    def __setInputPipe(self, pipe):
        self.__inputPipe = pipe
        self.__inputPipe.statusChanged.connect(self.inputUpdate)
        self.__inputPipe.hasOutput = True

    def __disconnectInputPipe(self):
        self.__inputPipe.statusChanged.disconnect(self.inputUpdate)
        self.__inputPipe.hasOutput = False
        self.__inputPipe = None

    """
    ===========================================================================
        Execution routines
    """

    def inputUpdate(self, pipe):
        if pipe.status == "finished" and not pipe.stopHere:
            self.run()

    def run(self, stopHere=False):
        if (self.status != "running" and self.status != "paused"):
            self.stopHere = stopHere

            self.resetStdout()

            t0 = time()
            if not self.hasInput or self.__inputPipe.streamSection is None:
                self.streamSection = self.__newStreamSection(self.id)
                lastID = None
            else:
                self.streamSection = self.__inputPipe.streamSection.copy(
                    self.id)
                lastID = self.__inputPipe.id
            self.__inittime = time() - t0

            self.worker.setName(self.name)
            self.worker.setPath(self.filePath)
            self.worker.setLibs(self.__libs)
            self.worker.enqueue(self.streamSection, self.id, lastID)
            self.status = "running"

    def pause(self):
        if self.status == "running":
            if self.worker.pause():
                self.status = "paused"

    def resume(self):
        if self.status == "paused":
            if self.worker.resume():
                self.status = "running"

    def stop(self):
        if self.status == "running" or self.status == "paused":
            if self.status == "paused":
                self.worker.resume()
            if self.worker.stop():
                self.status = "incomplete"

    def __finish(self, success, log, out, times, testResults):
        self.__runtime, self.__savetime = times
        self.__testResults = testResults
        self.streamSection.changelog.update(log)

        if False in testResults.values():
            self.status = "test failed"
        elif success:
            self.status = "finished"
        else:
            self.__errorMessage = out
            self.addStdout(out + "\n")
            self.status = "error"
