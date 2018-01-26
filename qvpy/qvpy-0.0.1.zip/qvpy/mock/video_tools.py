# -*- coding: utf-8 -*-

###############################################################################
class Tool:
    def __init__(self):
        pass
    
    def Run(self, **kwargs):
        return 1

    def SetFilter(self, **kwargs):
        return 1

    def SetMode(self, **kwargs):
        return 1
        

###############################################################################
class BoxTool(Tool):
    def __init__(self):
        pass


###############################################################################
class BrightnessTool(Tool):
    def __init__(self):
        pass
    
    def GetBrightness(self, **kwargs):
        return 0.62


###############################################################################
class CircleTool(Tool):
    def __init__(self):
        self.Alg = 1


###############################################################################
class DualAreaContrastTool(Tool):
    def __init__(self):
        self.LightType = 0


###############################################################################
class FocusTool(Tool):
    def __init__(self):
        pass


###############################################################################
class PatternTool(Tool):
    def __init__(self):
        pass


###############################################################################
class SmartRecovery:
    def __init__(self):
        self.Focus = True


###############################################################################
class Video:
    def __init__(self):
        self.HWND = 66330
        self.IsLive = 1
        self.SmartRecovery = SmartRecovery()
