#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import re
import hashlib
import httplib
import urllib
import urllib2
import socket
import StringIO
import json
import gzip
import uuid
import base64
import threading
import websocket
import utils
from CoralResultSet import CoralResultSet
from CoralParallelJob import CoralParallelJob


class CoralParallelClient(object):
    """
    Coral Parallel Client
    """
    def __init__(self, address):
        # url = 'coraldb://test:123456@localhost:8086'
        p = re.compile(r"""^coraldb://(([^:]*)?(:[^@]*)?@)?([^:]+):(\d+)$""", re.IGNORECASE)
        m = p.match(address)
        if not m:
            raise Exception('illegal CoralDB address: ' + address)
        self.username = m.group(2)
        self.password = m.group(3)[1:] if m.group(3) else None
        if self.password:
            md5 = hashlib.md5()
            md5.update(self.password)
            self.password = md5.hexdigest()
        self._host = m.group(4)
        self._port = int(m.group(5))
        self._token = None
        self.timeout = 120
        self.compress = False

    def login(self, username=None, password=None):
        """
        login: 登陆
        :param username: 用户名
        :param password: 密码
        :return: None
        :exception: 登陆失败抛出异常
        """
        if username is not None:
            self.username = username
        if password is not None:
            self.password = utils.encodePwd(password)
        params = {'u': self.username, 'p': self.password}
        rep = self.__request('parallel/login', params, login=True)
        if rep['error'] == "":
            self._token = rep['token']
        return CoralResultSet()

    def map(self, func, args, context=None, reduce=None):
        """
        :param func: Map函数
        :param args: Map参数
        :param context: 上下文参数
        :param reduce: Reduce函数
        :return: 执行结果
        """
        url = "ws://%s:%s/parallel/run?token=%s" % (self._host, self._port, self._token)
        job = CoralParallelJob(url)
        job.map(func, args, context)
        if reduce:
            job.reduce(reduce)
        job.commit()
        job.wait()
        return job.get()

    def __request(self, path, params=None, data=None, login=False):
        """
        """
        if params is None:
            params = {}
        if self._token:
            params['token'] = self._token
        for k, v in params.iteritems():
            if isinstance(v, unicode):
                params[k] = v.encode('UTF-8')
        url = 'http://%s:%s/%s?%s' % (self._host, self._port, path, urllib.urlencode(params))
        headers = {'User-Agent': 'PyCoralDB/1.1'}
        if data:
            headers['Content-Type'] = 'application/json'
        if self.compress:
            headers['Accept-Encoding'] = 'gzip'
        # Try to send the request a maximum of three times.
        retry_times = 5
        for i in xrange(1, retry_times + 1):
            try:
                req = urllib2.Request(url, data=data, headers=headers)
                f = urllib2.urlopen(req, timeout=10 if login else self.timeout)
                html = f.read()
                encoding = f.info().get('Content-Encoding')
                if encoding == 'gzip':
                    buf = StringIO.StringIO(html)
                    zf = gzip.GzipFile(fileobj=buf)
                    html = zf.read()
                    zf.close()
                rep = json.loads(html)
                if rep['error']:
                    err = '%s failed: %s' % (path, rep['error'])
                    raise Exception(err.encode('UTF-8'))
                return rep
            except urllib2.URLError, e:
                if not login and e.reason == 'Unauthorized':
                    self.login()
                    if self._token:
                        params['token'] = self._token
                    url = 'http://%s:%s/%s?%s' % (self._host, self._port, path, urllib.urlencode(params))
                    login = True
                    continue
                elif i < retry_times and e.reason in ['Too Many Requests', 'Bad Gateway']:
                    time.sleep(10)
                    continue
                elif i < retry_times and e.reason not in ['Forbidden', 'Bad Request']:
                    time.sleep(5)
                    continue
                else:
                    raise e
            except socket.timeout, e:
                if i >= retry_times:
                    raise e
                time.sleep(5)
            except socket.error, e:
                if i >= retry_times:
                    raise e
                time.sleep(5)
            except httplib.UnknownProtocol, e:
                if i >= retry_times:
                    raise e
                time.sleep(5)
        return None


if __name__ == '__main__':
    client = CoralParallelClient('coraldb://127.0.0.1:5167')
    client.login('test', '123456')
    def f(x):
        return x * 2
    pr = client.map(f, range(5)).commit()
    pr.wait_interactive()
    print pr.get()

