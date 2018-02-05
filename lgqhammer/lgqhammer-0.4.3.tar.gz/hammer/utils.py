# -*- coding=utf-8 -*-

import json
import os
from configparser import ConfigParser


def get_full_url(url, param):
    p = ''
    for k, v in param.items():
        p = '%s&%s=%s' % (p, k, v)
    full = '%s?%s' % (url, p)
    return full


def full_url(url, param):
    return get_full_url(url, param)


def ini2json(file):
    cf = ConfigParser()
    cf.read(file)
    conf = {}
    for section in cf.sections():
        conf[section] = {}
        for name, value in cf.items(section):
            conf[section][name] = value

    return conf


def check_kwargs(body, kwargs, res):
    if res and kwargs is not None:
        for key, val in kwargs.items():
            if body.get(key) is None or val not in body.get(key):
                res = False

    return res


# kwargs = {
#     'path': 'getEntDetail',
#     'query': 'unique',
#     'request': {
#
#     },
#     'response': {
#
#     }
# }
def parse_charles(dir, kwargs, callback):
    for file in os.listdir(dir):
        if 'charles' not in file or '.chlsj' not in file:
            continue
        full_path = dir + file
        with open(full_path, 'r') as f:
            text = f.read()

        body_list = json.loads(text)
        req_kwargs = kwargs.get('request', None)
        res_kwargs = kwargs.get('response', None)
        kwargs.pop('request', None)
        kwargs.pop('response', None)

        bodys = []
        for body in body_list:
            res = True
            check_kwargs(body, kwargs, res)
            req_body = body.get('request')
            check_kwargs(req_body, req_kwargs, res)
            res_body = body.get('response')
            check_kwargs(res_body, res_kwargs, res)
            if res:
                bodys.append(body)
        callback(file, bodys)

#
# if __name__ == '__main__':
#     url = 'https://apphouse.58.com/api/list/hezu?&localname=bj&os=android&format=json&v=1&geotype=baidu&page=2'
#
#     param = {
#         'action':'getListInfo',
#         'curVer': '7.13.1',
#         'appId':'1'
#     }
#
#     print(full_url(url, param))


#
# def call(file, bodys):
#     print(file)
#
#
# if __name__ == '__main__':
#     dir = '/Users/lgq/Charles/'
#     kwargs = {
#         'path': 'getEntDetail',
#         'query': 'unique'
#     }
#     p = parse_charles(dir, kwargs, call)
#     # print(p)
