from os import path
import re
try:
    from urllib.parse import unquote
    py = 3
except ImportError:
    from urllib import unquote
    py = 2

from pbraw import dispatcher
from pbraw.util import urlparse

CD_FILENAME_RE = re.compile('.*?;\s*filename\s*(\*?)\s*=\s*(?:\"(.*)\"\s*|(.*))', flags=re.I | re.X)

def handle(string):
    enc, _, string = string.partition('\'')
    lang, _, content = string.partition('\'')
    enc, content = enc.strip(), content.strip()
    if py == 3:
        return unquote(content, enc)
    else:
        return unquote(content).decode(enc)

@dispatcher.handler(priority=0)
def grab_plain(url, req):
    if req.headers['content-type'].startswith('text/html'):
        return False
    try:
        ret = req.text
    except ValueError: # invalid encoding
        return False
    name = ''
    if 'content-disposition' in req.headers:
        for m in CD_FILENAME_RE.finditer(req.headers['content-disposition']):
            star, filename = m.group(1), m.group(2) or m.group(3)
            name = handle(filename) if star else filename
    if not name:
        name = path.split(urlparse(url).path)
        if name: name = name[-1]
    if not name:
        name = urlparse(url).netloc # for the lack of a better name
    return [(name, ret)]
