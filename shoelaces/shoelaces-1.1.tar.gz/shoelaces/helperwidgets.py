from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from OpenGL.GLUT import *
from PyQt5.Qt import *
from PyQt5 import QtCore
from shoelaces.resource import resourceItemDelegate
from ctypes import *
import datetime
import math

import shoelaces.settings as settings


class exportDialog(QDialog):
    def __init__(self, offsets, parent=None):
        super(exportDialog, self).__init__(parent)

        self.centerWidget = self
        self.mainLayout = QGridLayout(self.centerWidget)
        self.setLayout(self.mainLayout)

        self.outputType = QComboBox(self.centerWidget)
        self.outputType.addItems(['Single File', 'Per footprint length'])
        self.offsetBox = QComboBox(self.centerWidget)
        self.offsetBox.addItems(['Orginal', 'Use Offsets','Per transcript', 'Per transcript w/offsets'])
        self.offsetBox.setCurrentIndex(1)
        self.mmBox = QComboBox(self.centerWidget)
        self.mmBox.addItems(['Ignore', 'Merge', 'Split'])

        self.fileNameInput = QLineEdit(self.centerWidget)
        self.fileNameButton =  QPushButton('...', self.centerWidget)

        self.okButton = QPushButton("OK",self)
        self.cancelButton = QPushButton("Cancel",self)

        self.offsetBoxes = {}

        for idx, key in enumerate(offsets):
            label = QLabel(str(key) + ': ' + str(offsets[key]), self.centerWidget)
            checkBox = QCheckBox(self.centerWidget)
            self.mainLayout.addWidget(label, 2,idx)
            self.mainLayout.addWidget(checkBox, 3,idx)
            self.offsetBoxes[key] = checkBox

        self.mainLayout.addWidget(QLabel("Output:"), 0, 0)
        self.mainLayout.addWidget(self.outputType, 1, 0)
        self.mainLayout.addWidget(QLabel("Position:"), 0, 1)
        self.mainLayout.addWidget(self.offsetBox, 1, 1)
        self.mainLayout.addWidget(QLabel("Multimappers:"), 0, 2)
        self.mainLayout.addWidget(self.mmBox, 1, 2)

        self.mainLayout.addWidget(QLabel("Filename:"), 4, 0 )
        self.mainLayout.addWidget(self.fileNameInput, 4, 1, 1, 1)
        self.mainLayout.addWidget(self.fileNameButton, 4, 2)
        self.mainLayout.addWidget(self.okButton, 5, 1)
        self.mainLayout.addWidget(self.cancelButton, 5, 2)
        self.offsets = offsets
        self.adjustSize()


        self.okButton.pressed.connect(self.accept)
        self.cancelButton.pressed.connect(self.reject)
        self.fileNameButton.pressed.connect(self.browseFileName)

    def getConfig(self):
        lengths = []
        for length, box in self.offsetBoxes.items():
            if box.checkState():
                lengths.append(length)

        useOffset = self.offsetBox.currentText() == 'Use Offsets' or self.offsetBox.currentText() == 'Per transcript w/offsets'
        relative = self.offsetBox.currentText() == 'Per transcript' or self.offsetBox.currentText() == 'Per transcript w/offsets'
        split = self.outputType.currentText() == 'Per footprint length'
        filename = str(self.fileNameInput.text())
        multimappers = self.mmBox.currentText()
        return useOffset, lengths, filename, split, multimappers, relative

    def browseFileName(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Wig File", '',
                    "Wig files (*.wig)")
        self.fileNameInput.setText(filename)

class batchDialog(QDialog):
    def __init__(self, resources,  offsets, parent=None):
        super(batchDialog, self).__init__(parent)

        self.centerWidget = self
        self.mainLayout = QGridLayout(self.centerWidget)
        self.setLayout(self.mainLayout)

        self.outputType = QComboBox(self.centerWidget)
        self.outputType.addItems(['Single File', 'Per footprint length'])
        self.offsetBox = QComboBox(self.centerWidget)
        self.offsetBox.addItems(['Orginal', 'Use Offsets','Per transcript', 'Per transcript w/offsets'])
        self.offsetBox.setCurrentIndex(1)
        self.mmBox = QComboBox(self.centerWidget)
        self.mmBox.addItems(['Output Wig'])


        self.fileNameInput = QComboBox(self.centerWidget)
        transcriptFiles = []
        self.fileNames = []
        for res in resources:
            if res.GetType() == 'TranscriptResource':
                transcriptFiles.append(res.GetName())
            elif res.GetType() == 'SequenceResource':
                self.fileNames.append(res.GetName())
        self.fileNameInput.addItems(transcriptFiles)

        self.fileNameButton = QPushButton('...', self.centerWidget)

        self.fileNameView = QTreeWidget(self.centerWidget)
        self.fileNameView.setColumnCount(2)
        self.fileNameView.setHeaderLabels(['Include', 'Name'])

        for name in self.fileNames:
            item = QTreeWidgetItem()
            item.setData(1, Qt.DisplayRole, name)

            item.setCheckState(0,Qt.Checked);
            self.fileNameView.addTopLevelItem(item)




        self.addFileButton = QPushButton('Add', self.centerWidget)

        self.directoryOutput = QLineEdit(self.centerWidget)
        self.directoryOutputButton = QPushButton('...', self.centerWidget)

        self.offsetView = QTreeWidget(self.centerWidget)
        self.offsetView.setColumnCount(3)
        self.offsetView.setHeaderLabels(['Include', 'Length', 'Offset'])


        self.okButton = QPushButton("OK",self)
        self.cancelButton = QPushButton("Cancel",self)



        for key, value in offsets.items():
            item = QTreeWidgetItem()
            item.setData(1, Qt.DisplayRole, key)
            item.setData(2, Qt.DisplayRole, value)
            item.setCheckState(0,Qt.Checked);

            self.offsetView.addTopLevelItem(item)


        self.mainLayout.addWidget(QLabel("Output:"), 1, 0)
        self.mainLayout.addWidget(self.outputType, 1, 1)
        self.mainLayout.addWidget(QLabel("Position:"), 1, 2)
        self.mainLayout.addWidget(self.offsetBox, 1, 3)
        #self.mainLayout.addWidget(QLabel("Multimappers:"), 3, 0)
        self.mainLayout.addWidget(self.mmBox, 0,0,1,4)


        self.mainLayout.addWidget(QLabel("Data Files"), 3, 2)
        self.mainLayout.addWidget(self.addFileButton, 3, 3)

        self.mainLayout.addWidget(self.fileNameView, 4, 2, 1, 2)

        self.mainLayout.addWidget(QLabel("Transcript File:"), 2, 0)
        self.mainLayout.addWidget(self.fileNameInput, 2,1, 1, 2)
        self.mainLayout.addWidget(self.fileNameButton, 2, 3)
        self.mainLayout.addWidget(QLabel("Offsets"), 3, 0, 1, 2)
        self.mainLayout.addWidget(self.offsetView, 4, 0, 1, 2)

        self.mainLayout.addWidget(QLabel("Output Directory:"), 5, 0)
        self.mainLayout.addWidget(self.directoryOutput, 5,1, 1, 2)
        self.mainLayout.addWidget(self.directoryOutputButton, 5, 3)


        self.mainLayout.addWidget(self.okButton, 6, 2)
        self.mainLayout.addWidget(self.cancelButton, 6, 3)
        self.offsets = offsets
        self.adjustSize()


        self.okButton.pressed.connect(self.accept)
        self.cancelButton.pressed.connect(self.reject)
        self.fileNameButton.pressed.connect(self.browseTranscriptFileName)
        self.addFileButton.pressed.connect(self.browseFileName)
        self.directoryOutputButton.pressed.connect(self.browseDirectory)

    def getConfig(self):

        lengths = []
        itemIterator =  QTreeWidgetItemIterator(self.offsetView, QTreeWidgetItemIterator.Checked)
        while itemIterator.value():
            item = itemIterator.value()
            key = eval(str(item.data(1,Qt.DisplayRole)))
            lengths.append(key)
            itemIterator += 1


        itemIterator =  QTreeWidgetItemIterator(self.fileNameView, QTreeWidgetItemIterator.Checked)
        dataFiles = []
        while itemIterator.value():


            item = itemIterator.value()

            name = str(item.data(1,Qt.DisplayRole))

            dataFiles.append(name)

            itemIterator += 1

        useOffset = self.offsetBox.currentText() == 'Use Offsets' or self.offsetBox.currentText() == 'Per transcript w/offsets'
        relative = self.offsetBox.currentText() == 'Per transcript' or self.offsetBox.currentText() == 'Per transcript w/offsets'
        split = self.outputType.currentText() == 'Per footprint length'
        operation = str(self.mmBox.currentText())

        transcriptFilename = str(self.fileNameInput.currentText()).replace(".bam","")
        outputDirectory = str(self.directoryOutput.text())

        print ("using lengths:", lengths)

        return useOffset, split, operation, lengths, relative, transcriptFilename, dataFiles, outputDirectory

    def browseTranscriptFileName(self):
        filename= QFileDialog.getOpenFileName(self, 'File', '.', '*.gtf *.bed')
        self.fileNameInput.addItem(filename)

    def browseFileName(self):
        filename= QFileDialog.getOpenFileName(self, 'File', '.', '*.bam')
        self.addFile(filename)

    def browseDirectory(self):

        dirname = QFileDialog.getExistingDirectory(self, 'File', '.')

        self.directoryOutput.setText(dirname)




    def addFile(self, filename):
        if filename == '':
            return
        item = QTreeWidgetItem()
        item.setData(0, Qt.DisplayRole, filename)
        item.setData(1, Qt.CheckStateRole,  Qt.Checked )

        self.fileNameView.addTopLevelItem(item)
        self.fileNames.append(str(filename))

