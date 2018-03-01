
import requests

def send_slack_message(api_key, text, send_as= None, user_list = None, channel = None):
    slack = SlackAPI(api_key = api_key)
    success, response = slack.quick_send_notification(text, send_as= send_as, user_list = user_list, channel = channel)
    
    return success, response
    
class SlackAPI(object):
    SLACK_POST_MESSAGE_URL = "https://slack.com/api/chat.postMessage"
    
    DEFAULT_CHANNEL = 'hal9000'
    
    def __init__(self, api_key):
        self.api_key = api_key
        
        if self.api_key == None:
            raise ValueError('please provide valid api key')

    def quick_send_notification(self, text, send_as= None, user_list = None, channel = None):
        payload = self.generate_payload(text = text, send_as = send_as)
        
        success, response = self.send_notification(payload = payload, user_list = user_list, channel = channel)
        
        return success, response
        
    def send_notification(self, payload, user_list=None, channel=None):
        
        if user_list is None and channel is None:
            channel = 'hal9000'
            payload['text'] += ' Please specify a proper channel or user to send this to.'
        
        if user_list:
            response = self._send_to_users(users = user_list, payload = payload)
            
        if channel:
            response = self._send_to_channel(channel = channel, payload = payload)

        success = self.process_response(response)
        return success, response
    
    def process_response(self, response):
        success = False
        if response.status_code == 200:
            success = True
            
            
        return success
    
    
    def _send_to_users(self, users, payload):
        for user in users:
            print('check me')
            payload.update(channel="@"+user)
            response = requests.post(self.SLACK_POST_MESSAGE_URL, data=payload)
            
        return response
        
    def _send_to_channel(self, channel, payload):
        payload.update(channel=channel)
        response = requests.post(self.SLACK_POST_MESSAGE_URL, data=payload)
        return response
    
    
    def generate_payload(self, text, send_as = None):
        
        payload = dict(
            token=self.api_key,
            text=text,
            as_user=True
            )
        
        
        if send_as != None:
            payload['username'] = send_as
            payload['as_user'] = False
        return payload
        
def main():
    api_key = None
    
    user_list = ['ka']
    success, response = send_slack_message(api_key = api_key, text = 'test', send_as= None, user_list = user_list, channel = None)
    
    print(success, response)
    
    
if __name__ == '__main__':
    main()