import requests

from blueforge.apis.facebook.attachments import *
from blueforge.apis.facebook.buttons import *
from blueforge.apis.facebook.elements import *
from blueforge.apis.facebook.message import *
from blueforge.apis.facebook.quick_reply import *
from blueforge.apis.facebook.template import *


class FacebookMessageException(Exception):
    pass


class CreateFacebookApiClient(object):
    def __init__(self, access_token):
        self.access_token = access_token

    async def send_message(self, message):
        req = requests.post(url='https://graph.facebook.com/v2.6/me/messages?access_token=%s' % self.access_token,
                            data=json.dumps(message.get_data()),
                            headers={'Content-Type': 'application/json'},
                            timeout=30)

        return req.json()

    async def __send_action(self, recipient_id, action):
        return await self.send_message(RequestDataFormat(recipient=recipient_id, sender_action=action))

    async def set_typing_on(self, recipient_id):
        return await self.__send_action(recipient_id, 'typing_on')

    async def set_typing_off(self, recipient_id):
        return await self.__send_action(recipient_id, 'typing_off')

    async def set_mark_seen(self, recipient_id):
        return await self.__send_action(recipient_id, 'mark_seen')
