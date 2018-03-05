'''
Created on Apr 27, 2015
import requests

@author: karpagm1
'''
from dataObjects.ContactViewObject import ContactViewObject


    
class OrganizationViewObject:
    
    def __init__(self):
        self.id = None
        self.shortName = None
        self.name = None
        self.description = None
        self.type = None
        self.contactVo = ContactViewObject()
        self.contactPersonVos = None
        
        #private List<SubjectViewObject> contactPersonVos=new ArrayList<SubjectViewObject>();