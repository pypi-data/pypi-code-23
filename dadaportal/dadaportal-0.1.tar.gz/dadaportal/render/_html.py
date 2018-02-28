import logging
import warnings
import os
import datetime
import re

import lxml.html
import lxml.etree

from .. import config
from .templates import ENV
from . import meta

logger = logging.getLogger(__name__)

_utf8parser = lxml.etree.HTMLParser(encoding='utf-8')
def _fromutf8(x):
    tree = lxml.etree.HTML(x, parser=_utf8parser)
    if tree is None:
        raise ValueError('Could not parse HTML tree')

    body = tree.xpath('./body')[0]
    body.tag = 'div'

    # Remove comments.
    for parent in body.xpath('//*[comment()]'):
        for comment in parent.xpath('comment()'):
            parent.remove(comment)
    return body

def _link_img(html):
    for img in html.xpath('//img[not(../self::a)]'):
        a = lxml.html.Element('a', href = img.xpath('@src')[0])
        parent = img.getparent()
        parent.replace(img, a)
        a.append(img)
    return html

def _link_headers(html):
    x = '//*[self::h1 or self::h2 or self::h3 or self::h4 or self::h5 or self::h6]'
    for h in html.xpath(x):
        if not h.text:
            continue
        if 'id' not in h.attrib:
            h.attrib['id'] = h.text.lower().replace(' ', '-')
        a = lxml.html.Element('a', href = '#' + h.attrib['id'])
        parent = h.getparent()
        parent.replace(h, a)
        a.append(h)
    return html

def _video_fallback(html):
    for video in html.xpath('//video'):
        if not video.text:
            video.text = 'Your web browser can not play this video. Try playing it with another program: '
            if 'src' in video.attrib:
                a = lxml.html.Element('a', href=video.attrib['src'])
                a.text = video.attrib['src']
                video.append(a)
    return html

def listing(singular, plural, slugs):
    tpl = ENV.get_template('listing.html')
    return tpl.render(singular=singular, plural=plural, slugs=slugs)

def _crumbs(root, top, bottom):
    if top.is_dir() and bottom.is_dir():
        if (top / 'index.html').is_file():
            href = os.path.relpath(str(top), str(bottom))
        else:
            href = ''
        if top == root:
            name = '~'
        else:
            name = top.name
            yield from _crumbs(root, top.parent, bottom)
        yield href, name
    else:
        raise ValueError('top and bottom must both be directories.')

def _page(crumbs, relroot, basename, title, description, body, centered, bread):
    tpl = ENV.get_template('page.html')

    x = _fromutf8(body)
    # y = _video_fallback(_link_img(_link_headers(x)))
    y = _link_img(_link_headers(x))

    fallbacks = meta.from_html(y)
    if title == None:
        title = fallbacks.get('title', basename.title())
    if description == None and 'description' in fallbacks:
        description = fallbacks['description']
    if description:
        description = description.strip()

    body = lxml.html.tostring(y, encoding='utf-8').decode('utf-8')

    now = datetime.datetime.now()

    return tpl.render(title=title, description=description, body=body,
                      centered=centered, bread=bread,
                      relroot=relroot, crumbs=crumbs,
                      modified=now.strftime('%Y-%m-%d %H:%M UTC'),
                      modified_c=now.ctime())

def formatter(func):
    def wrapper(outroot, inpath, outpath):
        with inpath.open() as fp:
            head_fp, body_fp = meta.split_header(fp)
            with warnings.catch_warnings(record=True) as ws:
                data = config.article_header(head_fp)
                for w in ws:
                    logger.warning('[%s] %s' % (inpath, w.message))
            data['body'] = func(inpath, body_fp)

        crumbs = _crumbs(outroot, outpath.parent, outpath.parent)
        relroot = os.path.relpath(str(outroot), str(outpath.parent))

        base = inpath.with_suffix('').name
        if base == 'index':
            base = inpath.parent.with_suffix('').name
        rendered = _page(crumbs, relroot,
                         base,
                         data['title'], data['description'],
                         data['body'],
                         data['centered'] != None,
                         data['nobread'] == None)
        with outpath.open('w') as fp:
            fp.write(rendered)
    wrapper.func = func
    return wrapper
