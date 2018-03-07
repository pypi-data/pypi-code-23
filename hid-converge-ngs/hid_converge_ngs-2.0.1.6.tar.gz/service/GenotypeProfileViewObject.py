'''
Created on Apr 27, 2015
import requests

@author: karpagm1
'''


    
class GenotypeProfileViewObject:
    
    def __init__(self):
        self.id = None
        self.uid = None
        self.lastModified = None
        self.createdDate = None
        self.kitName = None
        self.locusTypeName = None
        self.isVirtual = None
        self.subject = None
        self.sample = None #not required for post.
        self.isDefault = None
        self.bioSampleUID = None
        self.sampleUID = None
        self.bioSampleExternalUid = None
        self.kitId = None
        self.genotypeLoci = None
        self.profileCategory = None
        self.errorMessage = None
        self.profileCategoryValid = None
        self.dnaCaseUpdateDate = None
        self.imported = None