class introPage (QWizardPage):
    def __init__(self, parent):
        super(introPage, self).__init__(parent)
        self.setTitle("Introduction")
        self.layout = QVBoxLayout()
        self.label = QLabel("This wizard will guide you through the process\nof setting up Shoelaces.\n\nYou will need an indexed sequence alignment data file\nin BAM format and gene annotations file in GTF format.")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

class finishPage(QWizardPage):
    def __init__(self, parent):
        self.layout = QVBoxLayout()

class resourcePage (QWizardPage):
    def __init__(self, parent, title, description, resources, fileType):
        super(resourcePage, self).__init__(parent)
        self.setTitle(title)
        self.layout = QVBoxLayout()
        self.resourceView = QListView(self)
        self.resourceView.setAutoFillBackground(True)

        model = QStandardItemModel(self.resourceView)
        self.resourceView.setModel(model)
        self.resourceView.setItemDelegate(resourceItemDelegate(resources, self.resourceView))
        self.resourceView.setWordWrap(True)

        self.resourceView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.resourceView.clicked.connect(self.resourceSelected)
        self.resourceView.setContextMenuPolicy(Qt.CustomContextMenu);

        self.desc = QLabel(description,self)
        self.openFileButton = QPushButton("Open file..", self)
        self.openFileButton.pressed.connect(self.openFile)
        self.fileType = fileType
        self.layout.addWidget(self.desc)
        self.layout.addWidget(self.openFileButton)
        self.layout.addWidget(self.resourceView)
        self.setLayout(self.layout)

        self.selectedLabel =QLineEdit();
        self.pageTitle= title

        self.registerField(title+"*", self.selectedLabel)
        self.updateView()

    def openFile(self):
        filename, _ = QFileDialog.getOpenFileName(settings.getMainApp(), "Open File", '', self.fileType)
        if not filename:
            return;
        settings.getMainApp().loadFile(filename)
        self.updateView();

    def updateView(self):
        resources = settings.getMainApp().resources.getResourcesDict()

        self.resourceView.model().clear()

        for name, resource in resources.items():
            resourceItem = QStandardItem(resource.GetName())

            if resource.GetFileEXT() in self.fileType:
                self.resourceView.model().appendRow(resourceItem)

    def resourceSelected(self, index):

        #item = self.resourceView.model().data(index, Qt.DisplayRole)
        key = str(index.data(Qt.DisplayRole))
        settings.getMainApp()
        self.selectedLabel.setText(key)

    def getResource(self):
        return str(self.selectedLabel.text())

class wizardDialog(QWizard):
    def __init__(self,parent, resources, startup):
        super(wizardDialog, self).__init__(parent)
        self.addPage(introPage(self))
        self.seqResPage = resourcePage(self,"Sequence alignment (BAM)","Select a sequence alignment file.", resources, "*.bam")
        self.addPage( self.seqResPage)
        self.transResPage =resourcePage(self,"Gene annotations (GTF)","Select a gene annotations file.", resources, "*.gtf")
        self.addPage(self.transResPage)
        self.noiseResPage =resourcePage(self,"Gene annotations (GTF)","Select a gene annotations file to define noise regions (optional)", resources, "*.gtf")
        self.addPage(self.noiseResPage)

        widge = QWidget()
        side_widge_layout = QGridLayout(widge)
        widge.setLayout(side_widge_layout)

        self.runAtStartupCheck = QCheckBox()
        self.runAtStartupCheck.setChecked(startup)
        side_widge_layout.addWidget(QLabel("Run wizard at startup"), 0, 0)
        side_widge_layout.addWidget(self.runAtStartupCheck,0,1)

        self.setSideWidget(widge)
        self.currentIdChanged.connect(self.checkStatus)
        self.calcOffset = False;
        layout = [QWizard.BackButton,QWizard.CancelButton, QWizard.NextButton]
        self.setButtonLayout(layout)
        self.setOption(QWizard.NoBackButtonOnStartPage,True)

    def getResources(self):
        res = {}
        res['sequence'] = self.seqResPage.getResource()
        res['transcript'] = self.transResPage.getResource()
        res['noise'] = self.noiseResPage.getResource()

        return res;

    def runAtStartup(self):
        return self.runAtStartupCheck.isChecked()

    def checkStatus(self, id):
        if (self.page(id) == self.noiseResPage):
            self.setOption(QWizard.HaveCustomButton1, True)
            self.setButtonText(QWizard.CustomButton1, "Set offset")
            layout = [QWizard.BackButton,QWizard.CancelButton, QWizard.FinishButton, QWizard.CustomButton1]
            self.customButtonClicked.connect(self.setOffsetClicked)
            self.setButtonLayout(layout)
        else:

            layout = [QWizard.BackButton,QWizard.CancelButton, QWizard.NextButton]
            self.setButtonLayout(layout)


    def setOffsetClicked(self):
        self.calcOffset = True;
        self.done(1)

