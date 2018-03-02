import json
import logging

import requests

from blueforge.util.trans import detect_none_value

logger = logging.getLogger(__name__)


# TODO: 향후 Messenger.__str__()를 할 시 메시지 data를 생성할 수 있도록 변경함
class Messenger(object):
    def __init__(self, access_token):
        self.__access_token = access_token

    def __send_message(self, message):
        req = requests.post(url='https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(self.access_token),
                            data=json.dumps(message),
                            headers={'Content-Type': 'application/json'})
        logger.debug(req.json())
        return req.content

    def __send_action(self, recipient_id, action):
        message_data = {
            "recipient": {
                "id": recipient_id
            },
            "sender_action": action
        }
        logger.debug("make_mark:: %s" % message_data)
        self.__send_message(message_data)

    def set_typing_on(self, recipient_id):
        return self.__send_action(recipient_id, 'typing_on')

    def set_typing_off(self, recipient_id):
        return self.__send_action(recipient_id, 'typing_off')

    def set_mark_seen(self, recipient_id):
        return self.__send_action(recipient_id, 'mark_seen')

    def send_message(self, recipient_id, message):
        final_message = {
            "recipient": recipient_id,
            "message": message
        }

        self.__send_message(detect_none_value(final_message))

    @staticmethod
    def make_quick_reply(content_type=None, title=None, image_url=None, payload=None):
        reply = {
            "content_type": content_type,
            "title": title,
            "image_url": image_url,
            "payload": payload
        }
        return detect_none_value(reply)

    @staticmethod
    def make_url_button(url=None, title=None, webview_height_ratio=None, messenger_extensions=False,
                        fallback_url=None):
        reply = {
            "type": "web_url",
            "url": url,
            "title": title,
            "webview_height_ratio": webview_height_ratio,
            "messenger_extensions": messenger_extensions,
            "fallback_url": fallback_url
        }
        return detect_none_value(reply)

    @staticmethod
    def make_postback_button(title=None, payload=None):
        reply = {
            "type": "postback",
            "title": title,
            "payload": payload
        }
        return detect_none_value(reply)

    @staticmethod
    def make_phone_number_button(title=None, payload=None):
        reply = {
            "type": "phone_number",
            "title": title,
            "payload": payload
        }
        return detect_none_value(reply)

    @staticmethod
    def make_share_button(share_contents=None):
        reply = {
            "type": "element_share",
            "share_contents": share_contents
        }
        return detect_none_value(reply)
