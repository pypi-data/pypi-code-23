#!/usr/bin/env python2.7

from __future__ import print_function


import os,sys
import shutil
import helper_funcs as HF

class SidebarClass():
    def __init__(self):
        paramDict = dict()
        
    def initialize_from_file(self):
        pass
    
    def initialize_from_mat(self, paramMat):
        self.paramDict = HF.initialize_from_paramMat(paramMat)
        HF.setVar(self, self.paramDict)
