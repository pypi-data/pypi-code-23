# coding: utf8

import time
import random
import threading
from ..core.decorators import sync
from ..core.errors import NoProxyError


class Proxy(object):

    def __init__(self, host=None, port=None, user=None, password=None):
        # TODO 合法性检查
        self.host = host
        self.port = port
        self.user = user
        self.password = password


class ProxyHelper(object):

    def __init__(self, proxy_list=None, fetch_func=None, cache_seconds=None):
        if not proxy_list and not fetch_func:
            raise ValueError
        if proxy_list and fetch_func:
            raise ValueError

        if proxy_list:
            self.proxy_list = proxy_list
        if fetch_func:
            self.cache_seconds = cache_seconds or 5
            self.proxy_list = []
            self.last_fetch_at = time.time()
            self.fetch_func = fetch_func
            self.fetch_proxy_list()

    @sync(threading.Lock())
    def random_choice(self):
        # TODO 支持更加复杂的 proxy 调度逻辑？
        if hasattr(self, 'fetch_func') and (time.time()-self.last_fetch_at) >= self.cache_seconds:
            self.fetch_proxy_list()

        if not self.proxy_list:
            raise NoProxyError

        proxy = random.choice(self.proxy_list)

        if proxy.user and proxy.password:
            proxy_meta = 'http://%(user)s:%(password)s@%(host)s:%(port)s' % {
                'host': proxy.host,
                'port': proxy.port,
                'user': proxy.user,
                'password': proxy.password,
            }
        else:
            proxy_meta = 'http://%(host)s:%(port)s' % {
                'host': proxy.host,
                'port': proxy.port,
            }

        return {
            'http': proxy_meta,
            'https': proxy_meta,
        }
        
    def fetch_proxy_list(self):
        return self.fetch_func()
