import lxml.html

from pbraw import dispatcher
from pbraw.util import urlparse

@dispatcher.handler(priority=2)
def grab_from_ubuntu(url, req):
    loc = urlparse(url).netloc
    if not (loc == 'paste.ubuntu.com' or loc == 'pastebin.ubuntu.com'):
        return False
    if not req.headers['content-type'].startswith('text/html'):
        return False
    try:
        text = req.text
    except ValueError: # invalid encoding
        return False
    doc = lxml.html.document_fromstring(text)
    elem = doc.xpath('//td[@class="code"]/div/pre')
    if not elem:
        return False
    return [(urlparse(url).path.split('/')[-1], elem[0].text_content())]
