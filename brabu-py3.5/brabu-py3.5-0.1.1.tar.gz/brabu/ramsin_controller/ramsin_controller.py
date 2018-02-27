import datetime, sys, os
if sys.version_info[0] == 3:
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import QMessageBox
else:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import QMessageBox

brabu_data_dir = str(os.environ['BRABU_DATA_DIR'])

# TODO - ramsin_rule_validator
class LineEditDelegate():

    def evaluate(self, item, keyText):
        pass


class LineEditTextDelegate(LineEditDelegate):

    def evaluate(self, ramsinController, item, keyText):
        try:
            item.setText(ramsinController.dic_one[keyText])
            ramsinController.highlightItemOk(item)
        except:
            # TODO log to import error
            # self.screen.statusMessage("Parameter: " + keyText + " of RAMSIN not found in possible values ")
            ramsinController.highlightItemError(item)
            return -1
        return 0


class LineEditNumberDelegate(LineEditDelegate):

    def evaluate(self, ramsinController, item, keyText):
        try:
            # TODO check wheter the value is an integer or a float value
            # just testing whether the text can be converted to number
            # int(self.dic_one[keyText])
            float(ramsinController.dic_one[keyText])
            item.setText(ramsinController.dic_one[keyText])
            ramsinController.highlightItemOk(item)
        except:
            # TODO log to import error
            # self.screen.statusMessage("Parameter: " + keyText + " of RAMSIN not found in possible values ")
            ramsinController.highlightItemError(item)
            return -1
        return 0


