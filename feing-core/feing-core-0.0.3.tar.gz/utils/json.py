# -*- coding: UTF-8 -*-
import json
import re
from urllib import parse


def loads_jsonp(data):
    """
    jsonp解析
    :param data: jsonp字符串
    :return: json格式字典
    """
    try:
        data = json.loads(re.match(".*?({.*}).*", data, re.S).group(1))
        return data
    except Exception:
        raise ValueError('Invalid Input')


def qs(url):
    """
    url的查询参数转换为字典
    :param url: 带查询参数的请求url
    :return: json格式字典
    """
    query = parse.urlparse(url).query
    return dict([(k, v[0]) for k, v in parse.parse_qs(query).items()])
