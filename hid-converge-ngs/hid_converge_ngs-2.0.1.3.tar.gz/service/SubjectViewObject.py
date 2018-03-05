'''
Created on Apr 27, 2015
import requests

@author: karpagm1
'''


class SubjectViewObject:

    def __init__(self):
        self.ageAtRegistration = None
        self.birthDate = None
        # self.contact
        self.ethnicityId = None
        self.ethnicityName = None
        self.externalAppId = None
        self.externalId = None
        self.firstName = None
        self.gender = None
        self.lastComment = None
        self.lastName = None
        self.middleName = None
        self.relationship = None
        self.title = None
        self.id = None
        self.uid = None
        
    def __repr__(self):
        return {'id':self.id}       
        #return {'ageAtRegistration':self.ageAtRegistration,'birthDate':self.birthDate,'ethnicityId':self.ethnicityId,'ethnicityName':self.ethnicityName,'externalAppId':self.externalAppId,'externalId':self.externalId,'firstName':self.firstName,'gender':self.gender,'lastComment':self.lastComment,'lastName':self.lastName,'middleName':self.middleName,'relationship':self.relationship,'title':self.title,'id':self.id,'uid':self.uid}      
        
