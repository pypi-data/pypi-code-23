"""
Using scrapy shell methods in Jupyter notebook.
"""
import os
from random import choice
import requests
import hashlib
from os import path
from scrapy.http import TextResponse
from werkzeug.local import LocalProxy

from .fileutil import write_file

__author__ = 'Aollio Hou'
__email__ = 'aollio@outlook.com'

_here = path.abspath(path.dirname(__file__))

_resp = [None]
response = LocalProxy(lambda: _resp[0])

user_agents = [line for line in open(path.join(_here, 'user_agents.txt'), 'r').read().split('\n')]
user_agent = LocalProxy(lambda: choice(user_agents))


def fetch(url, meta=None, *args, **kwargs):
    """fetch url. """
    resp = requests.get(url, *args, **kwargs, timeout=30)
    resp.encoding = 'UTF-8'
    rv = TextResponse(resp.url, status=resp.status_code, body=resp.text,
                      encoding='UTF-8')
    rv.request = rv.follow(url, meta=meta)
    _set_response(rv)
    return rv


def _set_response(res):
    """Update local response from requests response"""
    global _res
    _resp[0] = res


def _platform():
    return os.uname().sysname


def _get_var_path():
    platform = _platform()
    var_path = ''
    if platform == 'Darwin':
        # macOs
        var_path = '/tmp/'
    assert var_path, 'unknown system platform.'
    return var_path


def view(resp=None):
    if not resp:
        resp = response
    md5 = hashlib.md5()
    md5.update(resp.url.encode())
    path = _get_var_path() + md5.hexdigest() + '.html'
    write_file(path, resp.text.encode(), bytes_mode=True)
    os.system('open %s' % path)


if __name__ == '__main__':
    fetch('http://jianshu.com')
    view()