class saveButton(QPushButton):
    saveAs=pyqtSignal()

    def __init__(self,  icon, parent):
        super(saveButton,self).__init__(icon,"", parent)

    def mousePressEvent(self,e):
        if e.button()==1:
            super(saveButton,self).mousePressEvent(e)
        elif e.button()==2:

            saveAs = QAction('Save as..')
            saveAs.triggered.connect(self.saveAs)

            QMenu.exec([saveAs],e.globalPos())


############################################
## Render Widgets


class glPlotWidget(QOpenGLWidget):

    offsetUpdated = pyqtSignal(int, int)
    def __init__(self, parent=None, ID = -1, data = {}):
        super(glPlotWidget, self).__init__(parent)

        f = QSurfaceFormat()
        f.setVersion(2,1)
        f.setProfile(QSurfaceFormat.CoreProfile)

        f.setSamples(2)
        self.setFormat(f)

        self.setMinimumSize(200, 100)

        self.processor = None

        self.viewCenter = 250
        self.viewTop = 300
        self.viewBottom = -11;

        self.viewLeft = 0
        self.viewRight = 500

        self.interaction = ""
        self.updateHist = False
        self.offset = 0

        self.temp = 0
        self.ID = ID
        self.codon = "start"

        self.mode = "def"
        self.hist_array = []
        self.color_array = []
        self.maxValue = 0
        self.barSize = 0.9
        self.xAxisIncr = 1
        self.displayOffset = True;
        self.displayMaxValue = True;
        self.renderYaxis = False
        self.renderXaxis = True
        self.yAxisWidth = 1
        self.yAxis = []
        self.xAxis = []


        self.textOverlayImage = QImage()
        self.textTexture = -1

        self.imageSize = QSize(1, 1)

        self.originalHistogram = {}
        self.glElementFormat = GL_QUADS
        self.glElementSize = 4



        if data:
            self.updatePlot(data)
        self.saveGraphButton = saveButton(QIcon(settings.appDir()+"/shoelaces/resources/save-icon.png"), self)
        self.saveGraphButton.clicked.connect(self.saveGraph)
        self.saveGraphButton.saveAs.connect(self.saveGraphAs)
        self.saveGraphButton.setVisible(False)
        self.setMouseTracking(True)


    def updatePlot(self, histogram, alternatingColor = [[1.0,0,0],[0.3,0.5,0.8]]):
        return

    def updateTextOverlay(self, fontSize = 12):
        self.textOverlayImage = QImage(self.imageSize, QImage.Format_ARGB32)
        font = QFont("Helvetica", fontSize)
        metric = QFontMetrics(font)
        painter = QPainter(self.textOverlayImage)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(0,0,self.imageSize.width(),self.imageSize.height(),QColor(0,0,0,0))
        painter.setFont(font);


        yRatio = self.imageSize.height() / float((self.viewTop - self.viewBottom))
        xRatio = self.imageSize.width() / float((self.viewRight - self.viewLeft))

        if self.displayMaxValue:
            text = '{:.0f}'.format(self.maxValue)
            painter.drawText(self.imageSize.width()- metric.width(text), 10*yRatio, text)

        ###########################
        ## X axis
        if self.renderXaxis:
            for (v1,v2) in self.xAxis:
                value = v1[0]
                text =  str(round(value))
                pos = self.glToImagePos(v1)
                width = metric.width(text)/2
                yPos =self.imageSize.height() - (5*yRatio)
                # if self.imageSize.height()  - yPos  < metric.height():
                #
                #     yPos -=  metric.height() - (self.imageSize.height()  - yPos)
                painter.drawText(pos[0] - width , yPos, text)



        ###########################
        ## Y axis
        if self.renderYaxis:
            for (v1,v2) in self.yAxis:

                value = self.posToValue(v1[1])
                text = str(round(value))
                width = metric.width(text)
                pos = self.glToImagePos(v1)
                painter.drawText( self.imageSize.width() - width ,  pos[1], text)

        if self.displayOffset:
            text = "Offset: " + str(self.offset+self.temp)

            painter.drawText(5, 10*yRatio, text)
        painter.end()

    def createXAxis(self, left, right):

        self.xAxis = []
        if self.renderYaxis:
            right -= 0.5

        xoffset = self.barSize*0.5

        for i in range(int(left),int(right+1), self.xAxisIncr):

            self.xAxis.append(([i + xoffset, self.viewBottom, 0],[i + xoffset,self.viewBottom +5, 0]))

    def setOffset(self, offset):
        return

    def renderTranscript(self):
        return

    def render(self):
        if not self.hist_array:
            return

        if self.updateHist and self.hist_array:

            glBindBuffer (GL_ARRAY_BUFFER, self.vboHist)
            glBufferData (GL_ARRAY_BUFFER, len(self.hist_array)*self.glElementSize,  (c_float*len(self.hist_array))(*self.hist_array), GL_STATIC_DRAW)

            glBindBuffer (GL_ARRAY_BUFFER, self.cboCol)
            glBufferData (GL_ARRAY_BUFFER, len(self.color_array)*self.glElementSize,  (c_float*len(self.color_array))(*self.color_array), GL_STATIC_DRAW)



        self.renderTranscript()

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        drawLeft = self.viewLeft + (self.offset+self.temp)
        drawRight = self.viewRight + (self.offset+self.temp)


        gluOrtho2D(drawLeft, drawRight, self.viewBottom, self.viewTop)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glBindBuffer(GL_ARRAY_BUFFER, self.cboCol)
        glColorPointer(3,GL_FLOAT,0,None)


        glBindBuffer (GL_ARRAY_BUFFER, self.vboHist)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glDrawArrays(self.glElementFormat, 0, int(len(self.hist_array)/3))

    def renderText(self):
        if not self.hist_array:
            return
        if not self.textTexture:
            glGenTextures( 1, self.textTexture );
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.textOverlayImage.width(), self.textOverlayImage.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, None )


        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)

        ptr = self.textOverlayImage.bits()
        ptr.setsize(self.textOverlayImage.byteCount())

        ## copy the data out as a string
        strData = ptr.asstring()

        ## get a read-only buffer to access the data
        buf = memoryview(ptr)

        ## view the data as a read-only numpy array

        arr = np.frombuffer(buf, dtype=np.ubyte).reshape(self.textOverlayImage.height(), self.textOverlayImage.width(), 4)

        glActiveTexture(GL_TEXTURE0)

        glBindTexture( GL_TEXTURE_2D, self.textTexture );

        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR );
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR );
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.textOverlayImage.width(), self.textOverlayImage.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, arr )

        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();
        gluOrtho2D(self.viewLeft , self.viewRight , self.viewBottom, self.viewTop)
        glMatrixMode(GL_MODELVIEW);
        glLoadIdentity();
        #glTranslate(0,self.viewBottom+5,0)
        glBegin(GL_QUADS)

        glTexCoord2f(0.0,1.0)
        glVertex3f(self.viewLeft,self.viewBottom,0.0)
        glTexCoord2f(1.0,1.0)
        glVertex3f(self.viewRight,self.viewBottom,0.0)
        glTexCoord2f(1.0,0.0)
        glVertex3f(self.viewRight,self.viewTop,0.0)
        glTexCoord2f(0.0,0.0)
        glVertex3f(self.viewLeft,self.viewTop,0.0)

        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)

    def renderScale(self):
        if not self.hist_array:
            return
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluOrtho2D(self.viewLeft , self.viewRight , self.viewBottom, self.viewTop)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glColor3f(0,0,0)

        glLineWidth(1)
        glLineStipple(1,0x0307)
        glEnable(GL_LINE_STIPPLE)

        glBegin(GL_LINES)
        glVertex3f(self.viewLeft,100 ,0)
        glVertex3f(self.viewRight,100 ,0)
        glEnd()
        glDisable(GL_LINE_STIPPLE)

    def renderaxis(self, l, r, t, b):
        if not self.hist_array:
            return

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluOrtho2D(self.viewLeft , self.viewRight , self.viewBottom, self.viewTop)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glBegin(GL_LINES)
        if self.renderXaxis:
            for pos in self.xAxis:
                glVertex(pos[0])
                glVertex(pos[1])

        if self.renderYaxis:
            for pos in self.yAxis:
                glVertex(pos[0])
                glVertex(pos[1])

        glEnd()

    def paintGL(self):
        glClearColor(1.0,1.0,1.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.render()
        self.renderScale()
        self.renderaxis(self.viewLeft,self.viewRight, self.viewTop, self.viewBottom)

        self.renderText()

        glFlush()

    def resizeGL(self, w, h):

        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        self.imageSize = QSize(w,h)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.imageSize.width(), self.imageSize.height(), 0, GL_RGBA, GL_UNSIGNED_BYTE,None )

        self.updateTextOverlay()

    def initializeGL(self):


        self.vboHist = glGenBuffers(1)


        self.cboCol = glGenBuffers(1)
        glutInit()

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #gluPerspective(40.0, 1.0, 1.0, 30.0)

        self.updateTextOverlay()

    def saveGraphAs(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Image", '',
                    "images (*.png)")
        if not filename:
            return

        self.saveGraph(filename)

    def saveGraph(self, filename=""):
        if filename == "" or type(filename) is bool:
            filename=str(datetime.datetime.now())+'.png'
        s = self.size()
        self.resize(640,480)
        self.updateTextOverlay(24)
        self.update()
        output = self.grabFramebuffer()
        self.resize(s)
        output.save(filename)

    def getCanvasPos(self, pos):

        relX = pos.x() / float(self.width())
        relY = pos.y() / float(self.height())
        viewX = (relX* float(self.viewRight - self.viewLeft)) + self.viewLeft
        viewY = (relY* float(self.viewTop - self.viewBottom)) + self.viewBottom
        result = QtCore.QPoint(viewX, viewY)
        return result

    def eventFilter(self, widget, event):

        return super(self).eventFilter(self, widget, event)

    def enterEvent(self, QEvent):
        self.saveGraphButton.setVisible(True)

    def leaveEvent(self, QEvent):
        self.saveGraphButton.setVisible(False)

    def glToImagePos(self,pos):
        xRatio = self.imageSize.width() / float((self.viewRight - self.viewLeft))
        x = pos[0]

        x -= self.viewLeft
        x *= xRatio

        y = pos[1]
        y -= self.viewBottom
        y /= float(self.viewTop - self.viewBottom)
        y = 1 - y
        y *= self.imageSize.height()

        return (x , y )

    def imageToGlPos(self,pos):
        x = float(pos.x()) / float(self.imageSize.width());
        y = 1.0 - (float(pos.y()) / float(self.imageSize.height()));



        x = x * (self.viewRight - self.viewLeft) + self.viewLeft;
        y = y * (self.viewTop - self.viewBottom) + self.viewBottom;



        return (x , y )

    def posToValue(self, y):
        if y < 0:
            return 0
        y /= (self.viewTop-10)
        if y >= 1.0:
            return self.maxValue
        return y * self.maxValue

    def valueToPos(self, value):
        y = value / self.maxValue
        y *= self.viewTop - 10
        return y

    # def mouseMoveEvent(self, e):
    #     tempPos =e.pos()
    #     relY = tempPos.y() / float(self.height())
    #     relY = 1 - relY
    #
    #     viewY = (relY* float(self.viewTop - self.viewBottom)) + self.viewBottom
    #     print(self.posToValue(viewY))

