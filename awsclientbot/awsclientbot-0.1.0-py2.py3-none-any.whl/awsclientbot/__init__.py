import requests

__author__ = 'itertychnyy@gmail.com (Ivan Tertychnyy)'


class AWSClientBot():
    def __init__(self, token):
        self._base_url = "https://b45599xxme.execute-api.us-west-2.amazonaws.com/prod/awsclientbot_push"
        r = requests.get("http://169.254.169.254/latest/meta-data/instance-id")
        self._instance_id = r.text
        self._token = token

    def push(self, message):

        data = {
            "token": self._token,
            "message": "{i}: {m}".format(i=self._instance_id, m=message)
        }
        r = requests.post(self._base_url, json=data)
