# -*- coding: utf-8 -*-

### imports ###################################################################
import logging
from win32com.client.dynamic import Dispatch

###############################################################################
class Mitutoyo:
    def __init__(self):
        self.logger = logging.getLogger('qvpak_com')
        
        self.qv = Dispatch('QV')

    def initQV(self):
        self.logger.debug('Initialising QV')
        self.qv.BreakOnErrors = True
        self.qv.ShowImageTools = True
        self.qv.ShowTravelLimitWarnings = False
        self.qv.AutoRunSmartRecovery = False        
        
mitutoyo = Mitutoyo()