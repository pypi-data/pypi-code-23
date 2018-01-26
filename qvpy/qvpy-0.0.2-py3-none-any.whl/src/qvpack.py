# -*- coding: utf-8 -*-

### imports ###################################################################
import logging
from win32com.client.dynamic import Dispatch

###############################################################################
class Mitutoyo:
    def __init__(self):
        self.logger = logging.getLogger('qvpak_com')
        
        try:
            self.qv = Dispatch('QV')
        except:
            self.logger.warning('Could not dispatch QV')
            self.mock = True

    def initQV(self):
        self.logger.debug('Initialising QV')
        self.qv.BreakOnErrors = True
        self.qv.ShowImageTools = True
        self.qv.ShowTravelLimitWarnings = False
        self.qv.AutoRunSmartRecovery = False        

###############################################################################
if __name__ == "__main__":        
    mitutoyo = Mitutoyo()