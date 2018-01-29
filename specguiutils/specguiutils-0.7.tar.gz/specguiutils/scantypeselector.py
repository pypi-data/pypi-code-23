'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
import logging
logger = logging.getLogger(__name__)

SCAN_TYPES = ['All',]

class ScanTypeSelector(qtWidgets.QDialog):
    '''
    Provide a ComboBox to allow switching scan between scan types included 
    in the spec file.  An additional item is added at the top to allow selecting 
    all types.  This widget was developled to work along with the 
    :py:class:`.ScanBrowser`
    '''
    scanTypeChanged = qtCore.pyqtSignal(int, name='scanTypeChanged')
    
    def __init__(self, parent=None):
        super(ScanTypeSelector, self).__init__(parent)
        logger.debug ("Enter")

        layout = qtWidgets.QHBoxLayout()
        label =qtWidgets.QLabel("Scan Type")
        self.scanTypes = list(SCAN_TYPES)
        self.scanTypeSelection = qtWidgets.QComboBox()
        self.scanTypeSelection.insertItems(0, self.scanTypes)
 
        layout.addWidget(label)
        layout.addWidget(self.scanTypeSelection)
        self.scanTypeSelection.currentIndexChanged[int] \
            .connect(self.typeSelectionChanged)
         
        self.setLayout(layout)
        self.show()

            
    def loadScans(self, scanTypes):
        '''
        Load this module with a list scan types discovered in the spec these 
        items, along with \'All\' will be added to the comboBox options
        '''
        self.scanTypeSelection.currentIndexChanged[int] \
            .disconnect(self.typeSelectionChanged)
        self.scanTypeSelection.clear()
        logger.debug("SCAN_TYPES %s" % SCAN_TYPES)
        self.scanTypes = list(SCAN_TYPES)
        self.scanTypes.extend(scanTypes)
        logger.debug("scanTypes %s" % scanTypes)
        logger.debug("self.scanTypes %s" % self.scanTypes)
        self.scanTypeSelection.insertItems(0, self.scanTypes)
        #self.scanTypeSelection.insertItems(1, scanTypes)
        #self.setCurrentType(0)
        self.scanTypeSelection.currentIndexChanged[int] \
            .connect(self.typeSelectionChanged)
         
    def getTypeNames(self):
        '''
        return a list of types from the widget.
        '''
        typeNames = []
        nameCount = self.scanTypeSelection.count()
        for index in range(nameCount):
            typeNames.append(str(self.scanTypeSelection.itemText(index)))
        return typeNames
     
    def getTypeIndexFromName(self, typeName):
        '''
        Return an index of for a particular type name
        '''
        names = self.getTypeNames()
        index = names.index(typeName)
        return index
         
    def getCurrentType(self):
        '''
        return the currently selected type
        '''
        return str(self.scanTypeSelection.currentText())
    
    def setCurrentType(self, newType):
        '''
        Set the current type programatically
        '''
        self.scanTypeSelection.setCurrentIndex(newType)
         
    @qtCore.pyqtSlot(int)
    def typeSelectionChanged(self, newType):
        '''
        Send a signal to the rest of the application that the selected type has 
        changed.  Applications that want to be notified should look for the 
        signal appSelectorName.scanTypeChanged.connect(appHandlerMethod)
        '''
#        self.scanTypeSelection.setCurrentIndex(newType)
        logger.debug("Enter")
        self.scanTypeChanged[int].emit(newType)
        