# -*- coding: utf-8 -*-

###############################################################################
class Camera:
    def __init__(self):
        self.Depth = 8
        self.Height = 480
        self.IsMono = 1
        self.Width = 640

###############################################################################
class Lens:
    def __init__(self):
        self.lensInfo = LensInfo()
        self.Name = 'Mock'
        self.NomMag = 0.0
        self.NumPositions = 3
    
    def Info(self):
        return self.lensInfo
    
    def Select(self, name):
        self.objective = name

###############################################################################
class LensInfo:
    def __init__(self):
        self.XScale = 9.0
        self.YScale = 9.0

###############################################################################
class Light:
    def __init__(self):
        self.Coax = LightChannel()
        self.PRL = PRL()
        self.Stage = LightChannel()


###############################################################################
class LightChannel:
    def __init__(self):
        self.Level = 0


###############################################################################
class PRL:
    def __init__(self):
        pass
    
    def SetAll(self, **kwargs):
        return 1


###############################################################################
class Stage:
    def __init__(self):
        self.APos = 0
        self.IsInMotion = 0
        self.RPos = 0
    
    def MoveTo(self, **kwargs):
        return 1
