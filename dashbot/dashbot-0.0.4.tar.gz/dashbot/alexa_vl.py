import sys
import requests
import json
import traceback
import os
import logging

import alexa

class alexa_vl(alexa.alexa):
    #vl initialize     
    def initialize(self,apiKey,session): 
        self.apiKey=apiKey
        self.session=session
        
    #vl track    
    def track(self,intent_name,intent_request,response):
        event = self.regenerateEvent(intent_name,intent_request['intent']['slots'])
        
        if isinstance(response, self.getBasestring()):
            speechText = response
        elif response is not None and 'response' in response and 'outputSpeech' in response.get('response',{}):
            speechObj = response['response']['outputSpeech']
            if 'type' in speechObj:
                if speechObj['type']=='SSML':
                    speechText=response['response']['outputSpeech']['ssml']
                elif speechObj['type']=='PlainText':
                    speechText=response['response']['outputSpeech']['text']
                
        responseGenerated = self.generateResponse(speechText)
        self.logIncoming(event)
        self.logOutgoing(event,responseGenerated)
        
    #vl helper
    def regenerateEvent(self,intent,slots):
        request = {
            'type':'intent',
            'intent': {
                'name':intent,
                'slots':slots
            }
        }
        event = {
            'session': self.session,
            'request':request,
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
