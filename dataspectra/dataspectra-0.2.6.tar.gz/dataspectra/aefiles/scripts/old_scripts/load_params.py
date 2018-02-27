#!/usr/bin/env python2.7

'''

TO DO:  
    - Update this so that we just read in a new page for each dataset. 
    - This way, it'll be a simpler read procedure. 
    -   

FUNCTION Reads in param file
PARAM FILE CONTENTS:
    NAMEOFSITE
    LINKTOHOME
    SETKEY: 1
    IMAGEDIR: Directory of images
    GENELISTFILE: Path to list of gene names
    SETNAMELONG:
    BUTTONNAME:
    CITATION:
    SEARCHTYPE:
    INFO:
    SETKEY: 2
    IMAGEDIR:
    GENELISTFILE
    SETNAMELONG:
    BUTTONNAME:
    CITATION:
    INFO:

FAQ: 
#Why not do rows and columns?
    - This can create a pretty long file. 
    - I guess that'll be fine too...
    - We should think about it. 

 i = i.decode('latin-1').rstrip().split("\t")
     
'''

import dataset_class
import file_manipulation as FM

def read_in_param_file_and_create_dataset_objects(self, paramFilePath):
    '''
    Creates separate objects for each dataset. Later we can put together the objects.  
    NOTES: Owner of this is site_generator Class
    '''

    fileIN = open(paramFilePath)
    paramMat = list()
    for i in fileIN:
        i =i.rstrip().split("\t")
        paramMat.append(i)
    fileIN.close()

    self.nameOfSite = [x[1] for x in paramMat if x[0]=="NAMEOFSITE"][0]
    self.labLink = [x[1] for x in paramMat if x[0]=="LABLINK"][0]
    self.labName = [x[1] for x in paramMat if x[0]=="LABNAME"][0]
    self.appId = [x[1] for x in paramMat if x[0]=="APPID"][0]
    self.defaultTerm = [x[1] for x in paramMat if x[0]=="DEFAULTTERM"][0]

    currentDataset = False
    flag = False
    for i in paramMat:
        if i[0]=="SETKEY":
            if currentDataset: self.datasets.append(currentDataset) #Append new if true
            currentDataset = dataset_class.Dataset()  #Create new datset.
            currentDataset.setKey = i[1]
            flag = True
        if flag:
            if i[0]=="IMAGEDIR": currentDataset.imageDir = i[1]
            elif i[0]=="GENELISTFILE": currentDataset.geneListFile = i[1]
            elif i[0]=="SEARCHTYPE": currentDataset.searchType = i[1]
            elif i[0]=="SETNAMELONG": currentDataset.setNameLong = i[1]
            elif i[0]=="BUTTONNAME": currentDataset.buttonName = i[1]
            elif i[0]=="CITATION": currentDataset.citation = i[1]
            elif i[0]=="CITATIONLINK": currentDataset.citationLink = i[1]
            elif i[0]=="INFO": currentDataset.info =i[1]
    if currentDataset: self.datasets.append(currentDataset) #Append new if true
            
            

