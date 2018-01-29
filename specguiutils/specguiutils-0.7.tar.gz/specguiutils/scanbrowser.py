'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
import PyQt5.QtGui as qtGui
import logging
from specguiutils import METHOD_ENTER_STR
logger = logging.getLogger(__name__)

SCAN_COL_WIDTH = 40
CMD_COL_WIDTH = 240
NUM_PTS_COL_WIDTH = 40
MINIMUM_WIDGET_WIDTH = 420
SCAN_COL = 0
CMD_COL = 1
NUM_PTS_COL = 2
DEFAULT_COLUMN_NAMES = ['S#', 'Command', 'Points']

class ScanBrowser(qtWidgets.QWidget):
    '''
    This class provides information about scans in a spec file.  By default, 
    scan number, the scan command and number of points each in a column in the 
    table.  This class can be combined with other classes such as the 
    :py:class:.ScanTypeSelector and :py:class:.PositionerSelector to provide 
    more function.  
    :py:class:.ScanTypeSelector allows the user to select a 
    particular scan type or All scan Types.
    :py:class:.PositionerSelector allows the user to select from a list of 
    positioners available in the scan. The results of this selection can be fed
    back in via :py:func:setPositionersToDisplay.  This will add an additional 
    column to the table for each positioner listed in the scan.  The list of 
    positioners is given in the #P fields in the file header and the values 
    to display are from the corresponding #O values in the scan header.
    '''
    # Define some signals that this class will provide to users
    scanSelected = qtCore.pyqtSignal(list, name="scanSelected")
    scanLoaded = qtCore.pyqtSignal(bool, name="scanLoaded")
              
    def __init__(self, parent=None):
        '''
        Construct an empty table with columns for scan number, scan command and
        number of points.  Data is added to the table via the :py:func:loadScans
        command
        '''
        super(ScanBrowser, self).__init__(parent)
        layout = qtWidgets.QHBoxLayout()
        self.positionersToDisplay = []
        self.userParamsToDisplay = []
        self.lastScans = None
        self.scanList = qtWidgets.QTableWidget()
        #
        font = qtGui.QFont("Helvetica", pointSize=10)
        self.scanList.setFont(font)
        self.scanList.setEditTriggers(qtWidgets.QAbstractItemView.NoEditTriggers)
        #self.scanList.setRowCount(1)
        self.scanList.setColumnCount(len(DEFAULT_COLUMN_NAMES) + len(self.positionersToDisplay))
        self.scanList.setColumnWidth(SCAN_COL, SCAN_COL_WIDTH)
        self.scanList.setColumnWidth(CMD_COL, CMD_COL_WIDTH)
        self.scanList.setColumnWidth(NUM_PTS_COL, NUM_PTS_COL_WIDTH)
        self.scanList.setHorizontalHeaderLabels(['S#', 'Command', 'Points'])
        self.scanList.setSelectionBehavior(qtWidgets.QAbstractItemView.SelectRows)
        self.scanList.verticalHeader().setVisible(False)
        self.setMinimumWidth(400)
        self.setMaximumWidth(900)
        self.setMinimumHeight(250)
        layout.addWidget(self.scanList)
        self.setLayout(layout)
        self.show()
        
        self.scanList.itemSelectionChanged.connect(self.scanSelectionChanged)

    def loadScans(self, scans, newFile=True):
        '''
        loads the list of scans into the browser. At the end, it will 
        pass emit a message that the scan is loaded and from the input 
        newFile, it will pass along whether or not this is a new file. 
        This is helpful when the scan is reloaded with just a single 
        type of scan.  This causes recognition that this is not an
        overall change of file, just changing to a subset of the list.
        '''
        logger.debug(METHOD_ENTER_STR)
        self.lastScans = scans
        self.scanList.itemSelectionChanged.disconnect(self.scanSelectionChanged)
        self.scanList.setRowCount(len(scans.keys()) )
        scanKeys = sorted(scans, key=int)
        logger.debug("scanKeys %s" % str(scanKeys))
        row = 0
        for scan in scanKeys:
            scanItem = qtWidgets.QTableWidgetItem(str(scans[scan].scanNum))
            self.scanList.setItem(row, SCAN_COL, scanItem)
            cmdItem = qtWidgets.QTableWidgetItem(scans[scan].scanCmd)
            self.scanList.setItem(row, CMD_COL, cmdItem)
            nPointsItem = qtWidgets.QTableWidgetItem(str(len(scans[scan].data_lines)))
            self.scanList.setItem(row, NUM_PTS_COL, nPointsItem)
            row +=1
        self.fillSelectedPositionerData()
        self.fillSelectedUserParamsData()
        self.scanList.itemSelectionChanged.connect(self.scanSelectionChanged)
        self.scanLoaded.emit(newFile)
            
    def fillSelectedPositionerData(self):
        '''
        If positioners have been selected to supplement the table, then
        this cause will grab the values out for each scan and places it 
        in a column of the table
        '''
        if self.lastScans is None:
            return
        scanKeys = sorted(self.lastScans, key=int)
        row = 0
        if (not (self.lastScans is None)) and (len(self.positionersToDisplay)) > 0:
            for scan in scanKeys:
                posNum = 1
                for positioner in self.positionersToDisplay:
                    item = qtWidgets.QTableWidgetItem(str(self.lastScans[scan].positioner[positioner]))
                    self.scanList.setItem(row, NUM_PTS_COL + posNum, item)
                    posNum += 1
                row += 1
        
    def fillSelectedUserParamsData(self):
        '''
        If user parameters have been selected to supplement the table, 
        then this cause will grab the values out for each scan and 
        places it in a column of the table
        '''
        if self.lastScans is None:
            return
        scanKeys = sorted(self.lastScans, key=int)
        row = 0
        if (not (self.lastScans is None)) and (len(self.userParamsToDisplay)) > 0:
            for scan in scanKeys:
                posNum = 1
                for userParam in self.userParamsToDisplay:
                    try:
                        item = qtWidgets.QTableWidgetItem(str(self.lastScans[scan].U[userParam]))
                        self.scanList.setItem(row, \
                                              NUM_PTS_COL + posNum \
                                              + len(self.positionersToDisplay), \
                                              item)
                    except KeyError:
                        item = qtWidgets.QTableWidgetItem(str("N/A"))
                        self.scanList.setItem(row, \
                                              NUM_PTS_COL + posNum \
                                              + len(self.positionersToDisplay), \
                                              item)
                    posNum += 1
                row += 1
        
    def filterByScanTypes(self, scans, scanTypes):
        '''
        selects scans fron the list that have a given scan Type and 
        causes these to be loaded into the scan table.
        '''
        filteredScans = {}
        scanKeys = sorted(scans, key=int)
        if scanTypes is None:
            raise ValueError("Invalid ScanFilter %s" % scanTypes)
        for scan in scanKeys:
            if len(scanTypes) > 0:
                thisType = scans[scan].scanCmd.split()[0]
                if thisType in scanTypes:
                    filteredScans[scan] = scans[scan]
            else:
                filteredScans[scan] = scans[scan]
        logger.debug ("Filtered Scans %s" % filteredScans)
        self.loadScans(filteredScans, newFile = False)

    def getCurrentScan(self):
        '''
        retifmx the currently selected scan
        '''
        return str(self.scanList.item(self.scanList.currentRow(), 0).text())
        
    def setCurrentScan(self, row):
        '''
        Sets the current scan selection
        '''
        logger.debug(METHOD_ENTER_STR)
        self.scanList.setCurrentCell(row, 0)
        
    def setPositionersToDisplay(self, positioners):
        '''
        Sets a list of positiorers that will be added to the table 
        whenever new data is loaded 
        '''
        self.positionersToDisplay = positioners
        self.scanList.setColumnCount(len(DEFAULT_COLUMN_NAMES) + \
                                     len(self.positionersToDisplay) + \
                                     len(self.userParamsToDisplay))
        self.scanList.setHorizontalHeaderLabels(DEFAULT_COLUMN_NAMES + \
                                            self.positionersToDisplay + \
                                            self.userParamsToDisplay)
        self.fillSelectedPositionerData()
        self.fillSelectedUserParamsData()
        
    def setUserParamsToDisplay(self, userParams):
        '''
        Sets a list of positiorers that will be added to the table 
        whenever new data is loaded 
        '''
        self.userParamsToDisplay = userParams
        self.scanList.setColumnCount(len(DEFAULT_COLUMN_NAMES) + \
                                     len(self.positionersToDisplay) + \
                                     len(self.userParamsToDisplay))
        self.scanList.setHorizontalHeaderLabels(DEFAULT_COLUMN_NAMES + \
                                            self.positionersToDisplay +
                                            self.userParamsToDisplay)
        self.fillSelectedPositionerData()
        self.fillSelectedUserParamsData()
        
    @qtCore.pyqtSlot()
    def scanSelectionChanged(self):
        '''
        This method runs when a scans are selected.  A signal is emitted 
        with the 
        '''
        logger.debug(METHOD_ENTER_STR)
        selectedItems = self.scanList.selectedIndexes()
        logger.debug("SelectedItems %s" % selectedItems)
        selectedScans = []
        for item in selectedItems:
            if item.column() == 0:
                scan = str(self.scanList.item(item.row(),0).text())
                selectedScans.append(scan)
        logger.debug("Selected scans %s" % selectedScans)
        self.scanSelected[list].emit(selectedScans)