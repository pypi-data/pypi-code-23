# !/usr/bin/env python

# -*- coding:utf-8 -*-
# Shiny Python SDK
import collections
import hashlib
import json

import requests


def md5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()


def sha1(text):
    m = hashlib.sha1()
    m.update(text)
    return m.hexdigest()


class ShinyError(Exception):
    def __init__(self, message, code='unknown_error'):
        self.message = message
        self.code = message


class Shiny:
    def __init__(self, api_key, api_secret_key, api_host='https://shiny.kotori.moe'):
        self.API_KEY = api_key
        self.API_SECRET_KEY = api_secret_key
        self.API_HOST = api_host

    def sign(self, payload={}):
        """ API 请求签名 """
        data = self.API_KEY + self.API_SECRET_KEY
        for key in sorted(payload.keys()):
            data += str(payload[key])
        return sha1(data.encode('utf-8'))

    def add(self, spider_name, level, data=None, hash=False):
        """添加数据项"""
        if data is None:
            data = {}

        url = self.API_HOST + '/Data/add'

        payload = {"api_key": self.API_KEY}

        event = {"level": int(level), "spiderName": spider_name}

        # 如果没有手动指定Hash，将会把data做一次md5生成hash
        try:
            if hash:
                event["hash"] = str(hash)
            else:
                event["hash"] = md5(json.dumps(collections.OrderedDict(
                    sorted(data.items()))).encode('utf-8'))
        except Exception as e:
            raise ShinyError('Fail to generate hash')

        event["data"] = data

        payload["sign"] = sha1(
            (self.API_KEY + self.API_SECRET_KEY + json.dumps(event)).encode('utf-8'))

        payload["event"] = json.dumps(event)

        response = requests.post(url, payload)

        if response.status_code != 200:
            try:
                error = json.loads(response.text)
            except Exception as e:
                raise ShinyError('Network error: ' + str(response.status_code))

            raise ShinyError(
                'Shiny error: ' + str(error['error']['info']), code=str(error['error']['code']))

    def recent(self):
        """获取最新项目"""
        url = self.API_HOST + '/Data/recent'
        response = requests.get(url)
        if response.status_code != 200:
            raise ShinyError('Network error:' + str(response.status_code))
        return json.loads(response.text)

    def get_jobs(self):
        url = self.API_HOST + \
            '/Job/query?api_key={}&sign={}'.format(self.API_KEY, self.sign())
        response = requests.get(url)
        if response.status_code != 200:
            raise ShinyError('Network error:' + str(response.status_code))
        return json.loads(response.text)

    def report(self, job_id, status):
        url = self.API_HOST + '/Job/report'
        payload = {
            "jobId": job_id,
            "status": status
        }
        sign = self.sign(payload)
        payload["api_key"] = self.API_KEY
        payload["sign"] = sign
        response = requests.post(url, payload)
        if response.status_code != 200:
            try:
                error = json.loads(response.text)
            except Exception as e:
                raise ShinyError('Network error: ' + str(response.status_code))

            raise ShinyError('Shiny error: ' + str(error['error']['info']), code=str(error['error']['code']))
