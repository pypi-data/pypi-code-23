from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import re

from . import request


ip_pattern = '(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\:\d{2,5}'


class ParserNotFoundException(Exception):
    pass


class Source(object):
    def __init__(self, url):
        self.url = url

    @staticmethod
    def factory(name, url):
        if name == 'spy': return Spys(url)
        raise ParserNotFoundException


class Proxy(object):
    def __init__(self, url):
        self.ip, port = url.split(':')
        self.port = int(port)


class Spys(Source):
    def list(self):
        content = request.read(self.url)
        ips = re.findall(ip_pattern, content)
        return map(Proxy, ips)