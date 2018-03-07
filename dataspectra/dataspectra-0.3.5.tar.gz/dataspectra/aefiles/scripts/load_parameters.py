#!/usr/bin/env python2.7

'''
 This is where to keep all the commands and variables to be set on instance start. 
'''
import lib.cloudstorage as gcs
import load_funcs as LF
import jinja2
from google.appengine.ext import ndb
import os

#Load json data
siteJsonData = LF.json_load_byteified(open("static/site.json"))


#Set for local testing
os.environ['SERVER_SOFTWARE'] = 'Development (remote_api)/1.0'  #ONLY FOR TESTING

#Set parameters for google cloud storage
gcs.set_default_retry_params(gcs.RetryParams(initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=20, max_retries=1000))

#Set up templating info
JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader("web/templates"),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True)

#Load dataset info and create their models
datasets = LF.json_load_byteified(open("static/datasets.json"))
#Dynamically create list of models for each dataset
datasetModelDict = dict()
for datasetParam in datasets.values():
    datasetModel = type(
        datasetParam["datasetkey"], 
        (ndb.Model,), 
        dict(
            searchTerm=ndb.StringProperty(),
            data=ndb.StringProperty(repeated=True, indexed=False)
            )
        )
    datasetModelDict[datasetParam["datasetkey"]] = datasetModel

searchlookupDict = LF.json_load_byteified(open("static/search_lookup.json"))

#Create model for search lookup for each type of searchlookupdict
searchlookupDict["datastoremodel"] = type(
    "searchterm",
    (ndb.Model,),
    dict(
        searchTerm = ndb.StringProperty(),
        data = ndb.StringProperty(repeated=True, indexed=False)
        )
    )