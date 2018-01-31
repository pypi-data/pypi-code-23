import os
import sys
import os.path
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
try:
    import version
except:
    from . import version
try:
    import alexa
except:
    from . import alexa

class alexa_vl(alexa.alexa):
    
    def __init__(self,apiKey=None,debug=False,printErrors=False):
        
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
        self.source = 'pip_vl'
    
    #vl initialize     
    def initialize(self,apiKey,session): 
        self.apiKey=apiKey
        self.session=session
        
    #vl track    
    def track(self,intent_name,intent_request,response):
        event = self.regenerateEvent(intent_request)
        self.logIncoming(event)
        self.logOutgoing(event,response)
        
    #vl helper
    def regenerateEvent(self,intent_request):
        event = {
            'session': self.session,
            'request':intent_request,
            'context':{
                'System':{
                    'application':self.session['application'],
                    'user':self.session['user']
                }
            }
        }
        return event
    
    #vl helper
    def generateResponse(self,speechText):
        if speechText[0:7]=='<speak>':
            return {
                'response':{
                    'outputSpeech':{
                        'type':'SSML',
                        'ssml': speechText
                    }
                }       
            }
        else:
            return {
                'response':{
                    'outputSpeech':{
                        'type':'Plaintext',
                        'text':speechText
                    }
                }
            }
