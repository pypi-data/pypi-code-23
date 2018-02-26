import lxml.html
import requests

from requests.exceptions import RequestException

from pbraw import dispatcher
from pbraw.util import urlparse, urlunparse, get_url
from pbraw.handlers.plain import grab_plain

@dispatcher.handler(priority=5)
def grab_from_links(url, req):
    if not req.headers['content-type'].startswith('text/html'):
        return False
    try:
        text = req.text
    except ValueError: # invalid encoding
        return False
    purl = list(urlparse(url))
    purl[2:6] = [''] * 4
    doc = lxml.html.document_fromstring(text)
    doc.make_links_absolute(urlunparse(purl))
    links = set()
    for el, attr, dest, pos in doc.iterlinks():
        if el.tag != 'a':
            continue
        for name in ['raw', 'download', 'plain']:
            if name in el.text_content().lower():
                links.add(dest)
                break
    res = []
    for link in links:
        r = get_url(link)
        if not r:
            continue
        ret = grab_plain(link, r)
        if ret:
            res.extend(ret)
    return res if res else False
