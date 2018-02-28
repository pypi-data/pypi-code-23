#!/usr/bin/env python2.7

import os
import webapp2
import jinja2
import lib.cloudstorage as gcs
from google.appengine.api import app_identity
from google.appengine.ext import ndb
from google.appengine.api import images

import web_module_to_load as WMTL
import talk_with_google as TWG

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(WMTL.template_dir),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True)

gcs.set_default_retry_params(gcs.RetryParams(initial_delay=0.1, max_delay=10.0, backoff_factor=2, max_retry_period=30.0,urlfetch_timeout=None, min_retries=3, max_retries=100))

chunksize = 100

# [START upload]
class Upload(webapp2.RequestHandler):
    '''
    FUNCTION:
    - Uploads data from the google cloud storage to the datastore.
    - We want to keep information in the datastore because it is easier to access as a database.
    - This class is a one time use class. Once it is used - it would be wise to disable the function.
    - Another option, would be to load this as a temporary function for the app.
    - where it is used to upload the created ndb data into datastore. Do not use more than once, or it might be expensive money wise. 

    NOTES: 
    QUESTION: Should we deploy first before running this?

    - Only run this in production. 
    - Upload the data by using the tag: /upload
    - Then disable the upload by changing the data.
    - We cannot load all the files while simultaneaously doing get_serving_url because the server will time out. 
    - We may encounter a local serving error: because it takes so much time to load.  can we even load everything in the file to the datastore too?
    - Let's hope so... If not, we'll have to split it up. 

    #Problem is that it takes too much time to do this for each sample.

    #Chunk it into groups:
        - Read 5,000 lines at a time. 
    #Create buttons

    '''
  

    def get(self):

        bucketName = WMTL.get_bucketName()
        filename = "/" + bucketName + '/search_lookup_file.txt'
        numlines = self.count_num_lines(filename)        
        numChunks =  numlines/chunksize +1
        chunkList = ["chunk" + str(x) for x in range(1,numChunks+1)]   
        self.response.write("Number of chunks: "+ str(numChunks) + "<br>")

        template_values = {
                "start": 0, 
                "chunkList": chunkList 
                }
     
        template = JINJA_ENVIRONMENT.get_template('upload_chunks2.html')
        self.response.write(template.render(template_values))

                #
#        self.upload_file(filename)
#        self.get_serving_urls_for_samples()
   #     self.upload_file_while_get_serving_url(filename, bucketName)
    
    def post(self):
        bucketName = WMTL.get_bucketName()
        filename = "/" + bucketName + '/search_lookup_file.txt'
        lastChunk = self.request.get('lastChunk')
        chunkList = self.request.get('chunkList').split("$")

        if lastChunk != chunkList[-1]:
            if lastChunk =="NA": 
                chunkToUpload = chunkList[0] 
            else:
                lastIndex = chunkList.index(lastChunk)
                chunkToUpload= chunkList[lastIndex+1]
            self.response.write("number of chunks: "  + str(len(chunkList)))
            self.response.write("<br> ")
            self.response.write("chunk uploaded: " + lastChunk) 
            self.response.write("<br> ") 
            self.response.write("chunk to upload: " + chunkToUpload) 
            self.response.write("<br> ") 
            
            template_values = { 
                    "start": 1,
                    "lastChunk": chunkToUpload,
                    "chunkList": chunkList
                }
            template = JINJA_ENVIRONMENT.get_template('upload_chunks2.html')
            self.response.write(template.render(template_values))
            self.upload_file_chunks(filename, int(chunkToUpload.split("chunk")[1]))
        else: #last element loaded. 
            self.response.write("all chunks loaded") 
            chunkToUpload = "NA"
            

