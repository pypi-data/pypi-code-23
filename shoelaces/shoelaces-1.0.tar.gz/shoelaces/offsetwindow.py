__author__ = 'birkeland'
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import QSize

from shoelaces.helperwidgets import *
import shoelaces.settings as settings

class offsetWidget(QWidget):
    def __init__(self, parent = None):
        super(offsetWidget,self).__init__(parent)
        self.mainWidget = QScrollArea(self)
        self.mainWidget.setWidgetResizable(True)
        self.centralWidget = QMainWindow(self.mainWidget)
        self.centralWidget.setWindowFlags(QtCore.Qt.Widget)

        self.mainWidget.setWidget(self.centralWidget)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.mainWidget)
        self.widgets = []

    def addPlot(self, p, name):
        plotDock = QDockWidget(self.centralWidget)
        plotDock.setWidget(p)
        plotDock.setWindowTitle(name)
        self.centralWidget.addDockWidget(QtCore.Qt.LeftDockWidgetArea, plotDock)
        self.centralWidget.updateGeometry()
        p.parentDock = self


    def removeDock(self, dock):
        self.centralWidget.removeDockWidget(dock)


    #def updateSize(self):
    #    self.mainWidget.setWidget(self.centralWidget)

class offsetDock(QDockWidget):

    emitUpdate = pyqtSignal(int, int)

    def __init__(self, parent = None, processor = None, currentRatio = 0.1):

        super(offsetDock, self).__init__(parent)
        self.startplots = {}
        self.endplots = {}
        self.freqplots = {}
        self.modulusplots = {}
        self.updateRequried = False
        self.ratios = [1.0, 0.1, 0.05, 0.01]

        self.processor = processor

        self.mainWidget = QWidget(self)
        self.mainWidget.setMinimumSize(QSize(1000, 300))

        self.mainLayout = QGridLayout(self.mainWidget)

        self.percentage = QComboBox(self.mainWidget)
        self.percentage.addItem("All")
        self.percentage.addItem("Top 10 %")
        self.percentage.addItem("Top 5 %")
        self.percentage.addItem("Top 1 %")
        ind  = self.ratios.index(currentRatio)
        self.percentage.setCurrentIndex(ind)
        self.percentage.currentIndexChanged.connect(self.updatePlots)


        self.mainLayout.addWidget(self.percentage,1,0,1,2)


        self.tabsStart = QTabWidget(self.mainWidget)
        self.tabsEnd = QTabWidget(self.mainWidget)
        self.tabsFreq = QTabWidget(self.mainWidget)
        self.tabsModulus = QTabWidget(self.mainWidget)
        self.mainLayout.addWidget(self.tabsStart,3,0)
        self.mainLayout.addWidget(QLabel("Start codon"), 2, 0)
        self.mainLayout.addWidget(self.tabsEnd,3,1)
        self.mainLayout.addWidget(QLabel("Stop codon"), 2, 1)
        self.mainLayout.addWidget(self.tabsFreq,3,3)
        self.mainLayout.addWidget(QLabel("Reading frame"), 2, 2)
        self.mainLayout.addWidget(self.tabsModulus,3,2)
        self.mainLayout.addWidget(QLabel("Periodicity"), 2, 3)

        self.commonStartPlots = offsetWidget(self.tabsStart)
        self.otherStartPlots = offsetWidget(self.tabsStart)

        self.commonEndPlots = offsetWidget(self.tabsEnd)
        self.otherEndPlots = offsetWidget(self.tabsEnd)

        self.commonFreqGraphs = offsetWidget(self.tabsFreq)
        self.otherFreqGraphs = offsetWidget(self.tabsFreq)

        self.commonModulusGraphs = offsetWidget(self.tabsModulus)
        self.otherModulusGraphs = offsetWidget(self.tabsModulus)


        self.tabsStart.addTab(self.commonStartPlots, 'Common')
        self.tabsStart.addTab(self.otherStartPlots,'Others')

        self.tabsEnd.addTab(self.commonEndPlots, 'Common')
        self.tabsEnd.addTab(self.otherEndPlots,'Others')

        self.tabsFreq.addTab(self.commonFreqGraphs, 'Common')
        self.tabsFreq.addTab(self.otherFreqGraphs,'Others')

        self.tabsModulus.addTab(self.commonModulusGraphs, 'Common')
        self.tabsModulus.addTab(self.otherModulusGraphs,'Others')


        self.setWidget(self.mainWidget)


        #self.setRatio(currentRatio)

        self.createPlots()


        self.setWindowTitle("CDS Offset Plots")
        self.setObjectName("offset plots")

    def updatePlots(self, state):

        self.createPlots()

    def setRatio(self, ratio):


        ind  = self.ratios.index(ratio)
        self.percentage.setCurrentIndex(ind)
        self.updateRequried = True


    def getRatio(self):
        ratios = [1.0, 0.1, 0.05, 0.01]

        index = self.percentage.currentIndex()

        return ratios[index]

    def createPlots(self):


        if not self.processor:
            return
        self.percentage.hidePopup()

        ratios = [1.0, 0.1, 0.05, 0.01]

        index = self.percentage.currentIndex()

        result = self.processor.plotDifferenceToCDS(True, False, ratios[index])
        freqPlots =  self.processor.fourierTransform(result)
        modplots = self.processor.createModulusPlots(result)
        common = self.processor.findUsefulLengths(freqPlots, result)
        #print(common)
        #################
        #detect offsets
        subPlots =  {}
        for key, wig in result.items():
            subPlots[key] = self.processor.getSubWig(wig, sorted(wig.keys()), -15, -5)
        offsets = self.processor.detectOffset(subPlots)
        for key, offset in offsets.items():
            settings.getMainApp().setOffset(key, offset)
         #################
        #print(offsets)
        #print(common)

        self.createPlotsDocks(result, (-20,40),self.startplots, (self.commonStartPlots, self.otherStartPlots), common, glOffsetPlotWidget)

        result = self.processor.plotDifferenceToCDS(False, False, ratios[index])



        self.createPlotsDocks(result, (-40,20),self.endplots, (self.commonEndPlots, self.otherEndPlots), common, glOffsetPlotWidget, "stop")

        self.createPlotsDocks(freqPlots, (0,10),self.freqplots, (self.commonFreqGraphs, self.otherFreqGraphs), common, glGraphPlotWidget)
        self.createPlotsDocks(modplots, (0,3),self.modulusplots, (self.commonModulusGraphs, self.otherModulusGraphs), common, glModularPlotWidget)
        self.updateRequried = False

    def createPlotsDocks(self, result, interval, plotList, plotDocks, common, plotType, codon = "start"):


        for key in sorted(result.keys()):

            wig = result[key]
            hist = self.processor.getSubWig(wig, sorted(wig.keys()), interval[0], interval[1])

            plotParent = plotDocks[1]
            notParent = plotDocks[0]


            if key in common:
                plotParent =plotDocks[0]
                notParent = plotDocks[1]



            if key in plotList:

                 plotList[key].updatePlot(hist)
                 if plotList[key].parentDock != plotParent:
                     dock = plotList[key].parent()
                     plotParent.addPlot(plotList[key],str(key))
                     notParent.removeDock(dock)

                 continue

            plot = plotType(plotParent, key, hist, codon)
            plotParent.addPlot(plot, str(key))
            plotList[key] = plot
            plot.offsetUpdated.connect(self.emitUpdate)
            plot.offsetUpdated.connect(self.updateOffset)

            if key in self.processor.lengthOffsets:
                plot.setOffset(self.processor.lengthOffsets[key])

        plotDocks[0].show()
        plotDocks[1].show()



    def updateOffset(self, key, offset):
        try:
            if self.sender().codon == 'start':
                self.endplots[self.sender().ID].setOffset(offset)
                self.modulusplots[self.sender().ID].setOffset(offset)
            elif self.sender().codon == 'stop':
                self.startplots[self.sender().ID].setOffset(offset)
                self.modulusplots[self.sender().ID].setOffset(offset)
            else:
                self.startplots[self.sender().ID].setOffset(offset)
                self.endplots[self.sender().ID].setOffset(offset)
        except :
            print ("error")

    def sizeHint(self):
        return QSize(500, 500)