class glStatsPlotWidget(glPlotWidget):

    offsetUpdated = pyqtSignal(int, int)

    def __init__(self, parent=None, ID = -1, histogram = {}, codon = "start"):
        super(glStatsPlotWidget, self).__init__(parent, ID, histogram)

        self.codon = codon
        self.mode = "hist"
        self.renderYaxis = True
        self.displayOffset = False

    def updatePlot(self, histogram, alternatingColor = [[1.0,0,0],[0.3,0.5,0.8]]):
        glDeleteBuffers(2, [self.vboHist, self.cboCol])
        self.vboHist = glGenBuffers(1)
        self.cboCol = glGenBuffers(1)

        self.hist_array = []
        self.color_array = []
        maxValue = 1;
        maxX = 0
        minX = 0

        counter = 0

        for diff in sorted(histogram.keys()):

            value = histogram[diff]

            color = alternatingColor[1]
            self.color_array += color
            counter +=1;

            self.hist_array += [float(diff), float(value), 0]
            self.hist_array += [float(diff), 0, 0]
            self.hist_array += [float(diff) + self.barSize, 0, 0]
            self.hist_array += [float(diff) + self.barSize, float(value), 0]

            self.color_array += color
            self.color_array += color
            self.color_array += color

            maxValue = max(value, maxValue)

            maxX = max(diff, maxX)
            minX = min(diff, minX)


        self.maxValue = maxValue

        if self.maxValue > 0:
            fScale = 100.0/float(self.maxValue)
        else:
            fScale = 0
        for i in range(0, len(self.hist_array), 3):
            self.hist_array[i+1] *= fScale

        self.viewTop = 100 + 10


        self.viewLeft = float(min(histogram.keys()))


        self.viewRight = float(max(histogram.keys())+self.barSize)
        if self.renderYaxis:
            self.viewRight += 0.3
            self.yAxisWidth = 0.1

        self.updateHist = True
        self.updateTextOverlay()
        self.update()

        self.originalHistogram = histogram

        self.createXAxis(self.viewLeft,self.viewRight)
        self.createYAxis(0, self.viewTop)

    def createYAxis(self, bottom, top):
        self.yAxis = []
        if not self.hist_array or not self.maxValue:
            return

        numberOfDigits = int(math.log10(self.maxValue))
        divider = math.pow(10,numberOfDigits)



        numberOfLines = self.maxValue/divider
        while (numberOfLines < 2 and divider >=2):
            divider /= 2.0
            numberOfLines = self.maxValue/divider




        for i in range(0,self.maxValue, int(divider)):
            ypos = self.valueToPos(i)
            self.yAxis.append(([self.viewRight, ypos, 0],[self.viewRight - self.yAxisWidth ,ypos, 0] ))