#            self.upload_file_chunks(
        #get_chunk = queryIn.split("-")[0].strip()
        #chunkList = queryIn.split("-")[1].strip().split("$")
    
    def count_num_lines(self, filename):
        gcs_file = gcs.open(filename)
        count = 0
        entities = list()
        for row in gcs_file:
            count +=1
        gcs_file.close()
        return count

    def upload_file_chunks(self, filename, chunkNum):
        '''
        chunkNum ranges from 1 to X
        Problem is that this makes several queries.
        - what if we edited this - so that no queries are made. 
        - we can batch delete. - then batch upload.  

        '''
        self.response.write("uploading")
        gcs_file = gcs.open(filename)
        count = 0
        currentChunk = 1
        entities = list()
        for row in gcs_file:
            count +=1
            if count%chunksize==0: currentChunk +=1
            if currentChunk==chunkNum:
                row = row.split("\t")
                searchQuery = WMTL.SearchResult.query(WMTL.SearchResult.keyName == row[0])
                matches = searchQuery.fetch()
                #If multiple matches - then delete all but one and add. 
                if len(matches)>1:
                    for i in matches[1:]:
                        i.key.delete() 
                    matches[0].locationTabbed = "\t".join(row[1:])
                    matches[0].urlsTabbed = "NA"
                    entities.append(matches[0])
                elif len(matches)==1:
                    matches[0].locationTabbed = "\t".join(row[1:])
                    matches[0].urlsTabbed="NA"
                    entities.append(matches[0])
                else:
                    newProd = WMTL.SearchResult(parent = None, keyName=row[0],  locationTabbed  = "\t".join(row[1:]), urlsTabbed = "NA")
                    entities.append(newProd)
    
                newProd = WMTL.SearchResult(parent = None, keyName=row[0],  locationTabbed  = "\t".join(row[1:]), urlsTabbed = "NA")
                entities.append(newProd)
                if count%50==0 and entities:
                    ndb.put_multi(entities)
                    entities = []
        if entities:
            ndb.put_multi(entities)
        gcs_file.close()

        
    ### 
    def upload_file(self, filename):
        #Depracated##
        gcs_file = gcs.open(filename)
        count = 0
        entities = list()
        for row in gcs_file:
            count +=1
            
            row = row.split("\t")
            searchQuery = WMTL.SearchResult.query(WMTL.SearchResult.keyName == row[0])
            matches = searchQuery.fetch()
            #If multiple matches - then delete all but one and add. 
            if len(matches)>1:
                for i in matches[1:]:
                    i.key.delete() 
                matches[0].locationTabbed = "\t".join(row[1:])
                matches[0].urlsTabbed = "NA"
                entities.append(matches[0])
            elif len(matches)==1:
                matches[0].locationTabbed = "\t".join(row[1:])
                matches[0].urlsTabbed="NA"
                entities.append(matches[0])
            else:
                newProd = WMTL.SearchResult(parent = None, keyName=row[0],  locationTabbed  = "\t".join(row[1:]), urlsTabbed = "NA")
                entities.append(newProd)

            if count%50==0 and entities:
                ndb.put_multi(entities)
                entities = []
        if entities:
            ndb.put_multi(entities)
        gcs_file.close()


# [START] UploadForTesting 
class UploadForTesting(webapp2.RequestHandler):
    ''' 
    DESCRIPTION: Uploads data from google cloud storage to the datastore. 
    
    Note, for some reason, this stopped working...
    Looks like it is due to permission issues. 


    NOTES:
        - Use this for local development server
    '''
#    os.environ['SERVER_SOFTWARE'] = 'Development (remote_api)/1.0'  #Telling local_dev to use the production google cloud storage. . 
#This is working... so download file directly using gsutil 
    
    def get(self):
        #First copy the file to the current direcotry. 
        #using gsutil
        gcs_file = "datastore_sample.txt"
        fileIN = open(gcs_file)
        count = 0
        entities = list()
        for row in fileIN:
            row = row.rstrip()
            count +=1
            row = row.split("$$$")
            newProd = WMTL.SearchResult(parent = None, keyName=row[0],  locationTabbed  = row[1], urlsTabbed = row[2])
            entities.append(newProd)
            if count%1000==0 and entities:
                ndb.put_multi(entities)
                entities = []
        if entities:
            ndb.put_multi(entities)
        fileIN.close()


#        bucketName = WMTL.get_bucketName() 
#        filename = "/" + bucketName + '/datastore_sample.txt'
#        gcs_file = gcs.open(filename)
#        count = 0
#        entities = list()
        
#        for row in gcs_file:
#            count +=1
#            row = row.split("$$$")
#            newProd = WMTL.SearchResult(parent = None, keyName=row[0],  locationTabbed  = row[1], urlsTabbed = row[2])
#            entities.append(newProd)
#            if count%1000==0 and entities:
#                ndb.put_multi(entities)
#                entities = []
#        if entities:
#            ndb.put_multi(entities)
#        gcs_file.close()
# [END] UploadForTesting


class Get_Serving_Urls_For_Sample(webapp2.RequestHandler):
    #[START] get_serving_ursl_for_samples()
    def get(self):
        '''
        Takes a sub sample - and gets serving urls. 
        '''
        searchQuery = WMTL.SearchResult.query()
        searchQuery.order(WMTL.SearchResult.keyName)
        matches = searchQuery.fetch(10)
        for match in matches:
            imageLocations = match.locationTabbed.rstrip().split("\t")
            self.response.write(imageLocations)
#            urls = [images.get_serving_url(None, filename="/gs/" + WMTL.get_bucketName() + "/" + x) for x in imageLocations]
#            match.urlsTabbed = "\t".join(urls)
#            match.put()


class TransferToStorage(webapp2.RequestHandler):
    '''
    DESCRIPTION: Transfers the search query values from datastore to storage. 
    
    NOTES:
        - For use on production server.
        - Use as part of testing pipeline, so that the local dev_server can access. 
        - Transfers only the files with the url tab intact.
    
    TODO:
        - We can do this at the same time as uploads, but this may be better, in case we want to transfer later
    '''
    def get(self):
        bucketName = WMTL.get_bucketName()
        filename = "/" + bucketName + '/datastore_sample.txt'
        gcs_file = gcs.open(filename, "w")
        searchQuery = WMTL.SearchResult.query(WMTL.SearchResult.urlsTabbed!="NA")
        matches = searchQuery.fetch()
        for match in matches:
            #Write the data? 
            outUnicode = match.keyName + "$$$" + match.locationTabbed.rstrip() + "$$$" + match.urlsTabbed.rstrip() + "\n"
            gcs_file.write(outUnicode.encode("utf-8"))
        gcs_file.close()
# [END} TransferToSTorage
