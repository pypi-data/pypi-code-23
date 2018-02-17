# -*- coding: utf-8 -*-
"""Manager module.

contains PSManager, a subclass of QObject
"""

import json
import os
import shutil
from math import sqrt
from threading import Thread
from time import time, sleep

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from puzzlestream.backend.config import PSConfig
from puzzlestream.backend.stream import PSStream
from puzzlestream.backend.streamsection import PSStreamSection
from puzzlestream.backend import notificationsystem
from puzzlestream.ui.graphicsscene import PSGraphicsScene
from puzzlestream.ui.module import PSModule
from puzzlestream.ui.pipe import PSPipe
from puzzlestream.ui.puzzleitem import PSPuzzleItem
from puzzlestream.ui.valve import PSValve


class PSManager(QtCore.QObject):

    """
    ===========================================================================
        Eventinitialisation
    """

    configChanged = QtCore.pyqtSignal(object)

    """
    ===========================================================================
        Creation and Initialisation
    """

    def __init__(self):
        super().__init__()
        self.__stream, self.__projectPath, self.__libs = None, None, []
        self.__workers, self.__pendingWorkers = {}, []
        self.__scene = PSGraphicsScene()
        self.__scene.installEventFilter(self)
        self.__scene.mousePressed.connect(self.__itemDrag)
        self.__scene.positionChanged.connect(self.__positionChanged)
        self.__scene.mouseReleased.connect(self.__mouseReleased)

        self.addStatus = None
        self.config = PSConfig()
        self.config.edited.connect(self.configChanged.emit)
        self.__dockingrange = 200
        self.__connectionOnDrop = False
        self.__connectionPair = None
        self.__oldCursorPos = QtGui.QCursor.pos()

        self.__workerPollTimer = QtCore.QTimer()
        self.__workerPollTimer.setInterval(10)
        self.__workerPollTimer.timeout.connect(self.__pollWorkers)

    @property
    def projectPath(self):
        return self.__projectPath

    @property
    def scene(self):
        return self.__scene

    @property
    def stream(self):
        return self.__stream

    @property
    def libs(self):
        return self.__libs

    """
    ===========================================================================
        load - save - close
    """

    def close(self):
        self.config.save()
        self.__stream.clear()
        self.__stream.close()

    """
    ===========================================================================
        Handle additional libaries
    """

    def addLib(self, path):
        if path not in self.libs:
            self.__libs.append(path)
            self.save()

    def deleteLib(self, path):
        i = self.__libs.index(path)
        del self.__libs[i]
        self.save()

    """
    ===========================================================================
        Process Management
    """

    def registerWorker(self, ID, worker):
        if ID in self.__workers:
            del self.__workers[ID]
        else:
            self.__pendingWorkers.append((ID, worker))

    def stopAllWorkers(self):
        for w in self.__workers.values():
            w.stop()

        self.__pendingWorkers = []

    def startWorkerPollTimer(self):
        if not self.__workerPollTimer.isActive():
            self.__workerPollTimer.start()

    def __pollWorkers(self):
        nWorkers = self.config["numberOfProcesses"]
        if nWorkers == 0:
            nWorkers = os.cpu_count()

        for w in list(self.__workers.values()):
            w.poll()

        while (len(self.__workers) <= nWorkers and
               len(self.__pendingWorkers) > 0):
            w = self.__pendingWorkers.pop()
            w[1].run()
            self.__workers[w[0]] = w[1]

        if len(self.__workers) == 0:
            self.__workerPollTimer.stop()

    """
    ===========================================================================
        GUI Interaction
    """

    def eventFilter(self, target, event):
        if isinstance(event, QtWidgets.QGraphicsSceneMouseEvent):
            x, y = event.scenePos().x(), event.scenePos().y()

            if (self.addStatus is not None and
                    event.button() == QtCore.Qt.LeftButton):
                if self.addStatus == "intModule":
                    self.newModule(x, y)
                elif self.addStatus == "extModule":
                    path = QtWidgets.QFileDialog.getOpenFileName()
                    if os.path.isfile(path[0]):
                        self.newModule(x, y, path[0])
                elif self.addStatus == "pipe":
                    self.newPipe(x, y)
                elif self.addStatus == "valve":
                    self.newValve(x, y)
                self.addStatus = None
        return QtCore.QObject.eventFilter(self, target, event)

    def checkModulePipeConnectable(self, module, pipe):
        directionPossible = (
            # module -> pipe
            (not module.hasOutput) and (not pipe.hasInput),
            # pipe -> module
            (not module.hasInput) and (not pipe.hasOutput)
        )

        preConnectionDirection = module.calculatePreconnectionDirection(pipe)
        if preConnectionDirection is None:
            return (False, "")

        preConnectPosition = preConnectionDirection[0]
        pref = module.connectionPreference(preConnectPosition)

        if pref == "output":
            if directionPossible[0]:
                return (pipe.preConnect(module), ">")
            elif directionPossible[1]:
                return (module.preConnect(pipe), "<")
            else:
                return (False, "")

        elif pref == "input":
            if directionPossible[1]:
                return (module.preConnect(pipe), "<")
            elif directionPossible[0]:
                return (pipe.preConnect(module), ">")
            else:
                return (False, "")

    def checkPipePipeConnectable(self, pipe1, pipe2):
        if (not pipe1.hasOutput) and (not pipe2.hasInput):
            # pipe1 -> pipe2
            return (pipe2.preConnect(pipe1), ">")
        elif (not pipe1.hasInput) and (not pipe2.hasOutput):
            # pipe2 -> pipe1
            return (pipe1.preConnect(pipe2), "<")
        else:
            return (False, "")

    def checkPipeValveConnectable(self, pipe, valve):
        if pipe.hasInput and pipe.hasOutput:
            return (False, "")
        elif valve.numberOfInputs + valve.numberOfOutputs == 4:
            return (False, "")

        preConnectionDirection = valve.calculatePreconnectionDirection(pipe)
        if preConnectionDirection is None:
            return (False, "")

        elif pipe.hasInput and (not pipe.hasOutput):
            if valve.numberOfInputs < 3:
                # pipe -> valve
                return (valve.preConnect(pipe), ">")
            else:
                return (False, "")

        elif pipe.hasOutput and (not pipe.hasInput):
            if valve.numberOfOutputs < 3:
                # valve -> pipe
                return (pipe.preConnect(valve), "<")
            else:
                return (False, "")
        else:
            preConnectPosition = preConnectionDirection[0]
            pref = valve.connectionPreference(preConnectPosition)
            if pref == "input":
                if valve.numberOfInputs < 3:
                    return (valve.preConnect(pipe), ">")
                else:
                    return (pipe.preConnect(valve), "<")
            elif pref == "output":
                if valve.numberOfOutputs < 3:
                    return (pipe.preConnect(valve), "<")
                else:
                    return (valve.preConnect(pipe), ">")

    def __itemDrag(self, puzzleItem):
        """OnClick of any puzzleitem, save initial Position of selection

        Force the scene to save the position of all selected puzzleitems
        to allow position reset, if there is no valid constellation OnDrop
        """
        self.__oldCursorPos = QtGui.QCursor.pos()
        self.scene.bkSelectedItemPos()
        self.__connectionOnDrop = False
        self.__positionChangeAllowed = False

    def __positionChanged(self, puzzleItem):
        """On movement of puzzleitem, disconnect selection from surrounding and
        prepare reconnect to destination.

        Check if the complete selection is bounded together.
        If the selection is not one block, puzzleitemmovements are restricted.
        Block selections are disconnected from its surroundings and can be
        moved as a free selection block.
        Handling of new connection preparation is done by the
        moveFreeSelectionBlock routine
        """

        self.__connectionOnDrop = False
        if self.scene.selectionIsOneBlock:
            sel = self.scene.selectedItemList
            unsel = self.scene.unselectedItemList
            self.__scene.registerConnectionsToCut()
            connectionsToCut = self.scene.connectionsToCut

            for pair in connectionsToCut:
                pair[1].removeConnection(pair[0])
                self.scene.unregisterConnection(pair[0], pair[1])

            self.__positionChangeAllowed = True
            self.__moveFreeSelectionBlock(puzzleItem)
        else:
            self.__positionChangeAllowed = False

    def __moveFreeSelectionBlock(self, puzzleItem):
        """Move Selection consisting of only unconnected Items and check for
        possible connections to unselected Items.

        1. Calculate the dists of any selected item to any unselected
           item and save those pairs as possible connection canidates
        2. Find the pair of selected and unselected items with
           minimum distance
        3. Check if this distance is smaller than the docking range
           that shall be experienced
                a) distance > dockingrange:
                    - set flag: connectionOnDrop = False
                b) distance < dockingrange:
                    - check if the connection would lead to a valid
                      Puzzle
                        i) connection NOT valid:
                            - delete the pair of items from connection
                                cannidates
                            - go back to step 2
                        ii) connection valid:
                            - Save the right dockingstation for connection
                            - set flag: connectionOnDrop = True
                            - GUI feedback: dockingstation now visible

        """

        sel = self.scene.selectedItemList
        unsel = self.scene.unselectedItemList
        # ---  1. ---#
        if len(unsel) != 0:
            dists = np.empty(
                [len(sel), len(unsel)]
            )
            for i in range(len(sel)):
                for j in range(len(unsel)):
                    dists[i, j] = self.scene.itemDistance(sel[i], unsel[j])

            edgeOutsiders = np.ones(dists.shape)
            edgeOutsiders[dists < self.__dockingrange] = 0
            edgeOutsiders[dists > 1.5 * self.__dockingrange] = 0

            for i in range(len(unsel)):
                if np.count_nonzero(edgeOutsiders[:, i]) > 0:
                    edgeOutsider = unsel[i]
                    if (isinstance(edgeOutsider, PSModule) or
                            isinstance(edgeOutsider, PSValve)):
                        edgeOutsider.hideDocksWithState("disconnected")
                        edgeOutsider.hideDocksWithState("preconnected")

            for i in range(len(sel)):
                edgeOutsider = sel[i]
                if (isinstance(edgeOutsider, PSModule) or
                        isinstance(edgeOutsider, PSValve)):
                    edgeOutsider.hideDocksWithState("disconnected")
                    edgeOutsider.hideDocksWithState("preconnected")

        # ---  2. ---#
            TryAnotherPair = True
            while TryAnotherPair:
                if np.count_nonzero(~np.isnan(dists)) == 0:
                    self.__connectionOnDrop = False
                    TryAnotherPair = False
                else:
                    minPairIndizes = np.unravel_index(
                        np.nanargmin(dists), dists.shape)
                    minDist = dists[minPairIndizes[0], minPairIndizes[1]]
                    if minDist > self.__dockingrange:
                        self.__connectionOnDrop = False
                        TryAnotherPair = False
                    else:
                        minPair = [sel[minPairIndizes[0]],
                                   unsel[minPairIndizes[1]]]
                        # -----------------------------------------------------
                        # Selected Module:
                        # -----------------------------------------------------
                        if isinstance(minPair[0], PSModule):
                            # Connection to pipe worth a check
                            if isinstance(minPair[1], PSPipe):
                                checkresult = self.checkModulePipeConnectable(
                                    minPair[0], minPair[1]
                                )
                                if checkresult[0]:
                                    self.__connectionOnDrop = True
                                    self.__connectionPair = (minPair[0],
                                                             minPair[1],
                                                             checkresult[1])

                            # Connect to Module or Valve impossible
                            else:
                                self.__connectionOnDrop = False

                        # -----------------------------------------------------
                        # Selected Pipe:
                        # -----------------------------------------------------
                        elif isinstance(minPair[0], PSPipe):
                            # Connect to Module worth a check
                            if isinstance(minPair[1], PSModule):
                                checkresult = self.checkModulePipeConnectable(
                                    minPair[1], minPair[0]
                                )
                                if checkresult[0]:
                                    self.__connectionOnDrop = True
                                    self.__connectionPair = (minPair[1],
                                                             minPair[0],
                                                             checkresult[1])
                            # Connect to Pipe worth a check
                            elif isinstance(minPair[1], PSPipe):
                                checkresult = self.checkPipePipeConnectable(
                                    minPair[0], minPair[1]
                                )
                                if checkresult[0]:
                                    self.__connectionOnDrop = True
                                    self.__connectionPair = (minPair[0],
                                                             minPair[1],
                                                             checkresult[1])
                            # Connect to Valve worth a check
                            elif isinstance(minPair[1], PSValve):
                                checkresult = self.checkPipeValveConnectable(
                                    minPair[0], minPair[1]
                                )
                                if checkresult[0]:
                                    self.__connectionOnDrop = True
                                    self.__connectionPair = (minPair[0],
                                                             minPair[1],
                                                             checkresult[1])
                            else:
                                self.__connectionOnDrop = False

                        # -----------------------------------------------------
                        # Selected Valve:
                        # -----------------------------------------------------
                        elif isinstance(minPair[0], PSValve):
                            # Connect to Pipe worth a check
                            if isinstance(minPair[1], PSPipe):
                                checkresult = self.checkPipeValveConnectable(
                                    minPair[1], minPair[0]
                                )
                                if checkresult[0]:
                                    self.__connectionOnDrop = True
                                    self.__connectionPair = (minPair[1],
                                                             minPair[0],
                                                             checkresult[1])
                            # Connection to module or valve impossible
                            else:
                                self.__connectionOnDrop = False
                        # If we find a connection we don't look for another one
                        if self.__connectionOnDrop:
                            TryAnotherPair = False
                        # Exclude entry if there is no possible connection
                        if TryAnotherPair:
                            dists[minPairIndizes[0], minPairIndizes[1]] = None

    def __mouseReleased(self, puzzleItem):
        if QtGui.QCursor.pos() != self.__oldCursorPos:
            sel = self.scene.selectedItemList
            unsel = self.scene.unselectedItemList

            # Check if there are collisions with unselected items that shall
            # not be connected to the selected puzzle items
            # In this case there is no position change allowed
            collisionFlag = False
            for selItem in sel:
                if not collisionFlag:
                    for item in self.scene.collidingItems(selItem):
                        if (isinstance(item, PSPuzzleItem) and
                                not (item in sel)):
                            if self.__connectionOnDrop:
                                if (selItem != self.__connectionPair[0] and
                                        selItem != self.__connectionPair[1]):
                                    collisionFlag = True
                                    break
                            else:
                                collisionFlag = True
                                break
            if collisionFlag:
                self.__positionChangeAllowed = False

            # If there is no acceptable change of position, all positions are
            # reset to the drag position
            if not self.__positionChangeAllowed:
                notificationsystem.newNotification(
                    "You cannot move a selection, \
                    that is not one connected block.")
                self.scene.resetItemPos()
                return False

            # If there is a acceptable change of position,
            # the complete selection has to be moved
            if self.__connectionOnDrop:
                self.scene.bkAllItemPos()

                if self.__connectionPair[2] == "<":
                    self.__connectionPair = (
                        self.__connectionPair[1], self.__connectionPair[0]
                    )

                movementVector = self.__connectionPair[1].establishConnection(
                    self.__connectionPair[0])
                self.scene.registerConnection(self.__connectionPair[0],
                                              self.__connectionPair[1])

                if self.__connectionPair[0] in sel:
                    for item in sel:
                        item.setCenterPos(item.centerPos() - movementVector)
                else:
                    for item in sel:
                        item.setCenterPos(item.centerPos() + movementVector)

                self.__connectionPair, self.__connectionOnDrop = None, False

                # Check for additional valve connections to build data reunion
                for valve in self.scene.valves.values():
                    neighbors = []
                    if valve.topFree:
                        neighbor = self.scene.neighbor(valve, "top")
                        if neighbor is not None:
                            neighbors.append(neighbor)
                    if valve.rightFree:
                        neighbor = self.scene.neighbor(valve, "right")
                        if neighbor is not None:
                            neighbors.append(neighbor)
                    if valve.leftFree:
                        neighbor = self.scene.neighbor(valve, "left")
                        if neighbor is not None:
                            neighbors.append(neighbor)
                    if valve.bottomFree:
                        neighbor = self.scene.neighbor(valve, "bottom")
                        if neighbor is not None:
                            neighbors.append(neighbor)

                    for neighbor in neighbors:
                        if isinstance(neighbor, PSPipe):
                            checkresult = self.checkPipeValveConnectable(
                                neighbor, valve
                            )
                            if checkresult[0]:
                                connPair = (neighbor, valve, checkresult[1])
                                if connPair[2] == "<":
                                    connPair = (connPair[1], connPair[0])

                                connPair[1].establishConnection(connPair[0])

                                self.scene.registerConnection(connPair[0],
                                                              connPair[1])
                self.save()

            elif self.__connectionPair is not None:
                for item in self.__connectionPair[:2]:
                    item.removePreconnects()

            self.scene.bkSelectedItemPos()
            return True
        return True

    def newModule(self, x, y, path=None):
        moduleID = self.scene.getNextID()

        if path is None:
            modPath, name = ".", "Module_" + str(moduleID)
        else:
            modPath, name = os.path.split(os.path.splitext(path)[0])

        module = PSModule(
            moduleID, x, y, modPath, name,
            self.newStreamSection, self.registerWorker,
            self.startWorkerPollTimer, self.libs
        )

        if path is None or os.stat(module.filePath).st_size == 0:
            with open(module.filePath, "w") as f:
                f.write("\ndef main(data):\n\treturn data\n")

        self.scene.addModule(module)

    def newPipe(self, x, y):
        pipe = PSPipe(self.scene.getNextID(), x, y)
        self.scene.addPipe(pipe)

    def newValve(self, x, y):
        valve = PSValve(self.scene.getNextID(), x, y)
        self.scene.addValve(valve)

    def newStreamSection(self, pipeID):
        return PSStreamSection(pipeID, self.__stream)

    def newProject(self, path):
        if self.__stream is not None:
            self.__stream.close()
        self.__stream = PSStream(path + "/pscache")
        self.__projectPath = path
        os.chdir(self.__projectPath)
        self.__scene.clear()
        self.config.addRecentProject(path)
        self.scene.lastID = -1
        self.save()

    def save(self, thread=True):
        if thread:
            thr = Thread(target=self.__savePuzzle, args=(self.__projectPath,))
            thr.start()
        else:
            self.__savePuzzle(self.__projectPath)

    def saveAs(self, path):
        shutil.rmtree(path)
        shutil.copytree(self.__projectPath, path)
        thr = Thread(target=self.__savePuzzle, args=(path,))
        thr.start()

        for module in self.scene.modules.values():
            if module.path == self.__projectPath:
                module.path = path

        self.__projectPath = path
        self.__stream.close()
        self.__stream = PSStream(self.__projectPath + "/pscache")
        self.config.addRecentProject(path)

    def load(self, path):
        if self.__stream is not None:
            self.__stream.close()
        self.__stream = PSStream(path + "/pscache")
        self.__projectPath = path
        os.chdir(self.__projectPath)
        self.__loadPuzzle(self.__projectPath, False)
        self.config.addRecentProject(path)

    def __savePuzzle(self, path):
        self.config.save()

        moduleProps = []
        for moduleID in self.__scene.modules:
            moduleProps.append(self.__scene.modules[moduleID].saveProperties)

        pipeProps = []
        for pipeID in self.__scene.pipes:
            pipeProps.append(self.__scene.pipes[pipeID].saveProperties)

        valveProps = []
        for valveID in self.__scene.valves:
            valveProps.append(self.__scene.valves[valveID].saveProperties)

        with open(path + "/puzzle.json", "w") as f:
            json.dump({"modules": moduleProps, "pipes": pipeProps,
                       "valves": valveProps, "lastID": self.__scene.lastID,
                       "libs": self.libs}, f)

    def __loadPuzzle(self, path, clearStream=True):
        if clearStream:
            self.__stream.clear()
        with open(path + "/puzzle.json", "r") as f:
            puzzle = json.load(f)

        self.__scene.lastID = puzzle["lastID"]
        self.__libs = puzzle["libs"]

        self.__scene.clear()
        pipes = []
        for props in puzzle["pipes"]:
            pipe = PSPipe(props["id"], props["x"], props["y"],
                          props["orientation"])
            pipe.restoreProperties(props, self.__stream)
            pipes.append(pipe)
            self.__scene.addPipe(pipe)

        for props in puzzle["valves"]:
            valve = PSValve(props["id"], props["x"], props["y"])
            inPipeIDs = props["inPipeIDs"]
            self.__scene.addValve(valve)

            for i in inPipeIDs:
                pipe = self.__scene.pipes[i]
                valve.preConnect(pipe)
                valve.establishConnection(pipe, silent=True)
                self.scene.registerConnection(pipe, valve)

            valve.restoreProperties(props, self.__stream)

        for props in puzzle["modules"]:
            module = PSModule(props["id"], props["x"], props["y"],
                              props["path"], props["name"],
                              self.newStreamSection, self.registerWorker,
                              self.startWorkerPollTimer, self.__libs)

            self.__scene.addModule(module)

            if "inPipeID" in props:
                pipe = self.__scene.pipes[props["inPipeID"]]
                module.preConnect(pipe)
                module.establishConnection(pipe, silent=True)
                self.scene.registerConnection(pipe, module)

            module.restoreProperties(props, self.__stream)

        for i in range(len(pipes)):
            props = puzzle["pipes"][i]
            if "inItemID" in props:
                if props["inItemID"] in self.__scene.pipes:
                    inItem = self.__scene.pipes[props["inItemID"]]
                elif props["inItemID"] in self.__scene.modules:
                    inItem = self.__scene.modules[props["inItemID"]]
                else:
                    inItem = self.__scene.valves[props["inItemID"]]

                pipes[i].preConnect(inItem)
                pipes[i].establishConnection(inItem, silent=True)
                self.scene.registerConnection(inItem, pipes[i])
