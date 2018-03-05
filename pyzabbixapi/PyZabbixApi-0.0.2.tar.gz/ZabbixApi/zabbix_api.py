import requests
import json


class ZabbixApi:
    def __init__(self, api_url, user, password):
        self.api_url = api_url
        login_data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": user,
                "password": password
            },
            "id": 1
        }
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.access_token = requests.post(self.api_url, data=json.dumps(login_data), headers=self.headers).json()[
            'result']

    def get_item_history(self, item, start, stop, history):
        post_param = {
            "jsonrpc": "2.0",
            "method": "history.get",
            "params": {
                "output": "extend",
                "history": history,
                "itemids": item,
                "time_from": start,
                "time_till": stop,
                "sortfield": "clock",
                "sortorder": "DESC"
            },
            "auth": self.access_token,
            "id": 1
        }
        result = requests.post(self.api_url, data=json.dumps(post_param), headers=self.headers).json()[
            'result']
        # print(self.access_token)
        # print(result)
        return result

    def get_host_info(self, ip):
        post_param = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "filter": {
                    "host": [
                        ip
                    ]
                }
            },
            "auth": "d75145c592a9e6590ac5e1d388964759",
            "id": 1
        }
        result = requests.post(self.api_url, data=json.dumps(post_param), headers=self.headers).json()[
            'result']
        return result

    def get_host_items(self, hostid, key):
        post_param = {
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": "extend",
                "hostids": hostid,
                "search": {
                    "key_": key
                },
                "sortfield": "name"
            },
            "auth": self.access_token,
            "id": 1
        }
        result = requests.post(self.api_url, data=json.dumps(post_param), headers=self.headers).json()['result']
        return result

