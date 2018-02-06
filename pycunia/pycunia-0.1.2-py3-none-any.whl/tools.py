import requests
import ujson


def get_json(url, auth=None):
    if not auth:
        data = requests.get(url).text
    else:
        data = requests.get(url, auth=auth).text
    res = ujson.loads(data)
    return res

def post_json(url, json, auth):
    data = requests.post(url, json=json, auth=auth).text
    res = ujson.loads(data)
    return res

def delete(url, auth):
    data = requests.delete(url, auth=auth)
    res = ujson.loads(data)
    return res