import sys
import requests
import json
import traceback
import os
import logging

import generic

class alexa(generic.DashBotGeneric):
        
    def logIncoming(self,event):
        url = self.urlRoot + '?apiKey=' + self.apiKey + '&type=incoming&platform='+ self.platform + '&v=' + self.version + '-' + self.source
        
        if self.debug:
            print('Dashbot Incoming:'+url)
            print(json.dumps(event))
            
        data={
            'event':event,
            }
            
        self.makeRequest(url,'POST',data)
            
    def logOutgoing(self,event,response):
        url = self.urlRoot + '?apiKey=' + self.apiKey + '&type=outgoing&platform='+ self.platform + '&v=' + self.version + '-' + self.source
        
        if self.debug:
            print('Dashbot Incoming:'+url)
            print(json.dumps(event))
            
        data={
            'event':event,
            'response':response            
        }
        
        self.makeRequest(url,'POST',data)    