'''
Created on Apr 27, 2015
import requests

@author: karpagm1
'''

import logging
import json

from authentication.gateway import GateWayService
import xml.etree.ElementTree as et
import urllib
import re
from service import RelationshipEnum
from service.DictionaryEntry import DictionaryEntry
from QueueModule.q import flushableQ


title = 'person.title'
gender = 'Gender'
relationship = 'Relationship'
country = 'Country'
state = 'State'
    
class CaseService:
    
    def __init__(self):
        #print ('initialized')
        logging.INFO('initialized')

    # Case related related   API
    @staticmethod
    def createCase(dnaCase, baseUrl):
        CaseService.logService('createCase' )
        caseCreationUrl = baseUrl+'/platform/dnacase/dnaCase/'
        payload= json.dumps(dnaCase.__dict__)
        #response = authentication.session.post(caseCreationUrl, data=payload)
        return GateWayService.callConverge(caseCreationUrl, 'true', payload)

    @staticmethod    
    def addSubjectToCase(dnaCaseId, subject, baseUrl):
        CaseService.logService('addSubjectToCase' )
        addSubjectUrl = baseUrl+'/platform/dnacase/dnaCase/addsubject/'+str(dnaCaseId)+'/false'
        payload= json.dumps(subject.__dict__)
        flushableQ.put(dnaCaseId)
        return GateWayService.callConverge(addSubjectUrl,'true', payload)
    
    @staticmethod    
    def addProfileToCase(dnaCaseId, profiles, baseUrl):
        CaseService.logService('addProfileToCase' )
        addSubjectUrl = baseUrl+'/platform/dnacase/dnaCase/addAllProfiles/'+str(dnaCaseId)
        payload= json.dumps([p.__dict__ for p in profiles])
        flushableQ.put(dnaCaseId)
        #print(payload)
        return GateWayService.callConverge(addSubjectUrl,'true', payload)

    @staticmethod    
    def getAnalysisInput(dnaCaseId, baseUrl):
        CaseService.logService('getAnalysisInput' )
        addSubjectUrl = baseUrl+'/kinship/kinship/analysisInput/'+str(dnaCaseId)
        return GateWayService.callConverge(addSubjectUrl,'false', '')
    
    @staticmethod    
    def postAnalysisInput(dnaCaseId, baseUrl, analysisInput):
        CaseService.logService('postAnalysisInput' )
        addSubjectUrl = baseUrl+'/kinship/kinship/analysisInput/'+str(dnaCaseId)
        return GateWayService.callConverge(addSubjectUrl,'true', analysisInput)
    
    @staticmethod    
    def getPedigreeTreeXml(baseUrl, type):
        CaseService.logService('getPedigreeTreeXml' + type)
        addSubjectUrl = baseUrl+'/platform/common/dictionary/?category=Sys.Kinship.Tree.ImageTemplate&name='+type
        return GateWayService.callConverge(addSubjectUrl,'false', '')
    
    @staticmethod    
    def saveSessionImage(baseUrl, analysisId,image):
        CaseService.logService('saveSessionImage' )
        addSubjectUrl = baseUrl+'/kinship/kinship/saveSessionImage/'+str(analysisId)
        return GateWayService.callConverge(addSubjectUrl,'true', image)
    
    @staticmethod    
    def calculate(baseUrl,dnaCaseId, analysisId):
        CaseService.logService('calculate' )
        addSubjectUrl = baseUrl+'/kinship/kinship/calculate/'+str(dnaCaseId)+'/'+str(analysisId)
        return GateWayService.callConverge(addSubjectUrl,'true', '')
    
    @staticmethod    
    def saveAnalysisResults(baseUrl,dnaCaseId, analysisId, analysisResults):
        CaseService.logService('saveAnalysisResults' )
        addSubjectUrl = baseUrl+'/kinship/kinship/saveAnalysisResult/'+str(dnaCaseId)+'/'+str(analysisId)
        flushableQ.put(dnaCaseId)
        return GateWayService.callConverge(addSubjectUrl,'true', analysisResults)
    
    @staticmethod    
    def getSubjectsForDnaCase(baseUrl,dnaCaseId):
        CaseService.logService('getSubjectsForDnaCase')
        getSubjectsForDnaCaseUrl = baseUrl+'/kinship/kinship/getSubjectsForCaseForKinship/'+str(dnaCaseId)
        return GateWayService.callConverge(getSubjectsForDnaCaseUrl,'false', dnaCaseId)
    
    
    @staticmethod    
    def creatPedigreeTreeImageForCase1(baseUrl,dnaCaseId, analysisId):    
        subjectDict = CaseService.getSubjectsForDnaCase(baseUrl, dnaCaseId)
        subjectsJson = json.dumps(subjectDict)
        CaseService.createXmlConfigAndSaveSessionImage(baseUrl,subjectsJson,analysisId,414,919,'ScriptedTree')

    @staticmethod    
    def createXmlConfigAndSaveSessionImage(baseUrl,subjectDict,analysisID,height,width,modelName):
        CaseService.logService('createXmlConfig' )
        addSubjectUrl = baseUrl+'/kinship/kinship/createSaveSessionImage/'+str(analysisID)+'/'+str(height)+'/'+str(width)+'/'+modelName
        return GateWayService.callConverge(addSubjectUrl,'true', subjectDict)
    
    @staticmethod 
    def buildGraph(caseId, caseType, profilesDict, subjects):    
        graph = {'edges':[], 'vertices':[]}
        kinshipGraph = {'graph':graph,'motherNodeId':None, 'fatherNodeId':None , 'childNodeId':None, 'prosVertexId':None, 'defVertexId':None,
                        'untypedFatherNodeId':None, 'defMotherNodeId':None, 'defChildNodeId':None, 'defVertexId':None, 'untypedMotherNodeId': None,
                        'defChildNodeId':None, 'seqId':1}
        #print(profilesDict)
        for v in profilesDict:
            profileId = v['id']
            subjectId = v['subject']['id']
            gender = subjects[subjectId]['gender']
            relationship = subjects[subjectId]['relationship']
            #print(' profile ' + str(profileId) + ' subject ' +str(subjectId) + ' gender' + gender+ '  relaton ' + relationship)
            CaseService.buildProsecutionVertex(2, subjectId ,profileId, gender, relationship, kinshipGraph )
            CaseService.buildDefenceVertex(3,  subjectId ,profileId, gender, relationship, kinshipGraph)
        noOfSubjects = len (profilesDict);
        if(noOfSubjects == 3 and caseType == 'Trio Paternity'):
            CaseService.buildDefenceVertex(3, '', None, 'M', 'FUntyped', kinshipGraph)
        elif(noOfSubjects == 3 and caseType == 'Trio Maternity'):
            CaseService.buildDefenceVertex(3, '', None, 'F', 'MUntyped', kinshipGraph)    
        elif(noOfSubjects == 2 and caseType == 'Duo Motherless'):
            CaseService.buildDefenceVertex(3, '', None, 'M', 'FUntyped', kinshipGraph)
            CaseService.buildDefenceVertex(3, '', None, 'F', 'MUntyped', kinshipGraph)
            CaseService.buildProsecutionVertex(2, '', None, 'F', 'Mother', kinshipGraph)
        elif(noOfSubjects == 2 and caseType == 'Duo Fatherless'):
            CaseService.buildDefenceVertex(3, '', None, 'M', 'FUntyped', kinshipGraph)
            CaseService.buildDefenceVertex(3, '', None, 'F', 'MUntyped', kinshipGraph)
            CaseService.buildProsecutionVertex(2, '', None, 'M', 'Father', kinshipGraph)    

        CaseService.buildEdge(2 ,kinshipGraph['fatherNodeId']  ,kinshipGraph['motherNodeId'] ,None , kinshipGraph);
        CaseService.buildEdge(2 ,kinshipGraph['childNodeId']  ,kinshipGraph['prosVertexId'] ,'Vertex' , kinshipGraph)

        if(noOfSubjects == 3 and caseType == 'Trio Paternity'):
            CaseService.buildEdge(3 ,kinshipGraph['untypedFatherNodeId']  ,kinshipGraph['defMotherNodeId'],None, kinshipGraph )
            CaseService.buildEdge(3 ,kinshipGraph['defChildNodeId'],kinshipGraph['defVertexId'] ,'Vertex', kinshipGraph  )
        elif(noOfSubjects == 3 and caseType == 'Trio Maternity'):
            CaseService.buildEdge(3 ,kinshipGraph['untypedMotherNodeId']  ,kinshipGraph['defFatherNodeId'],None, kinshipGraph )
            CaseService.buildEdge(3 ,kinshipGraph['defChildNodeId'],kinshipGraph['defVertexId'] ,'Vertex', kinshipGraph  )    
        elif(noOfSubjects == 2 and caseType == 'Duo Motherless' ):
            CaseService.buildEdge(3 , kinshipGraph['untypedFatherNodeId']  ,kinshipGraph['untypedMotherNodeId'] ,None, kinshipGraph )
            CaseService.buildEdge(3 ,kinshipGraph['defChildNodeId']  ,kinshipGraph['defVertexId'] ,'Vertex' , kinshipGraph)
        elif(noOfSubjects == 2 and caseType == 'Duo Fatherless' ):
            CaseService.buildEdge(3 , kinshipGraph['untypedFatherNodeId']  ,kinshipGraph['untypedMotherNodeId'] ,None, kinshipGraph )
            CaseService.buildEdge(3 ,kinshipGraph['defChildNodeId']  ,kinshipGraph['defVertexId'] ,'Vertex' , kinshipGraph)
                
        #print(kinshipGraph)
        jsonKinshipGraph = json.dumps(kinshipGraph)
        #print(jsonKinshipGraph)
        return kinshipGraph    
    
    @staticmethod
    def createReport(baseUrl,caseId,analysisId):
        CaseService.logService('createReport' )
        reportTemplateUrl = baseUrl+'/platform/common/template/getTemplateByGroup/Kinship%20Report'
        reportTemplteDict = GateWayService.callConverge(reportTemplateUrl, 'false', '')
        #print(reportTemplteDict)
        reportTemplteAccessionId = reportTemplteDict[0]['templateAccessionId']
        kinshipReportInputDataDict = {'templateAccessionID': reportTemplteAccessionId, 'reportName': 'Report created from script', 'conclusion': None, 'caseID': caseId, 'analysisID': analysisId }
        kinshipReportInputDataJson = json.dumps(kinshipReportInputDataDict)
        reportGenerationUrl = baseUrl+'/kinship/kinship/createKinshipReport/'+str(caseId)
        flushableQ.put(caseId)
        GateWayService.callConverge(reportGenerationUrl, 'true', kinshipReportInputDataJson)

    @staticmethod 
    def performAnalysis(baseUrl, dnaCaseDict,profilesDict,subjects): 
        caseId = dnaCaseDict['id']
        caseUid = dnaCaseDict['uid'] 
        caseType = dnaCaseDict['caseType'] 
        analysisInputDict = CaseService.getAnalysisInput(caseId, baseUrl)
        kinshipGraph = CaseService.buildGraph(caseId,caseType,profilesDict,subjects)
        analysisId = CaseService.saveAnalysisInput(baseUrl,caseId, caseUid, analysisInputDict, kinshipGraph)
        #CaseService.creatPedigreeTreeImageForCase(baseUrl, caseId, analysisId)
        analysisResultsDict = CaseService.calculate(baseUrl, caseId, analysisId);
        analysisResults = json.dumps(analysisResultsDict)
        CaseService.saveAnalysisResults(baseUrl, caseId, analysisId, analysisResults)
        encodedString = CaseService.getEncodedStringGorImage(baseUrl,dnaCaseDict['caseType'],subjects)
        CaseService.creatPedigreeTreeImageForCase(baseUrl,analysisId,encodedString,'414','919','ScriptedQuickKinshipModel')   
        return analysisId
    
    @staticmethod    
    def creatPedigreeTreeImageForCase(baseUrl,analysisID,decodeString,height,width,modelName):    
        CaseService.logService('creatPedigreeTreeImageForCase' )
        addSubjectUrl = baseUrl+'/kinship/kinship/saveSessionImage/'+str(analysisID)
        kinshipImageModelDict = {'decodeString':decodeString, 'height':height,'width':width, 'modelName':modelName} 
        kinshipImageModel = json.dumps(kinshipImageModelDict)
        return GateWayService.callConverge(addSubjectUrl,'true', kinshipImageModel)
            
    @staticmethod
    def getEncodedStringGorImage(baseUrl,caseType,subjects):
        isFemale = 'false'
        for id, subject in subjects.items():
            relationship = subject['relationship']
            gender =  subject['gender']
            if( relationship == RelationshipEnum.Relationship.child.value):
                if(gender == 'F'):
                    isFemale = 'true'
                
        data = CaseService.getPedigreeTreeXml(baseUrl, caseType)
        data = re.sub('/\\"/g', '"', data)
        data = re.sub('/^"(.*)"$/', '$1', data)
        root = et.fromstring(data)
        
        #print(isFemale)
        #if(isFemale == 'true'):
            #for image in root.findall('.//image[@relation="Child"][@src="/ui/img/male.png"]'):
                #print (image.attrib)
        #else:
            #for image in root.findall('.//image[@relation="Child"][@src="/ui/img/female.png"]'):
                #print (image.attrib)
                
        if(isFemale == 'true'):
            for image in root.findall('.//image[@relation="Child"][@src="/ui/img/male.png"]'):
                root.remove(image)
        else:   
            for image in root.findall('.//image[@relation="Child"][@src="/ui/img/female.png"]'):
                root.remove(image)
                            
        for image in root.findall('image'):
            for name, value in image.attrib.items():
                if(name == 'src'):
                    value =  baseUrl + value
                    image.attrib['src'] =value
                      
        

                            
        xmlstr = et.tostring(root)   
        #print( xmlstr)
        encodedString= urllib.parse.quote(xmlstr)
        #print(encodedString)
        return  encodedString
    
    @staticmethod 
    def saveAnalysisInput(baseUrl,caseId, caseUid,analysisInputDict,kinshipGraph): 
        analysisInputDict['graph'] = kinshipGraph['graph']
        analysisInputDict['warnings']=[]
        analysisInputDict['caseUid']=caseUid
        analysisInput = json.dumps(analysisInputDict)
        return  CaseService.postAnalysisInput(caseId, baseUrl,analysisInput)
    @staticmethod 
    def buildProsecutionVertex(containerId , subjectId , profileId , gender , relationShip, kinshipGraph):
        vertex = {'id':kinshipGraph['seqId'] ,'containerId':containerId,'gender':gender, 'subjectId':subjectId, 'profileId': profileId}
        kinshipGraph['graph']['vertices'].append(vertex)
        if(relationShip == 'Mother'):
            kinshipGraph['motherNodeId'] = kinshipGraph['seqId']
        elif(relationShip == 'Father'):
            kinshipGraph['fatherNodeId'] = kinshipGraph['seqId']
        elif(relationShip == 'Child'):
            kinshipGraph['childNodeId'] = kinshipGraph['seqId']
        kinshipGraph['seqId'] = kinshipGraph['seqId'] + 1
    
    @staticmethod 
    def buildDefenceVertex(containerId ,subjectId , profileId , gender , relationShip,  kinshipGraph):
        vertex = {'id':kinshipGraph['seqId'] ,'containerId':containerId,'gender':gender, 'subjectId':subjectId, 'profileId': profileId}  
        kinshipGraph['graph']['vertices'].append(vertex)
        #print(relationShip)
        if(relationShip == 'Mother'):
            kinshipGraph['defMotherNodeId'] = kinshipGraph['seqId']
        elif(relationShip == 'Father'):
            kinshipGraph['defFatherNodeId'] = kinshipGraph['seqId']
        elif(relationShip == 'Biological Father'):
            kinshipGraph['defFatherNodeId'] = kinshipGraph['seqId']    
        elif(relationShip =='Child'):
            kinshipGraph['defChildNodeId'] = kinshipGraph['seqId']
        elif(relationShip =='FUntyped'):
            kinshipGraph['untypedFatherNodeId' ]= kinshipGraph['seqId']
        elif(relationShip == 'MUntyped'):
            kinshipGraph['untypedMotherNodeId'] = kinshipGraph['seqId']
        kinshipGraph['seqId'] = kinshipGraph['seqId'] + 1;

        
    @staticmethod 
    def buildEdge(containerId , sourceId ,targetId, type,   kinshipGraph):
        edge = {'id':kinshipGraph['seqId'], 'containerId':containerId, 'sourceId': sourceId, 'targetId': targetId}  
        kinshipGraph['graph']['edges'].append(edge)
        if(type != 'Vertex'):
            if(containerId == 2):
                kinshipGraph['prosVertexId'] = kinshipGraph['seqId']
            elif(containerId == 3):
                kinshipGraph['defVertexId'] = kinshipGraph['seqId'];
        kinshipGraph['seqId'] = kinshipGraph['seqId'] + 1;
        
     
    # Master data related   API  
    
    @staticmethod    
    def deleteDictionaryEntries(id, baseUrl ):
        CaseService.logService('getDictionaryEntries' )
        getDictUrl = baseUrl+'/platform/common/dictionary/'+str(id)
        return GateWayService.callConvergeRestApi(getDictUrl, 'DELETE', '')
    
    @staticmethod    
    def getDictionaryEntries(category, baseUrl ):
        CaseService.logService('getDictionaryEntries' )
        getDictUrl = baseUrl+'/platform/common/dictionary/entries?category='+category
        return GateWayService.callConverge(getDictUrl, 'false', '')
    
    @staticmethod    
    def saveDictionaryEntries(baseUrl, dictionaryEntry ):
        CaseService.logService('saveDictionaryEntries' )
        getDictUrl = baseUrl+'/platform/common/dictionary/'
        return GateWayService.callConverge(getDictUrl, 'true', dictionaryEntry)
    
    @staticmethod    
    def getDictionaryEntriesWithParent(category, parentCategory, baseUrl ):
        CaseService.logService('getDictionaryEntriesWithParent' )
        getDictUrl = baseUrl+'/platform/common/dictionary/entries?category='+category+'&parent='+parentCategory
        return GateWayService.callConverge(getDictUrl,'false', '')
   
    @staticmethod    
    def getAllKits(baseUrl):
        CaseService.logService('getAllKits' )
        getDictUrl = baseUrl+'/platform/profile/kit/getAllKits'
        return GateWayService.callConverge(getDictUrl,'false', '')
    
    @staticmethod    
    def getAllMasterData(baseUrl):
        CaseService.logService('getAllMasterData' )
        getDictUrl = baseUrl+'/kinship/kinshipAdmin/masterDataWithEthnicity'
        return GateWayService.callConverge(getDictUrl,'false', '')
    
    @staticmethod    
    def getDefaultMasterData(baseUrl):
        CaseService.logService('getDefaultMasterData' )
        getDictUrl = baseUrl+'/platform/common/dictionary/MasDat'
        return GateWayService.callConverge(getDictUrl,'false', '')
    
    @staticmethod 
    def getAllEthinicity(masterDataName, baseUrl):
        CaseService.logService('getAllEthinicity' )
        getEthinictyUrl = baseUrl+'/kinship/kinshipAdmin/getEthnicityForSubject/'+masterDataName
        return GateWayService.callConverge(getEthinictyUrl,'false', '')
    
    @staticmethod 
    def getAllCaseTypes(baseUrl):
        CaseService.logService('getAllEthinicity' )
        getCaseTypeurl = baseUrl+'/platform/common/dictionary/entries?category=CaseType'
        return GateWayService.callConverge(getCaseTypeurl,'false', '')
    
    
    @staticmethod
    def logService(methodName):
        print ( 'In method ' + methodName)
        logging.info('In method ' + methodName)
    
