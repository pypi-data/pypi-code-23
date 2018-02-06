import os
import sys
import os.path
import datetime
import time
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    import version
except:
    from . import version
try:
    import generic
except:
    from . import generic

class google(generic.generic):
        
    def __init__(self,apiKey,debug=False,printErrors=False):
        
        if 'DASHBOT_SERVER_ROOT' in os.environ:
            serverRoot = os.environ['DASHBOT_SERVER_ROOT']
        else:
            serverRoot = 'https://tracker.dashbot.io'        
        self.urlRoot = serverRoot + '/track'        
        self.apiKey=apiKey
        self.debug=debug
        self.printErrors=printErrors
        self.platform='google'
        self.version = version.__version__
        self.source = 'pip'        
        
    def logIncoming(self,event):
        url = self.urlRoot + '?apiKey=' + self.apiKey + '&type=incoming&platform='+ self.platform + '&v=' + self.version + '-' + self.source
                    
        now = datetime.datetime.now()
        timestamp = int(1000*(time.mktime(now.timetuple()) + now.microsecond * 1e-6))
        
        try:
            event = json.loads(event)
        except Exception as e:
            if self.debug:
                print(e)            
        
        data={
            'dashbot_timestamp':timestamp,
            'request_body':event,
            }
        
        if self.debug:
            print('Dashbot Incoming:'+url)
            print(json.dumps(data))
            
        self.makeRequest(url,'POST',data)
            
    def logOutgoing(self,event,response,metadata=None):
        url = self.urlRoot + '?apiKey=' + self.apiKey + '&type=outgoing&platform='+ self.platform + '&v=' + self.version + '-' + self.source
                    
        now = datetime.datetime.now()
        timestamp = int(1000*(time.mktime(now.timetuple()) + now.microsecond * 1e-6))
        
        try:
            event = json.loads(event)
        except Exception as e:
            if self.debug:
                print(e)           
 
        try:
            response = json.loads(response)
        except Exception as e:
            if self.debug:
                print(e)      
                
        data={
            'dashbot_timestamp':timestamp,            
            'request_body':event,
            'message':response            
        }
        if metadata is not None:
            data['metadata']=metadata
        
        if self.debug:
            print('Dashbot Outgoing:'+url)
            print(json.dumps(data))
                    
        self.makeRequest(url,'POST',data)