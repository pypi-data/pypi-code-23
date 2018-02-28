import logging
import os
import datetime
import urllib
import gzip
import lxml.html
from collections import namedtuple
from pathlib import Path
from functools import partial
from . import formats, templates
from . import meta

logger = logging.getLogger(__name__)

RESERVED_ROUTES = set(map(Path, [
    '.htaccess',
    'lib',
    'robots.txt',
    'sitemap.xml', 'sitemap.rss',
]))

def _now():
    return datetime.datetime.now()

def _date_modified(path):
    return datetime.datetime.fromtimestamp(path.stat().st_mtime)

def _has_modified(inpath, outpath):
    return (not outpath.exists()) or \
            (_date_modified(inpath) > _date_modified(outpath))

def _mkdirp(path):
    os.makedirs(str(path.parent), exist_ok=True)

def _multi(func, force, inpath, outpath, **kwargs):
    subpaths = (sub.relative_to(inpath) for sub in inpath.glob('**/*'))
    for subpath in subpaths:
        if 'ignore' in subpath.parts or 'ignored' in subpath.parts \
                or subpath.suffix == '.checked' \
                or subpath.suffix == '.new' \
                or subpath.suffix == '.orig' or subpath.suffix == '.bak':
            logger.info('Not rendering: %s' % subpath)
        elif subpath in RESERVED_ROUTES:
            logger.error('Route is not allowed: %s' % subpath)
        elif (inpath / subpath).is_file():
            try:
                yield func(force, inpath / subpath, outpath / subpath,
                           **kwargs)
            except Exception as e:
                logger.exception('Error rendering %s' % subpath)

def copy(force, inpath, outpath):
    if force or _has_modified(inpath, outpath):
        _mkdirp(outpath)
        formats.copy(inpath, outpath)
    return Page(route=outpath, modified=_date_modified(inpath))
copies = partial(_multi, copy)

def article(force, inpath, base_outpath, outroot=''):
    if base_outpath.name.startswith('index.') and inpath.suffix in formats.article:
        outpath = base_outpath.with_suffix('.html')
        func = partial(formats.article[inpath.suffix], outroot)
    elif inpath.name in {'index.htm', 'index.html'}:
        outpath = base_outpath.with_suffix('.html')
        func = partial(formats.raw, outroot)
    elif inpath.suffix in formats.figure:
        outpath = base_outpath
        func = formats.figure[inpath.suffix]
    else:
        outpath = base_outpath
        func = formats.copy
    if force or _has_modified(inpath, outpath):
        _mkdirp(outpath)
        func(inpath, outpath)
    return Page(route=outpath, modified=_date_modified(inpath))
articles = partial(_multi, article)

def fossil(executable, reppath, debug, outpath):
    template = '''#!%s
directory: %s
repolist
'''
    cgi = template % (executable, reppath)
    if debug:
        cgi += 'debug: %s\n' % debug

    _mkdirp(outpath)
    with outpath.open('w') as fp:
        fp.write(cgi)
    outpath.chmod(0o755)
    return Page(route=outpath, modified=_now())

def lib(serve_gzip, root_address, redirects, error404_path, fossils_route, outpath):
    absroot = Path('/' + urllib.parse.urlsplit(root_address).path.strip('/'))
    lib = outpath / 'lib'
    if error404_path.is_file():
        error404_body = formats.error404(error404_path, str(absroot))
        error404_suffix = 'html'
    else:
        error404_body = 'Page not found'
        error404_suffix = 'txt'
    _e = 'lib/404.%s' % error404_suffix
    error404_route = str(absroot / _e)
    error404_outpath = outpath / _e

    valid_redirects = []
    for redirect in map(tuple, redirects):
        if not redirect[0].startswith('/'):
            logger.warning('Invalid redirect source: %s -> %s' % redirect)
        elif not redirect[1].startswith('/'):
            logger.warning('Invalid redirect target: %s -> %s' % redirect)
        elif (outpath / redirect[0].lstrip('/')).exists():
            logger.warning('Redirect source exists: %s -> %s' % redirect)
        elif not (outpath / redirect[1].lstrip('/')).exists():
            logger.warning('Redirect target does not exist: %s -> %s' % redirect)
        else:
            valid_redirects.append(redirect)

    yield from copies(False,
       Path(__file__).parent / 'lib', lib)

    with error404_outpath.open('w') as fp:
        fp.write(error404_body)
    yield Page(route=error404_outpath, modified=_now())

    robots = outpath / 'robots.txt'
    with robots.open('w') as fp:
        fp.write('''\
User-Agent: *
Disallow: /license.txt
Disallow: /wp-login.php
Disallow: /!/feed.xml
Disallow: /favicon.ico
Disallow: /static/
''')
    yield Page(route=robots, modified=_now())

    tpl = templates.ENV.get_template('htaccess')
    rendered = tpl.render(redirects=valid_redirects,
                          gzip=serve_gzip,
                          error404_route=error404_route,
                          fossils_route=fossils_route)
    htaccess = outpath / '.htaccess'
    with htaccess.open('w') as fp:
        fp.write(rendered)
    yield Page(route=htaccess, modified=_now())

Page = namedtuple('Page', ['route', 'modified'])

def sitemap(root, pages, outpath):
    def str_route(x):
        href = x.relative_to(outpath)
        if href.name.startswith('index.'):
            return str(href.parent).rstrip('/') + '/'
        else:
            return str(href)

    def itemdata(x):
        with x.open('rb') as fp:
            html = lxml.html.fromstring(fp.read())

        y = meta.from_html(html)

        url = root.rstrip('/') + '/' + str_route(x)
        html.make_links_absolute(url)
        y['body'] = lxml.html.tostring(html.xpath('//article')[0]).decode('utf-8')
        return y

    for fileformat in ['xml', 'rss']:
        filename = 'sitemap.' + fileformat
        route = outpath / filename
        tpl = templates.ENV.get_template(filename)

        if fileformat == 'xml':
            str_pages = sorted((str_route(page.route), page.modified.isoformat()) for page in pages)
        elif fileformat == 'rss':
            str_pages = sorted((
                    page.modified.isoformat(),
                    str_route(page.route),
                    itemdata(page.route),
                ) for page in pages if page.route.name == 'index.html')

        with route.open('w') as fp:
            fp.write(tpl.render(root=root.rstrip('/'), pages=str_pages))

        yield Page(route=route, modified=_now())

def gz(htaccess_path, fossil_path, force, out):
    '''
    Run this last, or close to last, because it taxes the output
    directory as input.
    '''
    NO_GZ_PATHS = {htaccess_path, fossil_path}
    NO_GZ_EXTENSIONS = {
        '.gif', '.jpg', '.jpeg', '.png',
        '.ogg', '.mkv', '.webm',
        '.gz', '.zip',
        '.cgi',
    }
    for inpath in (out).glob('**/*'):
        if inpath.is_file() and \
            inpath not in NO_GZ_PATHS and \
            inpath.suffix.lower() not in NO_GZ_EXTENSIONS:
            outpath = inpath.parent / (inpath.name + '.gz')
            if force or _has_modified(inpath, outpath):
                with inpath.open('rb') as infp, outpath.open('wb') as outfp:
                    with gzip.open(outfp, 'wb') as g:
                        g.write(infp.read())
            yield Page(route=outpath, modified=_date_modified(inpath))
