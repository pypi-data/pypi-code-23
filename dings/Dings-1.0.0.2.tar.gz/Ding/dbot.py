#!/usr/bin/env python3
# coding=utf-8

"""
@version:1.0.0
@author: ysicing
@file: Ding/dbot.py
@time: 23/02/2018 11:24
"""

import requests
import json
import datetime

headers = {'Content-Type': 'application/json'}


class DtalkBot(object):
    def __init__(self, webhook):
        self.webhook = webhook

    def msg(self, text, isatall=False, atmobiles=[]):
        data = {"msgtype": "text", "text": {"content": text}, "at": {"atMobiles": atmobiles, "isAtAll": isatall}}
        return self.post(json.dumps(data))

    def post(self, data):
        req = requests.post(self.webhook, data=data, headers=headers).json()
        res = req['errcode']
        if res == 0:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%s") + " send ok " + "\n")
        else:
            print(datetime.datetime.now() + " send eror :" + str(res) + "\n")