'''
Created on Apr 27, 2015
import requests

@author: karpagm1
'''


    
class LocusViewObject:
    
    def __init__(self):
        self.name = None
        self.classification = None
        self.locusType = None
        
    def __repr__(self):
        return {'name':self.name,'classification':self.classification,'locusType':self.locusType}    
