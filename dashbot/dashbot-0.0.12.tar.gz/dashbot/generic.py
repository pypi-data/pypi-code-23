from __future__ import print_function
import os
import sys
import requests
import os.path
import logging
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    import version
except:
    from . import version

class generic():
    
    def __init__(self,apiKey,debug=False,printErrors=False):
        
        if 'DASHBOT_SERVER_ROOT' in os.environ:
            serverRoot = os.environ['DASHBOT_SERVER_ROOT']
        else:
            serverRoot = 'https://tracker.dashbot.io'        
        self.urlRoot = serverRoot + '/track'        
        self.apiKey=apiKey
        self.debug=debug
        self.printErrors=printErrors
        self.platform='generic'
        self.version = version.__version__
        self.source = 'pip'
        
    def getBasestring(self):
        if (sys.version_info > (3, 0)):
            return (str, bytes)
        else:
            return basestring        

    def makeRequest(self,url,method,json):
        try:
            if method=='GET':
                r = requests.get(url, params=json)
            elif method=='POST':
                r = requests.post(url, json=json)
            else:
                print('Error in makeRequest, unsupported method')
            if self.debug:
                print('dashbot response')
                print (r.text)
            if r.status_code!=200:
                logging.error("ERROR: occurred sending data. Non 200 response from server:"+str(r.status_code))
        except ValueError as e:
            logging.error("ERROR: occurred sending data. Exception:",str(e))
            
    def logIncoming(self,data):
        url = self.urlRoot + '?apiKey=' + self.apiKey + '&type=incoming&platform='+ self.platform + '&v=' + self.version + '-' + self.source
                                  
        try:
            data = json.loads(data)
        except Exception as e:
            if self.debug:
                print(e)       
                                            
        if self.debug:
            print('Dashbot Incoming:'+url)
            print(json.dumps(data))
     
        self.makeRequest(url,'POST',data)
            
    def logOutgoing(self,data):
        url = self.urlRoot + '?apiKey=' + self.apiKey + '&type=outgoing&platform='+ self.platform + '&v=' + self.version + '-' + self.source
                    
        try:
            data = json.loads(data)
        except Exception as e:
            if self.debug:
                print(e)                        
                    
        if self.debug:
            print('Dashbot Outgoing:'+url)
            print(json.dumps(data))
                    
        self.makeRequest(url,'POST',data)            