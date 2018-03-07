import os

import sys

if sys.version_info[0] == 3:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
else:
    from PyQt4 import QtGui  # Import the PyQt4 module we'll need
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

from mpl_toolkits.basemap import Basemap
from gui import brams
from gui.__ptd__ import *
from ramsin_controller.ramsin_controller import RamsinController, brabu_data_dir

class listModel(QAbstractListModel):
    def __init__(self, datain, parent=None, *args):
        """ datain: a list where each item is a row
        """
        QAbstractListModel.__init__(self, parent)
        self.listdata = datain

        # def rowCount(self):
        #     return len(self.listdata)
        #     # QAbstractItemModel.rowCount(self, QModelIndex_parent, *args, **kwargs)

        # def rowCount(self, parent=QModelIndex()):
        #     return len(self.listdata)

        # def data(self, qModelIndex, int_role=None):
        #     if qModelIndex.isValid() and int_role == Qt.DisplayRole:
        #         return QVariant(self.listdata[int_role.row()])
        #     else:
        #         return QVariant()

        # def data(self, index, role):
        #     if index.isValid() and role == Qt.DisplayRole:
        #         return QVariant(self.listdata[index.row()])
        #     else:
        #         return QVariant()
        #
        # def rowCount(self, qModelIndex_parent=None, *args, **kwargs):
        #     return len(self.listdata)
        #     #QAbstractItemModel.rowCount(self, qModelIndex_parent, *args, **kwargs)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        #QAbstractItemModel.rowCount(self, QModelIndex_parent, *args, **kwargs)
        return len(self.listdata)

    def data(self, QModelIndex, int_role=None):
        #return QAbstractItemModel.data(self, QModelIndex, int_role)
        if QModelIndex.isValid() and int_role == Qt.DisplayRole:
            return QVariant(self.listdata[QModelIndex.row()])
        else:
            return QVariant()


class QPixmapSelection(QPixmap):
    def __init__(self, *__args):
        QPixmap.__init__(self, *__args)


class Square(QGraphicsRectItem):
	def __init__(self, *args):
		QGraphicsRectItem.__init__(self, *args)
		self.setFlag(QGraphicsItem.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.ItemIsSelectable, True)

	# def mousePressEvent(self, e):
	# 	print("Square got mouse press event")
	# 	#print self.mouse.pos
	# 	print("Event came to us accepted: %s"%(e.isAccepted(),))
	# 	QtGui.QGraphicsRectItem.mousePressEvent(self, e)
    #
	# def mouseReleaseEvent(self, e):
	# 	print("Square got mouse release event")
	# 	print("Event came to us accepted: %s"%(e.isAccepted(),))
	# 	QtGui.QGraphicsRectItem.mouseReleaseEvent(self, e)


