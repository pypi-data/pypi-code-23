# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'raw_02.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from puzzlestream.ui.graphicsview import PSGraphicsView
from puzzlestream.ui.outputtextedit import PSOutputTextEdit


class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralGrid = QtWidgets.QWidget(MainWindow)
        self.centralGrid.setObjectName("centralGrid")
        self.gridLayout = QtWidgets.QGridLayout(self.centralGrid)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalSplitter = QtWidgets.QSplitter(self.centralGrid)
        self.horizontalSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSplitter.setObjectName("horizontalSplitter")
        self.verticalSplitter = QtWidgets.QSplitter(self.horizontalSplitter)
        self.verticalSplitter.setOrientation(QtCore.Qt.Vertical)
        self.verticalSplitter.setObjectName("verticalSplitter")
        self.puzzleWidget = QtWidgets.QWidget(self.verticalSplitter)
        self.puzzleWidget.setObjectName("puzzleWidget")
        self.puzzleWidgetLayout = QtWidgets.QVBoxLayout()
        self.puzzleWidget.setLayout(self.puzzleWidgetLayout)
        self.puzzleToolbar = QtWidgets.QToolBar(self.puzzleWidget)
        self.puzzleWidgetLayout.addWidget(self.puzzleToolbar)
        self.puzzleGraphicsView = PSGraphicsView(self.puzzleWidget)
        self.puzzleGraphicsView.setObjectName("puzzleGraphicsView")
        self.puzzleWidgetLayout.addWidget(self.puzzleGraphicsView)
        self.outputTabWidget = QtWidgets.QTabWidget(self.verticalSplitter)
        self.outputTabWidget.setObjectName("outputTabWidget")
        self.textTab = QtWidgets.QWidget()
        self.textTab.setObjectName("textTab")
        self.textTabGridLayout = QtWidgets.QGridLayout(self.textTab)
        self.textTabGridLayout.setObjectName("textTabGridLayout")
        self.outputTextEdit = PSOutputTextEdit(self.textTab)
        self.outputTextEdit.setObjectName("outputTextEdit")
        self.textTabGridLayout.addWidget(self.outputTextEdit, 0, 0, 1, 1)
        self.outputTabWidget.addTab(self.textTab, "")
        self.statisticsTab = QtWidgets.QWidget()
        self.statisticsTab.setObjectName("statisticsTab")
        self.statisticsTabGridLayout = QtWidgets.QGridLayout(
            self.statisticsTab)
        self.statisticsTabGridLayout.setObjectName("statisticsTabGridLayout")
        self.vertPlotTabLayout = QtWidgets.QVBoxLayout()
        self.vertPlotTabLayout.setObjectName("vertPlotTabLayout")
        self.horPlotSelComboBoxLayout = QtWidgets.QHBoxLayout()
        self.horPlotSelComboBoxLayout.setObjectName("horPlotSelComboBoxLayout")
        self.vertPlotTabLayout.addLayout(self.horPlotSelComboBoxLayout)
        self.statisticsTabGridLayout.addLayout(
            self.vertPlotTabLayout, 0, 0, 1, 1)
        self.outputTabWidget.addTab(self.statisticsTab, "")
        self.statisticsTextEdit = QtWidgets.QTextEdit(self.statisticsTab)
        self.statisticsTextEdit.setReadOnly(True)
        self.statisticsTextEdit.setObjectName("statisticsTextEdit")
        self.statisticsTabGridLayout.addWidget(self.statisticsTextEdit,
                                               0, 0, 1, 1)
        self.gridLayout.addWidget(self.horizontalSplitter, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralGrid)
        self.MainMenuBar = QtWidgets.QMenuBar(MainWindow)
        self.MainMenuBar.setGeometry(QtCore.QRect(0, 0, 800, 27))
        self.MainMenuBar.setObjectName("MainMenuBar")
        self.menuFile = QtWidgets.QMenu(self.MainMenuBar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.MainMenuBar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(self.MainMenuBar)
        self.menuView.setObjectName("menuView")
        self.menuLib = QtWidgets.QMenu(self.MainMenuBar)
        self.menuLib.setObjectName("menuLib")
        self.menuStream = QtWidgets.QMenu(self.MainMenuBar)
        self.menuStream.setObjectName("menuStream")
        self.menuHelp = QtWidgets.QMenu(self.MainMenuBar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.MainMenuBar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.MainMenuBar.addAction(self.menuFile.menuAction())
        self.MainMenuBar.addAction(self.menuEdit.menuAction())
        self.MainMenuBar.addAction(self.menuView.menuAction())
        self.MainMenuBar.addAction(self.menuLib.menuAction())
        self.MainMenuBar.addAction(self.menuStream.menuAction())
        self.MainMenuBar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.outputTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Puzzle Stream"))
        self.outputTabWidget.setTabText(
            self.outputTabWidget.indexOf(self.textTab), _translate(
                "MainWindow", "Output"))
        self.outputTabWidget.setTabText(
            self.outputTabWidget.indexOf(self.statisticsTab), _translate(
                "MainWindow", "Statistics"))
        self.menuFile.setTitle(_translate("MainWindow", "&File"))
        self.menuEdit.setTitle(_translate("MainWindow", "&Edit"))
        self.menuView.setTitle(_translate("MainWindow", "&View"))
        self.menuLib.setTitle(_translate("MainWindow", "&Libraries"))
        self.menuStream.setTitle(_translate("MainWindow", "&Stream"))
        self.menuHelp.setTitle(_translate("MainWindow", "&Help"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
