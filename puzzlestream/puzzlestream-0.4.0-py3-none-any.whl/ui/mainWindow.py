# -*- coding: utf-8 -*-
"""Main window module.

contains PSMainWindow, a subclass of QMainWindow
"""

import os
import shutil
import subprocess
import sys
import time

import psutil
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu

from puzzlestream.ui.about import PSAboutWindow
from puzzlestream.ui.dataview import PSDataView
from puzzlestream.ui.mainWindowUi_02 import Ui_MainWindow
from puzzlestream.ui.manager import PSManager
from puzzlestream.ui.module import PSModule
from puzzlestream.ui.pipe import PSPipe
from puzzlestream.ui.plotview import PSPlotView
from puzzlestream.ui.preferences import PSPreferencesWindow
from puzzlestream.ui.codeeditor import PSCodeEdit
from puzzlestream.ui.notificationtab import PSNotificationTab
from puzzlestream.ui.editorwidget import PSEditorWidget
from puzzlestream.backend import notificationsystem
from puzzlestream.ui import colors


class PSMainWindow(QtWidgets.QMainWindow):

    __newProjectText = "Welcome to Puzzle Stream!\nPlease create a new project folder using File -> New Project\nor open an existing project."
    __projectOpenText = "Add a new module or select an existing one to edit its source code."
    __newItemText = "Click left on the scrollable puzzle region to add a "

    def __init__(self):

        super().__init__()

        self.__manager = PSManager()
        self.__manager.configChanged.connect(self.__configChanged)
        self.__manager.scene.nameChanged.connect(self.__nameChanged)
        self.__manager.scene.itemDeleted.connect(self.__itemDeleted)

        self.__designerUI = Ui_MainWindow()
        self.__designerUI.setupUi(self)
        self.__designerUI.puzzleGraphicsView.setScene(self.__manager.scene)
        self.__designerUI.puzzleGraphicsView.setConfig(self.__manager.config)

        currentDir = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(
            os.path.join(currentDir, "../icons//PuzzleStream.png")))

        # editor initialisation
        w = self.__newEditorWidget()
        self.__editorWidgets = [w]
        self.__editors = [w.editor]
        self.__designerUI.horizontalSplitter.insertWidget(0, w)
        self.btnOpenCloseSecondEditor = QtWidgets.QPushButton("+", self)
        self.__editorWidgets[0].editorHeaderLayout.addWidget(
            self.btnOpenCloseSecondEditor)
        self.btnOpenCloseSecondEditor.setFixedWidth(25)
        self.btnOpenCloseSecondEditor.setToolTip("Open second editor")
        self.btnOpenCloseSecondEditor.pressed.connect(
            lambda: self.changeRightWidgetMode("editor"))
        self.__rightWidget = self.__designerUI.verticalSplitter
        self.__rightWidgetMode = "puzzle"

        # add active module run / pause / stop
        self.btnRunPauseActive = QtWidgets.QToolButton()
        self.btnRunPauseActive.setToolTip("Run current module")
        self.btnRunPauseActive.pressed.connect(self.__runPauseActiveModuleOnly)
        self.btnStopActive = QtWidgets.QToolButton()
        self.btnStopActive.setToolTip("Stop current module")
        self.btnStopActive.pressed.connect(self.__stopActiveModule)
        w.editorHeaderLayout.insertWidget(0, self.btnRunPauseActive)
        w.editorHeaderLayout.insertWidget(1, self.btnStopActive)

        # pre-add second editor for windows performance reasons
        w = self.__newEditorWidget()
        self.__editorWidgets.append(w)
        self.__editors.append(w.editor)

        # module switcher
        self.__connectSwitcher()

        # welcome screen
        self.__welcomeLabel = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.__welcomeLabel.setFont(font)
        self.__welcomeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.__designerUI.horizontalSplitter.insertWidget(
            0, self.__welcomeLabel)

        # toolbar
        self.__createToolBarActions()
        actionList = self.__getToolbarActions()
        for action in actionList:
            self.__designerUI.toolBar.addAction(action)

        self.__designerUI.toolBar.setMovable(False)
        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                             QtWidgets.QSizePolicy.Preferred)
        self.__designerUI.toolBar.insertSeparator(actionList[2])
        self.__designerUI.toolBar.insertSeparator(actionList[7])
        self.__designerUI.toolBar.insertWidget(actionList[-3], spacer)

        self.__designerUI.horizontalSplitter.setStretchFactor(0, 6)
        self.__designerUI.horizontalSplitter.setStretchFactor(1, 6)
        self.__designerUI.horizontalSplitter.setStretchFactor(2, 8)
        self.__designerUI.horizontalSplitter.setCollapsible(0, True)
        self.__designerUI.horizontalSplitter.setCollapsible(1, True)

        self.__designerUI.verticalSplitter.setStretchFactor(0, 120)
        self.__designerUI.verticalSplitter.setStretchFactor(1, 0)
        self.__designerUI.verticalSplitter.setCollapsible(1, True)

        # create puzzle toolbar actions
        self.__createPuzzleToolBarActions()
        for action in self.__getPuzzleToolbarActions():
            self.__designerUI.puzzleToolbar.addAction(action)

        self.__btnAddStatusAbort = QtWidgets.QPushButton(
            "Abort", self.__designerUI.toolBar)
        self.__btnAddStatusAbort.pressed.connect(self.__abortAdding)
        self.__btnAddStatusAction = self.__designerUI.puzzleToolbar.addWidget(
            self.__btnAddStatusAbort)
        self.__btnAddStatusAction.setVisible(False)
        self.__puzzleLabel = QtWidgets.QLabel(self.__designerUI.puzzleToolbar)
        self.__designerUI.puzzleToolbar.addWidget(self.__puzzleLabel)

        # create menu bar
        self.__createFileMenuActions()
        self.__createEditMenuActions()
        self.__createViewMenuActions()
        self.__createStreamMenuActions()
        self.__createHelpMenuActions()

        # create graphics scene
        self.__createGraphicsScene()

        # set active module to None
        self.__resetActiveModule()

        # set style
        self.__currentStyle = None
        design = self.__manager.config["design"]
        self.__setStyle(design[1][design[0]])

        # shortcuts
        self.__shortcuts = {}
        self.addShortcut("F5", self.__runPauseActiveModuleOnly)
        self.addShortcut("Alt+F5", self.__runPauseActiveModule)
        self.addShortcut("Ctrl+F5", self.__run)
        self.addShortcut("F11", self.__toggleFullscreen)
        self.addShortcut("Ctrl+s", self.__saveOpenFiles)
        self.addShortcut("Esc", self.__abortAdding)

        # notifications
        self.__notificationTab = PSNotificationTab(
            self.__designerUI.outputTabWidget)
        self.__designerUI.outputTabWidget.addTab(self.__notificationTab,
                                                 "Notifications (0)")
        notificationsystem.addReactionMethod(
            self.__notificationTab.addNotification)
        self.__notificationTab.setNumberUpdateMethod(
            self.__updateNotificationHeader)

        # collect elements that should be activated and deactivated
        self.__activeElements = [
            self.__designerUI.puzzleGraphicsView, self.__newModuleMenu,
            self.__newPipeAction, self.__newValveAction, self.__undoAction,
            self.__redoAction, self.__copyAction, self.__cutAction,
            self.__pasteAction, self.__runAction, self.__pauseAction,
            self.__stopAction
        ]

        """
        =======================================================================
            Show window
        """

        self.resize(1200, 800)
        self.showMaximized()
        self.__lastWindowState = "maximized"

        """
        =======================================================================
            Try to load last project
        """

        if len(self.__manager.config["last projects"]) > 0:
            path = self.__manager.config["last projects"][-1]
            if os.path.isdir(path) and os.path.isfile(path + "/puzzle.json"):
                self.__openProject(path, start=True)
            else:
                self.__deactivate()
        else:
            self.__deactivate()

        self.__createLibMenuActions()

        """
        =======================================================================
            Timer for CPU and RAM update
        """

        self.__loadViewer = QtWidgets.QLabel(self.__designerUI.statusbar)
        self.__designerUI.statusbar.addPermanentWidget(self.__loadViewer)
        self.__loadTimer = QtCore.QTimer(self)
        self.__loadTimer.setInterval(3000)
        self.__loadTimer.timeout.connect(self.__updateLoad)
        self.__updateLoad()
        self.__loadTimer.start()

    def __setStyle(self, style):
        self.__currentStyle = style
        currentDir = os.path.dirname(__file__)
        colors.update(os.path.join(currentDir, "style/" + style + ".yml"))
        self.setStyleSheet(
            colors.parseQSS(currentDir + "/style/sheet.qss"))
        for e in self.__editors:
            e.setSyntaxColorScheme(style)

        if style == "dark":
            self.__openProjectAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//folder_white.png")))
            self.__saveFileAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//save_blue_in.png")))
            self.__undoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//back_white.png")))
            self.__redoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//forward_white.png")))
            self.__copyAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//copy_blue_in.png")))
            self.__cutAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//cut_blue_in.png")))
            self.__pasteAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//paste_blue_in.png")))
            self.__runAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/play_blue_in.png")))
            self.__pauseAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/pause_blue_in.png")))
            self.__stopAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_in.png")))
            self.btnStopActive.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_in.png")))
        elif style == "light":
            self.__openProjectAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//folder_blue.png")))
            self.__saveFileAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//save_blue_out.png")))
            self.__undoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//back_blue.png")))
            self.__redoAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//forward_blue.png")))
            self.__copyAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//copy_blue_out.png")))
            self.__cutAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//cut_blue_out.png")))
            self.__pasteAction.setIcon(
                QIcon(os.path.join(currentDir,
                                   "../icons//paste_blue_out.png")))
            self.__runAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/play_blue_out.png")))
            self.__pauseAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons/pause_blue_out.png")))
            self.__stopAction.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_out.png")))
            self.btnStopActive.setIcon(
                QIcon(os.path.join(currentDir, "../icons//stop_blue_out.png")))

        self.updateActiveModuleButtons()

    def __saveOpenFiles(self):
        for e in self.__editors:
            e.file.save()

    def __closeOpenFiles(self):
        for e in self.__editors:
            e.file.close()

    def __stopAllEditors(self):
        for e in self.__editors:
            e.backend.stop()

    def __newEditorWidget(self):
        e = PSEditorWidget()
        design = self.__manager.config["design"]
        e.editor.setSyntaxColorScheme(design[1][design[0]])

        # editor settings
        e.editor.save_on_focus_out = self.__manager.config[
            "saveOnEditorFocusOut"]
        e.editor.replace_tabs_by_spaces = True
        e.editor.dirty_changed.connect(self.__fileDirty)
        e.editor.textChanged.connect(
            lambda: self.__editorTextChanged(e.editor))
        return e

    def openPuzzle(self):
        self.__designerUI.verticalSplitter.show()
        self.__enableAddActions()
        self.__rightWidget = self.__designerUI.verticalSplitter

    def closePuzzle(self):
        self.__designerUI.verticalSplitter.hide()
        self.__disableAddActions()
        self.__rightWidget = None

    def openSecondEditor(self, oldMode="puzzle"):
        w = self.__editorWidgets[1]
        self.__designerUI.horizontalSplitter.insertWidget(2, w)
        i = self.__designerUI.horizontalSplitter.indexOf(
            self.__designerUI.verticalSplitter)
        self.__updateModuleSwitchers()
        self.__updateEditorModule(self.__activeModule, 1)
        self.__connectSwitcher(1)
        self.btnOpenCloseSecondEditor.setText("-")
        self.btnOpenCloseSecondEditor.pressed.disconnect()
        self.btnOpenCloseSecondEditor.setToolTip("Close second editor")
        self.btnOpenCloseSecondEditor.pressed.connect(
            lambda: self.changeRightWidgetMode(oldMode))
        self.__rightWidget = w
        self.__rightWidgetMode = "editor"
        self.__rightWidget.show()

    def closeSecondEditor(self):
        w = self.__editorWidgets[1]
        w.editor.file.save()
        w.hide()
        w.setParent(None)
        self.btnOpenCloseSecondEditor.setText("+")
        self.btnOpenCloseSecondEditor.pressed.disconnect()
        self.btnOpenCloseSecondEditor.setToolTip("Open second editor")
        self.btnOpenCloseSecondEditor.pressed.connect(
            lambda: self.changeRightWidgetMode("editor"))
        self.__rightWidget = None

    def openDataview(self):
        w = PSDataView(self.__manager, self.__activeModule, self)
        self.__manager.scene.statusChanged.connect(w.statusUpdate)
        self.__designerUI.horizontalSplitter.insertWidget(2, w)
        self.__rightWidget = w
        self.__rightWidgetMode = "dataview"

    def closeDataview(self):
        self.__rightWidget.hide()
        self.__rightWidget.setParent(None)
        self.__rightWidget = None

    def openPlotview(self):
        w = PSPlotView(self.__manager, self.__activeModule, self)
        self.__manager.scene.statusChanged.connect(w.statusUpdate)
        self.__designerUI.horizontalSplitter.insertWidget(2, w)
        self.__rightWidget = w
        self.__rightWidgetMode = "dataview"

    def closePlotview(self):
        self.__rightWidget.hide()
        self.__rightWidget.setParent(None)
        self.__rightWidget = None

    def changeRightWidgetMode(self, mode):
        if mode != self.__rightWidgetMode:
            self.__manager.addStatus = None
            self.__puzzleLabel.setText("")
            self.__btnAddStatusAction.setVisible(False)
            s = self.__designerUI.horizontalSplitter.sizes()

            # close old mode
            if self.__rightWidgetMode == "editor":
                self.closeSecondEditor()
            elif self.__rightWidgetMode == "puzzle":
                self.closePuzzle()
            elif self.__rightWidgetMode == "dataview":
                self.closeDataview()
            elif self.__rightWidgetMode == "plotview":
                self.closePlotview()

            # choose new mode
            if mode == "editor":
                self.openSecondEditor(self.__rightWidgetMode)
            elif mode == "puzzle":
                self.openPuzzle()
            elif mode == "dataview":
                self.openDataview()
            elif mode == "plotview":
                self.openPlotview()

            self.__rightWidgetMode = mode

            # restore sizes
            if len(self.__designerUI.horizontalSplitter.sizes()) == 3:
                self.__designerUI.horizontalSplitter.setSizes(
                    [0, s[1], sum(s) - s[1]])
            else:
                self.__designerUI.horizontalSplitter.setSizes(
                    [0, s[1], sum(s) - s[1], 0])

    def __editorTextChanged(self, editor):
        if editor.hasFocus():
            for e in self.__editors:
                if e != editor and e.file.path == editor.file.path:
                    e.setPlainText(editor.toPlainText())

    def closeEvent(self, event):
        if self.__manager.projectPath is not None:
            self.__manager.stopAllWorkers()
            self.__manager.save(thread=False)
            self.__manager.stream.close()

        self.__saveOpenFiles()
        self.__closeOpenFiles()
        self.__stopAllEditors()
        event.accept()

    def __resetUI(self, path):
        self.__editorWidgets[0].hide()
        self.__designerUI.outputTextEdit.setText("")
        self.__designerUI.statisticsTextEdit.setText("")

    def __createGraphicsScene(self):
        scene = self.__manager.scene
        scene.stdoutChanged.connect(self.updateText)
        scene.statusChanged.connect(self.updateStatus)
        scene.itemAdded.connect(self.__itemAdded)
        scene.dataViewRequested.connect(self.__showData)
        scene.plotViewRequested.connect(self.__showPlots)
        scene.selectionChanged.connect(self.__selectionChanged)

        menu = QMenu()
        newModuleMenu = menu.addMenu("New module")
        newInternalModuleAction = newModuleMenu.addAction(
            "New internal module")
        newExternalModuleAction = newModuleMenu.addAction(
            "New external module")
        newPipeAction = menu.addAction("New pipe")
        newValveAction = menu.addAction("New valve")

        newModuleMenu.menuAction().triggered.connect(self.__newIntModule)
        newInternalModuleAction.triggered.connect(self.__newIntModule)
        newExternalModuleAction.triggered.connect(self.__newExtModule)
        newPipeAction.triggered.connect(self.__newPipe)
        newValveAction.triggered.connect(self.__newValve)

        scene.setStandardContextMenu(menu)
        return scene

    def addShortcut(self, sequence, target):
        sc = QtWidgets.QShortcut(QtGui.QKeySequence(sequence), self)
        sc.activated.connect(target)
        self.__shortcuts[sequence] = sc

    def __selectionChanged(self):
        if len(self.__manager.scene.selectedItemList) == 1:
            puzzleItem = self.__manager.scene.selectedItemList[0]
            if isinstance(puzzleItem, PSModule):
                self.__updateActiveModule(puzzleItem)

    def __updateActiveModule(self, module):
        self.__updateEditorModule(module)
        self.__activeModule = module
        self.__designerUI.outputTextEdit.setText(module.stdout)
        cursor = self.__designerUI.outputTextEdit.textCursor()
        cursor.movePosition(cursor.End)
        self.__designerUI.outputTextEdit.setTextCursor(cursor)
        self.__designerUI.outputTextEdit.ensureCursorVisible()
        self.__designerUI.outputTextEdit.setFontFamily("monospace")
        self.__designerUI.statisticsTextEdit.setHtml(module.statistics)
        self.__designerUI.outputTabWidget.setTabText(
            0, "Output - " + module.name)
        self.__welcomeLabel.hide()
        self.__editorWidgets[0].show()
        self.updateActiveModuleButtons()
        for a in [self.plotviewMenuAction, self.dataviewMenuAction,
                  self.__plotViewAction, self.__dataViewAction]:
            a.setEnabled(True)

    def __updateEditorModule(self, module, i=0):
        self.__disconnectSwitcher(i)
        self.__editors[i].file.open(module.filePath)
        self.__editorWidgets[i].editorFilePathLabel.setText(
            module.filePath)
        self.__editorWidgets[i].moduleSwitcher.setCurrentText(
            module.name)
        self.__connectSwitcher(i)

    def __connectSwitcher(self, i=0):
        e = self.__editorWidgets[i]
        if not e.currentIndexChangedConnected:
            e.moduleSwitcher.currentIndexChanged.connect(
                lambda index: self.__moduleSwitcherIndexChanged(i, index))
            e.currentIndexChangedConnected = True

    def __disconnectSwitcher(self, i=0):
        e = self.__editorWidgets[i]
        if e.currentIndexChangedConnected:
            e.moduleSwitcher.currentIndexChanged.disconnect()
            e.currentIndexChangedConnected = False

    def __updateModuleSwitchers(self):
        for i in range(len(self.__editorWidgets)):
            switcher = self.__editorWidgets[i].moduleSwitcher
            oldText = switcher.currentText()
            self.__disconnectSwitcher(i)
            switcher.clear()
            names = sorted(
                [m.name for m in self.__manager.scene.modules.values()])
            switcher.addItems(names)
            if oldText in names:
                switcher.setCurrentText(oldText)
            self.__connectSwitcher(i)

    def __moduleSwitcherIndexChanged(self, sw, index):
        for m in self.__manager.scene.modules.values():
            if m.name == self.__editorWidgets[sw].moduleSwitcher.currentText():
                if sw == 0:
                    self.__updateActiveModule(m)
                else:
                    self.__updateEditorModule(m, sw)
                break

    def __runPauseActiveModule(self, stopHere=False):
        if self.__activeModule is not None:
            if self.__manager.config["saveOnRun"]:
                self.__saveOpenFiles()

            if (self.__activeModule.status in
                    ["incomplete", "finished", "error"]):
                self.__activeModule.run(stopHere=stopHere)
            elif self.__activeModule.status == "paused":
                self.__activeModule.resume()
            elif self.__activeModule.status == "running":
                self.__activeModule.pause()

    def __runPauseActiveModuleOnly(self):
        self.__runPauseActiveModule(stopHere=True)

    def __stopActiveModule(self):
        self.__activeModule.stop()

    def __nameChanged(self, module):
        if module == self.__activeModule:
            self.__updateActiveModule(module)

    def __fileDirty(self, dirty):
        self.__saveFileAction.setEnabled(dirty)

    def __createFileMenuActions(self):
        newProjectAction = self.__designerUI.menuFile.addAction("&New project")
        openProjectAction = self.__designerUI.menuFile.addAction(
            "&Open project")
        saveprojectAsAction = self.__designerUI.menuFile.addAction(
            "&Save project as...")

        newProjectAction.triggered.connect(self.__newProject)
        openProjectAction.triggered.connect(self.__openProject)
        saveprojectAsAction.triggered.connect(self.__saveProjectAs)

        self.__recentProjectsMenu = QtWidgets.QMenu("Recent projects")
        self.__designerUI.menuFile.insertMenu(saveprojectAsAction,
                                              self.__recentProjectsMenu)

    def __createEditMenuActions(self):
        undoAction = self.__designerUI.menuEdit.addAction("&Undo")
        redoAction = self.__designerUI.menuEdit.addAction("&Redo")
        undoRedoSeparator = self.__designerUI.menuEdit.addSeparator()
        cutAction = self.__designerUI.menuEdit.addAction("&Cut")
        copyAction = self.__designerUI.menuEdit.addAction("&Copy")
        pasteAction = self.__designerUI.menuEdit.addAction("&Paste")
        cutCopyPasteSeparator = self.__designerUI.menuEdit.addSeparator()
        preferencesAction = self.__designerUI.menuEdit.addAction(
            "Pre&ferences")

        undoAction.triggered.connect(self.__editors[0].undo)
        redoAction.triggered.connect(self.__editors[0].redo)
        cutAction.triggered.connect(self.__editors[0].cut)
        copyAction.triggered.connect(self.__editors[0].copy)
        pasteAction.triggered.connect(self.__editors[0].paste)
        preferencesAction.triggered.connect(self.__showPreferences)

    def __createViewMenuActions(self):
        puzzleviewMenuAction = self.__designerUI.menuView.addAction(
            "Puzzle mode")
        puzzleviewMenuAction.triggered.connect(
            lambda: self.changeRightWidgetMode("puzzle"))
        self.dataviewMenuAction = self.__designerUI.menuView.addAction(
            "Data view mode")
        self.dataviewMenuAction.triggered.connect(
            lambda: self.changeRightWidgetMode("dataview"))
        self.plotviewMenuAction = self.__designerUI.menuView.addAction(
            "Plot view mode")
        self.plotviewMenuAction.triggered.connect(
            lambda: self.changeRightWidgetMode("plotview"))
        fullscreenAction = self.__designerUI.menuView.addAction(
            "&Toggle fullscreen")
        fullscreenAction.triggered.connect(self.__toggleFullscreen)

    def __createLibMenuActions(self):
        self.__designerUI.menuLib.clear()
        self.__addLibAction = self.__designerUI.menuLib.addAction(
            "Add lib path")
        self.__libSeparator = self.__designerUI.menuLib.addSeparator()
        self.__addLibAction.triggered.connect(self.__addLib)

        for path in self.__manager.libs:
            menu = self.__designerUI.menuLib.addMenu(path)
            openAction = menu.addAction("Open folder")
            openAction.triggered.connect(lambda: self.__open_file(path))
            deleteAction = menu.addAction("Delete")
            deleteAction.triggered.connect(lambda: self.__deleteLib(path))

    def __createStreamMenuActions(self):
        dataAction = self.__designerUI.menuStream.addAction("Show &data")
        plotAction = self.__designerUI.menuStream.addAction("Show &plots")
        self.__designerUI.menuStream.addSeparator()
        cleanAction = self.__designerUI.menuStream.addAction(
            "&Clean stream")

        dataAction.triggered.connect(self.__showStreamDataView)
        plotAction.triggered.connect(self.__showStreamPlotView)
        cleanAction.triggered.connect(self.__clearStream)

    def __createHelpMenuActions(self):
        aboutAction = self.__designerUI.menuHelp.addAction(
            "&About Puzzle Stream")
        aboutAction.triggered.connect(self.__showAboutWindow)

    def __toggleFullscreen(self):
        if self.isFullScreen():
            if self.__lastWindowState == "maximized":
                self.showMaximized()
            else:
                self.showNormal()
        else:
            if self.isMaximized():
                self.__lastWindowState = "maximized"
            else:
                self.__lastWindowState = "normal"
            self.showFullScreen()
        self.__updateLoad()

    def __showPreferences(self):
        preferences = PSPreferencesWindow(self.__manager.config, self)
        preferences.show()

    def __showStreamDataView(self):
        view = PSDataView(self.__manager, parent=self)
        self.__manager.scene.statusChanged.connect(view.statusUpdate)
        view.showMaximized()

    def __showStreamPlotView(self):
        view = PSPlotView(self.__manager, None, self)
        self.__manager.scene.statusChanged.connect(view.statusUpdate)
        view.show()

    def __clearStream(self):
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm clean up",
            "Are you sure you want to erase ALL data from the stream?",
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.__manager.stream.clear()

    def __showAboutWindow(self):
        about = PSAboutWindow(self)

    def __updateRecentProjects(self):
        self.__recentProjectsMenu.clear()

        for item in self.__manager.config["last projects"][::-1]:
            action = self.__recentProjectsMenu.addAction(item)
            action.triggered.connect(
                lambda x, item=item: self.__openProject(item))

    def __createToolBarActions(self):
        self.__openProjectAction = QAction("Open project", self)
        self.__saveFileAction = QAction("Save file", self)
        self.__undoAction = QAction("Back", self)
        self.__redoAction = QAction("Forward", self)
        self.__copyAction = QAction("Copy", self)
        self.__cutAction = QAction("Cut", self)
        self.__pasteAction = QAction("Paste", self)
        self.__runAction = QAction("Run puzzle", self)
        self.__pauseAction = QAction("Pause puzzle", self)
        self.__stopAction = QAction("Stop puzzle", self)
        self.__puzzleViewAction = QAction("Puzzle", self)
        self.__dataViewAction = QAction("Data view", self)
        self.__plotViewAction = QAction("Plot view", self)

        self.__saveFileAction.setEnabled(False)

        self.__openProjectAction.triggered.connect(self.__openProject)
        self.__saveFileAction.triggered.connect(self.__saveFileToolbar)
        self.__runAction.triggered.connect(self.__run)
        self.__pauseAction.triggered.connect(self.__pause)
        self.__stopAction.triggered.connect(self.__stop)
        self.__connectEditorActions(self.__editors[0])
        self.__puzzleViewAction.triggered.connect(
            lambda: self.changeRightWidgetMode("puzzle"))
        self.__dataViewAction.triggered.connect(
            lambda: self.changeRightWidgetMode("dataview"))
        self.__plotViewAction.triggered.connect(
            lambda: self.changeRightWidgetMode("plotview"))

    def __connectEditorActions(self, editor):
        self.__undoAction.triggered.connect(editor.undo)
        self.__redoAction.triggered.connect(editor.redo)
        self.__copyAction.triggered.connect(editor.copy)
        self.__cutAction.triggered.connect(editor.cut)
        self.__pasteAction.triggered.connect(editor.paste)

    def __disconnectEditorActions(self):
        self.__undoAction.triggered.disconnect()
        self.__redoAction.triggered.disconnect()
        self.__copyAction.triggered.disconnect()
        self.__cutAction.triggered.disconnect()
        self.__pasteAction.triggered.disconnect(e)

    def __getToolbarActions(self):
        return [self.__openProjectAction, self.__saveFileAction,
                self.__undoAction, self.__redoAction,
                self.__copyAction, self.__cutAction, self.__pasteAction,
                self.__runAction, self.__pauseAction, self.__stopAction,
                self.__puzzleViewAction, self.__dataViewAction,
                self.__plotViewAction]

    def __createPuzzleToolBarActions(self):
        self.__newModuleMenu = QMenu("New module", self)
        self.__newIntModuleAction = self.__newModuleMenu.addAction(
            "New internal module")
        self.__newExtModuleAction = self.__newModuleMenu.addAction(
            "New external module")
        self.__newPipeAction = QAction("New pipe", self)
        self.__newValveAction = QAction("New valve", self)

        self.__newModuleMenu.menuAction().triggered.connect(
            self.__newIntModule)
        self.__newIntModuleAction.triggered.connect(self.__newIntModule)
        self.__newExtModuleAction.triggered.connect(self.__newExtModule)
        self.__newPipeAction.triggered.connect(self.__newPipe)
        self.__newValveAction.triggered.connect(self.__newValve)

    def __getPuzzleToolbarActions(self):
        return [self.__newModuleMenu.menuAction(), self.__newPipeAction,
                self.__newValveAction]

    def updateText(self, module, text):
        if module == self.__activeModule:
            if text is None:
                self.__designerUI.outputTextEdit.setText("")
                self.__designerUI.outputTextEdit.activateAutoscroll()
            else:
                cursor = self.__designerUI.outputTextEdit.textCursor()
                cursor.movePosition(cursor.End)
                cursor.insertText(text)

    def updateStatus(self, module):
        if module == self.__activeModule:
            self.__designerUI.statisticsTextEdit.setHtml(module.statistics)
            self.updateActiveModuleButtons()

    def updateActiveModuleButtons(self):
        currentDir = os.path.dirname(__file__)

        if self.__currentStyle == "dark":
            if (self.__activeModule is not None and
                    self.__activeModule.status == "running"):
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/pause_blue_in.png")))
            else:
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/play_blue_in.png")))
        elif (self.__activeModule is not None and
                self.__currentStyle == "light"):
            if self.__activeModule.status == "running":
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/pause_blue_out.png")))
            else:
                self.btnRunPauseActive.setIcon(QIcon(os.path.join(
                    currentDir, "../icons/play_blue_out.png")))

    def __updateLoad(self):
        vm = psutil.virtual_memory()

        text = (str(psutil.cpu_percent()) +
                "% CPU   " +
                "%.1f" % (vm.used / vm.total * 100) +
                "% RAM   ")

        if (self.isFullScreen() or not
                self.__manager.config["clockOnlyFullscreen"]):
            text += time.strftime("%H:%M") + "  "

        self.__loadViewer.setText(text)

    def __configChanged(self, key):
        if key == "last projects":
            self.__updateRecentProjects()
        elif key == "clockOnlyFullscreen":
            self.__updateLoad()
        elif key == "saveOnEditorFocusOut":
            for e in self.__editors:
                e.save_on_focus_out = self.__manager.config[
                    "saveOnEditorFocusOut"]
        elif key == "design":
            design = self.__manager.config["design"]
            self.__setStyle(design[1][design[0]])

    def __updateNotificationHeader(self):
        self.__designerUI.outputTabWidget.setTabText(
            2,
            "Notifications (%d)" % (len(self.__notificationTab.notifications))
        )

    """
        reaction routines
    """

    def __deactivate(self):
        for e in self.__editorWidgets:
            e.hide()
        self.__welcomeLabel.setText(self.__newProjectText)
        self.__welcomeLabel.show()
        for e in self.__activeElements:
            e.setEnabled(False)

    def __activate(self):
        self.__welcomeLabel.setText(self.__projectOpenText)
        for e in self.__activeElements:
            e.setEnabled(True)

    def __updateProjectLoadedStatus(self):
        if self.__manager.projectPath is None:
            self.__deactivate()
        else:
            self.__activate()

    def __newProject(self, path=None):
        if not isinstance(path, str):
            path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "New project folder")

        if path != "":
            if len(os.listdir(path)) == 0:
                self.__manager.newProject(path)
                self.setWindowTitle(
                    "Puzzle Stream - " + self.__manager.projectPath)
                self.__resetUI(path)
            else:
                msg = QtWidgets.QMessageBox(self)
                msg.setText("Directory not empty.")
                msg.show()

        self.__updateProjectLoadedStatus()

    def __openProject(self, path=None, start=False):
        if not isinstance(path, str):
            path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Open project folder")

        if os.path.isdir(path):
            if os.path.isfile(path + "/puzzle.json"):
                self.__manager.load(path)
                self.setWindowTitle("Puzzle Stream - " + path)
                self.__resetUI(path)
            elif not start:
                msg = QtWidgets.QMessageBox(self)
                msg.setText(
                    "The chosen project folder is not valid. Please choose another one.")
                msg.exec()
                self.__openProject()

        self.__updateProjectLoadedStatus()
        self.__updateModuleSwitchers()

    def __saveProjectAs(self, path=None):
        if not isinstance(path, str):
            path = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Save project folder")

        if os.path.isdir(path):
            if len(os.listdir(path)) == 0:
                self.__manager.saveAs(path)
                self.setWindowTitle("Puzzle Stream - " + path)
                self.__resetUI(path)
            else:
                msg = QtWidgets.QMessageBox(self)
                msg.setText("Directory not empty.")
                msg.show()

        self.__updateProjectLoadedStatus()

    def __saveFileToolbar(self, value):
        self.__saveOpenFiles()

    def __abortAdding(self):
        self.__manager.addStatus = None
        self.__btnAddStatusAction.setVisible(False)
        self.__enableAddActions()
        self.__puzzleLabel.setText("")
        self.__welcomeLabel.setText(self.__projectOpenText)

    def __newIntModule(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "module.")
        self.__manager.addStatus = "intModule"
        self.__puzzleLabel.setText(
            "Click on a free spot inside the puzzle view to add a new internal module.")
        self.__btnAddStatusAction.setVisible(True)
        self.__updateModuleSwitchers()

    def __newExtModule(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "module.")
        self.__manager.addStatus = "extModule"
        self.__puzzleLabel.setText(
            "Click on a free spot inside the puzzle view to add a new external module.")
        self.__btnAddStatusAction.setVisible(True)
        self.__updateModuleSwitchers()

    def __newPipe(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "pipe.")
        self.__manager.addStatus = "pipe"
        self.__puzzleLabel.setText(
            "Click on a free spot inside the puzzle view to add a new pipe.")
        self.__btnAddStatusAction.setVisible(True)

    def __newValve(self):
        self.__disableAddActions()
        self.__welcomeLabel.setText(self.__newItemText + "valve.")
        self.__manager.addStatus = "valve"
        self.__puzzleLabel.setText(
            "Click on a free spot inside the puzzle view to add a new valve.")
        self.__btnAddStatusAction.setVisible(True)

    def __resetActiveModule(self):
        self.__activeModule = None
        for a in [self.plotviewMenuAction, self.dataviewMenuAction,
                  self.__plotViewAction, self.__dataViewAction]:
            a.setEnabled(False)

    def __itemAdded(self, item):
        self.__enableAddActions()
        self.__welcomeLabel.setText(self.__projectOpenText)
        self.__puzzleLabel.setText("")
        self.__btnAddStatusAction.setVisible(False)

    def __itemDeleted(self, item):
        if item == self.__activeModule:
            self.__welcomeLabel.setText(self.__projectOpenText)
            self.__editorWidgets[0].hide()
            self.__welcomeLabel.show()
            self.__designerUI.horizontalSplitter.setStretchFactor(0, 0)
            self.__resetActiveModule()

    def __enableAddActions(self):
        for a in self.__designerUI.puzzleToolbar.actions():
            if not isinstance(a, QtWidgets.QWidgetAction):
                a.setVisible(True)

        for a in (self.__runAction, self.__pauseAction, self.__stopAction):
            a.setEnabled(True)

    def __disableAddActions(self):
        for a in self.__designerUI.puzzleToolbar.actions():
            if not isinstance(a, QtWidgets.QWidgetAction):
                a.setVisible(False)

        for a in (self.__runAction, self.__pauseAction, self.__stopAction):
            a.setEnabled(False)

    def __showData(self, puzzleItem):
        if puzzleItem.streamSection is not None:
            view = PSDataView(self.__manager, puzzleItem, parent=self)
            self.__manager.scene.statusChanged.connect(view.statusUpdate)
            view.showMaximized()

    def __showPlots(self, puzzleItem):
        if puzzleItem.streamSection is not None:
            view = PSPlotView(self.__manager, puzzleItem, self)
            self.__manager.scene.statusChanged.connect(view.statusUpdate)
            view.show()

    def __run(self):
        if (self.__activeModule is not None and
                self.__manager.config["saveOnRun"]):
            self.__saveOpenFiles()

        for module in self.__manager.scene.modules.values():
            if ((module.status == "incomplete" or
                 module.status == "finished" or
                 module.status == "error" or
                 module.status == "test failed") and not module.hasInput):
                module.run()
            else:
                module.resume()

    def __pause(self):
        for module in self.__manager.scene.modules.values():
            module.pause()

    def __stop(self):
        for module in self.__manager.scene.modules.values():
            module.stop()

    """
    ===========================================================================
        Lib stuff
    """

    def __addLib(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                          "Add lib folder")
        if os.path.isdir(path):
            self.__manager.addLib(path)

            args = ["-s" + lib for lib in self.__manager.libs]

            for e in self.__editors:
                e.backend.start(
                    server.__file__, args=args)
            self.__createLibMenuActions()

    def __open_file(self, filename):
        if sys.platform == "win32":
            os.startfile(filename)
        else:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, filename])

    def __deleteLib(self, path):
        self.__manager.deleteLib(path)
        self.__createLibMenuActions()
