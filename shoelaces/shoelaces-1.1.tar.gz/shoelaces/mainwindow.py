import sys, os, random
from shoelaces.offsetwindow import *
from shoelaces.graphdockwidget import *
from shoelaces.resource import *
import argparse
import shoelaces.settings as settings
from PyQt5 import QtCore


class ApplicationWindow(QMainWindow):
    def __init__(self):

        super(ApplicationWindow, self).__init__()
        settings.init(self)
        self.setCentralWidget(None)
        self.setDockNestingEnabled(True);

        self.createMenus()
        self.createDockWidgets()
        self.createToolbar()
        self.createActions()
        self.createSignals()
        self.updateMenu()

        self.selectedtranscripts = []
        self.currentRatio = 0.1
        self.selectedGene = None
        self.geneView = None
        self.transcriptView = None
        self.activeTranscriptRes = None
        self.activeSequenceRes = None
        self.noiseResource = None
        self.configResource = ConfigResource()
        self.processor = sequenceProcessor()
        self.progress = None
        self.offsetWindow = None
        self.runWizardAtStartup = True

        self.processor.processStarted.connect(self.createProgressBar)
        self.processor.processFinished.connect(self.destroyProgressBar)
        self.processor.processUpdated.connect(self.updateProgressBar)


        self.setStyleSheet("QMainWindow::separator { background: rgb(200, 200, 200); width: 2px; height: 2px;}");

        self.configResource = ConfigResource("./test.xml")
        self.loadConfig()
        self.readSettings()
        self.tabify()

        self.show()
        if self.runWizardAtStartup:
            self.startWizard()

    def createActions(self):

        self.actionOpen = QAction('Open',self)
        self.actionSave_Session = QAction('Save project', self)
        self.actionOpen_Session = QAction('Open Session', self)
        self.actionExport_Wig = QAction('Export Wig', self)
        self.actionOffset = QAction('Set Offset', self)
        self.actionBatch = QAction('Batch...', self)
        self.actionWizard = QAction('Wizard', self)

        self.actionToggleTranscripts = QAction('Toggle Include', self)
        self.actionToggleGene = QAction('Toggle Include', self)

        self.menuFile = self.menubar.addMenu('File')
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionOpen_Session)
        self.menuFile.addAction(self.actionSave_Session)
        self.menuFile.addAction(self.actionExport_Wig)
        self.menuFile.addAction(self.actionOffset)
        self.menuFile.addAction(self.actionBatch)
        self.menuFile.addAction(self.actionWizard)

        self.menuWindows = self.menubar.addMenu("Windows")


        self.toolbar.addAction(self.actionOpen)
        self.toolbar.addAction(self.actionExport_Wig)
        self.toolbar.addAction(self.actionSave_Session)
        self.toolbar.addAction(self.actionOffset)
        self.toolbar.addAction(self.actionWizard)

    def createMenus(self):
        self.menubar = QMenuBar(self)
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

    def createToolbar(self):
        self.toolbar = QToolBar("Toolbar",self)
        self.addToolBar(self.toolbar)

    def createDockWidgets(self):
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.North)
        self.mainplot = graphdockwidget('Plot', self)
        self.mainplot.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.resources = resourceDock(self)
        self.resources.setObjectName("Resources")
        self.datastats = statsdockwidget(self)

        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.resources)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.mainplot)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.datastats)

        self.dockTabList = [self.mainplot, self.datastats, self.resources]

    def createSignals(self):
        self.actionOffset.triggered.connect(self.createOffsetDock)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionSave_Session.triggered.connect(self.saveConfigFile)
        self.actionOpen_Session.triggered.connect(self.openConfigFile)
        self.actionExport_Wig.triggered.connect(self.writeWigFile)
        self.actionBatch.triggered.connect(self.runBatch)
        self.actionWizard.triggered.connect(self.startWizard)


        self.resources.useTranscriptResource.connect(self.setActiveTranscriptRes)
        self.resources.useSequenceResource.connect(self.setActiveSequenceRes)
        self.resources.useNoiseResource.connect(self.setNoiseRes)

        self.datastats.refreshStats.connect(self.updateStats)
        self.datastats.filterData.connect(self.applyFilter)

    def updateMenu(self):
        self.menuWindows.clear()
        for a in  self.createPopupMenu().actions():
            self.menuWindows.addAction(a)

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", '',
                    "*.*")
        elements = filename.split('.')
        ext = elements[len(elements) - 1].lower()
        if ext == 'bam':
            #self.reader.openDatafile(filename)
            res = SequenceResource(filename)
            self.resources.append(res)

            res.processStarted.connect(self.createProgressBar)
            res.processFinished.connect(self.destroyProgressBar)
            res.processUpdated.connect(self.updateProgressBar)
            res.load()

        elif ext == 'bed' or ext == 'gtf':
            res = TranscriptResource(filename,ext)
            self.resources.append(res)

            res.processStarted.connect(self.createProgressBar)
            res.processFinished.connect(self.destroyProgressBar)
            res.processUpdated.connect(self.updateProgressBar)
            res.load()

        elif ext == 'xml':
            self.configResource = ConfigResource(filename)
            self.loadConfig()

    def loadFile(self, filename):
        elements = filename.split('.')
        ext = elements[len(elements) - 1].lower()
        if ext == 'bam':
            #self.reader.openDatafile(filename)
            res = SequenceResource(filename)
            self.resources.append(res)

            res.processStarted.connect(self.createProgressBar)
            res.processFinished.connect(self.destroyProgressBar)
            res.processUpdated.connect(self.updateProgressBar)
            res.load()

        elif ext == 'bed' or ext == 'gtf':
            res = TranscriptResource(filename,ext)
            self.resources.append(res)

            res.processStarted.connect(self.createProgressBar)
            res.processFinished.connect(self.destroyProgressBar)
            res.processUpdated.connect(self.updateProgressBar)
            res.load()

        elif ext == 'xml':
            self.configResource = ConfigResource(filename)
            self.loadConfig()

    def openConfigFile(self):

        filename, _ = QFileDialog.getOpenFileName(self, "Open Config File", '',
                    "Config files (*.xml)")
        self.configResource = ConfigResource(filename)
        self.loadConfig()

    def loadConfig(self):
        self.configResource.load()
        for name, res in self.configResource.resources.items():
            self.resources.append(res)

            res.processStarted.connect(self.createProgressBar)
            res.processFinished.connect(self.destroyProgressBar)
            res.processUpdated.connect(self.updateProgressBar)
            res.load()

        for (transcriptID, resourceName) in self.configResource.disabled:
            self.resources.getResource(resourceName).transcripts[transcriptID]['include'] = False

        if self.configResource.activeTranscript:
            self.resources.setSelectedResource(self.configResource.activeTranscript)

        if self.configResource.activeSequence:
            self.resources.setSelectedResource(self.configResource.activeSequence)

        if self.configResource.activeNoise:
            self.resources.setNoiceResource(self.configResource.activeNoise)

        self.currentRatio = self.configResource.currentRatio

        self.processor.lengthOffsets = self.configResource.lengthOffsets



    def saveConfigFile(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Config File", '',
                    "Config files (*.xml)")
        if not filename:
            return
        self.configResource.filename = filename
        self.configResource.resources = self.resources.resources
        self.configResource.lengthOffsets = self.processor.lengthOffsets
        self.configResource.activeTranscript = self.activeTranscriptRes
        self.configResource.activeSequence = self.activeSequenceRes
        self.configResource.activeNoise = self.noiseResource
        if self.offsetWindow:
            self.currentRatio = self.offsetWindow.getRatio()
            self.configResource.currentRatio = self.currentRatio
        self.configResource.write()

    def writeWigFile(self):
        self.runBatch()

    def runBatch(self):
        #print(self.processor.lengthOffsets)
        self.dlg = batchDialog(self.resources.getResources(), self.processor.lengthOffsets)

        if self.dlg.exec_():

            useOffset, split, operation, lengths,relative, transcriptFilename, dataFileNames, outputDirectory = self.dlg.getConfig()
            #print(useOffset, split, operation, lengths, relative, transcriptFilename, dataFileNames, outputDirectory)
            if not transcriptFilename or not dataFileNames or not outputDirectory:
                return
            if self.resources.hasResource(transcriptFilename):
                transcriptRes = self.resources.getResource(transcriptFilename)
            else:
                ext = transcriptFilename.split('.')[-1]
                transcriptRes = TranscriptResource(transcriptFilename,ext)

            self.processor.setTranscripts(transcriptRes)

            for file in dataFileNames:


                if self.resources.hasResource(file):
                    dataResource = self.resources.getResource(file)
                else:
                    dataResource = SequenceResource(file)



                dataResource.setOffsets(self.processor.lengthOffsets)
                dataResource.setUseOffsets(useOffset)

                if not dataResource:
                    continue
                self.processor.setData(dataResource)

                filename = (file.split('/')[-1]).replace(".bam", "")
                
                if relative:
                    self.processor.writeRelativeWigFile(outputDirectory+'/'+filename, lengths, split, useOffset, 'ignore')
                else:
                    self.processor.writeWigFile(outputDirectory+'/'+filename, lengths, split)

    def startWizard(self):
        self.wiz = wizardDialog(self, self.resources.getResourcesDict(), self.runWizardAtStartup)
        self.wiz.show()

        self.wiz.finished.connect(self.endWizard)

    def endWizard(self, result):

        self.runWizardAtStartup = self.wiz.runAtStartup()
        if result:
            resTran = str(self.wiz.transResPage.selectedLabel.text())
            self.resources.setSelectedResource(self.resources.resources[resTran])

            resources = self.wiz.getResources()
            self.resources.clearSelection();
            if resources['sequence'] in self.resources.resources:
                self.resources.setSelectedResource(self.resources.resources[resources['sequence']])
            if resources['transcript'] in self.resources.resources:
                self.resources.setSelectedResource(self.resources.resources[resources['transcript']])
            if resources['noise'] in self.resources.resources:
                self.resources.setNoiceResource(self.resources.resources[resources['noise']])
            if self.wiz.calcOffset:
                self.createOffsetDock()

    def setOffset(self, ID, offset):
        if not(self.processor):
            return

        self.processor.setOffsets(ID, offset)

        try:
            self.datastats.updateOffsets( self.processor.lengthOffsets)
        except:
            return

    def dataLoaded(self,fileName):
        self.statusbar.showMessage("Data file loaded: " + fileName)

    def transcriptLoaded(self, fileName):
        self.statusbar.showMessage("Transcript file loaded: " + fileName)

    def configLoaded(self,fileName):
        self.setWindowTitle("Shoelaces - " + fileName)

    def transcriptSelected(self, transcriptList):

        self.selectedtranscripts = transcriptList

        self.mainplot.updateTranscriptStats(self.selectedtranscripts, self.processor)
        self.mainplot.show()
        self.mainplot.raise_()
        self.activateWindow()

    def geneSelected(self, geneList):

        if not geneList:
            self.selectedGene = None
            self.updateListView(False, True)
            self.mainplot.updateGeneStats(None, self.processor)
            return

        self.selectedGene = geneList[0]
        self.mainplot.updateGeneStats(self.selectedGene, self.processor)
        self.updateListView(False, True)

        self.mainplot.show()
        self.mainplot.raise_()
        self.activateWindow()

    def setActiveTranscriptRes(self, res):
        self.activeTranscriptRes = res

        if self.activeSequenceRes and self.activeTranscriptRes:
            self.activeTranscriptRes.addReadsToGene(self.activeSequenceRes)


        self.createListView()
        self.processor.setTranscripts(self.activeTranscriptRes)

    def setActiveSequenceRes(self, res):
        self.activeSequenceRes = res

        if self.activeTranscriptRes:
            self.activeTranscriptRes.addReadsToGene(self.activeSequenceRes)
            self.createListView()

        if not res:
            return



        if self.noiseResource:
            self.activeSequenceRes.setNoise(self.noiseResource)


        self.processor.setData(self.activeSequenceRes)

    def setNoiseRes(self, res):
        self.noiseResource = res

        if self.activeSequenceRes:
            self.activeSequenceRes.setNoise(self.noiseResource)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def createOffsetDock(self):
        if(not(self.processor)):
            return
        #print("creating offset dock")
        #self.reader.writeToFile(False)
        #return
        if self.offsetWindow:
            self.dockTabList.remove(self.offsetWindow)
            self.offsetWindow.close()
            self.removeDockWidget(self.offsetWindow)

        self.offsetWindow = offsetDock(self, self.processor,self.currentRatio)
        self.offsetWindow.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea | QtCore.Qt.TopDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.offsetWindow)
        self.offsetWindow.emitUpdate.connect(self.setOffset)
        self.offsetWindow.resize(300,100)

        self.updateMenu()
        self.dockTabList.append( self.offsetWindow)

        self.tabify()
        self.offsetWindow.show()
        self.offsetWindow.raise_()
        self.offsetWindow.activateWindow()
        #self.setTabOrder(self.offsetWindow,self.dockTabList[0])

    def createListView(self):
        if not self.activeTranscriptRes:
            self.geneView.clear()
            self.transcriptView.clear()
            return
        if self.activeTranscriptRes.genes and not self.geneView:
            self.geneView = transcriptView('Genes',['Gene Name', '# transcripts', '# reads', 'Chromosome'], self)
            self.geneView.processStarted.connect(self.createProgressBar)
            self.geneView.processFinished.connect(self.destroyProgressBar)
            self.geneView.processUpdated.connect(self.updateProgressBar)
            self.geneView.selectionChanged.connect(self.geneSelected)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.geneView)

        if self.activeTranscriptRes and not self.transcriptView :
            self.transcriptView = transcriptView("Transcripts",['Transcript', 'Gene', 'Chromosome'],self)
            self.transcriptView.processStarted.connect(self.createProgressBar)
            self.transcriptView.processFinished.connect(self.destroyProgressBar)
            self.transcriptView.processUpdated.connect(self.updateProgressBar)
            self.transcriptView.view.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.transcriptView.selectionChanged.connect(self.transcriptSelected)
            self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.transcriptView)

        self.geneView.usageToggled.connect(self.transcriptView.update)
        self.transcriptView.usageToggled.connect(self.geneView.update)
        self.updateListView()
        self.updateMenu()

    def updateListView(self, updateGeneView= True, updateTranscriptView = True ):
        if not self.activeTranscriptRes:
            return

        if updateGeneView and self.geneView:
            self.geneView.clear()

        if self.activeTranscriptRes.genes and updateGeneView:
            self.geneView.updateView(self.activeTranscriptRes.genes, ['gene_id','NoT', 'NoR','chromosome'])

        if updateTranscriptView and self.transcriptView:
            self.transcriptView.clear()
        if self.activeTranscriptRes.transcripts and updateTranscriptView:
            currentTranscripts = {}

            if self.selectedGene:
                currentTranscripts.update(self.selectedGene['transcripts'])
                currentTranscripts.update(self.selectedGene['non_coding'])
            else:
                currentTranscripts.update(self.activeTranscriptRes.transcripts)
                currentTranscripts.update(self.activeTranscriptRes.noncodingtranscripts)
            self.transcriptView.updateView(currentTranscripts, ['transcript_id', 'gene_id', 'chromosome'])

    def updateStats(self):

        if not self.activeSequenceRes or not self.activeTranscriptRes:
            return
        self.activeSequenceRes.setOffsets(self.processor.lengthOffsets)
        self.activeSequenceRes.setUseOffsets(self.datastats.useOffsets())
        self.activeSequenceRes.createWig()

        self.datastats.updateAvailableLengths(self.activeSequenceRes.splitWig['forward'].keys(), self.processor.lengthOffsets)
        self.datastats.updatestats(self.processor, 'global')

    def applyFilter(self):
        self.activeSequenceRes.filter()

    def createProgressBar(self, maxValue, name):


        self.progress = QProgressBar(self)
        self.progress.setRange(0,maxValue)
        self.statusbar.addWidget(self.progress)

        self.statusLabel = QLabel(self.statusbar)
        self.statusLabel.setText(name)
        self.statusbar.addWidget(self.statusLabel)
        self.progress.show()

    def destroyProgressBar(self, value):

        self.statusbar.removeWidget(self.progress)
        self.progress.destroy()

        self.statusbar.removeWidget(self.statusLabel)
        self.statusLabel.destroy()

    def tabify(self):
        first = self.dockTabList[0]
        for a in self.dockTabList[1:]:
            self.tabifyDockWidget(first,a)
            first = a

    def updateProgressBar(self,value):
        self.progress.setValue(value)

    def closeEvent(self,event):

        settings = QSettings("Bio", "Shoelaces")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("startupWizard",self.runWizardAtStartup);

        QMainWindow.closeEvent(self, event)

    def readSettings(self):

        settings = QSettings("Bio", "Shoelaces")
        if settings.value("geometry"):
            self.restoreGeometry(settings.value("geometry"))
        if settings.value("windowState"):
            self.restoreState(settings.value("windowState"))

        if settings.value("startupWizard") == None:
            self.runWizardAtStartup = True
        else:
            self.runWizardAtStartup = bool(settings.value("startupWizard"))



