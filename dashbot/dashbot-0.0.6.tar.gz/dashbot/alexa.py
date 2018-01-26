import os
import sys
import os.path
import datetime
import time
import json


import generic

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import version

class alexa(generic.DashBotGeneric):
        
    def __init__(self,apiKey,debug=False,printErrors=False):
        
        if 'DASHBOT_SERVER_ROOT' in os.environ:
            serverRoot = os.environ['DASHBOT_SERVER_ROOT']
        else:
            serverRoot = 'https://tracker.dashbot.io'        
        self.urlRoot = serverRoot + '/track'        
        self.apiKey=apiKey
        self.debug=debug
        self.printErrors=printErrors
        self.platform='alexa'
        self.version = version.__version__
        self.source = 'pip'        
        
    def logIncoming(self,event):
        url = self.urlRoot + '?apiKey=' + self.apiKey + '&type=incoming&platform='+ self.platform + '&v=' + self.version + '-' + self.source
        
        if self.debug:
            print('Dashbot Incoming:'+url)
            print(json.dumps(event))
            
        now = datetime.datetime.now()
        timestamp = time.mktime(now.timetuple()) + now.microsecond * 1e-6
        
        data={
            'dashbot_timestamp':timestamp,
            'event':event,
            }
            
        self.makeRequest(url,'POST',data)
            
    def logOutgoing(self,event,response):
        url = self.urlRoot + '?apiKey=' + self.apiKey + '&type=outgoing&platform='+ self.platform + '&v=' + self.version + '-' + self.source
        
        if self.debug:
            print('Dashbot Outgoing:'+url)
            print(json.dumps(event))
            
        now = datetime.datetime.now()
        timestamp = time.mktime(now.timetuple()) + now.microsecond * 1e-6
        
        data={
            'dashbot_timestamp':timestamp,            
            'event':event,
            'response':response            
        }
        
        self.makeRequest(url,'POST',data)