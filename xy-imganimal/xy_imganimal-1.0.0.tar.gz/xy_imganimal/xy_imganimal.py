import requests
import json
import base64
import os
import sys


def _get_access_token():
    url = 'https://www.phpfamily.org/aniToken.php'
    r = requests.post(url)
    res = r.json()
    return res['access_token']

'''动物识别'''
def animal(filename='', topNum=1):
    if not filename:
        return -1
    url = 'https://www.phpfamily.org/imgAni.php'
    filepath = os.path.abspath(filename)
    b64img= base64.b64encode(open(filepath, 'rb').read()).rstrip().decode('utf-8')
    data = {}
    data['b64img'] = b64img
    data['access_token'] = _get_access_token()
    data['topNum'] = topNum
    r = requests.post(url, data=data)
    res = r.json()
    if res['result'] :
        if topNum == 1:
            return res['result'][0]['name']
        else:
            return res['result']

def main():
    res = animal('1.jpg')
    print(res)


if __name__ == '__main__':
    main()
