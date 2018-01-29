'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtGui as qtGui
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
from specguiutils.model.counterselectortablemodel import CounterSelectorTableModel
from specguiutils.view.counterselectorview import CounterSelectorView
import logging
from specguiutils import METHOD_ENTER_STR
logger = logging.getLogger(__name__)

COUNTER_LABEL_COLUMN = 0
COUNTER_HEADER_INIT = ['Counter',]

class CounterSelector(qtWidgets.QWidget):
    '''
    GUI to display the monitors/counters (from #L)  for a selected scan.  
    A number of columns are displayed along with the scan parameters.  
    Each column will represent a fairly large radiobox selection with 
    one radio button for each counter 
    '''
    # signal params (counterName, col, newVal)
    counterOptChanged = qtCore.pyqtSignal(str, int, bool, name='counterOptChanged')

    def __init__(self, parent=None, counterOpts=None):
        '''
        constructor
        '''
        super(CounterSelector, self).__init__(parent=parent)
        layout = qtWidgets.QHBoxLayout()
        self.counterModel = CounterSelectorTableModel(parent=self, counterOpts=counterOpts)
        self.counterView = CounterSelectorView(parent, tableModel=self.counterModel)
        self.counterView.setModel(self.counterModel)
        font = qtGui.QFont()
        font.setFamily("Helvetica")
        font.setPointSize(10)
        self.counterView.setFont(font)
        self.setMinimumWidth(400)
        self.setMinimumHeight(250)
        self.counterModel.headerDataChanged.connect(self.counterView.headerChanged)
        layout.addWidget(self.counterView)
        self.setLayout(layout) 
        self.show()

    

    @qtCore.pyqtSlot(qtWidgets.QTableWidgetItem)
    def flagChangingOpts(self, item):
        logger.debug( METHOD_ENTER_STR % item)
        row = item.row()
        col = item.column()
        logger.debug ("row %d, column %d" % (row, col))
        nameItem = self.counterList.item(row, 0)
        counter = str(nameItem.text())
        value = item.checkState()
        #print ("name item %s, %s" % (nameItem, nameItem.text()))
        if value == True:
            for otherRows in range(self.counterListModel.rowCount()):
                otherItems = self.counterList.item(otherRows, col)
                if otherItems != item:
                    otherItems.setCheckState(False )
                
        self.counterOptChanged.emit(counter, col-1, value )
        logger.debug("Exiting ")

    def getSelectedCounters(self):
        '''
        Rerturn a list of the selected counters
        '''
        counters = self.counterView.getSelectedCounters()
        logger.debug ("counters %s" %counters) 
        return counters

    def getSelectedCounterNames(self, counters):
        '''
        return a list of the selected counter names
        '''
        counterNames = []
        logger.debug ("counters %s" % counters)
        for counter in range(len(counters)):
            index = self.counterModel.index(counters[counter], 0,)
            name = str(self.counterModel.data(index))
            counterNames.append(name)
        logger.debug ("counters %s" % counterNames)
        return counterNames
        
    def setCurrentCounter(self, row):
        '''
        Set the current selected counter for a given row
        '''
        self.counterView.setCurrentIndex(self.counterModel.index(row,0))
        
    def setSelectedCounters(self, selections):
        '''
        Set the value for all of the counters
        '''
        logger.debug("Entering data size %d, %d" % (self.counterModel.rowCount(), self.counterModel.columnCount()))
        logger.debug("trying to set selections %s " % selections)
        foundName = {}
        for column in range(len(selections)):
            foundName[column] = False
        for row in range(self.counterModel.rowCount()):
            for column in range(len(selections)):
                if not (selections[column] == ''):
                    nameIndex = self.counterModel.index( row,0)
                    nameWidget = self.counterModel.data(nameIndex)
                    if str(nameWidget) == selections[column]:
                        foundName[column] = True
                        self.counterModel.setItem(row, column+1, True)
                else:
                    self.counterModel.setItem(0, column+1, True)
        for column in range(len(selections)):
            if not foundName[column]:
                self.counterModel.setItem(0, column+1, True)
                
