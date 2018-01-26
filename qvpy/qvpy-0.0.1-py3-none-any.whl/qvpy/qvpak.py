# -*- coding: utf-8 -*-

### imports ###################################################################
import logging
import time

### imports from ##############################################################
from win32com.client.dynamic import Dispatch

### relative imports from #####################################################
from .constants import Constants

### logging ###################################################################
logging.getLogger('qvpak_com').addHandler(logging.NullHandler())

###############################################################################
class Mitutoyo:
    def __init__(self):
        self.logger = logging.getLogger('qvpak_com')
        
        try:
            self.qv = Dispatch('QV')
        except:
            self.logger.warning('Could not dispatch QV')
            self.mock = True

        if self.mock:
            self.logger.info('Mocking QuickVision device')
            from .mock.quickvision import QuickVision
            self.qv = QuickVision()


    def init(self):
        self.selectObjective()
        self.initResults()
        self.initQV()
        self.initVideo()
        
        ### Maschinenkoordinatensystem wiederherstellen ###
        self.qv.PCS.RestoreMCS()
        
        ### Referenz Ebene festlegen ###
        self.qv.ReferencePlane = Constants.ReferencePlane['xy']
        
        ### Messgerät ###
        self.qv.MeasuringDevice = 0
        self.qv.CylUsesRefPlane = True
        
        self.deleteDatabases()
            
            
    def initQV(self):
        self.logger.debug('Initialising QV')
        self.qv.BreakOnErrors = True
        self.qv.ShowImageTools = True
        self.qv.ShowTravelLimitWarnings = False
        self.qv.AutoRunSmartRecovery = False

        # init units
        self.qv.DistanceUnits = Constants.DistanceUnits['mm']
        self.qv.CoordinateMode = Constants.CoordinateMode['cartesian']
        self.qv.ResolutionMode = 3 # dezimal 3
        self.qv.AngleRange = Constants.AngleRange['positive']
        self.qv.AngleUnits = 2 # dezimal 2


    def initResults(self):
        self.logger.debug('Initialising Results')
        ### Ergebnisformatierung ###
        self.qv.Results.ShowFeatureTypeInHdr = True
        self.qv.Results.ShowFeatureLabelInHdr = True
        self.qv.Results.ShowFeatureIDInHdr = True
        self.qv.Results.ShowNumOfPointsInHdr = True
        self.qv.Results.ShowColumnLabels = True
        self.qv.Results.FormatColumns(8, 1, 2, 3, 4, 5, 6)

        ### Meldungen ###
        self.qv.Results.ShowAlignmentMsg = False
        self.qv.Results.ShowUnitsChangeMsg = False
        self.qv.Results.ShowConstructionMsg = False
        self.qv.Results.ShowErrorMsg = False

        ### Ausgabefilter für Report ###
        self.qv.Results.ReportLevel = Constants.ReportLevel['all']
        
        ### Ergebnisausgabe ##
        self.qv.Results.LogFileName = ""
        self.qv.Results.LogToFile = False
        self.qv.Results.LogToCOM1 = False
        self.qv.Results.LogToCOM2 = False


    def initVideo(self):
        self.logger.debug('Initialising Video')
        ### Options für intelligente Programmfortführung ###
        self.qv.Video.SmartRecovery.Focus = True
        self.qv.Video.SmartRecovery.FocusRange = 1
        self.qv.Video.SmartRecovery.Lighting = True
        self.qv.Video.SmartRecovery.LightingRange = 1
        self.qv.Video.SmartRecovery.ToolPosition = True
        self.qv.Video.SmartRecovery.ToolPositionRange = 1
        self.qv.Video.SmartRecovery.ToolAngle = True
        self.qv.Video.SmartRecovery.ToolAngleRange = 1
        self.qv.Video.SmartRecovery.EdgeStrength = True
        self.qv.Video.SmartRecovery.EdgeStrengthRange = 1


    def cleanUp(self):
        result = self.qv.PCS.RestoreMCS()
        
        if not result:
            self.logger.warning('Could not restore MCS')
            return result
        
        result = self.stage_moveTo((0, 200, 150))

        return result
    
    
    def info(self):
        ### Camera
        logging.info('Depth: %i', self.qv.Camera.Depth) # 8
        logging.info('Width: %i', self.qv.Camera.Width) # 640
        logging.info('Height: %i', self.qv.Camera.Height) # 480
        logging.info('Mono: %i', self.qv.Camera.IsMono) # 1
        
        ### Video
        logging.info('HWND: %i', self.qv.Video.HWND) # 66330
        logging.info('Live: %i', self.qv.Video.IsLive) # 1
        
        ### Stage
        logging.info('Motion: %i', self.qv.Stage.IsInMotion)
        
        logging.info(
                'Cylindrical coords: %6.2f deg., %6.2f',
                self.qv.Stage.APos, self.qv.Stage.RPos)
        
        ### Lens
        logging.info('Lens: %s', self.qv.Lens.Name)
        logging.info('Number of lens positions: %s', self.qv.Lens.NumPositions)
     
        
    def deleteDatabases(self):
        # Vor jeder Messung muß die Datenbank der gemessenen Elemente geleert
        # werden, sonst kommt es zu Namenskonflikten 
        # mit den während der Messung neu erstellten Elementen
        
        self.logger.debug('Deleting FeatureDB')
        
        i = 0
        
        while True:
            try:
                self.qv.FeatureDB.DeleteAll()
                break
            except:
                print(i)
                time.sleep(1)
        
        self.logger.debug('Deleting PtBufDB')
        self.qv.PtBufDB.DeleteAll()
        
        self.logger.debug('Deleting TolDB')
        self.qv.TolDB.DeleteAll()        


    def pcs_import(self, fullfile):       
        result = self.qv.PCS.Import(fullfile)
        
        if not result:
            self.logger.warning('Could not import %s', fullfile)

        return result
    

    def selectObjective(self):
        self.qv.Lens.Select("1X (QVHR Objective)")


    def stage_moveTo(self, *args, **kwargs):

        for key, value in kwargs.items():
            if key == 'x':
                x = value
            elif key == 'y':
                y = value
            elif key == 'z':
                z = value
                
        for arg in args:
            x = arg[0]
            y = arg[1]
            z = arg[2]

        result = self.qv.Stage.MoveTo(X=x, Y=y, Z=z)
        
        if result:
            
            while self.qv.Stage.IsInMotion:
                time.sleep(0.01)
            
            self.logger.debug(
                    'Moved stage to (%7.3f, %7.3f, %7.3f)',
                    x, y, z)
        else:
            self.logger.warning(
                    'Could not move stage to (%6.3f, %6.3f, %6.3f)',
                    x, y, z)

        return result