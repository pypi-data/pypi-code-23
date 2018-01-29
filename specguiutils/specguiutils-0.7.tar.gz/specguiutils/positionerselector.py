'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtWidgets as qtWidgets
import PyQt5.QtCore as qtCore
import logging
from specguiutils import METHOD_ENTER_STR
logger = logging.getLogger(__name__)

class PositionerSelector(qtWidgets.QWidget):
    '''
    This class presents two lists.  Initially one list is populated with 
    the positioners available as provided by the #P lines in the spec
    file.  The user can Add or remove these parameters from the 
    available list to the selected list.  The user can then grab the 
    selected list for use in code.  One use is to pass this list to the
    :py:class:ScanBrowser and these parameters will be added as columns
    in the browser's table of scan information.
    '''
    
    def __init__(self, parent=None):
        '''
        Create widget with two selection lists.  Positioners will be 
        selected from an available list and can move these to selected 
        list using one of two buttons.  Likewise, items in the selected 
        list can be highlighted and moved back to the available list 
        using the other button.
        '''
        super(PositionerSelector, self).__init__(parent)
        layout = qtWidgets.QHBoxLayout()
        originalLayout = qtWidgets.QVBoxLayout()
        originalLabel = qtWidgets.QLabel("Available Positioners")
        self.originalList = qtWidgets.QListWidget()
        self.originalList.setMinimumWidth(300)
        self.originalList.setMinimumHeight(400)
        originalLayout.addWidget(originalLabel)
        originalLayout.addWidget(self.originalList)
        selectedLayout = qtWidgets.QVBoxLayout()
        selectedLabel = qtWidgets.QLabel("Available Positioners")
        self.selectedList = qtWidgets.QListWidget()
        self.selectedList.setMinimumWidth(300)
        self.selectedList.setMinimumHeight(400)
        selectedLayout.addWidget(selectedLabel)
        selectedLayout.addWidget(self.selectedList)
        self.addToSelection = qtWidgets.QPushButton("Add to Selection")
        self.removeFromSelection = qtWidgets.QPushButton("RemoveFromSelection")
        layout.addLayout(originalLayout)
        buttonLayout = qtWidgets.QVBoxLayout()
#        buttonLayout.addWidget(qtWidgets.QSpacerItem(100, 30))
        buttonLayout.addWidget(self.addToSelection)
        buttonLayout.addWidget(self.removeFromSelection)
#        buttonLayout.addWidget(qtWidgets.QSpacerItem(100, 30))
        layout.addLayout(buttonLayout)
        layout.addLayout(selectedLayout)
        self.setLayout(layout)
        self.show()
        self.addToSelection.clicked.connect(self._addItemToSelection)
        self.originalList.itemDoubleClicked.connect(self._originalListDoubleClicked)
        self.removeFromSelection.clicked.connect(self._removeItemFromSelection)
        self.selectedList.itemDoubleClicked.connect(self._selectedListDoubleClicked)
        
    @qtCore.pyqtSlot()
    def _addItemToSelection(self):
        '''
        Handler to move information from the available to selected list
        '''
        logger.debug(METHOD_ENTER_STR % self.originalList.currentItem())
        selectedItem = self.originalList.currentItem()
        if not (selectedItem is None):
            logger.debug("Taking item %s" % selectedItem)
            row = self.originalList.currentRow()
            self.originalList.takeItem(row)
            self.selectedList.addItem(selectedItem)
        
    def loadPositioners(self, positioners):
        logger.debug(METHOD_ENTER_STR % positioners)
        for positioner in positioners.keys():
            item = qtWidgets.QListWidgetItem(positioner)
            self.originalList.addItem(item)
            
    def getSelectedItems(self):
        selectedCount = self.selectedList.count()
        selectedItems = [(self.selectedList.item(x)).text() for x in range(selectedCount)]
        return selectedItems
    
    @staticmethod
    def getPositionSelectorModalDialog(positioners):
        class PositionerSelectDialog(qtWidgets.QDialog):
            def __init__(self, parent, positioners):
                super(PositionerSelectDialog,self).__init__(parent)
                self.selectedPositions = []
                self.setModal(True)
                layout = qtWidgets.QVBoxLayout()
                self.positionSelector = PositionerSelector()
                self.positionSelector.loadPositioners(positioners)
                buttonLayout = qtWidgets.QHBoxLayout()
                self.okButton = qtWidgets.QPushButton("OK")
                self.cancelButton = qtWidgets.QPushButton("Cancel")
                buttonLayout.addWidget(self.okButton)
                buttonLayout.addWidget(self.cancelButton)
                layout.addWidget(self.positionSelector)
                layout.addLayout(buttonLayout)
                self.okButton.clicked.connect(self.okPressed)
                self.cancelButton.clicked.connect(self.cancelPressed)
                self.setLayout(layout)
                self.setGeometry(300, 200, 460, 350)
                self.show()
                
            def cancelPressed(self):
                self.hide()
                self.deleteLater()
                
            def okPressed(self):
                self.selectedPositions = self.positionSelector.getSelectedItems()
                self.hide()
                self.deleteLater()
                
            def getSelectedPositioners(self):
                return self.selectedPositions
            
        positionSelector = PositionerSelectDialog(None, positioners)
        positionSelector.exec()
        return positionSelector.getSelectedPositioners()

    @staticmethod
    def getUserParamsOSelectorModalDialog(userParams):
        class PositionerSelectDialog(qtWidgets.QDialog):
            def __init__(self, parent, userParams):
                super(PositionerSelectDialog,self).__init__(parent)
                self.selectedUserParameters = []
                self.setModal(True)
                layout = qtWidgets.QVBoxLayout()
                self.userParamsSelector = PositionerSelector()
                self.userParamsSelector.loadPositioners(userParams)
                buttonLayout = qtWidgets.QHBoxLayout()
                self.okButton = qtWidgets.QPushButton("OK")
                self.cancelButton = qtWidgets.QPushButton("Cancel")
                buttonLayout.addWidget(self.okButton)
                buttonLayout.addWidget(self.cancelButton)
                layout.addWidget(self.userParamsSelector)
                layout.addLayout(buttonLayout)
                self.okButton.clicked.connect(self.okPressed)
                self.cancelButton.clicked.connect(self.cancelPressed)
                self.setLayout(layout)
                self.setGeometry(300, 200, 460, 350)
                self.show()
                
            def cancelPressed(self):
                self.hide()
                self.deleteLater()
                
            def okPressed(self):
                self.selecteduserParameters = \
                    self.userParamsSelector.getSelectedItems()
                self.hide()
                self.deleteLater()
                
            def getSelectedPositioners(self):
                return self.selecteduserParameters
            
        positionSelector = PositionerSelectDialog(None, userParams)
        positionSelector.exec()
        return positionSelector.getSelectedPositioners()

    def _originalListDoubleClicked(self, items):
        self._addItemToSelection()
        
        
    @qtCore.pyqtSlot()
    def _removeItemFromSelection(self):
        logger.debug(METHOD_ENTER_STR % self.selectedList.currentItem())
        selectedItem = self.selectedList.currentItem()
        if not (selectedItem is None):
            logger.debug("Taking item %s" % selectedItem)
            row = self.selectedList.currentRow()
            self.selectedList.takeItem(row)
            self.originalList.addItem(selectedItem)
            
    def _selectedListDoubleClicked(self, item):
        self._removeItemFromSelection()