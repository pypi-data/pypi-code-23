'''
Created on Apr 27, 2015
import requests

@author: karpagm1
'''


    
class DnaCaseMap:
    
    def __init__(self):
        self.dnaCase =  None
        self.subjectMap = None
        self.profileMap = None
        self.subjectProfileMap = None
        self.subjectLousMap = {}
        self.validForImport = True
        self.reasonForFailure = None
        self.uid = None
