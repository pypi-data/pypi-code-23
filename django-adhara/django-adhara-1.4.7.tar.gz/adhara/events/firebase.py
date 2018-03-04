from .base import AdharaEventHandler
import requests
import json


class FirebaseEventHandler(AdharaEventHandler):

    def __init__(self, server_key):
        self.url = "https://fcm.googleapis.com/fcm/send"
        self.server_key = server_key
        super(FirebaseEventHandler, self).__init__()

    def execute(self, method, data):
        headers = {
            "Authorization": "key=" + self.server_key,
            "Content-Type": "application/json"
        }
        requests.post(self.url + (method if method is not None else ""), json.dumps(data), headers=headers)

    def notify(self, unique_id, title, content, notification_params=None, data=None):
        notification = {
            "title": title,
            "body": content
        }
        if notification_params:
            notification.update(notification_params)
        notification_object = {
            "to": unique_id,
            "notification": notification,
            "data": data
        }
        self.execute(None, notification_object)
