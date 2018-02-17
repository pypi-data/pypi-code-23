# -*- coding: utf-8 -*-
"""Data view module.

contains PSDataView
"""

import matplotlib.backends.backend_qt5agg as mplAgg
import numpy as np
import pyqtgraph as pg
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtGui, QtWidgets

from puzzlestream.backend.numpymodel2D import PSNumpyModel2D
from puzzlestream.backend.reference import PSCacheReference
from puzzlestream.backend.standardtablemodel import PSStandardTableModel
from puzzlestream.backend.stream import PSStream
from puzzlestream.backend.treemodel import PSTreeModel
from puzzlestream.ui.dataviewexport import PSTableExportDialog
from puzzlestream.ui.tracebackview import PSTracebackView


class PSDataView(QtWidgets.QMainWindow):
    """Data view with table, plots and export functionality.

    One of the central parts of Puzzle Stream; the data view shows
    1D and 2D numpy arrays, matplotlib plots, ...
    Everything that cannot be dealt with is simply shown as its string
    representation.
    """

    def __init__(self, manager, puzzleItem=None, parent=None):
        """Data view init.

        Args:
            manager (PSManager): Current Puzzle Stream manager instance.
            puzzleItem (PSPuzzleItem): Puzzle item whose data is to be
                displayed.
            parent: Qt parent widget.
        """
        super().__init__(parent)

        if puzzleItem is None:
            self.setWindowTitle("Data view - complete stream")
        else:
            self.setWindowTitle("Data view - " + str(puzzleItem))

        self.__stream = manager.stream

        if puzzleItem is None:
            self.__data = self.__stream
        else:
            self.__data = puzzleItem.streamSection.data

        self.__puzzleItem = puzzleItem
        self.__modules = manager.scene.modules
        self.__config = manager.config
        self.canvas, self.mpltoolbar = None, None
        self.__x, self.__y = None, None
        self.__keys, self.__retranslatedKeys = None, None

        # horizontal splitter
        self.horizontalSplitter = QtWidgets.QSplitter()
        self.horizontalSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSplitter.setObjectName("horizontalSplitter")
        self.setCentralWidget(self.horizontalSplitter)

        # table view - added to the horizontal splitter
        self.tableView = QtWidgets.QTableView(self.horizontalSplitter)
        self.tableView.setEditTriggers(QtWidgets.QTableView.NoEditTriggers)
        self.tableView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(
            self.tableContextMenu)
        self.tableView.horizontalHeader().setDefaultSectionSize(150)
        self.horizontalSplitter.addWidget(self.tableView)

        # vertical layout on the right side
        self.verticalLayoutWidget = QtWidgets.QWidget(self.horizontalSplitter)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayoutWidget.setLayout(self.verticalLayout)
        self.horizontalSplitter.addWidget(self.verticalLayoutWidget)

        # tree model and view
        self.treeView = QtWidgets.QTreeView(self.verticalLayoutWidget)
        self.treeView.setEditTriggers(QtWidgets.QTreeView.NoEditTriggers)
        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(
            self.treeContextMenu)
        self.treeView.header().close()

        # pyqtgraph plot widget
        self.plotGroupWidget = QtWidgets.QWidget(self.verticalLayoutWidget)
        self.plotGroupWidgetLayout = QtWidgets.QVBoxLayout(
            self.plotGroupWidget)
        self.plotWidget = pg.PlotWidget(self.plotGroupWidget)
        self.plotCurve = pg.PlotCurveItem()
        self.plotWidget.addItem(self.plotCurve)

        # drop downs and swap button
        self.dropdownX = QtWidgets.QComboBox(self.plotGroupWidget)
        self.dropdownY = QtWidgets.QComboBox(self.plotGroupWidget)
        self.dropdownX.currentIndexChanged.connect(self.__setXDropdown)
        self.dropdownY.currentIndexChanged.connect(self.__setYDropdown)
        self.swapBtn = QtWidgets.QPushButton(self.plotGroupWidget)
        self.swapBtn.setText("swap axes")
        self.swapBtn.setMaximumWidth(100)
        self.swapBtn.clicked.connect(self.__swapAxes)
        self.hboxDropdown = QtWidgets.QHBoxLayout()
        self.hboxDropdown.addWidget(self.dropdownX)
        self.hboxDropdown.addWidget(self.swapBtn)
        self.hboxDropdown.addWidget(self.dropdownY)

        # add hbox and plot widget to plotGroupWidgetLayout
        self.plotGroupWidgetLayout.addLayout(self.hboxDropdown)
        self.plotGroupWidgetLayout.addWidget(self.plotWidget)

        # create matplotlib group widget
        self.mplGroupWidget = QtWidgets.QWidget(self.verticalLayoutWidget)
        self.mplLayout = QtWidgets.QVBoxLayout(self.mplGroupWidget)
        self.mplGroupWidget.setLayout(self.mplLayout)

        # add tree view and group widgets to vertical layout, hide mpl widget
        self.verticalLayout.addWidget(self.treeView)
        self.verticalLayout.addWidget(self.plotGroupWidget)
        self.verticalLayout.addWidget(self.mplGroupWidget)
        self.mplGroupWidget.hide()

        # resize horizontal splitter
        self.horizontalSplitter.setStretchFactor(0, 6)
        self.horizontalSplitter.setStretchFactor(1, 4)

        # create main menu
        self.toolbar = QtWidgets.QToolBar(self)
        self.toolbar.setMovable(False)
        completeExport = self.toolbar.addAction("Export complete table")
        completeExport.triggered.connect(self.exportCompleteTable)
        self.addToolBar(self.toolbar)

        # create status bar
        self.setStatusBar(QtWidgets.QStatusBar())
        self.statusBarLabel = QtWidgets.QLabel()
        self.statusBar().addWidget(self.statusBarLabel)

        # finalise setup
        self.__checkStates = {}
        self.update()

    def statusUpdate(self, item):
        if self.__puzzleItem is None or item == self.__puzzleItem:
            if item.status == "finished" or self.__puzzleItem is None:
                if not isinstance(self.__data, PSStream):
                    self.__data.reload()
                self.update()

    def update(self):
        if not isinstance(self.__data, PSStream):
            self.__data.cleanRam()
        self.hideMplWidget()
        self.createClassificationLists()
        self.createTree()
        self.createDropdowns()

        if (isinstance(self.tableView.model(), PSStandardTableModel) or
                self.tableView.model() is None):
            self.setToStandardModel(forceUpdate=True)

    def createClassificationLists(self):
        self.__keys = sorted(self.__data)
        self.__keys = [key for key in self.__keys
                       if not isinstance(self.__data[key], PSCacheReference)]
        self.__standardKeys, self.__numpy2DKeys, self.__mplKeys = [], [], []
        self.__otherKeys = []

        for key in self.__keys:
            data = self.__data[key]
            tKey = self.__translateKeyToUser(key)

            if tKey is not None:
                if isinstance(data, np.ndarray):
                    if len(data.shape) == 1:
                        self.__standardKeys.append(tKey)
                    elif len(data.shape) == 2:
                        self.__numpy2DKeys.append(tKey)
                elif isinstance(data, Figure):
                    self.__mplKeys.append(tKey)
                else:
                    self.__otherKeys.append(tKey)

    def createDropdowns(self):
        self.dropdownX.setCurrentIndex(0)
        self.dropdownY.setCurrentIndex(0)
        self.dropdownX.clear()
        self.dropdownY.clear()

        for key in self.__standardKeys:
            self.dropdownX.addItem(key)
            self.dropdownY.addItem(key)

        if len(self.__standardKeys) > 1:
            self.dropdownY.setCurrentIndex(1)

    def __translateKeyToUser(self, key):
        if isinstance(self.__data, PSStream):
            ID = key.split("-")[0]
            if not int(ID) in self.__modules:
                return
            return key.replace(ID + "-", self.__modules[int(ID)].name + ": ")
        return key

    def __translateKeyToInternal(self, key):
        if key in self.__retranslatedKeys:
            return self.__retranslatedKeys[key]

    def createTree(self):
        model = PSTreeModel(self.__standardKeys, self.__numpy2DKeys,
                            self.__mplKeys, self.__otherKeys,
                            self.__checkStates)
        self.__retranslatedKeys = {self.__translateKeyToUser(key): key
                                   for key in self.__keys}
        if None in self.__retranslatedKeys:
            del self.__retranslatedKeys[None]

        model.itemChanged.connect(self.__treeItemChanged)
        self.treeView.setModel(model)
        self.treeView.selectionModel().selectionChanged.connect(
            self.__treeSelectionChanged)
        self.treeView.expandAll()

    def setToStandardModel(self, selectColumn=None, forceUpdate=False):
        if not isinstance(self.__data, PSStream):
            self.__data.cleanRam()

        self.showTableViewHeaders()

        if forceUpdate or self.currentModelType != "standard":
            model = PSStandardTableModel()

            for key in self.__standardKeys:
                if self.__checkStates[key]:
                    model.addColumn(
                        key, self.__data[self.__translateKeyToInternal(key)])
            self.tableView.setModel(model)
            self.tableView.selectionModel().selectionChanged.connect(
                self.__tableSelectionChanged)

            for i in range(len(model.keys)):
                w = model.getPlotWidget(i)

                if w is not None:
                    index = self.tableView.model().index(0, i)
                    self.tableView.setIndexWidget(index, w)

            self.tableView.setRowHeight(0, 75)
        else:
            model = self.tableView.model()

        if isinstance(selectColumn, str) and selectColumn in model.keys:
            index = model.keys.index(selectColumn)
            self.tableView.selectColumn(index)
            self.treeView.setFocus()

    def setToNumpy2DModel(self, key):
        if not isinstance(self.__data, PSStream):
            self.__data.cleanRam()

        self.showTableViewHeaders()

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        data = self.__data[self.__translateKeyToInternal(key)]

        model = PSNumpyModel2D(data)
        self.tableView.setModel(model)
        self.tableView.selectionModel().selectionChanged.connect(
            self.__tableSelectionChanged)
        self.tableView.setRowHeight(0, 30)

        self.hideMplWidget()
        self.showMplWidget()

        fig = Figure()
        ax = fig.add_subplot(111)
        ax.imshow(data)
        self.canvas = mplAgg.FigureCanvasQTAgg(fig)
        self.canvas.setParent(self.mplGroupWidget)

        self.mpltoolbar = mplAgg.NavigationToolbar2QT(
            self.canvas,
            self.mplGroupWidget
        )

        self.mplLayout.addWidget(self.canvas)
        self.mplLayout.addWidget(self.mpltoolbar)
        QtWidgets.QApplication.restoreOverrideCursor()

    def setToOtherModel(self, key):
        model = QtGui.QStandardItemModel()
        try:
            text = str(self.__data[self.__translateKeyToInternal(key)])
        except Exception as e:
            text = str(e)
        model.appendRow(QtGui.QStandardItem(text))
        self.tableView.setModel(model)
        self.hideTableViewHeaders()

    def showTableViewHeaders(self):
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.tableView.verticalHeader().setStretchLastSection(False)
        self.tableView.horizontalHeader().show()
        self.tableView.verticalHeader().show()

    def hideTableViewHeaders(self):
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().hide()
        self.tableView.verticalHeader().hide()

    @property
    def currentModelType(self):
        if isinstance(self.tableView.model(), PSNumpyModel2D):
            return "2D"
        elif isinstance(self.tableView.model(), PSStandardTableModel):
            return "standard"
        return "none"

    """
    ===========================================================================
        Tree selection / item changed handlers and routines
    """

    def __treeItemChanged(self, item):
        if not isinstance(self.__data, PSStream):
            self.__data.cleanRam()
        self.hideMplWidget()

        userKey = item.text()
        key = self.__translateKeyToInternal(userKey)
        self.__checkStates[key] = item.checkState() == 2
        model = self.tableView.model()

        if isinstance(model, PSStandardTableModel):
            if self.__checkStates[key] and key not in model.keys:
                tKey = self.__translateKeyToUser(key)
                if tKey is not None:
                    self.tableView.model().addColumn(tKey, self.__data[key])
            elif not self.__checkStates[key] and userKey in model.keys:
                self.tableView.model().deleteColumn(userKey)

                if self.__puzzleItem is not None:
                    del self.__data[key]

            self.tableView.model().layoutChanged.emit()

    def __treeSelectionChanged(self):
        i = self.treeView.selectedIndexes()[0]
        key = self.treeView.model().data(i, 0)

        if key in self.__numpy2DKeys:
            self.numpy2DItemSelected(key)
        elif key in self.__mplKeys:
            self.matplotlibItemSelected(key)
        elif key in self.__standardKeys:
            self.standardItemSelected(key)
        elif key in self.__otherKeys:
            self.otherItemSelected(key)

    def standardItemSelected(self, key):
        self.setToStandardModel(key)
        self.showPlotWidget()

    def numpy2DItemSelected(self, key):
        self.setToNumpy2DModel(key)

    def matplotlibItemSelected(self, key):
        i = self.treeView.selectedIndexes()[0]
        self.treeView.setCurrentIndex(i)
        self.hideMplWidget()
        self.showMplWidget()

        fig = self.__data[self.__translateKeyToInternal(key)]
        self.canvas = mplAgg.FigureCanvasQTAgg(fig)
        self.canvas.setParent(self.mplGroupWidget)

        self.mpltoolbar = mplAgg.NavigationToolbar2QT(
            self.canvas,
            self.mplGroupWidget
        )

        self.mplLayout.addWidget(self.canvas)
        self.mplLayout.addWidget(self.mpltoolbar)

    def otherItemSelected(self, key):
        self.setToOtherModel(key)

    def __deleteItem(self):
        i = self.treeView.selectedIndexes()[0]
        userKey = self.treeView.model().data(i, 0)
        key = self.__translateKeyToInternal(userKey)

        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm clean up",
            ("Are you sure you want to erase \"" +
             userKey + "\" from the stream?"),
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes
        )

        if reply == QtWidgets.QMessageBox.Yes:
            if self.__puzzleItem is None:
                del self.__stream[key]
            else:
                self.__data.deleteFromStream(key)

        self.update()

    def __showItemTraceback(self):
        i = self.treeView.selectedIndexes()[0]
        userKey = self.treeView.model().data(i, 0)
        key = self.__translateKeyToInternal(userKey)

        if self.__puzzleItem is not None:
            key = str(self.__puzzleItem.id) + "-" + key

        traceback = PSTracebackView(key, userKey, self.__stream,
                                    self.__modules, self)

    def __setAsXTree(self):
        key = self.__keys[self.treeView.currentIndex().row()]
        self.dropdownX.setCurrentIndex(self.__standardKeys.index(key))

    def __setAsYTree(self):
        key = self.__keys[self.treeView.currentIndex().row()]
        self.dropdownY.setCurrentIndex(self.__standardKeys.index(key))

    def __setXDropdown(self):
        index = self.dropdownX.currentIndex()
        self.__x = self.__data[
            self.__translateKeyToInternal(self.__standardKeys[index])]
        self.plotUpdate()

    def __setYDropdown(self):
        index = self.dropdownY.currentIndex()
        self.__y = self.__data[
            self.__translateKeyToInternal(self.__standardKeys[index])]
        self.plotUpdate()

    def __swapAxes(self):
        ix, iy = self.dropdownX.currentIndex(), self.dropdownY.currentIndex()
        self.dropdownX.setCurrentIndex(iy)
        self.dropdownY.setCurrentIndex(ix)

    def plotUpdate(self):
        if self.__x is not None and self.__y is not None:
            try:
                self.plotCurve.setData(self.__x, self.__y)
            except Exception as e:
                pass
            keyx = self.__standardKeys[self.dropdownX.currentIndex()]
            keyy = self.__standardKeys[self.dropdownY.currentIndex()]
            self.plotWidget.getPlotItem().setLabel("bottom", keyx)
            self.plotWidget.getPlotItem().setLabel("left", keyy)

    def treeContextMenu(self, event):
        menu = QtWidgets.QMenu(self)

        i = self.treeView.selectedIndexes()[0]
        key = self.treeView.model().data(i, 0)

        if key in self.__standardKeys:
            xAction = menu.addAction("Set as x")
            xAction.triggered.connect(self.__setAsXTree)
            yAction = menu.addAction("Set as y")
            yAction.triggered.connect(self.__setAsYTree)
            menu.addSeparator()

        if self.__translateKeyToInternal(key) in self.__keys:
            if self.__puzzleItem is not None:
                tracebackAction = menu.addAction("Show traceback")
                tracebackAction.triggered.connect(self.__showItemTraceback)
            deleteAction = menu.addAction("Delete from stream")
            deleteAction.triggered.connect(self.__deleteItem)

            action = menu.exec_(self.treeView.mapToGlobal(event))

    def tableContextMenu(self, event):
        menu = QtWidgets.QMenu(self)
        exportAction = menu.addAction("Export")
        exportAction.triggered.connect(self.exportSelected)
        action = menu.exec_(self.tableView.mapToGlobal(event))

    def showPlotWidget(self):
        self.hideMplWidget()

        for e in (self.plotWidget, self.dropdownX,
                  self.dropdownY, self.swapBtn):
            e.show()

    def hidePlotWidget(self):
        for e in (self.plotWidget, self.dropdownX,
                  self.dropdownY, self.swapBtn):
            e.hide()

    def showMplWidget(self):
        self.hidePlotWidget()
        self.mplGroupWidget.show()

    def hideMplWidget(self):
        if self.canvas is not None:
            self.canvas.setParent(None)
            self.mpltoolbar.setParent(None)
            self.canvas.hide()
            self.mpltoolbar.hide()
            self.mplLayout.removeWidget(self.canvas)
            self.mplLayout.removeWidget(self.mpltoolbar)
            del self.canvas, self.mpltoolbar
            self.canvas, self.mpltoolbar = None, None
            self.mplGroupWidget.hide()

    """
    ===========================================================================
        Selection stuff
    """

    def __tableSelectionChanged(self, selected, deselected):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        model = self.tableView.model()

        if (isinstance(model, PSStandardTableModel) and
                self.tableView.selectionModel().isRowSelected(
                    0, QtCore.QModelIndex())):

            for c in range(model.columnCount()):
                self.tableView.selectionModel().select(
                    model.index(0, c),
                    QtCore.QItemSelectionModel.Deselect
                )

        data = []

        for ind in self.tableView.selectedIndexes():
            item = model.getItemAt(ind.row(), ind.column())

            if item is not None:
                data.append(item)

        try:
            data = np.array(data)
            output = "Sum: " + str(np.sum(data))
            output += "; Mean: " + str(np.mean(data))

            if len(data) > 1:
                output += "; Standard deviation: " + str(np.std(data, ddof=1))
        except Exception:
            output = ""

        self.statusBarLabel.setText(output)
        QtWidgets.QApplication.restoreOverrideCursor()

    """
    ===========================================================================
        Export
    """

    def exportSelected(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        export = self.__getSelectionArray()
        QtWidgets.QApplication.restoreOverrideCursor()

        if export is not None:
            PSTableExportDialog(export, self.__config, self)

    def exportCompleteTable(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        export = self.__getTableArray()
        QtWidgets.QApplication.restoreOverrideCursor()

        if export is not None:
            PSTableExportDialog(export, self.__config, self)

    def __getSelectionArray(self):
        for c in range(self.tableView.model().columnCount()):
            if not self.tableView.selectionModel().isColumnSelected(
                    c, QtCore.QModelIndex()):
                break
        else:
            return self.__getTableArray()

        indices = self.tableView.selectedIndexes()
        countR = [i.row() for i in indices]
        countC = [i.column() for i in indices]

        if len(countR) > 0 and len(countC) > 0:
            minR, minC = min(countR), min(countC)
            maxR, maxC = max(countR), max(countC)
            nR, nC = maxR - minR + 1, maxC - minC + 1

            try:
                data = np.zeros((nR, nC))

                for i in indices:
                    r, c = i.row() - minR, i.column() - minC
                    data[r, c] = self.tableView.model().getItemAt(
                        i.row(), i.column())
                return data
            except Exception:
                pass
            return None

    def __getTableArray(self):
        model = self.tableView.model()

        if self.currentModelType == "2D":
            return model.array
        elif self.currentModelType == "standard":
            maxR, maxC = model.rowCount() - 1, model.columnCount()

            try:
                data = np.zeros((maxR, maxC))
                indices = self.tableView.model()

                for r in range(maxR):
                    for c in range(maxC):
                        data[r, c] = self.tableView.model().getItemAt(r + 1, c)
                return data
            except Exception as e:
                print(e)
        return None

    def closeEvent(self, event):
        self.setParent(None)
        event.accept()
