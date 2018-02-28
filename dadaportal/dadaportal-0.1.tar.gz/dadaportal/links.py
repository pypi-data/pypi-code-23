import logging
import re
from urllib.parse import urlsplit
from pathlib import Path
from enum import Enum
logger = logging.getLogger()
try:
    from requests import head
except ImportError:
    logger.warning('python-requests is not available, so I will not check external links.')
    class head(object):
        def __init__(*args, **kwargs):
            self.ok = True
import lxml.html
from . import config

INDEX = Path('index.html')

def _hrefs(html):
    seen = set()
    hrefs = html.xpath('//a/@href') + \
            html.xpath('//img/@src') + \
            html.xpath('//link/@href') + \
            html.xpath('//video/@src')
    for href in hrefs:
        if not href.startswith(('#', '?')):
            realhref = re.split(r'[#?]', href)[0]
            if realhref not in seen:
                if realhref.startswith('mailto:') or realhref.startswith('tel:'):
                    pass
                else:
                    yield realhref
                seen.add(realhref)

class Link(Enum):
    absolute = 1
    broken = 2
    missing = 3
    empty = 4
    remote = 5
    slash = 6

def missing_links(check_absent_indexes, alltargets, source, target):
    '''
    Find a directory's children that are not linked from the directory index.

    :param directory: Directory to look for links in
    :returns: Iterable of (source, destination)
    '''
    index = source / INDEX
    if not target:
        target = source

    if index.exists():
        with index.open('rb') as fp:
            html = lxml.html.fromstring(fp.read())
        linked = set(h.rstrip('/') for h in _hrefs(html) if '://' not in h)
    elif check_absent_indexes:
        linked = set()
    else:
        raise StopIteration

    if target.is_dir():
        available = set(str(l.relative_to(source)).rstrip('/') \
                            for l in target.iterdir() \
                            if (check_absent_indexes or (l / INDEX).exists()))
    else:
        available = set()
    for href in available - linked - {INDEX}:
        if alltargets or '.' not in Path(href).name:
            yield Link.missing, index, href

allowed_remotes = 'https://thomaslevine.com/scm/'
def bad_links(root_address, check_external_links, fossil_route, src):
    '''
    Find broken and absolute links from a file.

    :param src: File to look for links in
    :returns: Iterable of (source, destination)
    '''
    netloc = urlsplit(root_address).netloc
    with src.open('rb') as fp:
        html = lxml.html.fromstring(fp.read())
    for href in _hrefs(html):
        if fossil_route and href.startswith('/%s/' % fossil_route):
            pass # Don't check fossil repository links.
        elif '://' in href:
            if urlsplit(href).netloc == netloc and not \
                    any(href.startswith(remote) for remote in allowed_remotes):
                yield Link.remote, src, href
            elif check_external_links and not head(href).ok:
                yield Link.broken, src, href
        elif href.startswith('/'):
            yield Link.absolute, src, href
        elif href == '':
            yield Link.empty, src, '.'
        else:
            resolved = (src.parent / href)
            if resolved.is_file():
                if href.endswith('/'):
                    yield Link.slash, src, href
            elif resolved.is_dir() and (resolved / INDEX).is_file():
                if not href.endswith('/'):
                    yield Link.slash, src, href
            else:
                yield Link.broken, src, href
