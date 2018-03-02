#!/usr/bin/env python2.7

import os
import json
import base64
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.api import app_identity
import lib.cloudstorage as gcs

#os.environ['SERVER_SOFTWARE'] = 'Development (remote_api)/1.0'  #ONLY FOR TESTING

def basicAuth(func):
  def callf(webappRequest, *args, **kwargs):
    # Parse the header to extract a user/password combo.
    # We're expecting something like "Basic XZxgZRTpbjpvcGVuIHYlc4FkZQ=="
    auth_header = webappRequest.request.headers.get('Authorization')

    if auth_header == None:
      webappRequest.response.set_status(401, message="Authorization Required")
      webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="Unsecure Area"'
    else:
      # Isolate the encoded user/passwd and decode it
      auth_parts = auth_header.split(' ')
      user_pass_parts = base64.b64decode(auth_parts[1]).split(':')
      user_arg = user_pass_parts[0]
      pass_arg = user_pass_parts[1]

      if user_arg != "guest" or pass_arg != "barres":
        webappRequest.response.set_status(401, message="Authorization Required")
        webappRequest.response.headers['WWW-Authenticate'] = 'Basic realm="Secure Area"'
      else:
        return func(webappRequest, *args, **kwargs)
  return callf



def _byteify(data, ignore_dicts = False):
    '''
    DESCRIPTION:  
    - https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json

    '''
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data



# [START] SearchResult
class SearchResult(ndb.Model):
    '''
    DESCRIPTION: 
        - This is a class for the noSQL database use to store the locations of the images

    '''
    keyName = ndb.StringProperty()
    locationTabbed = ndb.StringProperty()
    urlsTabbed = ndb.StringProperty()
# [END] SearchResult

def get_bucketName():
    appId = app_identity.get_application_id()
    bucketName =   appId + ".appspot.com"
    return bucketName

def get_web_content():
    '''
    Edit this

    '''


def get_web_content(queryTerm, setkey,  showImage = "NA"):
    
    nameOfSite = json_data[0]["nameOfSite"]
    labLink = json_data[0]["labLink"]
    labName = json_data[0]["labName"]


    template_values = {
        'nameOfSite': nameOfSite,
        'labLink': labLink,
        'labName': labName,
    }
    #
    

    if queryTerm == "NA": 
        queryTerm = json_data[0]["defaultTerm"]

    #LOAD UP META DATA#
    if queryTerm != "NA":
        ### Load up images ### 
        # Look up query term in datastore #
        searchQuery = SearchResult.query(SearchResult.keyName == queryTerm)
        match = searchQuery.fetch(1)
        
        if len(match)==0:
            return {}
        else:
            match = searchQuery.fetch(1)[0]
        imageLocations = match.locationTabbed.rstrip().split("\t")
        #If term is in datastore and there is no urls. Then get_serving_urls. 
        if match.urlsTabbed=="NA":
            urls = [images.get_serving_url(None, filename="/gs/" + get_bucketName() + "/" + x) for x in imageLocations]
            match.urlsTabbed = "\t".join(urls)
            match.put()
        else:
            urls = match.urlsTabbed.rstrip().split("\t")

        datasetList = [[json.dumps(json_data[idx+1]), urls[idx] + "=s0", json_data[idx+1]["setKey"]] for idx, x  in enumerate(imageLocations) ] #idx+1 for the json_data because the first index is reserved for metadata.
        
        if setkey == "NA":  
            #Choose as the first path the first one that is not NA that is also not gene name
            firstPath = [ x[1] for x in datasetList if x[1]!="NA"][0]
        else:
            firstPath = [ x[1] for x in datasetList if x[2]==setkey][0]
        #Finish adding the template values
        template_values["searchTerm"] = queryTerm
        template_values["datasetList"] = datasetList
        template_values["firstPath"] = firstPath
        template_values["setkey"]  = setkey
    return template_values

# [END] 





