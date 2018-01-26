# -*- coding: utf-8 -*-

### imports ###################################################################
import os

###############################################################################
class Measure:
    def __init__(self):
        pass
        
    def Circle(self, **kwargs):
        return 1
    
    def EndMeas(self):
        return 1

    def KeyinDataPoint(self, x, y, z):
        return 1

    def Line(self, **kwargs):
        return 1
    
    def Point(self, **kwargs):
        return 1

    def RecallPtBuf(self, **kwargs):
        return 1
    
    def PtBuf(self, **kwargs):
        return 1

###############################################################################
class PatternTemplate:
    def __init__(self):
        pass
    
    def Import(self, filename):
        result = os.path.isfile(filename)
        return result


###############################################################################
class PCS:
    def __init__(self):
        pass
    
    def AlignAxis(self, **kwargs):
        return 1

    def AlignOrigin(self, **kwargs):
        return 1
    
    def RestoreMCS(self):
        return 1
    
    def Import(self, filename):

        result = 0
        
        if os.path.isfile(filename):
            result = 1
        
        return result

###############################################################################
class Results:
    def __init__(self):
        ### Ergebnisformatierung ###
        self.ShowFeatureLabelInHdr = None
        self.ShowFeatureTypeInHdr = None
        self.ShowFeatureIDInHdr = None
        self.ShowNumOfPointsInHdr = None
        self.ShowColumnLabels = None

        ### Meldungen ###
        self.ShowAlignmentMsg = False
        self.ShowUnitsChangeMsg = False
        self.ShowConstructionMsg = False
        self.ShowErrorMsg = False

        ### Ausgabefilter fÃ¼r Report ###
        self.ReportLevel = None
        
        ### Ergebnisausgabe ##
        self.LogFileName = ""
        self.LogToFile = False
        self.LogToCOM1 = False
        self.LogToCOM2 = False


    def FormatColumns(self, *argv):
        self._FormatColumns = argv
    

