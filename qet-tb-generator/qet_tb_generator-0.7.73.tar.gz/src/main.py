#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
QET Terminal Block generator
Creates new Terminal blocks elements
corresponding to terminals used in a QET project
python 3.5
"""

#---------|---------|---------|---------|---------|---------|---------|---------|


# Imports
from .frmMain import Ui_frmMain
import json
import os
import platform
from PyQt5 import QtWidgets, QtCore # QtGui  # Optional: QtCore
import re
import sys
import uuid
import xml.etree.ElementTree as etree
import pdb


# GLOBAL CONSTANTS
VERSION = 'v0.7.73'
IDX_UUID = 0
IDX_TB_NAME = 1
IDX_TER_NAME = 2
IDX_TER_XREF = 3
IDX_NORTH_ID1 = 4
IDX_NORTH_ID2 = 5
IDX_NORTH_CABLE_NUM = 6
IDX_NORTH_XREF = 7
IDX_SOUTH_ID1 = 8
IDX_SOUTH_ID2 = 9
IDX_SOUTH_CABLE_NUM = 10
IDX_SOUTH_XREF = 11
SEPARATOR = ':'
BORNE_INDEX_SEPARATOR = '/'


# Type field in collection
TYPE_TERMINAL = 'terminal'
TYPE_NEXT_REPORT = 'next_report'
TYPE_PREVIOUS_REPORT = 'previous_report'
ELEMENT_NAME_CONNECTORS = ['connecteur_m.elmt', 'connecteur_f.elmt', 'connecteur_mf.elmt']


class MainWindow(QtWidgets.QMainWindow, Ui_frmMain):

    CONFIG_FILE_NAME = 'QET_TB_generator.ini'


    def __init__(self):
        """ constructor """
        super(MainWindow, self).__init__()

        # attributes
        self.config = self._read_config()   # initizalize config

        # Customize ui
        self.setupUi(self)  # setup the user interface from Designer
        MainWindow.setWindowTitle(self,
                MainWindow.windowTitle(self) + ' - ' + VERSION)
        MainWindow.move(self, 100, 100)

        # Restore configuration from config
        self.txtDataPath.setText(str(self.config['collection']))
        self.txtSize_h.setText(str(self.config['head_height']))
        self.txtSize_w.setText(str(self.config['head_width']))
        self.txtSize_h1.setText(str(self.config['union_height']))
        self.txtSize_w1.setText(str(self.config['union_width']))
        self.txtSize_w2.setText(str(self.config['terminal_width']))
        self.txtRes.setText(str(self.config['reservation_label']))
        self.txtMaxPage.setText(str(self.config['max_page']))
        self.sldMaxPage.setValue(int(self.config['max_page']))
        if self.config['xref'] == QETProject.XREF_DEFAULT:
            self.rad_number.setChecked(True)
        else:
            self.rad_id.setChecked(True)
        self.lbl_info.setText('')

        # Fill recent projects list
        qet_settings = QtCore.QSettings('QElectroTech', 'QElectroTech')
        for i in range(10):
            foo = qet_settings.value('projects-recentfiles/file' + str(i))
            if foo: self.lst_recent.addItem(foo)

        # Enable/disable xref checkbox
        self.chk_implicit_clicked()


    def choose_project(self):
        """Slot: button select qet project
        Show dialog to select QET project"""
        file = QtWidgets.QFileDialog.getOpenFileName(self,
                caption="Choose user collection path", filter="*.qet")
        if file:
            self.txt_project_path.setText(file[0])
            self.lbl_info.setText('')  # clear info label


    def chk_implicit_clicked(self):
        """Slot: enable/disable the xref checkbox"""
        if self.chkImplicit.isChecked():
             self.chkXref.setEnabled(False)
        else:
             self.chkXref.setEnabled(True)


    def recent_picked(self):
        """Slot: for recent projects list"""
        self.txt_project_path.setText(self.lst_recent.selectedItems()[0].text())
        self.lbl_info.setText('')  # clear info label


    def save_config(self):
        """Slot: buton save pressed"""
        # Updates attributes and save
        self.config['collection'] = self.txtDataPath.text()
        self.config['head_height'] = int(self.txtSize_h.text())
        self.config['head_width'] = int(self.txtSize_w.text())
        self.config['union_height'] = int(self.txtSize_h1.text())
        self.config['union_width'] = int(self.txtSize_w1.text())
        self.config['terminal_width'] = int(self.txtSize_w2.text())
        self.config['reservation_label'] = self.txtRes.text()
        self.config['max_page'] = int(self.txtMaxPage.text())
        if self.rad_number.isChecked():
            self.config['xref'] = QETProject.XREF_DEFAULT
        else:
            self.config['xref'] = QETProject.XREF_AUTO
        self.sldMaxPage.setValue(int(self.config['max_page']))

        self._save_config()


    def sld_changed(self):
        """Slot: slider value changed"""
        self.txtMaxPage.setText(str(self.sldMaxPage.value()))


    def choosePath(self):
        """Slot,button select data path
        Show dialog to select user"""
        dir = QtWidgets.QFileDialog.getExistingDirectory(self,
                caption="Choose user collection path", directory=self.txtDataPath.text())
        if dir:
            if not dir.endswith(os.sep): dir += os.sep
            self.txtDataPath.setText(dir)
            self.save_config()


    def create_tb(self):
        """Slot; button Create terminal block
        Launch Terminal Block creation..."""

        self.lbl_info.setText('')  # clear info label

        qet_file = self.txt_project_path.text()


        if not os.path.exists(qet_file): #not exist
            self.lbl_info.setText('File not exists !!')
        else:
            self.lbl_info.setText('Creating terminal strips...')

            if self.rad_id.isChecked():  # determine type of reference to use
                ref_type = QETProject.XREF_AUTO
            else:
                ref_type = QETProject.XREF_DEFAULT

            qet_project = QETProject(
                    qet_file,
                    ref_type,
                    self.txtFromPage.text(),
                    self.txtToPage.text(),
                    self.chkImplicit.isChecked()) #analize QET xml code
            terminal_elements_in_project = qet_project.get_list_of_used_terminals()

            # For every diferent block terminal name: X1, X2,...
            # {TB:term/index : [element_uuid, terminal_block_name, terminal_name, terminal_xref
            # north_id1, north_id2, north_cable_num, north_xref,
            # south_id1, south_id2, south_cable_num, south_xref ] }
            all_tb_names = \
                    list( set ( [x.split( SEPARATOR )[0] \
                    for x in terminal_elements_in_project.keys() ] \
                    ) )  # get unique TerminalBlockID

            full_xref = not (self.chkXref.isEnabled() and self.chkXref.isChecked())
            for block_name in all_tb_names:
                block = TerminalBlock(block_name,
                        os.path.basename(qet_file[:-4]),
                        'temp_tb',
                        self.config,
                        self.chkReservation.isChecked(),
                        full_xref )
                block.addTerminals(terminal_elements_in_project)
                block.drawTerminalBlock()  #creates XML element file

            #  show info
            if len(all_tb_names) == 1:
                self.lbl_info.setText('1 terminals strip succesfully created !!')
            else:
                self.lbl_info.setText(
                        '%i terminals strips succesfully created !!' \
                        %len(all_tb_names))


    def create_cn(self):
        """Slot; button Create connector summary
        Launch Terminal Block creation..."""

        qet_file = self.txt_project_path.text()

        if not os.path.exists(qet_file): #not exist
            self.lbl_info.setText('File not exists !!')
        else:
            self.lbl_info.setText('Creating connectors...')

            if self.rad_id.isChecked():  # determine type of reference to use
                ref_type = QETProject.XREF_AUTO
            else:
                ref_type = QETProject.XREF_DEFAULT

            qet_project = QETProject(
                    qet_file,
                    ref_type,
                    self.txtFromPage.text(),
                    self.txtToPage.text(),
                    self.chkImplicit.isChecked()) #analize QET xml code
            connectors = qet_project.get_list_of_used_connectors()
            cnIdx = connectors[0]
            cnPins = connectors[1]

            # For every diferent connector name: X1, X2,...
            for cn in sorted(cnIdx.keys()):
                conn = Connector(cn,
                        max ( cnIdx[cn][0], cnIdx[cn][1] ),
                        cnIdx[cn][2],
                        os.path.basename(qet_file[:-4]),
                        'temp_cn',
                        self.config)
                conn.addPins(cnPins)
                conn.drawConnector()  #creates XML element file


            #  show info
            if len(cnIdx) == 1:
                self.lbl_info.setText('1 connector succesfully created !!')
            else:
                self.lbl_info.setText(
                        '%i connectors succesfully created !!' \
                        %len(cnIdx) )


    def create_connectors(self):
        """Slot; button Create connectors diagram"""

        qet_file = self.txt_project_path.text()

        if not os.path.exists(qet_file): #not exist
            self.lbl_info.setText('File not exists !!')
        else:
            self.lbl_info.setText('Creating connectors...')

            if self.rad_id.isChecked():  # determine type of reference to use
                ref_type = QETProject.XREF_AUTO
            else:
                ref_type = QETProject.XREF_DEFAULT

            qet_project = QETProject(
                    qet_file,
                    ref_type,
                    self.txtFromPage.text(),
                    self.txtToPage.text()) #analize QET xml code
            connector_elements_in_project = \
                    qet_project.get_list_of_used_connectors()

            # For every connector name: X1, X2,...
            # {
            #   Connector1/pin : [ pin_name, male/female, [xref1, xref2,...] ,
            #   Connector1/pin : [ pin_name, male/female,  [xref1, xref2,...] ,
            #   Connector_n/pin : [ pin_name, male/female,  [xref1, xref2,...] ,
            #   Connector1 : num_total_of_pins }
            """all_tb_names = \
                    list( set ( [x.split( SEPARATOR )[0] \
                    for x in terminal_elements_in_project.keys() ] \
                    ) )  # get unique TerminalBlockID

            for block_name in all_tb_names:
                block = TerminalBlock(block_name,
                        os.path.basename(qet_file[:-4]),
                        'temp_tb',
                        self.config,
                        self.chkReservation.isChecked() )
                block.addTerminals(terminal_elements_in_project)
                block.drawTerminalBlock()  #creates XML element file

            #  show info
            if len(all_tb_names) == 1:
                self.lbl_info.setText('1 terminals block succesfully created !!')
            else:
                self.lbl_info.setText(
                        '%i terminals blocks succesfully created !!' \
                        %len(all_tb_names)) """


    def salir(self):
            exit()


    def _read_config(self):
        """Read the config file and assign to config attribute
        If not exists, it will create and saves the default params
        @return dict with config"""

        filePath = self._get_platform_config_full_path()
        dirPath = os.path.dirname(filePath)

        if not os.path.isfile(filePath):  # create if not exist
            if not os.path.exists(dirPath): os.makedirs(dirPath)
            self._save_config(defaults=True)
        with open(filePath, 'r') as f:
            return json.load(f)


    def _save_config(self, defaults = False):
        """Save to config file the current user collection path.
        @param defaults: if true, save the defaults parameters.
        @return none"""
        default_config = {'collection': self._get_platform_collection_path(),
                          'head_height': 120,
                          'head_width': 44,
                          'union_height': 70,
                          'union_width': 6,
                          'terminal_width': 20,
                          'reservation_label': 'RES.',
                          'max_page': 50,
                          'xref': 'D'}
        with open(self._get_platform_config_full_path(), 'w') as f:
            if defaults:
                foo = default_config
            else:
                foo = self.config
            json.dump(foo, f)


    def _get_platform_collection_path(self):
        """Return QET Path collection path depending the OS.
        @return string: path with ending /"""
        system = platform.system()
        home = os.path.expanduser("~")
        if (system == 'Linux') or (system == 'Darwin'):
            path = home + '/.qet/elements/'
        elif system == 'Windows':
            path = home + '\\AppData\\Roaming\\qet\\elements\\'
        else:  # use defined by user
            path = ''

        return path


    def _get_platform_config_full_path(self):
        """Return path and file name for the application config file
        @return string: path + config file"""
        file = MainWindow.CONFIG_FILE_NAME
        if (platform.system() == 'Windows'):
            return os.path.expandvars("%appdata%/qet_tb_generator/" + file)
        else:
            return os.path.expanduser("~/.config/qet_tb_generator/" + file)


class QETProject:
    """This class works with the XML source file of a QET Project"""

    # class attributes
    XREF_DEFAULT = 'D'
    XREF_AUTO = 'A'
    QET_COL_ROW_SIZE = 25  # pixels offset for elements coord
    DEBUG = False


    def __init__(self, project_file, folio_reference_type, fromPage, toPage,
                 searchImplicitsConnections):
        """class initializer. Parses the QET XML file.
        @param project_file: file of the QET project
        @param folio_reference_type: how to calc XRefs when recover project info:
           'A' auto. Same xref as configured in the QET diagram project.
           'D' default (%f-%l%c) i.e. 15-F4
        @param fromPage: first page in range to be processed
        @param toPage: last page in range to be processed
        @param searchImplicitsConnections: True for search implicit connections in TB creation"""

        qet_tree = etree.parse(project_file)

        self.cnIdxDict = {}  # dict for index of connectors
        self.cnPinDict = {}  # dict for pins of connectors

        self.qet_project_file = project_file
        self.qet_project = qet_tree.getroot()

        # determine xref format to use
        if folio_reference_type == QETProject.XREF_AUTO:
            self.folio_reference_type = \
                self.qet_project.find('.//newdiagrams'). \
                find('report').attrib['label']
        else:
            self.folio_reference_type = '%f-%l%c'

        # pageOffset for folio numbers
        self.pageOffset = int (self.qet_project.attrib
                ['folioSheetQuantity'])  # offset table of contents

        # general project info
        self._totalPages = len (self.qet_project.findall('.//diagram')) + \
                self.pageOffset

        # range of pages to be tracted
        self.fromPage = int ( \
                ''.join( ele for ele in '0'+fromPage if ele.isdigit() ) )
        self.toPage = int ( \
                ''.join( ele for ele in '0'+toPage if ele.isdigit() ) )

        # Option implicit connections
        self.searchImplicitsConnections = searchImplicitsConnections

        # element of specified type used in project
        self.elementsOfTypeTerminal = \
                self._getListOfElementsByType( TYPE_TERMINAL )
        self.elementsOfTypeNext_Report = \
                self._getListOfElementsByType( TYPE_NEXT_REPORT )
        self.elementsOfTypePrevious_Report = \
                self._getListOfElementsByType( TYPE_PREVIOUS_REPORT )


    def _getFolioReferenceConfig(self):
        """Get reference configuration from the QET Project.
        """


    def _getListOfElementsByType(self, element_type):
        """Return a list of component in library(collection) that
        have 'link_type' as element_type parameter.

        @return [] list with el names of elements that
                   are terminal as 'like_type'"""

        collection = self.qet_project.find('collection')  # collection root
        ret = []  # return list

        for element in collection.findall('.//element'):
            definition = element[0]
            if 'link_type' in definition.attrib:
                if definition.attrib['link_type'] == element_type:
                    ret.append(element.attrib['name'])

        return list(set(ret))  # remove duplicates


    def _getXRef(self, diagram, element, offset_x = 0, offset_y = 0):
        """Return a string with the xreference.

        The element is specified by 'element' at page 'diagam'.
        The page number incremented in one if there are a "index" page

        @param diagram: diagram(page) XML etree object
        @param element: element XML etree object
        @param offset_x: correction of the coord x.
               Useful for Xref for the terminal of an element
        @param offset_y: correction of the coord y
        @return: string like "p-rc" (page - rowLetter colNumber)"""
        ret = self.folio_reference_type

        # get coord
        element_x = int(float(element.attrib['x'])) + int(float(offset_x))
        element_y = int(float(element.attrib['y'])) + int(float(offset_y))
        row, col = self._getXRefByCoord (diagram, element_x, element_y)
        diagram_page = str(int(diagram.attrib['order']) + self.pageOffset)

        # Change tags to real value
        if '%f' in ret:
            ret = ret.replace('%f', diagram_page)
        if '%F' in ret:
            # %F could include extra tags
            folio_label = diagram.attrib['folio']
            if '%id' in folio_label:
                folio_label = folio_label.replace('%id', diagram_page)
            if '%total' in folio_label:
                folio_label = folio_label.replace('%total', str(self._totalPages))
            if '%autonum' in folio_label:
                folio_label = folio_label.replace('%autonum', diagram_page)
            ret = ret.replace('%F', folio_label)
        if '%M' in ret:
            ret = ret.replace('%M', \
                self.qet_project.find('.//newdiagrams'). \
                find('inset').attrib['machine'])
        if '%LM' in ret:
            ret = ret.replace('%LM', \
                self.qet_project.find('.//newdiagrams'). \
                find('inset').attrib['locmach'])
        if '%l' in ret:
            ret = ret.replace('%l', row)
        if '%c' in ret:
            ret = ret.replace('%c', col)

        return ret


    def _getXRefByCoord(self, diagram, x, y):
        """Return a string with the xreference for the coordinates at page 'diagam'
        The page number incremented in one if there are a "index" page

        @param diagram: diagram(page) XML etree object
        @param x,y: coordinates
        @return: string like "p-rc" (page - rowLetter colNumber)"""

        # get requiered data
        cols = int(diagram.attrib['cols'])
        col_size = int(diagram.attrib['colsize'])
        rows = int(diagram.attrib['rows'])
        row_size = int(diagram.attrib['rowsize'])
        element_x = int(x)
        element_y = int(y)
        rows_letters = [chr(x + 65) for x in range(rows)]

        if self.DEBUG:
            print( '<getXRef>: Page order: {}\tCol size: {}\tRow size: {}\tX position: {}\tY Position: {}'. \
                format (page, col_size, row_size, element_x, element_y))

        row_letter = rows_letters[ int(
                (element_y - QETProject.QET_COL_ROW_SIZE) / row_size) - 1 + 1]
                # +1: cal calc. -1 index of lists start 0.
        column = str(int((element_x - QETProject.QET_COL_ROW_SIZE) / col_size) + 1)
        return (row_letter, column)


    def _getElementXrefByConectorId (self, page, conductorTerminalId):
        """Search in a page the element wich has a electricel terminal like
        the parameter passed.
        @param page:
        @param conductorTerminalId: the conductor terminal id to search
        @param iPagesOffset: offset to add at "page_order"
                             references (for XREF TYPE= 'D')
        @return: xref"""

        ret =''
        for element in page.findall('.//element'):  # all elements in diagram
            for terminal in element.find('terminals').findall( TYPE_TERMINAL ):
                if terminal.attrib['id'] == conductorTerminalId:
                    termOfElem_x = terminal.attrib['x']
                    termOfElem_y = terminal.attrib['y']
                    ret = self._getXRef( page, element, termOfElem_x, termOfElem_y)
                    ret += '.'  # + element.attrib['uuid'][-5:-1]
        return ret


    def _getCableNum(self, diagram, terminalId):
        """Return the cable number connected at 'terminalId' in the page 'diagram'
        @param diagram: diagram(page) XML etree object
        @param terminalId: text with the terminal Id
        @return: string whith cable  number"""

        ret = ''
        for cable in diagram.find('conductors').findall('conductor'):
            for cable_terminal in \
                    [x for x in cable.attrib if x[:8] == TYPE_TERMINAL ]:
                if cable.attrib[cable_terminal] == terminalId:
                    ret = cable.attrib['num']
        return ret


    def _testElementOfType (self, elementAttibType, typeCollection):
        """ Every element has as 'type' attrib a full path in the collection.
            If the last part of path is in the list, the Element is of these type.
        @param elementAttibType: type attrib to check
        @param typeCollection: list of all elements type of same type
        @return True / False"""

        name = elementAttibType.split( BORNE_INDEX_SEPARATOR )[-1]
        return name in typeCollection


    def _getElementName (self, element):
        """Returns the name of a terminal element.
        For terminal strips, the name is expectad is like as X1:1
        element: XML etree objet. Is possible that exists more than
        one '<input>' entry in the XML for that element. Check '<inputs>'
        until finds a non-blank 'text' property.
        If the label does not like as xx:xxx, return a ':' string
        return: Name of terminal"""

        lret = []
        for inp in element.find('inputs'):
            lret.append(inp.attrib['text'])

        #check for a text like 'X1:1'. Use REGEX for mor exactly match
        aux = [x for x in lret if (':' in x) and len(x)>2]

        if len(aux):
            return aux[0]
        else:
            return ''


    def _getListofConductorsWithId(self, diagram, terminalId):
        """Return a list for all conductor on a diagram(page) that have one
        side connected to a specific ID of a element.
        @param diagram: page to search ( is a XML etree object)
        @param terminalId: id of one of the sides of conductor
        @return: [ [terminal ID passed, terminalID of the other sid of conductor,
                 conductor num] , ...] """

        ret = []
        for cable in diagram.find('conductors').findall('conductor'):
            idCond = ''
            if cable.attrib['terminal1'] == terminalId:
                ret.append([ terminalId, cable.attrib['terminal2'], \
                        cable.attrib['num'] ] )
            elif cable.attrib['terminal2'] == terminalId:
                ret.append( [ terminalId, cable.attrib['terminal1'], \
                       cable.attrib['num'] ] )

        return ret


    def _testConductorIsABridge(self, diagram, terminalId, \
            terminalName, terminalUUID):
        """ Checks if a conductor that have a 'terminalId' are not a bridge.
        Is considered a brige:
            - Conductor is connected to a NEXT_FOLIO or PREVIOUS FOLIO
            - Conductor is connected to a terminal with same X:<num>
        @param diagram: page to search ( is a XML etree object)
        @param terminalId: id of one of the sides of conductor
        @param terminalName: name of the terminal from conductor comes
        @param terminalUUID: terminal UUID to ensure not check source element
        @return: '' if is a bridge
            xRef (e.g. 7-D3 if not is a bridge """

        for el in diagram.findall('.//element'):  # all elements in diagram
            if el.attrib['uuid'] != terminalUUID: # element is not the
                                                  # source of connection

                for terminal in el.find('terminals').findall( TYPE_TERMINAL ):
                    if (terminal.attrib['id'] == terminalId):
                        # destination element found. Now check type

                        # bridge to a NEXT_REPORT
                        if self._testElementOfType(
                                el.attrib['type'], self.elementsOfTypeNext_Report):
                            return ''

                        # bridge to another identical borne.
                        if self._testElementOfType (
                                el.attrib['type'],
                                self.elementsOfTypeTerminal) and \
                                self._getElementName (el) == terminalName:
                            return ''

                        # not a bridge
                        termOfElem_x = terminal.attrib['x']
                        termOfElem_y = terminal.attrib['y']
                        return self._getXRef(diagram,
                                             el,
                                             termOfElem_x,
                                             termOfElem_y)

        # if not found...
        return ''


    def _getTerminalIdOfFolios (self, page, reportType):
        """Returns a list with all 'terminal id' used by the 'next_report' elements
        allowing to search implicit borne connections
        @param page: diagram(page) XML etree object"""


        elementsToFind = self._getListOfElementsByType( reportType )
        ret = []

        for element in page.findall('.//element'):  # all elements in diagram
            if 'type' in element.attrib:  # elements must have a 'type'
                for el in elementsToFind:  # all elements in collection
                                           # that are 'next_report''
                    offset = len(element.attrib['type']) - len(el)
                    if (element.attrib['type'][offset:] == el):  # check if
                            # element is one of elements in collection collected
                        textField = element.find('terminals'). \
                                find( TYPE_TERMINAL ).attrib['id']
                        ret.append(textField)
        return list(set(ret))  # remove duplicates


    def _getTerminalIds (self, page, voltage):
        """Returns a list of terminals ID for all elements of type 'terminal'
        @param page: diagram(page) XML etree object
        @para voltage"""

        elementsToFind = self._getListOfElementsByType( TYPE_TERMINAL )
        ret = []

        for element in page.findall('.//element'):  # all elements in diagram
            if 'type' in element.attrib:  # elements must have a 'type'
                for el in elementsToFind:  # all elements in collection that are 'next_report''
                    offset = len(element.attrib['type']) - len(el)
                    if (element.attrib['type'][offset:] == el):  # check if element is one of elements in collection collected
                        for inp in element.find('inputs').findall('input'):
                            if 'text' in inp.attrib:
                                if inp.attrib['text'] == voltage:
                                    ret.append( element.find('terminals')[0]. \
                                            attrib['id'] )
                                    ret.append( element.find('terminals')[1]. \
                                            attrib['id'] )
        return list(set(ret))  # remove duplicates


    def _inPageRange (self, diagram):
        """Return True if the diagram in in the range of pages to be procesed
        @param diagram:  diagram(page) XML etree object
        @param pageOffset: offset for page numering consifering
                           the "table of contents"
        @return True/False"""

        page = int(diagram.attrib['order']) + self.pageOffset

        if page >= self.fromPage and (page <= self.toPage or self.toPage == 0):
            return True
        return False


    def _testElementType (self, listElements, element):
        """ Check if the name of 'element' is in the listElements
        and have a format like 'X1:1'
        @param listElements: list of elements names as patron
        @param element:  element  (XML etree object)
        @return: listElement that first input field has matched or '' if none"""

        if 'type' in element.attrib:  # elements must have a 'type'
            for el in listElements:
                offset = len( element.attrib['type'] ) - len( el )
                if self.DEBUG: print ("b) *%s* : *%s*" %(el, element.attrib['type'][offset:]))
                if (element.attrib['type'][offset:] == el):  # check if element is
                        # one of elements in collection collected
                    textField = self._getElementName (element)
                    if self.DEBUG: print ("c) %s" %textField)
                    if ( SEPARATOR in textField) and (len(textField) > 2):
                        return el
        return ''


    def get_list_of_used_terminals(self):
        """Return a list of all terminal elements used in the qet project.
         They could be of 2 types:
            - Explicits: represented by 'terminal' element.
            - Implicits: Search for conductors with same voltage
        For every terminal obtain data for the NOTH and SOUTH sides.

        @return [] dict of list where:
            {id: [element_uuid, terminal_block_name, terminal_name, terminal_xref
             north_id1, north_id2, north_cable_num, north_xref,
             south_id1, south_id2, south_cable_num, south_xref ] }

            where :
                id = terminal_block_name:terminal_name/index
            sample: ['{0fb2f876-b70f-44e2-9cb5-a4fecc52faf4}', 'X1', '9-D11'
                     '13', '27', '28', '13', '8-C6', '1', '', '13', '9-D12.']
        """

        elementsToFind = self._getListOfElementsByType( TYPE_TERMINAL )
        ret = {}  # return dict


        # first search for elements of type 'terminal'
        # in all pages and its conductors
        for diagram in self.qet_project.findall('diagram'):  # all diagrams

            if self._inPageRange (diagram):
                for element in diagram.findall('.//element'):  # all elements in diagram
                    if self._testElementType (elementsToFind, element):

                        # id and cable nums
                        terminals = element.find('terminals').findall( TYPE_TERMINAL )
                        terminalId1 = terminals[0].attrib['id']
                        terminalId2 = terminals[1].attrib['id']
                        cableNum0 = self._getCableNum(diagram, terminalId1)
                        cableNum1 = self._getCableNum(diagram, terminalId2)
                        terminalName = self._getElementName (element)
                        terminalUUID = element.attrib['uuid']
                        xRefTerminal = self._getXRef(diagram, element)  # xref for the terminal

                        if self.DEBUG:
                            print ('d) Terminal info. terminals: %s, id1: %s, id2: %s, terminal name: %s, term. UUID: %s'
                                %(terminals, terminalId1, terminalId2, terminalName, terminalUUID))


                        # check for conductors of one side of the terminal
                        lstCond = self._getListofConductorsWithId(diagram, terminalId1)
                        for cond in lstCond:
                            xRefDestination1 = self._testConductorIsABridge (diagram, cond[1], terminalName, terminalUUID)

                            if not xRefDestination1 == '' and terminalId1 != '':
                                # add/update to dicctionay
                                keyToUse = self._getIndexForNewTerminal (ret, terminalName,'1')

                                if not keyToUse in ret:  # it's a new key. adding new element
                                    ret[keyToUse] =  self._terminalStruct (terminalUUID,
                                                                       terminalName.split( SEPARATOR )[0],
                                                                       terminalName.split( SEPARATOR )[1])
                                cableNum = self._getCommonName (cableNum0, cableNum1)
                                ret[keyToUse][ IDX_TER_XREF ] = xRefTerminal
                                ret[keyToUse][ IDX_NORTH_ID1 ] = terminalId1
                                ret[keyToUse][ IDX_NORTH_ID2 ] = terminalId2
                                ret[keyToUse][ IDX_NORTH_CABLE_NUM ] = cableNum
                                ret[keyToUse][ IDX_NORTH_XREF ] = xRefDestination1


                        # check if the second conductor is considered a Bridge
                        lstCond = self._getListofConductorsWithId(diagram, terminalId2)
                        for cond in lstCond:
                            xRefDestination2 = self._testConductorIsABridge (diagram, cond[1], terminalName, terminalUUID)

                            if not xRefDestination2 == '' and terminalId2 != '':

                                # add/update to dicctionay
                                keyToUse = self._getIndexForNewTerminal (ret, terminalName,'2')

                                if not keyToUse in ret:  # it's a new key. adding new element
                                    ret[keyToUse] =  self._terminalStruct (terminalUUID,
                                                                       terminalName.split( SEPARATOR )[0],
                                                                       terminalName.split( SEPARATOR )[1])
                                cableNum = self._getCommonName (cableNum0, cableNum1)
                                ret[keyToUse][ IDX_TER_XREF ] = xRefTerminal
                                ret[keyToUse][ IDX_SOUTH_ID1 ] = terminalId1
                                ret[keyToUse][ IDX_SOUTH_ID2 ] = terminalId2
                                ret[keyToUse][ IDX_SOUTH_CABLE_NUM ] = cableNum
                                ret[keyToUse][ IDX_SOUTH_XREF ] = xRefDestination2

                        if self.DEBUG:
                            print ("-----------------------")
                            print ("Nombre terminal: " + terminalName.split( SEPARATOR )[0] + "   en " + xRefTerminal)
                            print ("Nuevo borne: " + keyToUse)
                            print ("Estado del bornero tras la insercion")
                            for l in ret.keys():
                                print (ret[l])
                            print ()


        # second, search for any conductor that is connected to a 'next_report' element
        if self.searchImplicitsConnections:
            for diagram in self.qet_project.findall('diagram'):  # all diagrams
                if self._inPageRange (diagram):
                    nextReportIds =  self._getTerminalIdOfFolios (diagram, TYPE_NEXT_REPORT)
                    previousReportIds =  self._getTerminalIdOfFolios (diagram, TYPE_PREVIOUS_REPORT)
                    allReportIds =  nextReportIds + previousReportIds

                    if diagram.find('conductors'):
                        for conductor in diagram.find('conductors').findall('conductor'):  # all conductor in a diagram
                            conductorIdTerminal1 = conductor.attrib['terminal1']
                            conductorIdTerminal2 = conductor.attrib['terminal2']

                            if ( conductorIdTerminal1 in allReportIds or conductorIdTerminal2 in allReportIds ) and not \
                                    (conductorIdTerminal1 in allReportIds and conductorIdTerminal2 in allReportIds):
                                # conductor is connected to a REPORT_FOLIO, buit not the 2 sides.
                                conductorNum = conductor.attrib['num']
                                if 'userx' in conductor.attrib and 'usery' in conductor.attrib:
                                    conductorX = int( conductor.attrib['userx'] )
                                    conductorY = int( conductor.attrib['usery'] )
                                else:
                                    conductorX = int( conductor.attrib['x'] )
                                    conductorY = int( conductor.attrib['y'] )

                                # check if condutor num  exists in the Terminal Block and none of its terminals don't
                                # correspond of an existing terminal
                                for ter in list(ret.keys()):

                                    # get all terminals ID used for all terminals that shares voltage in this page
                                    terminalsIdUsedByTerminals = []
                                    terminalsIdUsedByTerminals  =  self._getTerminalIds (diagram, ter.split( BORNE_INDEX_SEPARATOR )[0])


                                    if (conductorIdTerminal1 not in terminalsIdUsedByTerminals) and \
                                            (conductorIdTerminal2 not in terminalsIdUsedByTerminals) and \
                                            (conductorNum != '')  and \
                                            (ret[ter][ IDX_NORTH_CABLE_NUM ] == conductorNum or ret[ter][ IDX_SOUTH_CABLE_NUM ] == conductorNum):
                                            # conductor is not connected a processed terminal

                                        # add/update to dicctionay
                                        keyToUse = self._getIndexForNewTerminal (ret, ter.split(  BORNE_INDEX_SEPARATOR )[0], '')

                                        # assign data if is a new terminal
                                        if keyToUse not in ret:
                                            ret[keyToUse] = self._terminalStruct ('', ret[ter][ IDX_TB_NAME ], ret[ter][ IDX_TER_NAME ])

                                        # get Xref for the side of cable not connected to a netx-folio
                                        if (conductorIdTerminal1 not in terminalsIdUsedByTerminals):
                                            conductorTratado = conductorIdTerminal1
                                            xref = self._getElementXrefByConectorId (diagram, conductorIdTerminal1)
                                        else:
                                            conductorTratado = conductorIdTerminal2
                                            xref = self._getElementXrefByConectorId (diagram, conductorIdTerminal2)

                                        # assign the conductor to a free space
                                        if ret[keyToUse][ IDX_NORTH_XREF ] == '':  # NORTH side is free
                                            ret[keyToUse][ IDX_NORTH_ID1 ] = conductorTratado
                                            ret[keyToUse][ IDX_NORTH_CABLE_NUM ] = conductorNum
                                            ret[keyToUse][ IDX_NORTH_XREF ] = xref
                                        else:
                                            ret[keyToUse][ IDX_SOUTH_ID1 ] = conductorTratado
                                            ret[keyToUse][ IDX_SOUTH_CABLE_NUM ] = conductorNum
                                            ret[keyToUse][ IDX_SOUTH_XREF ] = xref

                                        break  # exit looping all terminals

                                        if self.DEBUG:
                                            print ("ids used :", end="")
                                            print (terminalsIdUsedByTerminals)
                                            print ("conductor num: " + conductorNum)
                                            print ("conductor id1: " + conductorIdTerminal1)
                                            print ("conductor id2: " + conductorIdTerminal2)
                                            print ("terminal where connect new conductor: " + keyToUse + '   ')
                                            print ("Estado del bornero tras la insecion")
                                            for l in ret.keys():
                                                print (ret[l])
                                            print ("---------------")

        return ret


    def _getDesignation (self, element):
        """ Return de designation label for the specified element.
        @param element:  element  (XML etree object)
        @return: Designation label or 0 if not exists"""

        for ei in element.find('elementInformations').findall('elementInformation'):
            if ei.attrib['name'] == 'designation':
                return int( ''.join( x for x in '0'+ ei.text if x.isdigit() ) )

        return 0


    def addPinToConnector (self, diagram, element, cnFullName, pinUUID, iNumPins, genere):
        """Adds info of the new pin to the connector
        cnIdxDict
        { Connector1/genere : [num_total_of_pins_specified_at_DESIGNATION_field,
                               num_pins_found, genere]
        }

        cnPinDict
        {
           Connector1/genere:pin : [ uuid, pin_name,  [xref1, xref2,...] ,
           Connector1/genere:pin : [ uuid, pin_name,  [xref1, xref2,...] ,
           Connector_n/genere:pin : [ uuid, pin_name,  [xref1, xref2,...] ,
        }

        @param diagram: page (XML etree object)
        @param element: element (XML etree object)
        @param cnDict: dict where add info
        @param cnFullName: fullname of the pin at the schema (e.g. X1:2)
        @param pinUUID: identificator of element
        @param iNumPins: num pins specified on the 'designator' field
        @param genere: male or femal ('m' or 'f')
        @return (modifies cnDict attribute) """

        _UUID_ = 0
        _PIN_NAME_ = 1
        _XREF_ = 2
        _NUM_PINS_DESIGNATION_ = 0
        _NUM_PINS_COUNT_ = 1

        cnNamePart = cnFullName.split( SEPARATOR )[0]  # e.g. X1
        cnPinPart = cnFullName.split( SEPARATOR )[1]  # e.g. 1

        cnIdxKey = cnNamePart + '/' + genere
        cnPinKey = cnIdxKey + ':' + cnPinPart

        if False:
            print("INFO:")
            print("cnFullName: " + cnFullName)
            print("cnNamePart: " + cnNamePart)
            print("cnPinPart: " + cnPinPart)
            print("pinUUID: " + pinUUID)
            print("iNumPins: " + str(iNumPins))
            print("genere: " + genere)
            print ()

        # Refresh num of pins for the connector
        if (not cnIdxKey in self.cnIdxDict):  # If is the first time: init
            self.cnIdxDict[ cnIdxKey ] = [0,0, genere]

        # Memo for 'designation' field
        if self.cnIdxDict[ cnIdxKey ][ _NUM_PINS_DESIGNATION_ ] < iNumPins:
            self.cnIdxDict[ cnIdxKey ][ _NUM_PINS_DESIGNATION_ ] = iNumPins

        # New pin: init & increment # pins
        if (not cnPinKey in self.cnPinDict):
            self.cnPinDict[ cnPinKey ] = [ '', '',[] ]  # blank data
            self.cnIdxDict[ cnIdxKey ][ _NUM_PINS_COUNT_ ] += 1

        # Update data for the current pin
        self.cnPinDict[ cnPinKey ][ _UUID_ ] = pinUUID
        self.cnPinDict[ cnPinKey ][ _PIN_NAME_ ] = cnPinPart
        self.cnPinDict[ cnPinKey ][ _XREF_ ].append(
                self._getXRef(diagram, element, offset_x = 0, offset_y = 0) )

        if True:
            print("Pin añadido")
            print (self.cnIdxDict[cnIdxKey])
            print (self.cnPinDict[cnPinKey])
            print ()


    def get_list_of_used_connectors(self):
        """Return a list of all connector elements used in the qet project.

        @return {} dict of list where:
            For every connector name: X1, X2,...
             {

               Connector1/genere:pin : [ uuid, pin_name,  [xref1, xref2,...] ,
               Connector1/genere:pin : [ uuid, pin_name,  [xref1, xref2,...] ,
               Connector_n/genere:pin : [ uuid, pin_name,  [xref1, xref2,...] ,
               Connector1/genere : num_total_of_pins_specified_at_DESIGNATION_field
              }
        """

        # search for elements of type conductor and fills dict
        for diagram in self.qet_project.findall('diagram'):  # all diagrams
            if self._inPageRange (diagram):
                for element in diagram.findall('.//element'):  # all elements in diagram
                    sType = self._testElementType ( ELEMENT_NAME_CONNECTORS, element)
                    if sType:
                        # common data
                        pinUUID = element.attrib['uuid']
                        cnFullName = self._getElementName (element)  # e.g. X1:1
                        iNumPins = self._getDesignation(element)

                        # print ("sType:  " + sType)
                        # determine genere
                        if '_m.' in sType:
                            self.addPinToConnector ( diagram, element, cnFullName, pinUUID, iNumPins, 'm' )
                        elif '_f.' in sType:
                            self.addPinToConnector ( diagram, element, cnFullName, pinUUID, iNumPins, 'f' )
                        else:  # male and female
                            self.addPinToConnector ( diagram, element, cnFullName, pinUUID, iNumPins, 'm' )
                            self.addPinToConnector ( diagram, element, cnFullName, pinUUID, iNumPins, 'f' )

        if False:
            for key in sorted(self.cnIdxDict):
                print ("%s: %s" % (key, self.cnIdxDict[key]) )
            print ()
            for key in sorted(self.cnPinDict):
                print ("%s: %s" % (key, self.cnPinDict[key]) )

        return [self.cnIdxDict, self.cnPinDict]


    def _getCommonName (self, cable1, cable2):
        """Returns the num of the cable according:
            - If are equal, returns
            - If one is blank, returns the no blank"""

        if cable1 == cable2:
            return cable1
        else:
            if cable1 == '':
                return cable2
            else:
                return cable1


    def _terminalStruct(self, uuid, tbName, terminalName):
        # {id: [element_uuid, terminal_block_name, terminal_name, termianl_xref
        #     north_id1, north_id2, north_cable_num, north_xref,
        #     south_id1, south_id2, south_cable_num, south_xref ] }
        return [uuid, tbName, terminalName, '', '', '', '', '', '', '','','']


    def _getIndexForNewTerminal (self, TBdict, terminalId, side):
        """ For every new terminal, we'll add if not exist or the side specified is yes occuped.
        If there are space, returns the key of existing terminal at block terminal.
        The dictionary keys like as : terminal_block_name:terminal_name/index

        @param TBdict: dictionary with terminals recolected
        @param textField: terminal_block_name:terminal_name
        @param side: 1 or 2 side (NORTH or SOUTH)

        TODO: optimize """

        # use a free space
        if side == '':
            #print (TBdict)
            for tb in [ x for x in TBdict.keys() if x[:-2] == terminalId ]:
                if TBdict[tb][ IDX_NORTH_XREF ] == '' or TBdict[tb][ IDX_SOUTH_XREF ]=='': # Xref for north or south is free
                    return tb
            # no space left. Calc a new ID
            filtered = [ int(x.split( BORNE_INDEX_SEPARATOR )[1]) for x in TBdict.keys() if x[:-2]== terminalId]
            index =  max ( filtered or [0]) + 1
            return terminalId + BORNE_INDEX_SEPARATOR + str(index)

        # new terminal block if...
        if side == '1,2' or side == '2,1':  # is a complete new terminal
            filtered = [ int(x.split( BORNE_INDEX_SEPARATOR )[1]) for x in TBdict.keys() if x[:-2] == terminalId]
            index =  max ( filtered or [0]) + 1
            return terminalId + BORNE_INDEX_SEPARATOR + str(index)

        # north side especified
        if side == '1':
            for tb in [ x for x in TBdict.keys() if x[:-2] == terminalId ]:
                if TBdict[tb][ IDX_NORTH_XREF ] == '': # Xref for north side is not used
                    return tb
            # no space left. Calc a new ID
            filtered = [ int(x.split( BORNE_INDEX_SEPARATOR )[1]) for x in TBdict.keys() if x[:-2]== terminalId]
            index =  max ( filtered or [0]) + 1
            return terminalId + BORNE_INDEX_SEPARATOR + str(index)

        # SOUTH side especified
        if side == '2':
            for tb in [ x for x in TBdict.keys() if x[:-2]== terminalId ]:
                if TBdict[tb][ IDX_SOUTH_XREF ] == '': # Xref for south side is not used
                    return tb
            # no space left. Calc a new ID
            filtered = [ int(x.split( BORNE_INDEX_SEPARATOR )[1]) for x in TBdict.keys() if x[:-2]== terminalId]
            index =  max ( filtered or [0]) + 1
            return terminalId + BORNE_INDEX_SEPARATOR + str(index)


class TerminalBlock:
    """This class represents a Terminal Block for a QET project."""

    DEBUG = False

    # Constants to clarify list access
    _IDX_TERM_NAME_ = 2


    def __init__(self, tb_id, qet_project_title, \
             tb_folder_name, config, reservation, implicit):
        """initializer.
        @param string tb_id: id for this terminal block (e.g. X1)
        @param string qet_project_title: label to give name to the
                     element at collection
        @param tb_folder_name: name of the folder to crete at personal
             collection dir (ends with /)
        @param config: dict with config info. This allows diferent config for every
            block terminal
        @param reservation: true/false for create terminals reservation
        @param implicit: true if tb was generated searching implicits connections.
            If true show xref for conductor in every terminal
            If false show xref for the terminal itself """

        self.tb_id = tb_id
        self.qet_project_title = qet_project_title
        self.tb_folder_name =  tb_folder_name
        self.config = config
        self.reservation = reservation
        self.implicit = implicit

        self.element_dir_name = self.config['collection'] + tb_folder_name + os.sep
        self.terminals = [] #terminals belongs this block
        self._create_collection_index_file(self.element_dir_name)


    def addTerminals (self, terminals):
        """Add terminals to the block, but only accept terminals that haves
        the same 'terminal block' as the defined on constructor.
        @param terminals: dict of lists with terminal info. The format is:
                {id: [element_uuid, terminal_block_name,
                      terminal_name, terminal1_id, terminal2_id
                NORTH_cable_num, NORTH_xref, SOUTH_cable_num, SOUTH_xref ] }"""
        for b in terminals.keys():
            if b.split( SEPARATOR )[0] == self.tb_id:
                self.terminals.append(terminals[b])


    def _create_collection_index_file(self, sCollectionPath):
        """Collection index file. Create directory if not exists
        @param sCollectionPath
        @return: none"""

        # creates if not exist
        if (sCollectionPath[-1] != os.sep): sCollectionPath += os.sep
        if not os.path.exists(sCollectionPath): os.makedirs(sCollectionPath)

        # create QET directory file
        f = open(sCollectionPath + 'qet_directory', 'w')
        xml = ['<qet-directory>',
               '    <names>',
               '        <name lang="en">TEMP: Terminal Blocks</name>',
               '    </names>',
               '</qet-directory>']
        f.writelines(["%s\n" % line for line in xml])
        f.close()


    def _sort_tb(self, listTerminals):
        """Sort a dict of lists. Every sublist have the info of a terminal
        like this:
                [element_uuid, terminal_block_name, terminal_name,
                terminal1_id, terminal2_id, NORTH_cable_num, NORTH_xref,
                SOUTH_cable_num, SOUTH_xref ]

        This function, considers that the 'terminal_block' field is the same
        for all terminals.
        The field 'terminal_number' are sorted in this order:
          Type 1: Untyped: GND, R, S, T, M1A, M2A, M3A,... sorted alphabetically
                  (GND, M1A, M2A, M3A, R, S, T)
          Type 2: Letters + Number : R1, V1, U1, U2, GND1, ... and every is sorted
                  alphabetically (GND1,R1,U1,V1,U2)
          Type 3: Negative + Number: -0, -1 : Order numerically
          Type 4: Positive + Number: +0, +1, +2, +1,: Order numerically
          Type 5: Only Numbers: 1, 3, 7, 33,... Order numerically

        Adds 3 temporal fields at every sublist for sort purposes:
        [-3]: Type of terminal
        [-2]: Numeric part of terminal name
        [-1]: No numeric part

        The last criteria to sort is ther number in NORTH XREF.

        @param listTerminals: list of lists
        @return listTerminals sorted."""

        TYPE_1 = 1  # untyped
        TYPE_2 = 2  # letters + numbers
        TYPE_3 = 3  # Negative + numbers
        TYPE_4 = 4  # Positive + numbers
        TYPE_5 = 5  # only numbers

        _IDX_TERMINAL_NUM = 2
        _IDX_NORTH_XREF = 6
        _IDX_NEW_SORT_TYPE = -3
        _IDX_NEW_SORT_NUM = -2
        _IDX_NEW_SORT_NOT_NUM = -1


        # determine type of terminal name and prepare temp data to sort
        for t in listTerminals:
            sTBName = t[ _IDX_TERMINAL_NUM ]
            if re.match('^\d+$', sTBName):  # Type 5
                newSortType = TYPE_5
                newSortNum = sTBName
                newSortNotNum = ''
            elif re.match('^(\+)(\d)+$', sTBName):  # Type 4
                newSortType = TYPE_4
                foo = re.match('^(\+)(\d)+$', sTBName)
                newSortNum = foo.group(2)
                newSortNotNum = foo.group(1)
            elif re.match('^(\-)(\d)+$', sTBName):  # Type 3
                newSortType = TYPE_3
                foo = re.match('^(\-)(\d)+$', sTBName)
                newSortNum = foo.group(2)
                newSortNotNum = foo.group(1)
            elif re.match('^(\D+)(\d+)$', sTBName):  # Type 2
                newSortType = TYPE_2
                foo = re.match('^([a-zA-Z]+)(\d+)$', sTBName)
                newSortNum = foo.group(2)
                newSortNotNum = foo.group(1)
            else:  # Type 1
                newSortType = TYPE_1
                newSortNum = ''
                newSortNotNum = sTBName

            t.append(newSortType)  # [-3]
            t.append(newSortNum)  # [-2]
            t.append(newSortNotNum)  # [-1]

        # Sort Type 1: untyped
        subData1 = [x for x in listTerminals if x[ _IDX_NEW_SORT_TYPE ] == TYPE_1]
        subData1.sort(key=lambda x:
                (
                    x[ _IDX_NEW_SORT_NOT_NUM ],
                    self._getNum( x[ _IDX_NORTH_XREF ] )
                 ))

        # Sort Type 2: letters + numbers
        subData2 = [x for x in listTerminals if x[ _IDX_NEW_SORT_TYPE ] == TYPE_2]
        subData2.sort(key=lambda x:
                (
                    int(x[ _IDX_NEW_SORT_NUM ]),
                    x[ _IDX_NEW_SORT_NOT_NUM ],
                    self._getNum( x[ _IDX_NORTH_XREF ] )
                 ))

        # Sort Type 3: Negative + numbers
        subData3 = [x for x in listTerminals if x[ _IDX_NEW_SORT_TYPE ] == TYPE_3]
        subData3.sort( key=lambda x:
                (   x[ _IDX_NEW_SORT_NUM ],
                    self._getNum( x[ _IDX_NORTH_XREF ] )
                ))

        # Sort Type 4: Positive + numbers
        subData4 = [x for x in listTerminals if x[ _IDX_NEW_SORT_TYPE ] == TYPE_4]
        subData4.sort( key=lambda x:
                (
                    x[ _IDX_NEW_SORT_NUM ],
                    self._getNum( x[ _IDX_NORTH_XREF ] )
                ))

        # sort type 5: only numbers
        subData5 = [x for x in listTerminals if x[ _IDX_NEW_SORT_TYPE ] == TYPE_5]
        subData5.sort(key=lambda x:
                (
                    int(x[ _IDX_NEW_SORT_NUM ]),
                    self._getNum( x[ _IDX_NORTH_XREF ] )
                ))

        # return
        return [x[:-3] for x in subData1 + subData2 + subData3 + subData4 + subData5]  # delete temp fields


    def _getNum(self, x):
        """ Returns the page part as integer of a XREF. Is there isn't digits,
        return 9999. Usefull for sort reasons.
        e.g. '12-B8' """

        foo = x.split('-')[0]
        if foo.isdigit():
            return int(foo)
        else:
            return 9999


    def _get_empty_terminal(self, terminal_name=''):
        """Returns a list corresponding a new empty terminalself.

        The new terminal haves the same teminal_block_name.

        @param terminal_name: name/number for the terminal block
        @return: valid list format for a terminal.
        """
        # [element_uuid, terminal_block_name, terminal_name/number, terminal_xref,
        # NORTH cable id side 1, N.cable id side 2, N.cable num, N. cable destination xref,
        # SOUTH cable id side 1, S.cable id side 2, S.cable num, S. cable destination xref]
        return ['', self.tb_id, str(terminal_name), '', \
                '', '', self.config['reservation_label'], '', \
                '', '', self.config['reservation_label'], '']


    def _generate_reservation_numbers(self):
        """Creates new terminals ID for gaps if exist.

        Only check gaps for numerical ID's (not for +1, -0,...).
        The list of terminal_numbers comes from a unique block terminal,
        i.e. X1, X12,...

        NOTE: Modify self.terminals
        @return list with gaps filled and sorted.
        """

        only_numbers = [int(x[self._IDX_TERM_NAME_])
            for x in self.terminals if x[self._IDX_TERM_NAME_].isdigit()]
        only_numbers.sort()
        if self.DEBUG:
            print ("<drawTerminalBlock> Reservation - {}". \
                format(only_numbers))

        print ('{}'.format(self.terminals[0]))

        if only_numbers:  # if the are digits in terminals numeration
            for i in range(1, int(only_numbers[-1])):
                if i not in only_numbers:
                    self.terminals.append( self._get_empty_terminal(i))


    def drawTerminalBlock(self):
        """Creates a XML file with the terminal block elements. if creates more
        than one folio (a lot of terminals) creates a index (0,1,...) as file name
        suffix.
        When start the firt terminal numered by a integer, inserts automatic
        RESERVATION of terminals format:
            [element_uuid, terminal_block_name, terminal_name, terminal1_id,
             terminal2_id, NORTH_cable_num, NORTH_xref, SOUTH_cable_num,
             SOUTH_xref ]

        coord (0,0) al corner upper-left

        @(param) self.terminals
        @return: none"""


        # Create reservation terminals. Terminals number are string,
        # and can be a number or not ('-0', '+2',...)
        if self.reservation:
            self._generate_reservation_numbers()  # changes self.terminals

        # sort the terminals of the block
        dataSorted = self._sort_tb(self.terminals)

        # Fill with reservations
        lastNum = 0
        fFinish = False
        reservation = []  # list of new reservations

        # Definitios to detect brigded terminals
        last_cable_number1 = '*'  # used to draw a bridge between terminals
        last_cable_number2 = '*'
        last_terminal_name = '*'

        # Vertical coord depend if TB was generated searching implitic or not connections
        if self.implicit:
            y_coord_num = 40
            y_coord_bridge = 0
            y_coord_north_xref = 85
            y_coord_south_xref = 3
        else:
            y_coord_num = 20
            y_coord_bridge = 20
            y_coord_xref = 65

        i2 = 0
        for i1 in range(0, len(dataSorted), self.config['max_page']):
            # process every Term- Block of max length per folio

            i2 = (i2 + self.config['max_page'])
            if i2 > len(dataSorted): i2 = len(dataSorted)
            subData = dataSorted[i1:i2]

            # Calcs
            iQuantity = len(subData)  # number of terminals

            totalWith = self.config['head_width'] + self.config['union_width'] + (iQuantity * self.config['terminal_width'])
            totalWithRoundedUp = totalWith + 1  # +1 to force round the next tenth
            while (totalWithRoundedUp % 10): totalWithRoundedUp += 1  # next tenth

            totalHeight = self.config['head_height'] + 20 + 20  # 20 is line to terminal north and south
            totalHeightRoundedUp = totalHeight + 1  # +1 to force round the next tenth
            while (totalHeightRoundedUp % 10): totalHeightRoundedUp += 1  # next tenth

            sUUID = uuid.uuid1().urn[9:]
            sID = self.qet_project_title + ' ' + self.tb_id + '(' + str(i1 + 1) + '-' + str(
                i2) + ')'  # element id in collection
            file_name = self.element_dir_name + self.qet_project_title + \
                        '_' + self.tb_id + '_' + str(i1 + 1) + '-' + str(i2) + '.elmt'  # file name for the element

            #### Start 'drawing'
            rect_style = ' antialias="false" style="line-style:normal;line-weight:normal;filling:white;color:black"'
            line_style = ' antialias="false" style="line-style:normal;line-weight:normal;filling:none;color:black"'

            xml = [
                '<definition link_type="simple" hotspot_x="5" hotspot_y="24" width="%i" type="element" orientation="dyyy" height="%i" >' \
                % (totalWithRoundedUp, totalHeightRoundedUp),
                '  <uuid uuid="%s"/>' % sUUID,
                '  <names>',
                '    <name lang="en">%s</name>' % sID,
                '  </names>',
                '  <informations></informations>',
                '  <description>']
            x = 0
            # head
            xml.append('    <rect x="%i" y="0" width="%i" height="%i"' \
                       % (x, self.config['head_width'], self.config['head_height']) + rect_style + '/>')
            x += self.config['head_width']

            # head union
            xml.append('    <rect x="%i" y="%i" width="%i" height="%i"' \
                       % (x, (self.config['head_height'] - self.config['union_height']) / 2, self.config['union_width'], self.config['union_height']) + \
                       rect_style + '/>')
            x += self.config['union_width']

            # TB ID
            xml.append('    <input text="%s" tagg="label" rotation="270" size="10" x="%i" y="%i"' \
                       % (self.tb_id, self.config['head_width'] / 2, self.config['head_height'] / 2 + (len(self.tb_id) / 2) * 10) + '/>')
            # All terminals
            for t in subData:
                halfx = x + self.config['terminal_width'] / 2
                # terminal rectangle
                xml.append('    <rect x="%i" y="0" width="%i" height="%i"' \
                           % (x, self.config['terminal_width'], self.config['head_height']) + rect_style + '/>')
                # terminal name
                xml.append('    <text text="%s" rotation="270" size="9" x="%i" y="%i"/>' % (
                t[ IDX_TER_NAME ], halfx + 4, self.config['head_height'] - y_coord_num))

                if self.implicit:  # configured for searching implicit
                    # terminal NORTH xref
                    xml.append('    <text text="%s" rotation="270" size="6" x="%i" y="%i"/>' % (
                    t[ IDX_NORTH_XREF ], halfx + 4, self.config['head_height'] - y_coord_north_xref))

                    #terminal SOUTH xref
                    xml.append('    <text text="%s" rotation="270" size="6" x="%i" y="%i"/>' % (
                    t[ IDX_SOUTH_XREF ], halfx + 4, self.config['head_height'] - y_coord_south_xref))

                else:
                    # terminal xref
                    xml.append('    <text text="%s" rotation="270" size="7" x="%i" y="%i"/>' % (
                    t[ IDX_TER_XREF ], halfx + 4, self.config['head_height'] - y_coord_xref))

                #north cable num
                xml.append(
                    '    <input text="%s" tagg="none" rotation="270" size="6" x="%i" y="%i"/>' % (
                    t[ IDX_NORTH_CABLE_NUM ], halfx - 4, -0))

                #south cable num
                xml.append('    <input text="%s" tagg="none" rotation="270" size="6" x="%i" y="%i"/>' % (
                    t[ IDX_SOUTH_CABLE_NUM ], halfx - 4, self.config['head_height'] + 40))
                xml.append(
                    '    <line length2="1.5" y1="%i" y2="%i" x1="%i" end1="none" x2="%i" end2="none" length1="1.5"' \
                    % (0, -20, halfx, halfx) + line_style + '/>')
                xml.append(
                    '    <line length2="1.5" y1="%i" y2="%i" x1="%i" end1="none" x2="%i" end2="none" length1="1.5"' \
                    % (self.config['head_height'], self.config['head_height'] + 20, halfx, halfx) + line_style + '/>')

                xml.append('    <terminal orientation="n" x="%i" y="%i"/>' % (halfx, 0 - 20))
                xml.append('    <terminal orientation="s" x="%i" y="%i"/>' % (halfx, self.config['head_height'] + 20))
                center = ( self.config['head_height'] / 2 ) - 16
                xml.append('    <circle x="%i" y="%i" diameter="4"' % (halfx - 2, center + y_coord_bridge) + line_style + '/>')
                # bridge

                if self._brigeNeeded( last_terminal_name, last_cable_number1, last_cable_number2,
                                      t[ IDX_TER_NAME ],
                                      t[ IDX_NORTH_CABLE_NUM ],
                                      t[ IDX_SOUTH_CABLE_NUM ] ):
                    xml.append(
                        '    <line length2="1.5" y1="%i" y2="%i" x1="%i" end1="none" x2="%i" end2="none" length1="1.5"' \
                        % (center + 2 + y_coord_bridge, center + 2 + y_coord_bridge, halfx - self.config['terminal_width'], halfx) + line_style + '/>')
                last_cable_number1 = t[ IDX_NORTH_CABLE_NUM ]
                last_cable_number2 = t[ IDX_SOUTH_CABLE_NUM ]
                last_terminal_name = t[ IDX_TER_NAME ]

                x += self.config['terminal_width']

            xml.append('  </description>')
            xml.append('</definition>')

            # write to file
            with open(file_name + '', 'w') as f:
                f.writelines(["%s\n" % line for line in xml])


    def _brigeNeeded (self, t1Name, t1c1, t1c2, t2Name, t2c1, t2c2):
        """Detect if a bridge is needed between current and previous terminal.

        A bridge is needed according the terminal names and cables numbers"""

        res = self.config['reservation_label']

        if self.DEBUG:
            print ('<_brigeNeeded> - Borne 1: {} {},{}  Borne 2:{} {},{}'. \
                format(t1Name, t1c1, t1c2, t2Name, t2c1, t2c2))

        # Check differents options
        if (t1c1 != '') \
            and (t1c1 == t2c1 or t1c1 == t2c2) \
            and (t1c1 != res): return True
        if (t1c2 != '') \
            and (t1c2 == t2c1 or t1c2 == t2c2) \
            and (t1c2 != res): return True
        if (t2c1 != '') \
            and (t2c1 == t1c1 or t2c1 == t1c2) \
            and (t2c1 != res): return True
        if (t2c2 != '') \
            and (t2c2 == t1c1 or t2c2 == t1c2) \
            and (t2c2 != res): return True
        if (t1c1 == '')  \
            and (t1c2 == '') \
            and (t1Name == t2Name) \
            and (t2Name != res): return True
        if (t2c1 == '') \
            and (t2c2 == '') \
            and (t1Name == t2Name) \
            and (t2Name != res): return True
        return False



class Connector:
    """This class represents a Connector for a QET project."""

    def __init__(self, cnId, iPins, genere, qet_project_title, \
             cnFolderName, config):
        """initializer.
        @param string cnId: id for this connector (e.g. X1)
        @param iPins: amount of pins
        @param genere: 'm' / 'f' (male/female)
        @param string qet_project_title: label to give name to the
                     element in collection
        @param cnFolderName: name of the folder to create at personal
             collection dir (ends with /)
        @param config: dict with config info. This allows diferent config for every
            block terminal """

        self.cnId = cnId
        self.cnName = cnId.split('/')[0]
        self.iPins = iPins
        self.genere = genere
        self.fullGenere = {'m':'Male', 'f':'Female'}[genere]
        self.qet_project_title = qet_project_title
        self.cnFolderName =  cnFolderName
        self.config = config

        self.element_dir_name = self.config['collection'] + cnFolderName + os.sep
        self.pins = []  # pins belongs this connector
        self._create_collection_index_file(self.element_dir_name)


    def addPins (self, pinsDict):
        """Add pins to the connector. Receive a dict with a los of pins, but only
        accept pins that haves the same ID as the defined on constructor.
        @param int amountOfPins: num total of pins for the connector
        @param dict pinsDict: dict with pins info. The format is:
            {
               Connector1/genere:pin : [ uuid, pin_name,  [xref1, xref2,...] ,
               Connector1/genere:pin : [ uuid, pin_name,  [xref1, xref2,...] ,
               Connector_n/genere:pin : [ uuid, pin_name,  [xref1, xref2,...] ,
            }
        @return (modify self.pins) """
        for p in pinsDict.keys():
            if p.split( ':' )[0] == self.cnId:
                self.pins.append(pinsDict[p])


    def drawConnector(self):
        """Creates a XML file with the connector element.

        coord (0,0) al corner top-left of the rectangle

        @(param) self.terminals
        @return: none"""

        PIN_NAME = 2
        LABEL_HEIGTH = 30
        CN_COLS = 2
        CN_ROWS = int(self.iPins / 2 + 0.5)
        CN_PIN_VERTICAL_SPACE = 30
        CN_TOP_BOTTOM_MARGIN = 20
        CN_WITH = 90
        CN_RECT_HEIGHT =((CN_ROWS - 1 ) * CN_PIN_VERTICAL_SPACE) + \
                    ( 2 * CN_TOP_BOTTOM_MARGIN )
        CN_FEMALE_DIAMETER = 10
        CN_PIN_LENGHT = 12

        # sort the pins of the connector
        self.pins.sort(key=lambda x: x[ PIN_NAME ], reverse = False)
        if False:
            for e in self.pins:
                print (e)

        # Calcs
        totalWith = CN_WITH
        totalHeight = CN_RECT_HEIGHT +  LABEL_HEIGTH

        sUUID = uuid.uuid1().urn[9:]
        sID = self.qet_project_title + ' ' + self.cnId  # element id in collection
        file_name = self.element_dir_name + self.qet_project_title + \
                '_' + self.cnId.replace('/','_') + '.elmt'  # file name for the element

        #### Start 'drawing'
        xml = self._getXMLHead(totalWith, totalHeight, sUUID, sID)

        # title
        xml.append( self._getXMLText (0, 6, 10, 'e', '' ) )
        xml.append( self._getXMLText (0, 6, 10, 'e', self.cnName ) )
        xml.append( self._getXMLText ( 38, 7, 8, 'e', self.fullGenere ) )
        xml.append( self._getXMLText ( 38, 19, 8, 'e', self.iPins ) )
        xml.append( self._getXMLLine (0, 12 , CN_WITH, 12) )
        xml.append( self._getXMLLine (40, 0 , 40, 22) )

        # rectangle
        xml.append( self._getXMLRect (0, LABEL_HEIGTH, CN_WITH, CN_RECT_HEIGHT) )  # contourn rectangle

        if self.genere == 'm':  # male
            for i in range(0, CN_ROWS):
                y = (i * CN_PIN_VERTICAL_SPACE) + CN_TOP_BOTTOM_MARGIN + LABEL_HEIGTH
                pin_name_left = i + 1
                pin_name_right = CN_ROWS + i + 1

                # left pin
                xml.append( self._getXMLPin (0, y, 'w') )
                xml.append( self._getXMLText ( 0 + 14, y, 8, 'e', pin_name_left ) )
                xml.append( self._getXMLLine (0, y , CN_PIN_LENGHT, y) )
                xml.append(self._getXMLLineStrong (CN_PIN_LENGHT, y, CN_PIN_LENGHT + 5, y) )
                sXref = self._getXREF(pin_name_left)
                xml.append( self._getXMLText ( -len(sXref) * 6, y, 6, 'e', sXref ) )

                # rigth pin
                xml.append( self._getXMLPin (CN_WITH, y, 'e') )
                xml.append( self._getXMLText (CN_WITH - 40 , y, 8, 'e', pin_name_right ) )
                xml.append( self._getXMLLine (CN_WITH, y , CN_WITH - CN_PIN_LENGHT, y) )
                xml.append(self._getXMLLineStrong (CN_WITH - CN_PIN_LENGHT - 5,
                         y, CN_WITH - CN_PIN_LENGHT, y) )  # male rigth
                xml.append( self._getXMLText ( CN_WITH, y, 6, 'e', self._getXREF(pin_name_right) ) )

        else:  # female
            for i in range(0, CN_ROWS):
                y = (i * CN_PIN_VERTICAL_SPACE) + CN_TOP_BOTTOM_MARGIN + LABEL_HEIGTH
                pin_name_left = CN_ROWS + i + 1
                pin_name_right = i + 1

                # left pin
                xml.append( self._getXMLPin (0, y, 'w') )
                xml.append( self._getXMLText ( 0 + 14, y, 8, 'e', pin_name_left ) )
                xml.append( self._getXMLLine (0, y , CN_PIN_LENGHT, y) )
                xml.append(self._getXMLArc ( CN_PIN_LENGHT , y - (CN_FEMALE_DIAMETER/4) ,
                            90, 180, CN_FEMALE_DIAMETER ) )
                sXref = self._getXREF(pin_name_left)
                xml.append( self._getXMLText ( -len(sXref) * 6, y, 6, 'e', sXref ) )


                # right pin
                xml.append( self._getXMLPin (CN_WITH, y, 'e') )
                xml.append( self._getXMLText (CN_WITH - 40 , y, 8, 'e', pin_name_right ) )
                xml.append( self._getXMLLine (CN_WITH, y , CN_WITH - CN_PIN_LENGHT, y) )
                xml.append(self._getXMLArc ( CN_WITH - CN_PIN_LENGHT - CN_FEMALE_DIAMETER/2,
                        y - (CN_FEMALE_DIAMETER / 4),
                        -90, 180, CN_FEMALE_DIAMETER ) )
                xml.append( self._getXMLText ( CN_WITH , y, 6, 'e', self._getXREF(pin_name_right) ) )

        xml.append('  </description>')
        xml.append('</definition>')

        # write to file
        with open(file_name + '', 'w') as f:
            f.writelines(["%s\n" % line for line in xml])


    def _getXREF(self, iPin):
        """Returns the xrefs for a specific pin
        @param iPin: pin number
        @return string of the xref comma separated"""

        ret = ''
        listOfXrefs = [x[2] for x in self.pins if x[1] == str(iPin)]
        if len(listOfXrefs):
            ret = ', '.join([x for x in listOfXrefs[0]] )

        return ret


    def _getXMLHead (self, totalWith, totalHeight, sUUID, name):
        """Return the starting of the XML for a element
        @param totalWith
        @param totalHeight
        @param sUUID
        @param name
        @return list with XML content
        """

        #Round to the next tenth
        totalWithRoundedUp = totalWith + 1  # +1 to force round the next tenth
        while (totalWithRoundedUp % 10): totalWithRoundedUp += 1  # next tenth

        totalHeightRoundedUp = totalHeight + 1  # +1 to force round the next tenth
        while (totalHeightRoundedUp % 10): totalHeightRoundedUp += 1  # next tenth

        return ['<definition link_type="simple" hotspot_x="0" hotspot_y="0" width="%i" type="element" orientation="dyyy" height="%i" >' \
                % (totalWithRoundedUp, totalHeightRoundedUp),
                '  <uuid uuid="%s"/>' % sUUID,
                '  <names>',
                '    <name lang="en">%s</name>' % name,
                '  </names>',
                '  <informations></informations>',
                '  <description>']


    def _getXMLRect (self, x, y, width, height):
        """Return XML rect for a QET element
        @param x: lower left corner coord
        @param y: lower left corner coord
        @param width
        @param height
        @return: list with XML content"""

        style = ' antialias="false" style="line-style:normal;line-weight:normal;filling:none;color:black"'
        return '    <rect x="%i" y="%i" width="%i" height="%i"' \
                % (x, y, width, height) + style + '/>'


    def _getXMLLine (self, x1, y1, x2, y2):
        """Return XML rect for a QET element
        @param x, y : first coord
        @param x1, y1 : second coord
        @return: list with XML content"""

        style = ' antialias="false" style="line-style:normal;line-weight:normal;filling:none;color:black"'
        return '    <line x1="%i" y1="%i" x2="%i"  y2="%i" end1="none" end2="none" length1="1.5" length2="1.5"' \
                % (x1, y1, x2, y2) + style + '/>'


    def _getXMLLineStrong (self, x1, y1, x2, y2):
        """Return XML rect for a QET element
        @param x, y : first coord
        @param x1, y1 : second coord
        @return: list with XML content"""

        style = ' antialias="false" style="line-style:normal;line-weight:hight;filling:none;color:black"'
        return '    <line x1="%i" y1="%i" x2="%i"  y2="%i" end1="none" end2="none" length1="1.5" length2="1.5"' \
                % (x1, y1, x2, y2) + style + '/>'


    def _getXMLCircle (self, x, y, diameter):
        """Return XML rect for a QET element
        @param x, y : first coord
        @param diameter
        @return: list with XML content"""

        style = ' antialias="false" style="line-style:normal;line-weight:normal;filling:none;color:black"'
        return '    <circle x="%i" y="%i" diameter="%i"' \
                % (x + diameter/2, y + diameter/2, diameter) + style + '/>'


    def _getXMLArc (self, x, y, startAngle, angle, diameter):
        """Return XML rect for a QET element
        @param x, y : first coord
        @param diameter
        @return: list with XML content"""

        style = ' style="line-style:normal;line-weight:normal;filling:none;color:black"  antialias="true"'
        return '    <arc x="%i" y="%i" height="%i" width="%i" start="%i" angle="%i"' \
                % (x, y, diameter / 2, diameter / 2, startAngle, angle) + style + '/>'


    def _getXMLPin (self, x, y, orientation):
        """Return XML rect for a QET element
        @param x: lower left corner coord
        @param y: lower left corner coord
        @param orientation: n, s, e, w
        @return: list with XML content"""

        return '    <terminal orientation="%s" x="%i" y="%i"/>' \
                % (orientation, x, y)


    def _getXMLText (self, x, y, size, orientation, text):
        """Return XML text for a QET element
        @param x: start coord
        @param y: start coord
        @param size: font size
        @param orientation: n,s,e,w
        @param text: text
        @return: list with XML content"""

        rotation = {'e':0, 'n':270, 'w':180, 's':90}
        return '    <input text="%s" tagg="label" rotation="%i" size="%i" x="%i" y="%i"' \
                       % (text, rotation[orientation], size, x, y) + '/>'


    def _create_collection_index_file(self, sCollectionPath):
        """Collection index file. Create directory if not exists
        @param sCollectionPath
        @return: none"""

        # creates if not exist
        if (sCollectionPath[-1] != os.sep): sCollectionPath += os.sep
        if not os.path.exists(sCollectionPath): os.makedirs(sCollectionPath)

        # create QET directory file
        f = open(sCollectionPath + 'qet_directory', 'w')
        xml = ['<qet-directory>',
               '    <names>',
               '        <name lang="en">TEMP: Connectors</name>',
               '    </names>',
               '</qet-directory>']
        f.writelines(["%s\n" % line for line in xml])
        f.close()


def main():
    """ Starts the app"""
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
