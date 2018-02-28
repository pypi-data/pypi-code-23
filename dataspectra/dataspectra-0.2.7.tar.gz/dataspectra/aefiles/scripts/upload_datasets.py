#!/usr/bin/env python2.7

import webapp2
from google.appengine.ext import ndb
import load_funcs as LF
import os


'''
There are two types of data stored within the datastore. 
1. The genome wide data. 
2. The search term data.


'''

class LocalUploadDatastore(webapp2.RequestHandler):
    '''
    Dynamically creates each model separately
    '''
    def get(self):
        #Read in parameter data for all datasets
        datasets = LF.json_load_byteified(open("static/datasets.json")) 

        #Dynamically create list of models for each dataset
        numberOfDatasets = len(datasets)
        datasetModelDict = dict()
        for datasetParam in datasets.values():
            datasetModel = type(
                datasetParam["datasetkey"], 
                (ndb.Model,), 
                dict(
                    searchTerm=ndb.StringProperty(), 
                    data=ndb.StringProperty(repeated=True,indexed=False) 
                    )
                )
            datasetModelDict[datasetParam["datasetkey"]] = datasetModel

        #Load the data into local Datastore
        for datasetParam in datasets.values():
            datasetModel = datasetModelDict[datasetParam["datasetkey"]]
            datasetfile = os.path.join("static", datasetParam["samplefile"])
            searchcol = int(datasetParam["searchcol"])
            with open(datasetfile) as F:
                for i in range(int(datasetParam["searchrowstart"])):
                    F.readline() #Skip the ones that aren't involved in search. 
                for i in F:
                    i =i.rstrip().split(",")
                    newEntity = datasetModel(searchTerm=i[searchcol-1], data = i)
                    k = newEntity.put()
      
        #Create the search lookup Model
        searchLookupDict = LF.json_load_byteified(open("static/search_lookup.json")) 
        searchTermModel = type(
            "searchterm",
            (ndb.Model,),
            dict(
                searchTerm = ndb.StringProperty(),
                data = ndb.StringProperty(repeated=True, indexed=False)
                )
            )
        
        #Load the data from the search lookup file
        searchlookupfile = os.path.join("static", searchLookupDict["samplefile"] )
        with open(searchlookupfile) as F:
            for i in F:
                i =i.rstrip().split(",")
                newEntity = searchTermModel(searchTerm = i[0], data = i)
                k = newEntity.put()





#class LocalUploadDatastore(webapp2.RequestHandler):
#    def upload(self):
#        '''
#        #To determine what to upload.
#        - We need a list of datasets.
#        - We can get a list of datasets in the initial specification.
#
#
#        #
#        '''
#        datasetFile, key, datadir="row"
#        searchQuery = WMTL.SearchResult.query(WMTL.SearchResult.keyName == row[0])
#                matches = searchQuery.fetch()
#                #If multiple matches - then delete all but one and add.
#                if len(matches)>1:
#                    for i in matches[1:]:
#                        i.key.delete()
#                    matches[0].locationTabbed = "\t".join(row[1:])
#                    matches[0].urlsTabbed = "NA"
#                    entities.append(matches[0])
#                elif len(matches)==1:
#                    matches[0].locationTabbed = "\t".join(row[1:])
#                    matches[0].urlsTabbed="NA"
#                    entities.append(matches[0])
#                else:
#                    newProd = WMTL.SearchResult(parent = None, keyName=row[0],  locationTabbed  = "\t".join(row[1:]), urlsTabbed = "NA")
#                    entities.append(newProd)
#
#                newProd = WMTL.SearchResult(parent = None, keyName=row[0],  locationTabbed  = "\t".join(row[1:]), urlsTabbed = "NA")
#                entities.append(newProd)
#                if count%50==0 and entities:
#                    ndb.put_multi(entities)
#                    entities = []
#        if entities:
#            ndb.put_multi(entities)
#        gcs_file.close()
#
#
#