class commandLineApplication:

    def __init__(self, args):



        parser = argparse.ArgumentParser(description='Shoelaces: ribosome profiling analysis pipeline')

        parser.add_argument('-e', '--end', help="use CDS end (default: CDS start)", action="store_true")
        parser.add_argument('-o', '--offset', help="use offsets (Config xml file)", action="store_true")
        parser.add_argument('-a', '--automatic', help="detect offsets", action="store_true")
        parser.add_argument('-r', '--relative', help="output in transcript coordinates (default: genome coordinates)", action="store_true")

        parser.add_argument('-p', '--printplot', help="print out offset plot", action="store_true")
        parser.add_argument('-s', '--split', help="Split wig files based on read lengths", action="store_true")
        parser.add_argument('-lengths', metavar='N', type=int, nargs='*', help='output selected lengths into separate files')
        parser.add_argument('-files', metavar='F', type=str, nargs='*', help='[Config file, BAM file, GTF file, Output file]')

        args = parser.parse_args()

        if not args.files:
            sys.exit("no input file given")

        processor = sequenceProcessor()
        output = ''
        data = None
        transcript = None

        ratio = 1

        for filename in args.files:

            elements = filename.split('.')
            ext = elements[len(elements) - 1].lower()
            name = '.'.join(elements[:len(elements) - 1])
            print (filename, ext)
            if ext == 'xml':
                configRes = ConfigResource(filename)
                configRes.load()
                processor.lengthOffsets = configRes.lengthOffsets
                transcript = configRes.activeTranscript
                data = configRes.activeSequence
                ratio = configRes.currentRatio

            elif ext == 'gtf' or ext == 'bed' and not transcript:
                transcript = TranscriptResource(filename, ext)
            elif ext == 'bam' and not data:
                data = SequenceResource(filename)
            elif ext == 'wig':
                output = name

        if not(transcript):
            print("No active transcript resource")
            return
        if not(data):
            print("No active sequence resource")
            return
        if not output and not args.printplot:
            print("No output-file given")
            return
        transcript.load()
        processor.setTranscripts(transcript)
        processor.setData(data)


        if args.printplot:
            #print(ratio)
            transcript.addReadsToGene(data)
            result = processor.plotDifferenceToCDS(not(args.end), False, ratio)

            freqPlots =  processor.fourierTransform(result)
            common = processor.findUsefulLengths(freqPlots, result)

            filename = transcript.GetName()
            for length in common:
                freqPlot = freqPlots[length]

                f = open(filename + "-" + str(length) + ".frq", "w")
                for freq in sorted(freqPlot.keys()):
                    value = freqPlot[freq]
                    f.write(str(freq) + "\t" + str(value) +"\n")
                f.close()
                positions = sorted(result[length].keys())
                subwig = processor.getSubWig(result[length],positions, -15, 15)
                processor.populateHist(subwig,(-15,15))

                print('Sequence length:', length)
                for pos in sorted(subwig.keys()):
                    print(pos, subwig[pos])

            plots = {}

            for key, wig in result.items():
                hist = processor.getSubWig(wig, sorted(wig.keys()), -15, -5)
                plots[key] = hist

            offsets = processor.detectOffset(plots)
            print("Automatically detected offsets: ", offsets)
            return

        if args.automatic:
            transcript.addReadsToGene(data)
            result = processor.plotDifferenceToCDS(not(args.end), False, ratio)
            freqPlots =  processor.fourierTransform(result)
            common = processor.findUsefulLengths(freqPlots,result)
            plots = {}
            for key, wig in result.items():
                hist = processor.getSubWig(wig, sorted(wig.keys()), -15, -5)
                plots[key] = hist

            offsets = processor.detectOffset(plots)
            for key in common:
                processor.setOffsets(key, offsets[key])

            print("Automatically detected offsets", processor.lengthOffsets)




        offset = args.offset or args.automatic
        if offset:
            data.setUseOffsets(True)
        data.setOffsets(processor.lengthOffsets)
        data.createWig()

        #print("Lenghts: ", args.lengths)
        if not args.lengths:
            args.lengths = []
        split = args.lengths != [] or args.split


        if args.relative:
            processor.writeRelativeWigFile(output, args.lengths, split)
        else:
            processor.writeWigFile(output, args.lengths, split)