class QGraphicsSceneSquare(QGraphicsScene):
    def __init__ (self, ramsinBrams, pixmap, parent=None):
        super(QGraphicsSceneSquare, self).__init__ (parent)
        self.x_init = 0
        self.y_init = 0
        self.ramsinBrams = ramsinBrams
        self.pixmap = pixmap
        self.isPressed = False
        self.lat_up = self.ramsinBrams.latUpEdit.value()
        self.lon_left = self.ramsinBrams.lonLeftEdit.value()
        self.lat_down = self.ramsinBrams.latDownEdit.value()
        self.lon_right = self.ramsinBrams.lonRightEdit.value()
        self.dlat = -self.lat_down + self.lat_up
        self.dlon = -self.lon_left + self.lon_right
        self.latInitMap = self.lat_up
        self.lonInitMap = self.lon_left
        self.latEndMap = self.latInitMap
        self.lonEndMap = self.lonInitMap
        self.latActualMap = self.latInitMap
        self.lonActualMap = self.lonInitMap


    def mousePressEvent(self, event):
        position = QPointF(event.scenePos())
        self.x_init = position.x()
        self.y_init = position.y()
        self.latInitMap = self.lat_up - self.dlat*position.y()/self.height()
        self.lonInitMap = self.lon_left + self.dlon * position.x() / self.width()
        self.addPixmap(self.pixmap)
        self.isPressed = True


    def updateMap(self):

        self.pixmap = self.pixmap.scaled(self.ramsinBrams.graphicsView.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.addPixmap(self.pixmap)
        self.ramsinBrams.graphicsView.setScene(self)
        self.ramsinBrams.graphicsView.fitInView(self.sceneRect(), Qt.IgnoreAspectRatio)
        # self.ramsinBrams.graphicsView.show()


    def mouseMoveEvent(self, event):
        position = QPointF(event.scenePos())
        #TODO desenhar ao mover
        # if self.isPressed is True:
        #     mapSquare = Square()
        #     mapSquare.setRect(self.x_init, self.y_init, position.x() - self.x_init, position.y() - self.y_init)
        #     self.addItem(mapSquare)
        #     sleep(0.01)
        #     self.addPixmap(self.pixmap)
        #     # self.updateMap()

        # TODO - erro de precisao .. maior area menor precisao
        try:
            self.latActualMap = max(self.lat_up - self.dlat * position.y() / self.height(), self.lat_down)
            self.lonActualMap = min(self.lon_left + self.dlon * position.x() / self.width(), self.lon_right)
            if self.isPressed is False:
                self.ramsinBrams.mapLat_up.setText('{:.2f}'.format(self.latActualMap))
                self.ramsinBrams.mapLon_Left.setText('{:.2f}'.format(self.lonActualMap))
            else:
                self.ramsinBrams.mapLat_Down.setText('{:.2f}'.format(self.latActualMap))
                self.ramsinBrams.mapLon_right.setText('{:.2f}'.format(self.lonActualMap))
        except:
            #TODO - tratar erro
            print("Unecpected error...")
            pass


    def mouseReleaseEvent(self, event):
        self.latEndMap = self.latActualMap
        self.lonEndMap = self.lonActualMap
        position = QPointF(event.scenePos())
        mapSquare = Square()
        mapSquare.setRect(self.x_init,self.y_init, position.x()-self.x_init, position.y()-self.y_init)
        self.addItem(mapSquare)
        self.isPressed = False


class RamsinBrams(QMainWindow, brams.Ui_brcMainWindow):
    filechoose = ''
    wMessage = ''
    messAppend = ''
    basemap = None
    splashPixMap = None
    splash = None


    def closeEvent(self, QCloseEvent):
        QMainWindow.closeEvent(self, QCloseEvent)
        self.sair()


    def plotMapStart(self):
        self.splashMessage("Plotting Map, please wait ...")
        self.tabWidget.setVisible(False)
        self.statusMessage("Plotting Map, please wait ...")


    def plotMapFromMap(self):
        if self.latLonValidate(self.scene.latInitMap, self.scene.lonInitMap, self.scene.latEndMap, self.scene.lonEndMap) is False:
            self.clearSplash()
            self.statusMessage("")
            self.tabWidget.setVisible(True)
            return
        self.latUpEdit.setValue(self.scene.latInitMap)
        self.lonLeftEdit.setValue(self.scene.lonInitMap)
        self.latDownEdit.setValue(self.scene.latEndMap)
        self.lonRightEdit.setValue(self.scene.lonEndMap)
        self.plotMap()


    def plotMap(self):
        import matplotlib.pyplot as plt
        import numpy as np


        # Calc deltax or Points
        if not self.calcLatLonOption.isChecked():
            try:
                lat_up = self.latUpEdit.value()
                lon_left = self.lonLeftEdit.value()
                lat_down = self.latDownEdit.value()
                lon_right = self.lonRightEdit.value()

                if self.latLonValidate(lat_up, lon_left, lat_down, lon_right) is False:
                    self.clearSplash()
                    self.statusMessage("")
                    self.tabWidget.setVisible(True)
                    return

                # lat_median = lat_down
                # lon_median = lon_left
                lat_median = (lat_up + lat_down) / 2
                lon_median = (lon_left/2 + lon_right/2) /2
                distanceLonMeters = distance((lat_median, lon_left), (lat_median, lon_right))
                distanceLatMeters = distance((lat_up, lon_median), (lat_down, lon_median))
                centlat = (lat_down + lat_up) / 2
                centlon = (lon_right + lon_left) / 2
                self.centerLatlineEdit.setValue(centlat)
                self.centerLonlineEdit.setValue(centlon)
                self.PoleLatlineEdit.setValue(centlat)
                self.PoleLonlineEdit.setValue(centlon)
            except Exception as e:
                print(e)
                self.warningMessage("Please insert valid values for Lat/Lon input values")

        # Calc deltax
        if self.calcDeltaOption.isChecked():
            try:
                deltaX = int( distanceLonMeters / float(self.npxlineEdit.text()) )
                self.dxlineEdit.setText(str(deltaX))
                deltaY = int(distanceLatMeters / float(self.npylineEdit.text()))
                self.dylineEdit.setText(str(deltaY))
            except Exception as e:
                print(e)
                self.warningMessage("Please insert valid values for Lat/Lon input values and Points X/Y")

        # Calc Points
        elif self.calcPointsOption.isChecked():
            try:
                pointsX = int(distanceLonMeters / float(self.dxlineEdit.text()))
                self.npxlineEdit.setText(str(pointsX))
                pointsY = int(distanceLatMeters / float(self.dylineEdit.text()))
                self.npylineEdit.setText(str(pointsY))
            except Exception as e:
                print(e)
                self.warningMessage("Please insert valid values for Lat/Lon input values and Delta X/Y" )

        elif self.calcLatLonOption.isChecked():
            try:
                centlat = self.centerLatlineEdit.value()
                centlon = self.centerLonlineEdit.value()
                nnxp = float(self.npxlineEdit.text())
                nnyp = float(self.npylineEdit.text())
                deltax = float(self.dxlineEdit.text())
                deltay = float(self.dylineEdit.text())
                lat_up, lat_down, lon_left, lon_right = latLonFromCentLatLon(centlat, centlon, nnxp, nnyp, deltax, deltay)
                self.latUpEdit.setValue(lat_up)
                self.lonLeftEdit.setValue(lon_left)
                self.latDownEdit.setValue(lat_down)
                self.lonRightEdit.setValue(lon_right)

            except Exception as e:
                print(e)
                self.warningMessage("Please insert valid values for Center Lat/Lon, Points X/Y, and Delta X/Y")

        dlat = -lat_down + lat_up
        dlon = -lon_left + lon_right
        self.listWidget.selectedItems()
        if dlat > 45:
            dlat = 10.0
        elif dlat > 20:
            dlat = 5.0
        elif dlat > 2:
            dlat = 1.0
        else:
            dlat = 0.5

        if dlon > 45:
            dlon = 10.0
        elif dlon > 20:
            dlon = 5.0
        elif dlat > 2:
            dlon = 1.0
        else:
            dlon = 0.5

        try:
            #merc - mercator
            self.basemap = Basemap(projection='cea', llcrnrlat=lat_down, urcrnrlat=lat_up, llcrnrlon=lon_left, \
                              urcrnrlon=lon_right, resolution='l')
            ax = plt.gca()
            ax.clear()

            if self.citiescheckBox.isChecked():
                fname = '{}/gui/municip07'.format(brabu_data_dir)
                shp_info = self.basemap.readshapefile(fname, 'borders', drawbounds=True)

            if self.statescheckBox.isChecked():
                fname = '{}/gui/estadosl_2007'.format(brabu_data_dir)
                shp_info = self.basemap.readshapefile(fname, 'borders', drawbounds=True)
                # self.basemap.drawcounties(color='blue')

            self.basemap.drawcoastlines()
            self.basemap.fillcontinents(color='lightgreen', lake_color='aqua')
            # draw parallels and meridians.
            self.basemap.drawparallels(np.arange(lat_down, lat_up, dlat)) # dlat
            self.basemap.drawmeridians(np.arange(lon_left, lon_right, dlon )) # dlon
            self.basemap.drawmapboundary(fill_color='aqua')

            plt.savefig('map.png', bbox_inches="tight", pad_inches=0.0)
            pic = QPixmap("map.png")
            self.scene = QGraphicsSceneSquare(self, pic)
            self.scene.updateMap()
        except Exception as e:
            self.warningMessage("Delta/Points/LatLon data calculated, but it generated a too streched map. Please check lat/lon values.")
            print(e)

        self.clearSplash()
        self.statusMessage("Map plotted succefully!")
        self.tabWidget.setVisible(True)


    def sair(self):
        self.statusMessage("See you soon!")
        self.close()
        self.destroy()
        exit(0)


    def putBramsLogo(self):
        self.scene = QGraphicsScene()
        pic = QPixmap("{}/gui/brams_logo.png".format(brabu_data_dir))
        pic = pic.scaled(self.graphicsView.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        self.scene.addPixmap(pic)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.fitInView(self.scene.sceneRect(), Qt.IgnoreAspectRatio)
        self.graphicsView.show()


    def warningMessage(self, msg):
        QMessageBox.warning(self, "Warning", msg, QMessageBox.Ok)


    def splashMessage(self, msg):
        self.splash.show();
        self.splash.showMessage(msg, alignment=Qt.AlignHCenter)
        # self.splash.repaint()


    def clearSplash(self):
        self.splash.clearMessage()
        self.splash.hide()


    def statusMessage(self, msg):
        self.statusBar.showMessage(msg)
        # self.statusBar.update()


    def about(self):
        QMessageBox.about(self, 'BRAMS RAMSIN Builder Utility Rev 1.0', '\n' + 'By Luiz Flavio Rodrigues, Denis Eiras'.center(40, ' ') +
                          '\n\n' + 'September/2017'.center(40, ' ') + '\n\n' + 'CPTEC-INPE'.center(40, ' ') +
                          '\n\n' + 'Brazil'.center(40, ' ') + '\n')

    def showpoint(self):
        print('showpoint')


    def selectSaveFile(self):
        self.filechoose = QFileDialog.getSaveFileName(self, self.wMessage)


    def selectOpenFile(self):
        self.filechoose = QFileDialog.getOpenFileName(self, self.wMessage)


    def selectDir(self):
        self.filechoose = QFileDialog.getExistingDirectory(self, self.wMessage)


    def fntBt01(self):
        self.wMessage = 'Please Select History input File'
        self.selectOpenFile()
        self.histFilelineEdit.setText(self.filechoose)


    def hisanabutton(self):
        self.wMessage = 'Please Select Init Analisys input File'
        self.selectOpenFile()
        self.hisAnaltFilelineEdit.setText(self.filechoose)


    def fntBt02(self):
        self.wMessage = 'Please Select Analisys input File'
        self.selectOpenFile()
        self.iaFilelineEdit.setText(self.filechoose)


    def fntBt03(self):
        self.wMessage = 'Please Select History output Dir'
        self.selectDir()
        self.histOutFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt04(self):
        self.wMessage = 'Please Select Analisys output Dir'
        self.selectDir()
        self.AnalFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt05(self):
        self.wMessage = 'Please Select path for topo out files'
        self.selectDir()
        self.topoFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt06(self):
        self.wMessage = 'Please Select File path for surface files'
        self.selectDir()
        self.sfcFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt07(self):
        self.wMessage = 'Please Select File path for SST out files'
        self.selectDir()
        self.sstFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt08(self):
        self.wMessage = 'Please Select File path for NDVI out files'
        self.selectDir()
        self.ndviFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt09(self):
        self.wMessage = 'Please Select File path for input DPREP'
        self.selectDir()
        self.dprepFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt10(self):
        self.wMessage = 'Please Select File path for ISAN files'
        self.selectDir()
        self.isanFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt11(self):
        self.wMessage = 'Please Select File path for Topo files'
        self.selectDir()
        self.topoOutFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt12(self):
        self.wMessage = 'Please Select File path for Soil files'
        self.selectDir()
        self.soilFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt13(self):
        self.wMessage = 'Please Select File path for SST files'
        self.selectDir()
        self.sstOutFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt14(self):
        self.wMessage = 'Please Select File path for NDVI files'
        self.selectDir()
        self.ndviOutFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt15(self):
        self.wMessage = 'Please Select path for Vegetation files'
        self.selectDir()
        self.vegFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt16(self):
        self.wMessage = 'Please Select path for Pos files'
        self.selectDir()
        self.posFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt17(self):
        self.wMessage = 'Please Select path for Soil Moisture files'
        self.selectDir()
        self.smFilelineEdit.setText(self.filechoose + '/{prefix}')


    def fntBt18(self):
        self.wMessage = 'Please Select path for Soil Moisture Pre files'
        self.selectDir()
        self.smpFilelineEdit.setText(self.filechoose + '/{prefix}')


    def srcchem(self):
        self.wMessage = 'Please Select path Source Map file prefix '
        self.selectDir()
        self.sfnFilelineEdit.setText(self.filechoose + '/{prefix}')


    def mapOnOff_group_clicked(self):
        if self.mapOnOff_group.isChecked():
            self.latLonInput_group.setChecked(False)

    def latLonInput_group_clicked(self):
        if self.latLonInput_group.isChecked():
            self.mapOnOff_group.setChecked(False)


    def zoomButton_clicked(self):
        lat_up = self.latUpEdit.value()
        lon_left = self.lonLeftEdit.value()
        lat_down = self.latDownEdit.value()
        lon_right = self.lonRightEdit.value()
        zoom = self.zoomEdit.value()

        if lat_up > 0:
            lat_up -= zoom
        else:
            lat_up -= zoom

        if lat_down > 0:
            lat_down += zoom
        else:
            lat_down += zoom

        if lon_left > 0:
            lon_left += zoom
        else:
            lon_left += zoom

        if lon_right > 0:
            lon_right -= zoom
        else:
            lon_right -= zoom

        if self.latLonValidate(lat_up, lon_left, lat_down, lon_right) is False:
            return

        self.latUpEdit.setValue(self.latUpEdit.value()-self.zoomEdit.value())
        self.lonLeftEdit.setValue(self.lonLeftEdit.value()+self.zoomEdit.value())
        self.latDownEdit.setValue(self.latDownEdit.value()+self.zoomEdit.value())
        self.lonRightEdit.setValue(self.lonRightEdit.value()-self.zoomEdit.value())


    def latLonValidate(self, lat_up, lon_left, lat_down, lon_right):

        if lat_down >= lat_up:
            self.warningMessage("Down Lat cant be greater or equal to Up Lat!")
            return False
        if lon_left >= lon_right:
            self.warningMessage("Left Lon cant be greater or equal to Rigth Lon!")
            return False
        if lat_up > 90:
            self.warningMessage("Upper Lat cant be greater than 90!")
            return False
        if lat_down < -90:
            self.warningMessage("Down Lat cant be less than -90!")
            return False
        if lon_left < -180:
            self.warningMessage("Left Lon cant be less than -180!")
            return False
        if lon_right > 180:
            self.warningMessage("Right Lon cant be greater than 180!")
            return False

        return True


    # def mousePressEvent(self, event):
    # print 'mouse Press event'
    # print event.pos()
    # print 'bookmark: ',self.mainwindow.booklist[int(item.zValue())]
    # bookmark = self.mainwindow.booklist[int(item.zValue())]
    # self.reloadTimer.start(300)
    # self.reloadbookmark = bookmark
    # self.graphicsView.mousePressEvent(self, event)

    def item_click(self):
        i = 0
        locallist = []
        # print self.listWidget.count() #total
        self.selvaListView.reset()
        for item in self.listWidget.selectedItems():
            locallist.append(item.text())
            i += 1
        model = listModel(locallist)
        self.selvaListView.setModel(model)
        self.varslcdNumber.intValue = i
        self.varslcdNumber.display(i)


    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        if sys.version_info[0] == 3:
            super().__init__()
        else:
            super(self.__class__, self).__init__()

        self.setupUi(self)  # T
        # self.doit.clicked.connect(self.readData)

        self.ramsinController = RamsinController(self)

        self.uSimcomboBox.setCurrentIndex(2)

        self.splashPixMap = QPixmap("{}/gui/brams_logo.png".format(brabu_data_dir))
        self.splashPixMap = self.splashPixMap.scaled(self.splashPixMap.size() * 1.4, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.splash = QSplashScreen(self.splashPixMap)

        self.splashMessage("Initializing ...")
        self.statusMessage("Hello, have a great day!")

        self.ramsinController.readVariables()

        # TODO - load SOME RAMSIN instead of set below
        lat_up = 90
        self.latUpEdit.setValue(lat_up)
        lon_left = -180
        self.lonLeftEdit.setValue(lon_left)
        lat_down = -90
        self.latDownEdit.setValue(lat_down)
        lon_right = 180
        self.lonRightEdit.setValue(lon_right)
        # self.basemap = Basemap(projection='cea', llcrnrlat=lat_down, urcrnrlat=lat_up, llcrnrlon=lon_left, \
        #                   urcrnrlon=lon_right, resolution='i')
        #
        self.centerLonlineEdit.setValue(0)
        self.centerLatlineEdit.setValue(0)
        self.PoleLatlineEdit.setValue(0)
        self.PoleLonlineEdit.setValue(0)

        self.varslcdNumber.intValue = 0

        self.listWidget.itemClicked.connect(self.item_click)

        # actions
        # self.actionNew_2.triggered.connect(self.teste)
        # self.actionMake.triggered.connect(self.makeRamsin)
        self.actionAbout.triggered.connect(self.about)
        # self.actionEdit_RAMSIN.connect(self.editr)

        # self.actionEdit_RAMSIN.connect(self.editr)
        # self.plotButton.clicked.connect(self.plotMapStart)
        self.plotButton.pressed.connect(self.plotMapStart)
        self.plotButton.released.connect(self.plotMap)
        self.plotMapButton.pressed.connect(self.plotMapStart)
        self.plotMapButton.released.connect(self.plotMapFromMap)

        # File select buttons
        self.sf01Button.clicked.connect(self.fntBt01)
        self.sf02Button.clicked.connect(self.fntBt02)
        self.sf03Button.clicked.connect(self.fntBt03)
        self.sf04Button.clicked.connect(self.fntBt04)
        self.sf05Button.clicked.connect(self.fntBt05)
        self.sf06Button.clicked.connect(self.fntBt06)
        self.sf07Button.clicked.connect(self.fntBt07)
        self.sf08Button.clicked.connect(self.fntBt08)
        self.sf09Button.clicked.connect(self.fntBt09)
        self.sf10Button.clicked.connect(self.fntBt10)
        self.sf11Button.clicked.connect(self.fntBt11)
        self.sf12Button.clicked.connect(self.fntBt12)
        self.sf13Button.clicked.connect(self.fntBt13)
        self.sf14Button.clicked.connect(self.fntBt14)
        self.sf15Button.clicked.connect(self.fntBt15)
        self.sf16Button.clicked.connect(self.fntBt16)
        self.sf17Button.clicked.connect(self.fntBt17)
        self.sf18Button.clicked.connect(self.fntBt18)
        self.srcfnButton.clicked.connect(self.srcchem)
        self.HisAnalpushButton.clicked.connect(self.hisanabutton)
        self.mapOnOff_group.clicked.connect(self.mapOnOff_group_clicked)
        self.latLonInput_group.clicked.connect(self.latLonInput_group_clicked)
        self.zoomButton.clicked.connect(self.zoomButton_clicked)

        self.actionSave_2.triggered.connect(self.ramsinController.saveRamsin)
        self.actionSave_as.triggered.connect(self.ramsinController.saveRamsinAs)
        self.saveRamsinButton.clicked.connect(self.ramsinController.saveRamsinManual)
        self.saveRamsinAsButton.clicked.connect(self.ramsinController.saveRamsinManualAs)
        self.actionOpen.triggered.connect(self.ramsinController.selectRamsinReadConfig)

        self.actionLight_Case.triggered.connect(self.ramsinController.readConfigFromPatternLightCase)
        self.actionChemical_Light.triggered.connect(self.ramsinController.readConfigFromPatternChemicalLight)
        self.actionSouth_America.triggered.connect(self.ramsinController.readConfigFromPatternSouthAmerica)
        self.actionChemical_Rio_1km.triggered.connect(self.ramsinController.readConfigFromPattern1kmRio)
        self.actionAmazon_1km.triggered.connect(self.ramsinController.readConfigFromPattern1kmAmazon)

        # self.dist()
        self.putBramsLogo()
        self.clearSplash()

        self.tmfcomboBox.count()


# def main():
#     app = QApplication(sys.argv)  # A new instance of QApplication
#     form = RamsinBrams()  # We set the form to be our ExampleApp (design)
#     form.show()  # Show the form
#     # QtWidgets.QApplication.setQuitOnLastWindowClosed(True)
#     #TODO
#     #app.connect(app, pyqtSignal(QApplication.lastWindowClosed()), app, pyqtSlot(quit()));
#     #setQuitOnLastWindowClose(true)
#     #app.setQuitOnLastWindowClosed(True)
#     app.exec_()  # and execute the app
#
# if __name__ == '__main__':  # if we're running file directly and not importing it
#     main()