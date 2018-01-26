# -*- coding: utf-8 -*-

### relative imports from #####################################################
from .database import FeatureDB, PtBufDB, TolDB
from .hardware import Camera, Lens, Light, Stage
from .software import Measure, PatternTemplate, PCS, Results
from .video_tools import BrightnessTool, BoxTool, CircleTool
from .video_tools import DualAreaContrastTool, FocusTool, PatternTool, Video


###############################################################################
class QuickVision:
    def __init__(self):
        # video tools
        self.BoxTool = BoxTool()
        self.BrightnessTool = BrightnessTool()
        self.CircleTool = CircleTool()
        self.DualAreaContrastTool = DualAreaContrastTool()
        self.FocusTool = FocusTool()
        self.PatternTool = PatternTool()
        self.Video = Video()

        # database
        self.FeatureDB = FeatureDB()
        self.PtBufDB = PtBufDB()
        self.TolDB = TolDB()

        # software controls
        self.Measure = Measure()
        self.PatternTemplate = PatternTemplate()
        self.PCS = PCS()
        self.Results = Results()

        # hardware controls
        self.Camera = Camera()
        self.Lens = Lens()
        self.Light = Light()
        self.Stage = Stage()
