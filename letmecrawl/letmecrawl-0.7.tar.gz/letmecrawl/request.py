from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


import httplib

from urlparse import urlparse


def request(url, method='GET', proxy_ip=None, proxy_port=None, timeout=5):

    parts = urlparse(url)

    if proxy_ip:
        con = httplib.HTTPConnection(proxy_ip, proxy_port, timeout=timeout)
        path = url
    else:
        con = httplib.HTTPConnection(parts.netloc)
        path = parts.path or '/'
    con.request(method, path)
    return con.getresponse()


def read(url):
    # TODO use contextual to close
    con = request(url)
    content = con.read()
    con.close()
    return content
