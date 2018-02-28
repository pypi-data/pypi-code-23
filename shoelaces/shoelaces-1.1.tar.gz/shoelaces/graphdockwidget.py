
from PyQt5.QtOpenGL import *
from shoelaces.dataprocessing import *
from shoelaces.helperwidgets import *
from shoelaces.offsetwindow import glOffsetPlotWidget


from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ctypes import *
from datetime import datetime


import shoelaces.settings as settings



class graphdockwidget(QDockWidget):
    def __init__(self, name = '', parent = None):
        super(graphdockwidget, self).__init__(parent)
        self.setWindowTitle(name)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea | Qt.BottomDockWidgetArea)
        self.graphWidget = QWidget(self)
        self.graphLayout = QGridLayout(self.graphWidget)

        self.mainplot = glGenePlotWidget(self)

        self.transcriptStatsLabel = QLabel(self.graphWidget)
        self.useOffsetBox = QComboBox(self.graphWidget)
        self.useOffsetBox.addItems(['Ignore Offsets', 'Use Offsets'])
        self.useOffsetBox.currentTextChanged.connect(self.updateStats)
        self.graphLayout.addWidget(self.useOffsetBox,0,1)
        self.graphLayout.addWidget(self.transcriptStatsLabel, 1, 1)
        self.graphLayout.addWidget(self.mainplot,0,0,2,1)
        self.graphLayout.setColumnStretch(0, 1)
        self.graphLayout.setColumnStretch(1, 0)

        self.graphWidget.setLayout(self.graphLayout)

        self.setWidget(self.graphWidget)

        self.setObjectName("plot")
        self.statsElement = None
        self.processor = None

    def updateStats(self):
        if not self.statsElement or not self.processor:
            return
        if 'transcripts' in self.statsElement:
            self.updateGeneStats(self.statsElement, self.processor)
        else:
            self.updateTranscriptStats(self.statsElement, self.processor)

    def plot(self, items, keys):
        return

    def updateGeneStats(self, gene, processor):
        self.statsElement = gene
        self.processor = processor
        if not gene or not processor:
            self.transcriptStatsLabel.clear()
            self.setWindowTitle('')
            return
        stats = processor.getgenestats(gene, self.useOffset())
        self.setWindowTitle(gene['gene_id'])
        output = ''
        for key, value in stats.items():
            output += key + ': %d \n' %(value)

        if gene['forward']:
            output += 'Strand: + \n'
        else:
            output += 'Strand: - \n'

        self.transcriptStatsLabel.setText(output)

        reads = processor.sequenceData.fetch(gene['chromosome'], gene['RNA_min'], gene['RNA_max'])

        self.mainplot.updateGene(gene)


        histogram = processor.plotSum(reads)
        self.mainplot.updateData(histogram)

    def updateTranscriptStats(self, selectedTranscripts, processor):
        self.statsElement = selectedTranscripts
        self.processor = processor


        if not selectedTranscripts or not processor:
            self.transcriptStatsLabel.clear()
            self.setWindowTitle('')
            return

        transcript = selectedTranscripts[0]
        reads = processor.sequenceData.fetch(transcript['chromosome'], transcript['RNA_min'], transcript['RNA_max'])
        histogram = processor.plotReads(reads, self.useOffset())




        self.mainplot.updateTranscript(selectedTranscripts)
        self.mainplot.updateData(histogram)


        stats = processor.gettranscriptStats(transcript['transcript_id'], self.useOffset())
        self.setWindowTitle(transcript['transcript_id'])

        output = ''
        for key, value in stats.items():
            output += key + ': %d \n' %(value)


        if transcript['forward']:
            output += 'Strand: +\n'
        else:
            output += 'Strand: -\n'

        self.transcriptStatsLabel.setText(output)

    def useOffset(self):
        return self.useOffsetBox.currentText() == 'Use Offsets'

class statsdockwidget(QDockWidget):
    refreshStats = pyqtSignal()
    filterData = pyqtSignal()
    def __init__(self, parent = None):
        super(statsdockwidget, self).__init__(parent)

        mainwidget = QWidget(self)
        self.setWidget(mainwidget)
        self.layout = QGridLayout(mainwidget)

        #self.layout.addWidget(QLabel(self,""), 1,0,1,2)

        self.useOffsetBox = QComboBox(mainwidget)
        self.useOffsetBox.addItems(['Ignore Offsets', 'Use Offsets'])
        self.layout.addWidget(self.useOffsetBox,0,0)

        self.offsetView = QTreeWidget(mainwidget)
        self.offsetView.setColumnCount(3)
        self.offsetView.setHeaderLabels(['Include','Length','Offset'])
        self.layout.addWidget(self.offsetView,1,0,2,2)

        self.distplot = glStatsPlotWidget(self, {})
        self.layout.addWidget(self.distplot,2,2,1,1)

        self.refreshButton = QPushButton('Refresh', mainwidget)
        self.layout.addWidget(self.refreshButton,0,1)
        self.refreshButton.pressed.connect(self.refreshStats)

        self.filterButton = QPushButton('Filter Data', mainwidget)
        self.layout.addWidget(self.filterButton,0,2)
        self.filterButton.pressed.connect(self.filterData)

        self.statslabel = QLabel(self)
        self.layout.addWidget(self.statslabel, 1,2,1,1)
        self.setWindowTitle("Data Overview")
        self.setObjectName("stats")
        self.nrofitems = 0

    def updateAvailableLengths(self, lengths, offsets):

        for length in sorted(lengths):
            if self.offsetView.findItems(str(length), Qt.MatchExactly, 1 ):
                continue
            item = QTreeWidgetItem()
            item.setData(1, Qt.DisplayRole, length)

            item.setData(2, Qt.DisplayRole, 0)

            item.setCheckState(0,Qt.Unchecked);

            self.offsetView.addTopLevelItem(item)
            self.nrofitems += 1

        for length, offset in offsets.items():
            items = self.offsetView.findItems(str(length), Qt.MatchExactly, 1 )
            if not items:
                continue
            for item in items:
                item.setData(2, Qt.DisplayRole, offset)
                #item.setCheckState(0,item.data(2,Qt.DisplayRole));

    def updateOffsets(self, offsets):

        for length, offset in offsets.items():
            items = self.offsetView.findItems(str(length), Qt.MatchExactly, 1 )
            if not items:
                continue
            for item in items:
                item.setData(2, Qt.DisplayRole, offset)
                item.setCheckState(0,Qt.Checked);

    def updatestats(self, processor = None ,type='', name =''):
        if not processor:
            return

        stats = {}
        if type == 'global':

            lengths = []
            itemIterator =  QTreeWidgetItemIterator(self.offsetView, QTreeWidgetItemIterator.Checked)
            count = 0

            while itemIterator.value():
                item = itemIterator.value()


                key = eval(str(item.data(1,Qt.DisplayRole)))

                lengths.append(key)

                count += 1
                itemIterator += 1


            stats, lengthdist = processor.getglobalstatsFromWig(self.useOffsets(), lengths)


            self.distplot.updatePlot(lengthdist, [[0.3,0.5,0.8],[0.3,0.5,0.8]])


        elif type == 'transcript':
            stats = processor.gettranscriptStats(name)
        elif type == 'gene':
            stats = processor.getgenestats(name)


        output = ''
        output += type + ' stats: ' + str(name) + '\n'
        for key, value in stats.items():

            output += key + ': '+ str(value) + '\n'

        self.statslabel.setText(output)

    def useOffsets(self):
        return self.useOffsetBox.currentText() == 'Use Offsets'


