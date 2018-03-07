#!/usr/bin/env python2.7

from google.appengine.ext import ndb
import os

def extract_data_for_term(searchTerm, datasetsDict, searchLookupDict):
    '''

    Step 1: Gets the search term for each dataset. 
    Step 2: Matches the resulting search terms for each 
    
    OUTPUT:
        datasetkey: [     ]

    #DatasetsDict - stores the search term model for each dataset. 
    #

    NOTES:
        - To do: implement asynchronous calls

    The querying process is using the NDB client datastore. 
    -Description is found in Google App Engine Python Standard Environment Documentation. 
    -Note that this is different from the Datastore API - which does not automatically connect with app engine. 

    '''
    
    #Lookup the search term for each dataset. 
    slmodel = searchLookupDict["datastoremodel"]
    query = slmodel.query(slmodel.searchTerm == unicode(searchTerm))
    result = query.fetch(1)
    columns = searchLookupDict["columns"] 
    if len(result)==0:
        datasetkeyTermDict = {datasetkey:searchTerm for i, datasetkey in enumerate(columns)}
    else:    
        result = result[0]
        datasetkeyTermDict = {datasetkey:result.data[i+2] for i, datasetkey in enumerate(columns)} #adding one because the species column and one because of the search term

    #Lookup the values for each dataset using the search terms
    outDict = dict()
    for datasetKey in datasetsDict.keys():
        if datasetKey not in datasetkeyTermDict: continue
        datasetSearchTerm = unicode(datasetkeyTermDict[datasetKey])
        query = datasetsDict[datasetKey].query(datasetsDict[datasetKey].searchTerm == datasetSearchTerm)
        result = query.fetch(1)
        if len(result)==0:
            outDict[datasetKey] = None
        else:
            outDict[datasetKey] = result[0].data
    return outDict

def extract_data_for_term_and_dataset(searchTerm, datasetsDict, datasetKey):
    query = datasetsDict[datasetKey].query(datasetsDict[datasetKey].searchTerm == searchTerm)
    result = query.fetch(1)
    if len(result)==0:
        return None
    else:
        return result[0].data
