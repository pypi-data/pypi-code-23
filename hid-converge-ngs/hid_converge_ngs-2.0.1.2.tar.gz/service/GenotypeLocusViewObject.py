'''
Created on Apr 27, 2015
import requests

@author: karpagm1
'''
from service import LocusViewObject



    
class GenotypeLocusViewObject:
    
    def __init__(self):
        self.id = None
        self.locus = None
        self.value = None
        
    def __repr__(self):
        return {'id':self.id,'locus':self.locus,'value':self.value}       