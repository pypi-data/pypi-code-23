import arrow
import requests
from django.conf import settings

def send_firebase_message(firebase_url, api_key, sender_id, device_token, title, message, sound = None):
    fb = FirebaseAPI(firebase_url =firebase_url, firebase_api_key = api_key, sender_id = sender_id)
    success, response = fb.quick_send_notification(device_token = device_token, title = title, text = message, sound = sound)
    return success, response
    
class FirebaseAPI(object):
    FIREBASE_URL = ''
    API_KEY = None
    SENDER_ID = None
    
    DEFAULT_SOUND = 'default' # a known firebase keyword for 'ding' sound
    
    
    def __init__(self, firebase_url = None, firebase_api_key = None, sender_id = None):
        self.firebase_url = firebase_url
        self.api_key = firebase_api_key
        self.sender_id = sender_id

        
        self.headers = {'Authorization' : 'key='+self.api_key, 'Content-Type' : 'application/json'}

        if self.api_key == None or self.sender_id == None or self.firebase_url == None:
            raise ValueError('Need proper firebase keys to send!')

        self.FIREBASE_URL = self.firebase_url
        self.API_KEY = self.api_key
        self.SENDER_ID = self.sender_id

    def quick_send_notification(self, device_token, title, text, sound = None):
        message = self.format_message(title = title, text = text, sound = None)
        payload = self.generate_payload(device_token = device_token, message = message, time_to_live = None, collapse_key = None)
        
        success, response = self.send_notification(payload = payload)
        return success, response


    def send_notification(self, payload):
        if type(payload) != dict or payload.get('to') == None or payload.get('notification') == None:
            raise ValueError('message must be dict with keys: to, notification')
        
        # actually sending the message
        response = requests.post(url = self.firebase_url, headers = self.headers, json = payload)  # send to Firebase
        
        # determine fail/success
        success = self.process_response(response = response)
        
        return success, response
    

    def process_response(self, response):
        
        response_json = response.json()  
        # typically valid:
        # {"multicast_id":5906667100243167686,"success":1,"failure":0,"canonical_ids":0,"results":[{"message_id":"0:1483586929366944%e4c7fee9e4c7fee9"}]}

        success = True
        if response_json['failure'] != 0:
            success = False
        
        return success


    def generate_payload(self, device_token, message, time_to_live = None, collapse_key = None):
        if time_to_live == None:
            time_to_live = 0 #Keep in mind that a time_to_live value of 0 means messages that can't be delivered immediately are discarded
        
        if collapse_key == None:
            collapse_key = "true" # if multiple messages are sent, before delivery, only one is shown.
            
        # the message should be a dict with body, title and sound
        if type(message) != dict or message.get('title') == None or message.get('body') == None:
            raise ValueError('message must be dict with keys: title, body, sound')
        
        payload = {
            "notification": message, # sets body, title, sound
            "to" : device_token,  # the GCM we are sending it to
            
            "time_to_live" : time_to_live, #Keep in mind that a time_to_live value of 0 means messages that can't be delivered immediately are discarded
            "collapse_key" : collapse_key, # if multiple messages are sent, before delivery, only one is shown.
            }
            
        return payload

    def format_message(self, title, text, sound = None):
        if sound == None:
            sound = self.DEFAULT_SOUND
            
        message = {
                    "body" : text,
                    "title" : title,
                    "sound" : sound, # we don't check if it is valid...but it defaults to : "default"
                    }
        return message