class RamsinController():

    def __init__(self, screen):
        self.screen = screen

        self.chNfit = ['STOP', 'LAST_SOURCES']
        self.nsoilc = ['n', 'i', 'h', 'a']
        self.nsoilf = ['s', 'h', 'l']
        self.timeUnitList = ['s', 'm', 'h']
        self.closure_type = [ 'EN', 'GR', 'LO', 'MC', 'SC', 'AS', 'PB' ]

        self.dic_one = {}
        self.line = ''
        self.ramsinFileName = 'RAMSIN.out'
        self.dicvar = {}
        self.importErrorsList = []
        self.importLogFileName = 'import_error'

    def readVariables(self):
        #TODO read from csv file variables.csv (to show description and unit)
        # reading and setting list of variables to output of pos
        with open("{}/ramsin_controller/variables.dat".format(brabu_data_dir), 'r') as f:
            self.line = f.readlines()
        i = 0
        while i < len(self.line):
            linesplit = self.line[i].split("$")
            self.screen.listWidget.addItem(linesplit[1])
            d = {linesplit[0]: linesplit[1]}
            self.dicvar.update(d)
            i += 1


    def setTextCombobox(self, item, keyText):
        itemOk = item.findText(self.dic_one[keyText][0])
        if itemOk > -1:
            item.setCurrentIndex(itemOk)
            self.highlightItemOk(item)
        else:
            self.logParameterImportError(keyText)
            self.highlightItemError(item)
            return 1
        return 0


    def setComboIndexFromText(self, item, list, keyText):
        try:
            index = list.index(self.dic_one[keyText][0])
            item.setCurrentIndex(index)
            self.highlightItemOk(item)
        except:
            self.logParameterImportError(keyText)
            self.highlightItemError(item)
            return 1
        return 0


    def setComboIndexFromNumber(self, item, keyText):
        try:
            indexC = int(self.dic_one[keyText][0])
            item.setCurrentIndex(indexC)
            if(indexC - 1 > item.count()):
                self.logParameterImportError(keyText)
                self.highlightItemError(item)
                return 1
            self.highlightItemOk(item)
        except:
            self.logParameterImportError(keyText)
            self.highlightItemError(item)
            return 1
        return 0


    def setLineEditNumber(self, item, keyText):
        try:
            # TODO check whether the value is an integer or a float value
            # just testing whether the text can be converted to number
            float(self.dic_one[keyText][0])
            item.setText(self.dic_one[keyText][0])
            self.highlightItemOk(item)
        except:
            self.logParameterImportError(keyText)
            self.highlightItemError(item)
            return 1
        return 0

    def setSpinNumber(self, item, keyText):
        try:
            # TODO check wheter the value is an integer or a float value
            # just testing whether the text can be converted to number
            float(self.dic_one[keyText][0])
            item.setValue(float(self.dic_one[keyText][0]))
            self.highlightItemOk(item)
        except Exception as e:
            self.logParameterImportError(keyText)
            self.highlightItemError(item)
            return 1
        return 0


    def setLineEditText(self, item, keyText):
        try:
            item.setText(self.dic_one[keyText][0])
            self.highlightItemOk(item)
        except:
            self.logParameterImportError(keyText)
            self.highlightItemError(item)
            return 1
        return 0


    def setCheckBox(self, item, keyText):
        try:
            valueStr = self.dic_one[keyText][0]
            if valueStr == 'NO':
                item.setChecked(False)
            elif valueStr == 'YES':
                item.setChecked(True)
            else:
                item.setChecked(bool(int(self.dic_one[keyText][0])))

            self.highlightItemOk(item)
        except:
            self.logParameterImportError(keyText)
            self.highlightItemError(item)
            return 1
        return 0


    def setLineEditTextList(self, item, keyText):
        try:
            lista = self.dic_one[keyText]
            firstItem = self.dic_one[keyText][0]
            listaStr = firstItem
            lista.remove(firstItem)
            for each in lista:
                listaStr += ', ' + each
            item.setText(listaStr)
            self.highlightItemOk(item)
        except:
            self.logParameterImportError(keyText)
            self.highlightItemError(item)
            return 1
        return 0


    def setTableItemText(self, item, keyText, icolumn):
        try:
            for i in range(0, len(self.dic_one[keyText])):
                item.item(i, icolumn).setText(self.dic_one[keyText][i])
            self.highlightItemOk(item)
        except:
            self.logParameterImportError(keyText)
            self.highlightItemError(item)
            return 1
        return 0


    def highlightItemError(self, item):
        item.setStyleSheet("background-color: red");


    def highlightItemOk(self, item):
        backColor = item.backgroundRole()
        item.setStyleSheet("background-color: {}".format(backColor));


    def logParameterImportError(self, keyText):
        self.logImportError("Parameter value {} missing in RAMSIN or have invalid value".format(keyText))


    def logImportError(self, text):
        self.importErrorsList.append(text + "\n")

    def readConfigFromPatternLightCase(self):
        self.readConfigFromRamsin("{}/ramsin_controller/patterns/RAMSIN_meteo-only".format(brabu_data_dir))
        self.saveRamsinAs()


    def readConfigFromPatternChemicalLight(self):
        self.readConfigFromRamsin("{}/ramsin_controller/patterns/RAMSIN_meteo-chem".format(brabu_data_dir))
        self.saveRamsinAs()

    def readConfigFromPatternSouthAmerica(self):
        self.readConfigFromRamsin("{}/ramsin_controller/patterns/RAMSIN_SAMERICA".format(brabu_data_dir))
        self.saveRamsinAs()

    def readConfigFromPattern1kmRio(self):
        self.readConfigFromRamsin("{}/ramsin_controller/patterns/RAMSIN_1km_RIO".format(brabu_data_dir))
        self.saveRamsinAs()

    def readConfigFromPattern1kmAmazon(self):
        self.readConfigFromRamsin("{}/ramsin_controller/patterns/RAMSIN_1km_AMAZON".format(brabu_data_dir))
        self.saveRamsinAs()

    def selectRamsinReadConfig(self):
        self.readConfigFromRamsin()


    def readConfigFromRamsin(self, fname=None):
        import os.path
        import re
        from gui.bramsrc import listModel

        if fname is None:
            self.wMessage = 'Please select RAMSIN file to read from'
            self.screen.selectOpenFile()
            fname = self.get_filechoose()
            ret = 1
            if os.path.isfile(fname):
                self.screen.statusMessage("RAMSIN file loaded: "+fname)
            else:
                return


        # testing .....
        #fname = 'RAMSIN_meteo-chem-tests'

        try:
            with open(fname, 'r') as f:
                ramsinLines = f.readlines()
            with open(fname, 'r') as f:
                lineOut = f.read()
        except:
            self.screen.statusMessage('Error unexpected loading RAMSIN file: ' + fname)
            sys.exit()

        readRamsinMsg = 'Reading RAMSIN, please wait ...'
        self.screen.statusMessage(readRamsinMsg)
        # TODO event not showing message - se plotButton
        # self.screen.splashMessage(readRamsinMsg)

        self.screen.RamsinlineEdit.setPlainText(lineOut)
        self.dic_one = {}
        numErrors = 0
        for linee in ramsinLines:
            stringsLine = re.split("!", linee)
            stringsLine = stringsLine[0] # remove coments
            stringsLine = re.split("\n|=|,", stringsLine)
            for idx in range(0,len(stringsLine)):
                stringsLine[idx] = stringsLine[idx].strip()

            stringsLine = [x for x in stringsLine if x is not None]

            if len(stringsLine) >= 2:
                key = stringsLine[0]
                value = []
                imax = len(stringsLine)
                # more than one value, comma separated
                for index in range(1,imax):
                    eachValue = stringsLine[index].replace("'", '')
                    if len(eachValue) > 0:
                        value.append(eachValue)
                self.dic_one[key] = value
            elif len(stringsLine) == 1:
                #if line continues, like variables (VP)...
                if stringsLine[0].startswith("'"):
                    strValue = stringsLine[0].replace("'", '')
                    self.dic_one[key].append(strValue)


        # TODO - "iaFilelineEdit - varfile initialization file prefix"

        #
        # # Combobox Text
        numErrors += self.setTextCombobox(self.screen.runTypecomboBox, 'RUNTYPE')
        numErrors += self.setTextCombobox(self.screen.splitcomboBox, 'SPLIT_METHOD')
        #
        # # A list from combobox index
        numErrors += self.setComboIndexFromText(self.screen.ctcomboBox, self.closure_type, 'CLOSURE_TYPE')
        numErrors += self.setComboIndexFromText(self.screen.uSimcomboBox, self.timeUnitList, 'TIMEUNIT')
        numErrors += self.setComboIndexFromText(self.screen.soilmcomboBox, self.nsoilc, 'SOIL_MOIST')
        numErrors += self.setComboIndexFromText(self.screen.wsmfcomboBox, self.nsoilf, 'SOIL_MOIST_FAIL')
        numErrors += self.setComboIndexFromText(self.screen.nfsrccomboBox, self.chNfit, 'DEF_PROC_SRC')

        # # Combobox Number
        dicComboNumber = {
            'IHTRAN': self.screen.projcomboBox,
            'IPOS': self.screen.PoscomboBox,
            'IOUTPUT': self.screen.outcomboBox,
            'CHEMISTRY': self.screen.chemcomboBox,
            'ITOPSFLG': self.screen.TopoSchcomboBox,
            'IZ0FLG': self.screen.RougSchcomboBox,
            'ITOPTFLG': self.screen.fild1comboBox,
            'ISOILFLG': self.screen.fild2comboBox,
            'ISSTFLG': self.screen.fild3comboBox,
            'NDVIFLG': self.screen.fild4comboBox,
            'IVEGTFLG': self.screen.fild5comboBox,
            'NOFILFLG': self.screen.fild6comboBox,
            'ISWRTYP': self.screen.radSccomboBox,
            'ADVMNT': self.screen.AdvcomboBox,
            'NNQPARM': self.screen.cparcomboBox,
            'NNSHCU': self.screen.scpcomboBox,
            'AEROSOL': self.screen.aercomboBox,
            'ICLOBBER': self.screen.ianexcomboBox,
            'IHISTDEL': self.screen.hisdelcomboBox,
            'ISFCL': self.screen.isflccomboBox,
            'NVGCON': self.screen.vtcomboBox,
            'NSLCON': self.screen.csoiltcomboBox,
            'IDIFFK': self.screen.dkfcomboBox,
            'IHORGRAD': self.screen.HgcomboBox,
            'MCPHYS_TYPE': self.screen.tmfcomboBox,
            'IPSFLG': self.screen.ipsflgcomboBox,
            'ITSFLG': self.screen.itsflgcomboBox,
            'IRTSFLG': self.screen.irtsflgcomboBox,
            'IUSFLG': self.screen.iusflgcomboBox
        }

        for key in dicComboNumber:
            numErrors += self.setComboIndexFromNumber(dicComboNumber[key], key)

        # # Calendar
        try:
            starDate = QDate(int(self.dic_one['IYEAR1'][0]), int(self.dic_one['IMONTH1'][0]), int(self.dic_one['IDATE1'][0]))
            self.screen.StartSimul.setSelectedDate(starDate)
            self.highlightItemOk(self.screen.StartSimul)
        except:
            # TODO log to import error
            # self.screen.statusMessage("Parameter: " + keyText + " of RAMSIN not found in possible values ")
            self.highlightItemError(self.screen.StartSimul)
            numErrors += 1

        # # DateTime
        try:
            self.screen.dateTimeEdit.setDateTime(QDateTime.fromString(self.dic_one['ITIME1'][0], 'hhmm'))
            self.highlightItemOk(self.screen.dateTimeEdit)
        except:
            # TODO log to import error
            # self.screen.statusMessage("Parameter: " + keyText + " of RAMSIN not found in possible values ")
            self.highlightItemError(self.screen.dateTimeEdit)
            numErrors += 1


        dicTextComponents = {
            'EXPNME': self.screen.enlineEdit,
            'HFILIN': self.screen.histFilelineEdit,
            'PASTFN': self.screen.hisAnaltFilelineEdit,
            'HFILOUT': self.screen.histOutFilelineEdit,
            'AFILOUT': self.screen.AnalFilelineEdit,
            'TOPFILES': self.screen.topoFilelineEdit,
            'SFCFILES': self.screen.sfcFilelineEdit,
            'SSTFPFX': self.screen.sstFilelineEdit,
            'NDVIFPFX': self.screen.ndviFilelineEdit,
            'ITOPTFN': self.screen.topoOutFilelineEdit,
            'ISSTFN': self.screen.sstOutFilelineEdit,
            'IVEGTFN': self.screen.vegFilelineEdit,
            'ISOILFN': self.screen.soilFilelineEdit,
            'NDVIFN': self.screen.ndviOutFilelineEdit,
            'USDATA_IN': self.screen.smFilelineEdit,
            'USMODEL_IN': self.screen.smpFilelineEdit,
            'IAPR': self.screen.dprepFilelineEdit,
            'VARPFX': self.screen.isanFilelineEdit,
            'VARFPFX' : self.screen.iaFilelineEdit,
            'MEAN_TYPE': self.screen.meantlineEdit,
            'GPREFIX': self.screen.posFilelineEdit,
            'ANL2GRA': self.screen.anl2gradslineEdit
        }
        for key in dicTextComponents:
            numErrors += self.setLineEditText(dicTextComponents[key], key)

        #
        # # lineEdit Number
        # TODO ...
        # self.line = self.line.replace('##nacoust##': '3',
        # numErrors += self.setLineEdit(self.screen.XXXXXXXXXX: 'XXXXXXXXXXXXXxx',
        # self.line = self.line.replace('##ngrids##': str(1,,
        # numErrors += self.setLineEdit(self.screen.XXXXXXXXXX: 'XXXXXXXXXXXXXxx',
        # self.line = self.line.replace('##gedsmh##': self.g3dshlineEdit.text(,,
        # self.line = self.line.replace('##gedsmv##': self.g3dsvlineEdit.text(,,

        dicNumberComponents = {
            'TIMMAX': self.screen.tslineEdit,
            'DELTAX': self.screen.dxlineEdit,
            'DELTAY': self.screen.dylineEdit,
            'DELTAZ': self.screen.dzlineEdit,
            'DZRAT': self.screen.dzratlineEdit,
            'DZMAX': self.screen.dzmaxlineEdit,
            'DTLONG': self.screen.dtlonlineEdit,
            'NNXP': self.screen.npxlineEdit,
            'NNYP': self.screen.npylineEdit,
            'NNZP': self.screen.npzlineEdit_3,
            'NZG': self.screen.sllineEdit,
            'NZS': self.screen.snowllineEdit,
            'CHEM_TIMESTEP': self.screen.tstepClineEdit,
            'DIUR_CYCLE': self.screen.DiuCyclineEdit,
            'NA_EXTRA2D': self.screen.n2dlineEdit,
            'NA_EXTRA3D': self.screen.n3dlineEdit,
            'PRFRQ': self.screen.plumfrqlineEdit,
            'AER_TIMESTEP': self.screen.aerFrqlineEdit,
            'FRQHIS': self.screen.HislineEdit,
            'FRQANL': self.screen.OutlineEdit,
            'TOPTWVL': self.screen.topowvllineEdit,
            'TOPTENH': self.screen.wtsalineEdit,
            'Z0MAX': self.screen.MaxZ0lineEdit,
            'Z0FACT': self.screen.z0faclineEdit,
            'GHOSTZONELENGTH': self.screen.gzlineEdit,
            'RADFRQ': self.screen.RFreqlineEdit,
            'G3D_SPREAD': self.screen.g3dsplineEdit,
            'CONFRQ': self.screen.couflineEdit,
            'SHCUFRQ': self.screen.suflineEdit,
            'WCLDBS': self.screen.vmotlineEdit,
            'PCTLCON': self.screen.clandlineEdit,
            'ZROUGH': self.screen.crouglineEdit,
            'ALBEDO': self.screen.calblineEdit,
            'SEATMP': self.screen.csstlineEdit,
            'DTHCON': self.screen.csltglineEdit,
            'DRTCON': self.screen.cslmglineEdit,
            'NPATCH': self.screen.ppgclineEdit,
            'NVEGPAT': self.screen.ppgcvlineEdit,
            'CSX': self.screen.hkdlineEdit,
            'CSZ': self.screen.vkdlineEdit,
            'XKHKM': self.screen.hrdlineEdit,
            'ZKHKM': self.screen.vrdlineEdit,
            'AKMIN': self.screen.akminlineEdit,
            'LEVEL': self.screen.mfllineEdit,
            'IRIME': self.screen.mfirimelineEdit,
            'IPLAWS': self.screen.mfiplawslineEdit,
            'ICLOUD': self.screen.icloudlineEdit,
            'IDRIZ': self.screen.idrizlineEdit,
            'IRAIN': self.screen.irainlineEdit,
            'IPRIS': self.screen.iprislineEdit,
            'ISNOW': self.screen.isnowlineEdit,
            'IAGGR': self.screen.iaggrlineEdit,
            'IGRAUP': self.screen.igrauplineEdit,
            'IHAIL': self.screen.ihaillineEdit,
            'CPARM': self.screen.mfcplineEdit,
            'RPARM': self.screen.mfrplineEdit,
            'PPARM': self.screen.mfpplineEdit,
            'SPARM': self.screen.mfsplineEdit,
            'APARM': self.screen.mfaplineEdit,
            'GPARM': self.screen.mfgplineEdit,
            'HPARM': self.screen.mfhplineEdit,
            'DPARM': self.screen.mfdplineEdit,
            'GNU': self.screen.mfgnulineEdit,
            'HS': self.screen.hslineEdit,
            'LATI': self.screen.posUpLeftLatlineEdit,
            'LATF': self.screen.posDnRightLatLeftlineEdit,
            'LONI': self.screen.posUpLeftLonlineEdit,
            'LONF': self.screen.posDnRightLonLeftlineEdit,
            'ZLEVMAX': self.screen.maxzlevlineEdit,
            'IPRESSLEV': self.screen.ipresslevlineEdit,
            'INPLEVS': self.screen.inlevlineEdit,
            'SITE_LAT': self.screen.siteLatlineEdit,
            'SITE_LON': self.screen.siteLonlineEdit
        }
        for key in dicNumberComponents:
            numErrors += self.setLineEditNumber(dicNumberComponents[key], key)

        dicNumberListComponents = {
            'IPLEVS': self.screen.iplevlineEdit
        }
        for key in dicNumberListComponents:
            numErrors += self.setLineEditTextList(dicNumberListComponents[key], key)

        dicSpinNumberComponents = {
            'POLELAT': self.screen.PoleLatlineEdit,
            'POLELON': self.screen.PoleLonlineEdit,
            'CENTLAT': self.screen.centerLatlineEdit,
            'CENTLON': self.screen.centerLonlineEdit
        }
        for key in dicSpinNumberComponents:
            numErrors += self.setSpinNumber(dicSpinNumberComponents[key], key)

        # Variables ~~~~~~~~
        for item in self.screen.listWidget.selectedItems():
            item.setSelected(False)

        if( 'VP' not in self.dic_one):
            self.logParameterImportError("Item 'VP' not found in RAMSIN")
            numErrors += 1
            self.highlightItemError(self.screen.varslcdNumber)
            self.highlightItemError(self.screen.selvaListView)
        else:
            self.highlightItemOk(self.screen.varslcdNumber)
            self.highlightItemOk(self.screen.selvaListView)
            for var in self.dic_one['VP']:
                item = self.screen.listWidget.findItems(var, Qt.MatchExactly)
                if(len(item) == 0):
                    self.logImportError("Variable '{}' from 'VP' not found in possible variables list".format(var))
                    self.highlightItemError(self.screen.varslcdNumber)
                    self.highlightItemError(self.screen.selvaListView)
                    numErrors += 1
                    break
                else:
                    item[0].setSelected(item is not None)

        selvaListCount = 0
        locallist = []
        # print self.listWidget.count() #total
        self.screen.selvaListView.reset()
        for item in self.screen.listWidget.selectedItems():
            locallist.append(item.text())
            selvaListCount += 1
        model = listModel(locallist)
        self.screen.selvaListView.setModel(model)
        self.screen.varslcdNumber.intValue = selvaListCount
        self.screen.varslcdNumber.display(selvaListCount)

        dicCheckBoxComponents = {
            'CCATT': self.screen.cattcheckBox,
            'CHEMISTRY_AQ': self.screen.achemcheckBox,
            'CHEM_ASSIM': self.screen.fddacheckBox,
            'RECYCLE_TRACERS': self.screen.rectraccheckBox,
            'PLUMERISE': self.screen.plumecheckBox,
            'VOLCANOES': self.screen.volccheckBox,
            'TEB_SPM': self.screen.tebcheckBox,
            'IPASTIN': self.screen.ifacheckBox,
            'IUPDNDVI': self.screen.unorcheckBox,
            'IUPDSST': self.screen.usorcheckBox,
            'PROJ': self.screen.projcheckBox,
            'ASCII_DATA': self.screen.asciicheckBox
        }
        for key in dicCheckBoxComponents:
            numErrors += self.setCheckBox(dicCheckBoxComponents[key], key)

        #
        # Tables
        numErrors += self.setTableItemText(self.screen.slztableWidget, 'SLZ', 0 )
        numErrors += self.setTableItemText(self.screen.slztableWidget, 'SLMSTR', 1)
        numErrors += self.setTableItemText(self.screen.stgofftableWidget, 'STGOFF', 0)
        numErrors += self.setTableItemText(self.screen.sndtableWidget, 'PS', 0)
        numErrors += self.setTableItemText(self.screen.sndtableWidget, 'TS', 1)
        numErrors += self.setTableItemText(self.screen.sndtableWidget, 'RTS', 2)
        numErrors += self.setTableItemText(self.screen.sndtableWidget, 'US', 3)
        numErrors += self.setTableItemText(self.screen.sndtableWidget, 'VS', 4)

        self.screen.calcLatLonOption.setChecked(True)
        # TODO - plot is not showing splash scrren
        self.screen.plotMap()

        if numErrors > 0:
            dateStr = datetime.datetime.now().strftime("%Y%m%d-%I:%M%p")
            logFileName = "{}-{}.log".format(self.importLogFileName, dateStr)
            with open(logFileName, 'w') as importFileLog:
                importFileLog.writelines(self.importErrorsList)

            self.screen.warningMessage(
                "There are incompatible type values or values are not in list of possible values.\nPlease check them in the log file {}.\nItens not changed are highlighted in red".format(logFileName))
        else:
            self.ramsinFileName = fname
            self.screen.fileLabel.setText(fname)
            msg = 'RAMSIN imported successfully!'
            self.screen.warningMessage(msg)
            self.screen.statusMessage(msg)

        self.importErrorsList = []


    def get_filechoose(self):
        if sys.version_info[0] == 3:
            fname = self.screen.filechoose[0]
        else:
            fname = self.screen.filechoose
        return fname


    def makeRamsin(self):
        self.readRamsinTemplate()
        # ComboBox
        self.line = self.line.replace('##runtype##', self.screen.runTypecomboBox.currentText())
        self.line = self.line.replace('##timeunit##', self.screen.uSimcomboBox.currentText()[0:1])
        self.line = self.line.replace('##simultime##', self.screen.tslineEdit.text())
        self.line = self.line.replace('##split##', self.screen.splitcomboBox.currentText())
        self.line = self.line.replace('##closu##', self.screen.ctcomboBox.currentText()[0:2])

        # A list from combobox index
        self.line = self.line.replace('##soilm##', self.nsoilc[self.screen.soilmcomboBox.currentIndex()])
        self.line = self.line.replace('##wsmf##', self.nsoilf[self.screen.wsmfcomboBox.currentIndex()])
        self.line = self.line.replace('##defp##', self.chNfit[self.screen.nfsrccomboBox.currentIndex()])

        # Combobox Number
        self.line = self.line.replace('##ihtran##', str(self.screen.projcomboBox.currentIndex()))
        self.line = self.line.replace('##ipos##', str(self.screen.PoscomboBox.currentIndex()))
        self.line = self.line.replace('##iout##', str(self.screen.outcomboBox.currentIndex()))
        self.line = self.line.replace('##chem##', str(self.screen.chemcomboBox.currentIndex() - 1))
        self.line = self.line.replace('##orog##', str(self.screen.TopoSchcomboBox.currentIndex()))
        self.line = self.line.replace('##iz0f##', str(self.screen.RougSchcomboBox.currentIndex()))
        self.line = self.line.replace('##itopof##', str(self.screen.fild1comboBox.currentIndex()))
        self.line = self.line.replace('##isoilf##', str(self.screen.fild2comboBox.currentIndex()))
        self.line = self.line.replace('##isstf##', str(self.screen.fild3comboBox.currentIndex()))
        self.line = self.line.replace('##indvif##', str(self.screen.fild4comboBox.currentIndex()))
        self.line = self.line.replace('##ivegf##', str(self.screen.fild5comboBox.currentIndex()))
        self.line = self.line.replace('##inof##', str(self.screen.fild6comboBox.currentIndex()))
        self.line = self.line.replace('##swrad##', str(self.screen.radSccomboBox.currentIndex()))
        self.line = self.line.replace('##lwrad##', str(self.screen.radSccomboBox.currentIndex()))
        self.line = self.line.replace('##advc##', str(self.screen.AdvcomboBox.currentIndex()))
        self.line = self.line.replace('##qparm##', str(self.screen.cparcomboBox.currentIndex()))
        self.line = self.line.replace('##shcu##', str(self.screen.scpcomboBox.currentIndex()))
        self.line = self.line.replace('##aer##', str(self.screen.aercomboBox.currentIndex()))
        self.line = self.line.replace('##iclob##', str(self.screen.ianexcomboBox.currentIndex()))
        self.line = self.line.replace('##hisdel##', str(self.screen.hisdelcomboBox.currentIndex()))
        self.line = self.line.replace('##isfcl##', str(self.screen.isflccomboBox.currentIndex()))
        self.line = self.line.replace('##nvgcon##', str(self.screen.vtcomboBox.currentIndex() + 1))
        self.line = self.line.replace('##nslc##', str(self.screen.csoiltcomboBox.currentIndex()))
        self.line = self.line.replace('##idifk##', str(self.screen.dkfcomboBox.currentIndex() + 1))
        self.line = self.line.replace('##horgrad##', str(self.screen.HgcomboBox.currentIndex() + 1))
        self.line = self.line.replace('##mptype##', str(self.screen.tmfcomboBox.currentIndex()))
        self.line = self.line.replace('##ipsf##', str(self.screen.ipsflgcomboBox.currentIndex()))
        self.line = self.line.replace('##itsf##', str(self.screen.itsflgcomboBox.currentIndex()))
        self.line = self.line.replace('##irts##', str(self.screen.irtsflgcomboBox.currentIndex()))
        self.line = self.line.replace('##iusf##', str(self.screen.iusflgcomboBox.currentIndex()))

        # Calendar
        self.line = self.line.replace('##month##', str(self.screen.StartSimul.monthShown()).zfill(2))
        self.line = self.line.replace('##day##', str(self.screen.StartSimul.selectedDate().day()).zfill(2))
        self.line = self.line.replace('##year##', str(self.screen.StartSimul.yearShown()).zfill(4))

        # DateTime
        self.line = self.line.replace('##time##', str(self.screen.dateTimeEdit.time().hour()).zfill(2))
        self.line = self.line.replace('##thst##', str(self.screen.HistdateTimeEdit.time().hour()).zfill(2))

        # lineEdit
        self.line = self.line.replace('##deltax##', self.screen.dxlineEdit.text())
        self.line = self.line.replace('##deltay##', self.screen.dylineEdit.text())
        self.line = self.line.replace('##deltaz##', self.screen.dzlineEdit.text())
        self.line = self.line.replace('##zratio##', self.screen.dzratlineEdit.text())
        self.line = self.line.replace('##dzmax##', self.screen.dzmaxlineEdit.text())
        self.line = self.line.replace('##dtlon##', self.screen.dtlonlineEdit.text())
        self.line = self.line.replace('##nacoust##', '3')
        self.line = self.line.replace('##polelat##', str(self.screen.PoleLatlineEdit.value()))
        self.line = self.line.replace('##polelon##', str(self.screen.PoleLonlineEdit.value()))
        self.line = self.line.replace('##centlat##', str(self.screen.centerLatlineEdit.value()))
        self.line = self.line.replace('##centlon##', str(self.screen.centerLonlineEdit.value()))
        self.line = self.line.replace('##ngrids##', str(1))
        self.line = self.line.replace('##nnxp##', self.screen.npxlineEdit.text())
        self.line = self.line.replace('##nnyp##', self.screen.npylineEdit.text())
        self.line = self.line.replace('##nnzp##', self.screen.npzlineEdit_3.text())
        self.line = self.line.replace('##nsoil##', self.screen.sllineEdit.text())
        self.line = self.line.replace('##nsnow##', self.screen.snowllineEdit.text())
        self.line = self.line.replace('##experiment##', self.screen.enlineEdit.text())
        self.line = self.line.replace('##chemts##', self.screen.tstepClineEdit.text())
        self.line = self.line.replace('##sfmap##', self.screen.sfnFilelineEdit.text())
        self.line = self.line.replace('##diurcy##', self.screen.DiuCyclineEdit.text())
        self.line = self.line.replace('##ne2d##', self.screen.n2dlineEdit.text())
        self.line = self.line.replace('##ne3d##', self.screen.n3dlineEdit.text())
        self.line = self.line.replace('##plfrq##', self.screen.plumfrqlineEdit.text())
        self.line = self.line.replace('##aerts##', self.screen.aerFrqlineEdit.text())
        self.line = self.line.replace('##hisfil##', self.screen.histFilelineEdit.text())
        self.line = self.line.replace('##pastfn##', self.screen.hisAnaltFilelineEdit.text())
        self.line = self.line.replace('##hfil##', self.screen.histOutFilelineEdit.text())
        self.line = self.line.replace('##anfil##', self.screen.AnalFilelineEdit.text())
        self.line = self.line.replace('##frqhis##', self.screen.HislineEdit.text())
        self.line = self.line.replace('##frqana##', self.screen.OutlineEdit.text())
        self.line = self.line.replace('##topf##', self.screen.topoFilelineEdit.text())
        self.line = self.line.replace('##sfcf##', self.screen.sfcFilelineEdit.text())
        self.line = self.line.replace('##sstf##', self.screen.sstFilelineEdit.text())
        self.line = self.line.replace('##ndvf##', self.screen.ndviFilelineEdit.text())
        self.line = self.line.replace('##itop##', self.screen.topoOutFilelineEdit.text())
        self.line = self.line.replace('##isst##', self.screen.sstOutFilelineEdit.text())
        self.line = self.line.replace('##iveg##', self.screen.vegFilelineEdit.text())
        self.line = self.line.replace('##isoil##', self.screen.soilFilelineEdit.text())
        self.line = self.line.replace('##indv##', self.screen.ndviOutFilelineEdit.text())
        self.line = self.line.replace('##topwvl##', self.screen.topowvllineEdit.text())
        self.line = self.line.replace('##wtsa##', self.screen.wtsalineEdit.text())
        self.line = self.line.replace('##z0max##', self.screen.MaxZ0lineEdit.text())
        self.line = self.line.replace('##z0fact##', self.screen.z0faclineEdit.text())
        self.line = self.line.replace('##gzone##', self.screen.gzlineEdit.text())
        self.line = self.line.replace('##radfreq##', self.screen.RFreqlineEdit.text())
        self.line = self.line.replace('##g3ds##', self.screen.g3dsplineEdit.text())
        self.line = self.line.replace('##gedsmh##', self.screen.g3dshlineEdit.text())
        self.line = self.line.replace('##gedsmv##', self.screen.g3dsvlineEdit.text())
        self.line = self.line.replace('##cfrq##', self.screen.couflineEdit.text())
        self.line = self.line.replace('##sfrq##', self.screen.suflineEdit.text())
        self.line = self.line.replace('##vmot##', self.screen.vmotlineEdit.text())
        self.line = self.line.replace('##pctl##', self.screen.clandlineEdit.text())
        self.line = self.line.replace('##zroug##', self.screen.crouglineEdit.text())
        self.line = self.line.replace('##albed##', self.screen.calblineEdit.text())
        self.line = self.line.replace('##seatp##', self.screen.csstlineEdit.text())
        self.line = self.line.replace('##dthco##', self.screen.csltglineEdit.text())
        self.line = self.line.replace('##drtco##', self.screen.cslmglineEdit.text())
        self.line = self.line.replace('##npatc##', self.screen.ppgclineEdit.text())
        self.line = self.line.replace('##nvegp##', self.screen.ppgcvlineEdit.text())
        self.line = self.line.replace('##sompref##', self.screen.smFilelineEdit.text())
        self.line = self.line.replace('##prepref##', self.screen.smpFilelineEdit.text())
        self.line = self.line.replace('##csx##', self.screen.hkdlineEdit.text())
        self.line = self.line.replace('##csz##', self.screen.vkdlineEdit.text())
        self.line = self.line.replace('##xkh##', self.screen.hrdlineEdit.text())
        self.line = self.line.replace('##zkh##', self.screen.vrdlineEdit.text())
        self.line = self.line.replace('##akm##', self.screen.akminlineEdit.text())
        self.line = self.line.replace('##mpleve##', self.screen.mfllineEdit.text())
        self.line = self.line.replace('##mpirim##', self.screen.mfirimelineEdit.text())
        self.line = self.line.replace('##mpplaw##', self.screen.mfiplawslineEdit.text())
        self.line = self.line.replace('##iclou##', self.screen.icloudlineEdit.text())
        self.line = self.line.replace('##idriz##', self.screen.idrizlineEdit.text())
        self.line = self.line.replace('##irain##', self.screen.irainlineEdit.text())
        self.line = self.line.replace('##ipris##', self.screen.iprislineEdit.text())
        self.line = self.line.replace('##isnow##', self.screen.isnowlineEdit.text())
        self.line = self.line.replace('##iaggr##', self.screen.iaggrlineEdit.text())
        self.line = self.line.replace('##igrau##', self.screen.igrauplineEdit.text())
        self.line = self.line.replace('##ihail##', self.screen.ihaillineEdit.text())
        self.line = self.line.replace('##cparm##', self.screen.mfcplineEdit.text())
        self.line = self.line.replace('##rparm##', self.screen.mfrplineEdit.text())
        self.line = self.line.replace('##pparm##', self.screen.mfpplineEdit.text())
        self.line = self.line.replace('##sparm##', self.screen.mfsplineEdit.text())
        self.line = self.line.replace('##aparm##', self.screen.mfaplineEdit.text())
        self.line = self.line.replace('##gparm##', self.screen.mfgplineEdit.text())
        self.line = self.line.replace('##hparm##', self.screen.mfhplineEdit.text())
        self.line = self.line.replace('##dparm##', self.screen.mfdplineEdit.text())
        self.line = self.line.replace('##gnu##', self.screen.mfgnulineEdit.text())
        self.line = self.line.replace('##snhs##', self.screen.hslineEdit.text())
        self.line = self.line.replace('##dprep##', self.screen.dprepFilelineEdit.text())
        self.line = self.line.replace('##isanf##', self.screen.isanFilelineEdit.text())
        self.line = self.line.replace('##varfpfx##', self.screen.iaFilelineEdit.text())
        self.line = self.line.replace('##mtype##', self.screen.meantlineEdit.text())
        self.line = self.line.replace('##plati##', self.screen.posUpLeftLatlineEdit.text())
        self.line = self.line.replace('##platf##', self.screen.posDnRightLatLeftlineEdit.text())
        self.line = self.line.replace('##ploni##', self.screen.posUpLeftLonlineEdit.text())
        self.line = self.line.replace('##plonf##', self.screen.posDnRightLonLeftlineEdit.text())
        self.line = self.line.replace('##zlemx##', self.screen.maxzlevlineEdit.text())
        self.line = self.line.replace('##iplev##', self.screen.ipresslevlineEdit.text())
        self.line = self.line.replace('##pinpl##', self.screen.inlevlineEdit.text())
        self.line = self.line.replace('##gpref##', self.screen.posFilelineEdit.text())
        self.line = self.line.replace('##pan2g##', self.screen.anl2gradslineEdit.text())
        self.line = self.line.replace('##pslat##', self.screen.siteLatlineEdit.text())
        self.line = self.line.replace('##pslon##', self.screen.siteLonlineEdit.text())
        self.line = self.line.replace('##ipllst##', self.screen.iplevlineEdit.text())

        # lcdNumber
        self.line = self.line.replace('##pnvar##', str(self.screen.varslcdNumber.intValue))

        # listwidget
        listvar = ''
        first = True
        for item in self.screen.listWidget.selectedItems():
            if first:
                listvar = listvar + '\'' + item.text() + '\''
                first = False
            else:
                listvar = listvar + ', \n         \'' + item.text() + '\''
        self.line = self.line.replace('##lstvr##', listvar)

        # CheckBox
        if self.screen.cattcheckBox.isChecked():
            self.line = self.line.replace('##ccatt##', '1')
        else:
            self.line = self.line.replace('##ccatt##', '0')
        if self.screen.achemcheckBox.isChecked():
            self.line = self.line.replace('##chemaq##', '1')
        else:
            self.line = self.line.replace('##chemaq##', '0')
        if self.screen.fddacheckBox.isChecked():
            self.line = self.line.replace('##chemas##', '1')
        else:
            self.line = self.line.replace('##chemas##', '0')
        if self.screen.rectraccheckBox.isChecked():
            self.line = self.line.replace('##recy##', '1')
        else:
            self.line = self.line.replace('##recy##', '0')
        if self.screen.plumecheckBox.isChecked():
            self.line = self.line.replace('##plum##', '1')
        else:
            self.line = self.line.replace('##plum##', '0')
        if self.screen.volccheckBox.isChecked():
            self.line = self.line.replace('##volc##', '1')
        else:
            self.line = self.line.replace('##volc##', '0')
        if self.screen.tebcheckBox.isChecked():
            self.line = self.line.replace('##teb_spm##', '1')
        else:
            self.line = self.line.replace('##teb_spm##', '0')
        if self.screen.ifacheckBox.isChecked():
            self.line = self.line.replace('##ipast##', '1')
        else:
            self.line = self.line.replace('##ipast##', '0')
        if self.screen.unorcheckBox.isChecked():
            self.line = self.line.replace('##iun##', '1')
        else:
            self.line = self.line.replace('##iun##', '0')
        if self.screen.usorcheckBox.isChecked():
            self.line = self.line.replace('##ius##', '1')
        else:
            self.line = self.line.replace('##ius##', '0')
        if self.screen.projcheckBox.isChecked():
            self.line = self.line.replace('##pproj##', 'YES')
        else:
            self.line = self.line.replace('##pproj##', 'NO')
        if self.screen.asciicheckBox.isChecked():
            self.line = self.line.replace('##acsdt##', 'YES')
        else:
            self.line = self.line.replace('##acsdt##', 'NO')

            # tables
        slz = self.screen.slztableWidget.item(0, 0).text()
        inm = self.screen.slztableWidget.item(0, 1).text()
        for i in range(1, self.screen.slztableWidget.rowCount()):
            slz = slz + ', ' + self.screen.slztableWidget.item(i, 0).text()
            inm = inm + ', ' + self.screen.slztableWidget.item(i, 1).text()
        self.line = self.line.replace('##sgridlev##', slz)
        self.line = self.line.replace('##sinitm##', inm)
        #
        tof = self.screen.stgofftableWidget.item(0, 0).text()
        for i in range(1, self.screen.stgofftableWidget.rowCount()):
            tof = tof + ', ' + self.screen.stgofftableWidget.item(i, 0).text()
        self.line = self.line.replace('##istoff##', tof)
        #
        snps = self.screen.sndtableWidget.item(0, 0).text()
        snts = self.screen.sndtableWidget.item(0, 1).text()
        snrs = self.screen.sndtableWidget.item(0, 2).text()
        snus = self.screen.sndtableWidget.item(0, 3).text()
        snvs = self.screen.sndtableWidget.item(0, 4).text()
        for i in range(1, self.screen.sndtableWidget.rowCount()):
            snps = snps + ', ' + self.screen.sndtableWidget.item(i, 0).text()
            snts = snts + ', ' + self.screen.sndtableWidget.item(i, 1).text()
            snrs = snrs + ', ' + self.screen.sndtableWidget.item(i, 2).text()
            snus = snus + ', ' + self.screen.sndtableWidget.item(i, 3).text()
            snvs = snvs + ', ' + self.screen.sndtableWidget.item(i, 4).text()
        self.line = self.line.replace('##snps##', snps)
        self.line = self.line.replace('##snts##', snts)
        self.line = self.line.replace('##snrs##', snrs)
        self.line = self.line.replace('##snus##', snus)
        self.line = self.line.replace('##snvs##', snvs)


    def readRamsinTemplate(self):
        try:
            with open('{}/ramsin_controller/RAMSIN_template'.format(brabu_data_dir), 'r') as f:  # Try to open the template file
                self.line = f.read()
        except:
            self.screen.statusMessage('RAMSIN_template not found. Please check it')
            sys.exit()


    def readRamsinOut(self):
        try:
            with open(self.ramsinFileName, 'r') as f:
                lineOut = f.read()
                self.screen.RamsinlineEdit.setPlainText(lineOut)
        except:
            self.screen.statusMessage('Output file not found. Please check it')
            sys.exit()


    def saveRamsin(self):
        if self.ramsinFileName == '':
            self.saveRamsinAs()
            return
        self.makeRamsin()
        with open(self.ramsinFileName, 'w') as fout:
            fout.write(self.line)
        self.readRamsinOut()
        QMessageBox.information(self.screen, "Notice", 'File ' + self.ramsinFileName + ' saved.\n' +
                                self.screen.messAppend)


    def saveRamsinAs(self):
        import os.path
        import shutil
        self.makeRamsin()
        self.screen.wMessage = 'Please Select output File'
        self.screen.selectSaveFile()

        fname = self.get_filechoose()
        ret = 1

        if os.path.isfile(fname):
            shutil.copy2(fname, fname + '_old')
            self.ramsinFileName = fname
            self.screen.fileLabel.setText(fname)
            self.screen.messAppend = 'The old file was saved with \'_old\' suffix.'
            self.saveRamsin()
        else:
            self.ramsinFileName = fname
            self.screen.fileLabel.setText(fname)
            self.screen.messAppend = ''
            self.saveRamsin()


    def saveRamsinManual(self):
        if self.ramsinFileName == '':
            self.saveRamsinManualAs()
            return
        with open(self.ramsinFileName, 'w') as fout:
            fout.write(self.screen.RamsinlineEdit.toPlainText())
        QMessageBox.information(self.screen, "Notice", 'File ' + self.ramsinFileName + ' saved.\n' +
                                self.screen.messAppend)


    def saveRamsinManualAs(self):
        import os.path
        import shutil
        self.screen.wMessage = 'Please Select output File'
        self.screen.selectSaveFile()
        fname = self.get_filechoose()

        ret = 1
        if os.path.isfile(fname):
            shutil.copy2(fname, fname + '_old')
            self.ramsinFileName = fname
            self.screen.fileLabel.setText(fname)
            self.screen.messAppend = 'The old file was saved with \'_old\' suffix.'
            self.saveRamsinManual()
        else:
            self.ramsinFileName = fname
            self.screen.fileLabel.setText(fname)
            self.screen.messAppend = ''
            self.saveRamsinManual()