class glGenePlotWidget(glPlotWidget):
    def __init__(self, parent, transcript = None, reads = []):


        super(glGenePlotWidget, self).__init__( parent)
        self.setMinimumSize(500, 300)
        self.transcripts = []
        self.noncoding= []

        self.reads = reads
        self.transcripThickness = 10
        self.maxWidth = 500
        self.padding  = 100
        self.gap = self.padding/10
        self.vgap = self.padding/20

        self.vboHist = 0
        self.exonBins  = []
        self.renderYaxis = False
        self.renderXaxis = False
        self.displayOffset = False
        self.binTorender = None

    def checkOverlap(self, pos, size):
        res = []
        for  bin in self.exonBins:
            if pos < bin['start'] and pos + size > bin['start']:
                res.append( bin)
            if pos >= bin['start'] and pos <=  bin['end']:
                res.append(bin)
            if pos < bin['start'] and pos+size > bin['end']:
                res.append( bin)
        return res

    def updateGene(self, gene):

        self.noncoding = []
        self.transcripts = []
        for key, t in gene['transcripts'].items():

            self.transcripts.append(t)

        self.noncoding = []
        for key, t in gene['non_coding'].items():
            self.noncoding.append(t)

        self.updateTranscriptData()

    def addTranscriptToBins(self, transcript):
        for size, pos in zip(transcript['exon_sizes'], transcript['exon_positions']):
            currentBins = self.checkOverlap(pos, size)



            if currentBins:
                minStart = currentBins[0]['start']
                maxEnd = currentBins[0]['end']

                for b in currentBins:
                    minStart = min(b['start'],minStart)
                    maxEnd = max(b['end'], maxEnd)
                    if b in self.exonBins:
                        self.exonBins.remove(b)
                bin = {}
                bin['start'] = min(minStart,pos)
                bin['end'] = max(maxEnd, pos + size)
                bin['size'] = bin['end'] - bin['start']
                self.exonBins.append(bin)

            else:
                bin = {}
                bin['start'] = pos
                bin['end'] = pos + size
                bin['size'] = size
                self.exonBins.append(bin)

    def updateTranscript(self, transcripts):
        self.noncoding = []
        self.transcripts = transcripts.copy()

        self.updateTranscriptData()

    def updateTranscriptData(self):
        self.exonBins = []
        reverseStrand = False;
        for t in self.transcripts:
            self.addTranscriptToBins(t)
            #reverseStrand = not t['forward']
        for t in self.noncoding:
            self.addTranscriptToBins(t)

        self.exonBins = sorted(self.exonBins, key=lambda bin: bin['start'] )


        self.gap= self.padding/(len(self.exonBins) + 2)
        self.transcriptWidth  = 0
        currentPos = 0;

        for i, bin in enumerate(self.exonBins):

            self.transcriptWidth += bin['size'] + self.gap
            bin['draw_start'] = currentPos
            bin['draw_end'] = currentPos + bin['size'] + 1
            print(bin['start'], currentPos)
            currentPos = bin['draw_end'] +  self.gap







        self.maxWidth = self.padding + self.transcriptWidth
        self.viewLeft = 0
        self.viewCenter = self.maxWidth / 2
        self.viewRight = self.maxWidth
        if reverseStrand:
            self.viewLeft = self.maxWidth
            self.viewRight = 0

        self.transcripThickness = self.vgap - 2

        self.viewBottom = - (len(self.transcripts)+len(self.noncoding)) * (self.transcripThickness*2 + self.vgap)

        self.update()



    def updateData(self, histogram):
        glDeleteBuffers(3, [self.vboHist, self.cboCol, self.cboCol2])
        self.vboHist = glGenBuffers(1)
        self.cboCol = glGenBuffers(1)
        self.cboCol2 = glGenBuffers(1)
        self.reads_array = []


        self.hist_array = []
        self.color_array = []
        maxValue = 0;

        histogramPos = sorted(histogram)


        color_array_2 = []
        for pos in histogramPos:
            value = histogram[pos]

            bin  = self.checkOverlap(pos, 1)
            if not bin:
                continue
            diff = pos - bin[0]['start']
            x = bin[0]['draw_start'] + diff

            self.hist_array += [x, value, 0]
            self.hist_array += [x, 0, 0]
            if pos % 3 == 1:
                color= [1.0,0.0,0.0]
            else:
                color = [0.3,0.5,0.8]
            self.color_array += color
            self.color_array += color

            color_array_2 += [0.3,0.5,0.8]
            color_array_2 += [0.3,0.5,0.8]

            maxValue = max(value, maxValue)



        self.maxValue = maxValue
        if self.maxValue > 0:
            fScale = 100.0/float(self.maxValue)
        else:
            fScale = 0
        for i in range(0, len(self.hist_array), 3):
            self.hist_array[i+1] *= fScale




        self.viewTop = 100 + 10


        glBindBuffer (GL_ARRAY_BUFFER, self.vboHist)

        glBufferData (GL_ARRAY_BUFFER, len(self.hist_array)*4,  (c_float*len(self.hist_array))(*self.hist_array), GL_STATIC_DRAW)

        glBindBuffer (GL_ARRAY_BUFFER, self.cboCol)
        glBufferData (GL_ARRAY_BUFFER, len(self.color_array)*4,  (c_float*len(self.color_array))(*self.color_array), GL_STATIC_DRAW)

        glBindBuffer (GL_ARRAY_BUFFER, self.cboCol2)
        glBufferData (GL_ARRAY_BUFFER, len(self.color_array)*4,  (c_float*len(color_array_2))(*color_array_2), GL_STATIC_DRAW)
        self.updateTextOverlay()
    def initializeGL(self):
        self.vboHist = glGenBuffers(1)
        self.cboCol = glGenBuffers(1)
        self.cboCol2 = glGenBuffers(1)
        glutInit()
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClearDepth(1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.updateTextOverlay()

    def paintGL(self):

        glClearColor(1.0,1.0,1.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        i = 0
        for t in self.transcripts:
            self.renderTranscript(t, i)
            i+=1

        for t in self.noncoding:
            self.renderTranscript(t, i, [0.8,0.1,0.1])
            i+=1

        if not self.transcripts or not self.vboHist:
            return

        glOrtho(self.viewLeft, self.viewRight, self.viewBottom, self.viewTop,-1,1)


        color = [0.1,0.1,0.8]
        glColor3fv(color)
        windowWidth = self.width()
        viewWidth = abs(self.viewRight - self.viewLeft)
        pixelsPerNuc = float(windowWidth)/float(viewWidth)

        pixelRatio = settings.getMainApp().devicePixelRatio()
        self.lineWidth = max(3,pixelsPerNuc*0.9*pixelRatio)

        maxWidth = glGetFloat(GL_ALIASED_LINE_WIDTH_RANGE)
        self.lineWidth = min(self.lineWidth, maxWidth[1])

        glLineWidth(self.lineWidth)
        lineImprint = self.lineWidth / float(self.imageSize.width())
        lineImprint *= viewWidth

        #print(maxWidth, self.lineWidth)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glColor3f(0.3, 0.5, 0.8)
        glTranslatef(lineImprint/2.0,0,0)

        if self.lineWidth <4:
            glBindBuffer(GL_ARRAY_BUFFER, self.cboCol2)
        else:
            glBindBuffer(GL_ARRAY_BUFFER, self.cboCol)

        glColorPointer(3,GL_FLOAT,0,None)
        glBindBuffer (GL_ARRAY_BUFFER, self.vboHist)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glDrawArrays(GL_LINES, 0, len(self.hist_array))

        glColor3f(0,0,0)
        glLineWidth(2)
        self.renderText()
        glLineStipple(1,0x0307)
        glEnable(GL_LINE_STIPPLE)

        glBegin(GL_LINES)
        glVertex3f(self.viewLeft,100 ,0)
        glVertex3f(self.viewRight,100,0)
        glEnd()
        glDisable(GL_LINE_STIPPLE)
        #self.renderBin(self.binTorender)
        glFlush()


    def renderTranscript(self, transcript, idx, color = [0.1,0.1,0.8]):

        if not transcript:
            return

        reverseStrand = not transcript['forward']

        exonSizes = transcript['exon_sizes']
        exonPositons = transcript['exon_positions']

        #currentPos = self.gap


        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(self.viewLeft, self.viewRight, self.viewBottom, self.viewTop)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glColor3fv(color)
        glEnable(GL_DEPTH_TEST)
        glBegin(GL_QUADS)

        thickness = self.transcripThickness
        center =  -(self.vgap * idx + self.transcripThickness *2 * idx) - self.vgap

        for i, s in enumerate(exonSizes):
            glColor3fv(color)
            bin = self.checkOverlap(exonPositons[i], s)
            #endBin = self.checkOverlap(exonPositons[i]+s, 1)

            size_render = s + 1
            if not bin:
                continue
            # if(endBin != bin and endBin):
            #
            #     size_render -= (endBin['start'] - bin['end'])
            #     size_render += self.gap

            diff = exonPositons[i] - bin[0]['start']

            currentPos = bin[0]['draw_start'] + diff


            if (i == transcript['start_exon'] and not reverseStrand) or (i == transcript['end_exon'] and  reverseStrand):


                toCDS = transcript['CDS_min'] - exonPositons[i]



                glVertex(currentPos, center - thickness, 0)
                glVertex(currentPos + toCDS, center - thickness, 0)
                glVertex(currentPos + toCDS, center + thickness, 0)
                glVertex(currentPos, center + thickness, 0)

                thickness *= 1.2

                glVertex(currentPos + toCDS, center - thickness, 0)
                glVertex(currentPos + size_render, center  - thickness, 0)
                glVertex(currentPos + size_render, center + thickness, 0)
                glVertex(currentPos + toCDS, center + thickness, 0)


                if reverseStrand:
                    glColor3fv([0.8,0.1,0.1]);

                    glVertex(currentPos + toCDS-3, center - thickness, 1)
                    glVertex(currentPos+ toCDS, center - thickness, 1)
                    glVertex(currentPos + toCDS, center + thickness, 1)
                    glVertex(currentPos + toCDS-3, center + thickness, 1)
                else:


                    glColor3fv([0.1,0.8,0.1]);

                    glVertex(currentPos+ toCDS, center - thickness, 1)
                    glVertex(currentPos+ toCDS + 3, center - thickness, 1)
                    glVertex(currentPos+ toCDS + 3, center + thickness, 1)
                    glVertex(currentPos+ toCDS, center + thickness, 1)


            elif (i == transcript['end_exon'] and not reverseStrand) or (i == transcript['start_exon'] and  reverseStrand):

                toCDS = transcript['CDS_max'] - exonPositons[i] + 1

                if  reverseStrand:
                    glColor3fv([0.1,0.8,0.1]);

                    glVertex(currentPos + toCDS-3, center - thickness, 1)
                    glVertex(currentPos + toCDS, center - thickness, 1)
                    glVertex(currentPos + toCDS, center + thickness, 1)
                    glVertex(currentPos + toCDS-3, center + thickness, 1)
                else:


                    glColor3fv([0.8,0.1,0.1]);

                    glVertex(currentPos+ toCDS, center - thickness, 1)
                    glVertex(currentPos+ toCDS + 3, center - thickness, 1)
                    glVertex(currentPos+ toCDS + 3, center + thickness, 1)
                    glVertex(currentPos+ toCDS, center + thickness, 1)
                glColor3fv(color)
                glVertex(currentPos, center - thickness, 0)
                glVertex(currentPos + toCDS, center - thickness, 0)
                glVertex(currentPos + toCDS, center + thickness, 0)
                glVertex(currentPos, center + thickness, 0)

                thickness /= 1.2

                glVertex(currentPos + toCDS, center - thickness, 0)
                glVertex(currentPos + size_render, center - thickness, 0)
                glVertex(currentPos + size_render, center + thickness, 0)
                glVertex(currentPos + toCDS , center + thickness, 0)


            else:
                glVertex(currentPos, center - thickness, 0)
                glVertex(currentPos + size_render, center - thickness, 0)
                glVertex(currentPos + size_render, center + thickness, 0)
                glVertex(currentPos, center + thickness, 0)




        glEnd()

    def renderBin(self, bin):

        if not bin:
            return
        print(bin)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(self.viewLeft, self.viewRight, self.viewBottom, self.viewTop)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glColor3fv([0.1,0.5,0.1])
        glDisable(GL_DEPTH_TEST);
        glBegin(GL_QUADS)

        center =  0;
        thickness = 10;


        glVertex(bin['draw_start'], center - thickness, 0)
        glVertex(bin['draw_end'] , center - thickness, 0)
        glVertex(bin['draw_end'] , center + thickness, 0)
        glVertex(bin['draw_start'] , center+ thickness, 0)


        glEnd()

    def mousePressEvent(self, e):



        if e.button() == 1:
            self.interaction = "translate"
        elif e.button() == 2:
            self.interaction = "zoom"

        canvasPos = self.getCanvasPos(e.pos())

        self.startPos = canvasPos

        self.newCenter = canvasPos.x()
        self.update()

    def mouseMoveEvent(self, e):

        self.currentPos = self.getCanvasPos(e.pos())
        (x,y) = self.imageToGlPos(e.pos());

        self.binTorender = self.getBin(x)
        if self.binTorender:
            ref_pos = x - self.binTorender['draw_start'] + self.binTorender['start']
            print(round(ref_pos), round(self.posToValue(y) + 0.5))

        if self.interaction == "zoom":

            diff = self.currentPos.x() - self.startPos.x()


            currentWidth =  abs(self.viewRight - self.viewLeft)
            ratioLeft = abs(self.newCenter - self.viewLeft) / float(currentWidth)
            ratioRigth = abs(self.viewRight - self.newCenter) / float(currentWidth)

            if  abs(self.viewRight - self.viewLeft) > diff:
                self.viewLeft += diff * ratioLeft
                self.viewRight -= diff * ratioRigth
                self.viewCenter = (self.viewRight + self.viewLeft)/2.0



        elif self.interaction == "translate":

            diff = self.currentPos.x() - self.startPos.x()
            self.viewLeft -= diff
            self.viewRight -= diff

            self.viewCenter = (self.viewRight + self.viewLeft)/2

        self.update()

    def mouseReleaseEvent(self, QMouseEvent):

        self.interaction = ""

    def getBin(self, glPos_x):
        for bin in self.exonBins:
            if bin['draw_start'] <= glPos_x <= bin['draw_end']:
                return bin

        return None

class glOffsetPlotWidget(glPlotWidget):

    offsetUpdated = pyqtSignal(int, int)

    def __init__(self, parent=None, ID = -1, histogram = {}, codon = "start"):
        super(glOffsetPlotWidget, self).__init__(parent, ID, histogram)

        self.codon = codon
        self.mode = "hist"
        self.xAxisIncr = 5

    def updatePlot(self, histogram, alternatingColor = [[1.0,0,0],[0.3,0.5,0.8]]):

        self.hist_array = []
        self.color_array = []
        maxValue = 1;
        maxX = 0
        minX = 0
        counter = 0;
        for diff in sorted(histogram.keys()):

            value = histogram[diff]
            colorOffset = ((self.temp+self.offset-diff)%3)
            if self.codon == 'stop':
                colorOffset = ((self.temp+self.offset-diff)%3)

            if colorOffset % 3 == 0:
                color= alternatingColor[0]
            else:
                color = alternatingColor[1]
            self.color_array += color
            counter +=1;

            self.hist_array += [float(diff), float(value), 0]
            self.hist_array += [float(diff), 0, 0]
            self.hist_array += [float(diff) + self.barSize, 0, 0]
            self.hist_array += [float(diff) + self.barSize, float(value), 0]

            self.color_array += color
            self.color_array += color
            self.color_array += color

            maxValue = max(value, maxValue)

            maxX = max(diff, maxX)
            minX = min(diff, minX)

        self.maxValue = maxValue

        if self.maxValue > 0:
            fScale = 100.0/float(self.maxValue)
        else:
            fScale = 0
        for i in range(0, len(self.hist_array), 3):
            self.hist_array[i+1] *= fScale

        self.viewTop = 100 + 10

        if self.codon == "start":
            self.viewLeft = float(-30)
            self.viewRight = float(10)
        else:
            self.viewLeft = float(-10)
            self.viewRight = float(30)
        self.updateHist = True
        self.updateTextOverlay()
        self.update()

        self.originalHistogram = histogram

        self.createXAxis(self.viewLeft,self.viewRight)

    def setOffset(self, offset):
        self.offset = offset

        if self.mode == "def":
            self.updateHist = True
        else:
            self.updatePlot(self.originalHistogram)
        self.updateTextOverlay()

        self.update()

    def renderTranscriptPart(self, thickness, start, end):
        glBegin(GL_QUADS)

        center = (self.viewTop + self.viewBottom) / 2.0

        glVertex(start, center - thickness, 0)
        glVertex(end, center - thickness, 0)
        glVertex(end, center + thickness, 0)
        glVertex(start, center + thickness, 0)

        glEnd()

    def renderTranscript(self):

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        gluOrtho2D(self.viewLeft, self.viewRight , self.viewBottom, self.viewTop)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glColor4f(0.1,0.1,0.8,0.3)

        thin = (self.viewTop + self.viewBottom) / 4.0
        thick = thin * 1.6
        if self.codon == "start":
            self.renderTranscriptPart(thin, self.viewLeft, 0)
            self.renderTranscriptPart(thick,3,self.viewRight)
            glColor4f(0.1,0.8,0.1,0.4)
            self.renderTranscriptPart(thick,0,3)
        else:
            self.renderTranscriptPart(thick, self.viewLeft, 0)
            self.renderTranscriptPart(thin,3,self.viewRight)
            glColor4f(0.8,0.1,0.1,0.4)
            self.renderTranscriptPart(thick,0,3)

    def mousePressEvent(self, e):

        if e.button() == 1:
            self.interaction = "translate"

        canvasPos = self.getCanvasPos(e.pos())

        self.startPos = canvasPos


        self.update()

    def mouseMoveEvent(self, e):




        self.currentPos = self.getCanvasPos(e.pos())

        if self.interaction == "translate":


            diff = self.currentPos.x() - self.startPos.x()
            self.temp = -int(diff)
            if self.mode == "def":
                    self.updateHist = True
            else:
                self.updatePlot(self.originalHistogram)




        self.updateTextOverlay()
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        self.offset += self.temp
        self.temp = 0
        self.offsetUpdated.emit( self.ID,self.offset)
        self.interaction = ""

class glGraphPlotWidget(glPlotWidget):

    offsetUpdated = pyqtSignal(int, int)

    def __init__(self, parent=None, ID = -1, histogram = {}, codon = "start"):
        super(glGraphPlotWidget, self).__init__(parent, ID, {})

        self.glElementType = GL_LINE_STRIP
        self.glElementSize = 1

        self.displayOffset = False
        self.barSize = 0.1
        self.codon = codon
        self.mode = "graph"
        self.updatePlot(histogram)




    def updatePlot(self, histogram, alternatingColor = [[1.0,0,0],[0.3,0.5,0.8]]):
        self.hist_array = []
        self.color_array = []
        maxValue = 1;
        maxX = 0
        minX = 0

        counter = 0;

        for diff in sorted(histogram.keys()):
            value = histogram[diff]
            color = alternatingColor[1]
            self.color_array += color
            counter +=1;
            self.hist_array += [float(diff), float(value), 0]
            maxValue = max(value, maxValue)

            maxX = max(diff, maxX)
            minX = min(diff, minX)


        self.maxValue = maxValue

        if self.maxValue > 0:
            fScale = 100.0/float(self.maxValue)
        else:
            fScale = 0
        for i in range(0, len(self.hist_array), 3):
            self.hist_array[i+1] *= fScale

        self.viewTop = 100 + 10


        self.viewLeft = float(0)
        self.viewRight = float(10)

        self.updateHist = True
        self.updateTextOverlay()
        self.update()

        self.originalHistogram = histogram

        self.createXAxis(self.viewLeft,self.viewRight)

    def render(self):

        if not self.hist_array:
            return

        if self.updateHist:
            glEnableClientState (GL_VERTEX_ARRAY)
            glBindBuffer (GL_ARRAY_BUFFER, self.vboHist)
            glBufferData (GL_ARRAY_BUFFER, len(self.hist_array)*4,  (c_float*len(self.hist_array))(*self.hist_array), GL_STATIC_DRAW)


        glPointSize(10)
        glLineWidth(2)
        glColor3f(0.3,0.5,0.8)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        drawLeft = self.viewLeft + (self.offset+self.temp)
        drawRight = self.viewRight + (self.offset+self.temp)
        gluOrtho2D(drawLeft, drawRight, self.viewBottom, self.viewTop)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glBindBuffer (GL_ARRAY_BUFFER, self.vboHist)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glDrawArrays(GL_LINE_STRIP, 0, int(len(self.hist_array)/3))

        #self.renderXaxis(drawLeft,drawRight)

class glModularPlotWidget(glPlotWidget):

    offsetUpdated = pyqtSignal(int, int)

    def __init__(self, parent=None, ID = -1, histogram = {}, codon = "start"):
        super(glModularPlotWidget, self).__init__(parent, ID, histogram)

        self.codon = codon
        self.mode = "def"

    def updatePlot(self, histogram, alternatingColor = [[1.0,0,0],[0.3,0.5,0.8]]):

        self.hist_array = []
        self.color_array = []
        maxValue = 1;
        maxX = 0
        minX = 0

        counter = 0;

        for diff in sorted(histogram.keys()):

            value = histogram[diff]
            #colorOffset = ((self.temp+self.offset)%3)

            if (diff) % 3 == 1:
                color= alternatingColor[0]
            else:
                color = alternatingColor[1]

            counter +=1;

            self.hist_array += [float(diff), float(value), 0]
            self.hist_array += [float(diff), 0, 0]
            self.hist_array += [float(diff) + self.barSize, 0, 0]
            self.hist_array += [float(diff) + self.barSize, float(value), 0]

            self.color_array += color
            self.color_array += color
            self.color_array += color
            self.color_array += color


            maxValue = max(value, maxValue)

            maxX = max(diff, maxX)
            minX = min(diff, minX)


        self.maxValue = maxValue

        if self.maxValue > 0:
            fScale = 100.0/float(self.maxValue)
        else:
            fScale = 0
        for i in range(0, len(self.hist_array), 3):
            self.hist_array[i+1] *= fScale

        self.viewTop = 100 + 10

        self.viewLeft = float(1)
        self.viewRight = float(3+self.barSize)

        self.updateHist = True
        self.updateTextOverlay()
        self.update()

        self.originalHistogram = histogram
        self.createXAxis(self.viewLeft,self.viewRight)

    def setOffset(self, offset):
        self.offset = offset

        if self.mode == "def":
            self.updateHist = True
        else:
            self.updatePlot(self.originalHistogram)
        self.updateTextOverlay()

        self.update()

    def render(self):
        if not self.hist_array:
            return

        if self.updateHist:

            hist_arry_shifted = []
            shift = ((self.offset+self.temp) % 3)*12


            for i in range(0,len(self.hist_array),12):

                currentIndex = (i+shift) % len(self.hist_array)

                hist_arry_shifted += [self.hist_array[i], self.hist_array[currentIndex+1], self.hist_array[currentIndex+2]]
                hist_arry_shifted += [self.hist_array[i+3], self.hist_array[currentIndex+4], self.hist_array[currentIndex+5] ]
                hist_arry_shifted += [self.hist_array[i+6], self.hist_array[currentIndex+7], self.hist_array[currentIndex+8]]
                hist_arry_shifted += [self.hist_array[i+9], self.hist_array[currentIndex+10], self.hist_array[currentIndex+11]]


            glBindBuffer (GL_ARRAY_BUFFER, self.vboHist)
            glBufferData (GL_ARRAY_BUFFER, len(hist_arry_shifted)*4,  (c_float*len(hist_arry_shifted))(*hist_arry_shifted), GL_DYNAMIC_DRAW)

            glBindBuffer (GL_ARRAY_BUFFER, self.cboCol)
            glBufferData (GL_ARRAY_BUFFER, len(self.color_array)*4,  (c_float*len(self.color_array))(*self.color_array), GL_STATIC_DRAW)


        glClearColor(1.0,1.0,1.0,1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


        glColor3f(0.3,0.5,0.8)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(self.viewLeft , self.viewRight, self.viewBottom, self.viewTop)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


        glBindBuffer(GL_ARRAY_BUFFER, self.cboCol)
        glColorPointer(3,GL_FLOAT,0,None)


        glBindBuffer (GL_ARRAY_BUFFER, self.vboHist)
        glVertexPointer(3, GL_FLOAT, 0, None)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)
        glDrawArrays(GL_QUADS, 0, len(self.hist_array)-1)

    def mousePressEvent(self, e):

        if e.button() == 1:
            self.interaction = "translate"

        canvasPos = self.getCanvasPos(e.pos())

        self.startPos = canvasPos


        self.update()

    def mouseMoveEvent(self, e):

        self.currentPos = self.getCanvasPos(e.pos())

        if self.interaction == "translate":

            diff = self.currentPos.x() - self.startPos.x()

            self.temp = -int(diff)
            self.updateHist = True


        self.updateTextOverlay()
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        self.offset += self.temp
        self.temp = 0
        self.offsetUpdated.emit( self.ID,self.offset)
        self.interaction = ""



###############################

