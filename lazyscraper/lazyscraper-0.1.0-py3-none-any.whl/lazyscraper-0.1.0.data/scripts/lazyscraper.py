#!C:\Python36\python.EXE
# -*- coding: utf8 -*-
"""Lazy scraping tool"""
import json
import os
import hashlib
import zlib
import time
import csv
import logging
import datetime
import io
import sys
from urllib.request import urlopen
from urllib.parse import urljoin
import requests
import lxml.html
import lxml.etree
import click
from io import StringIO
try:
    from bmemcached import Client
    from zlib import compress, decompress
except:
    pass

#logging.getLogger().addHandler(logging.StreamHandler())
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG)



DEFAULT_URL_FIELDS = ['_text', 'href']
DEFAULT_SELECT_FIELDS = ['_text', 'value']
TEXT_FIELD = "_text"
TAG_FIELD = "_tag"
DEFAULT_FIELDS = ['_tag', 'class', 'id', '_text']
URL_TAG_TYPES = ['href', 'src', 'srcset']
DEFAULT_CACHE_TIMEOUT = 3600


def _get_cached_post(url, postdata):
    """Returns url data from url with post request"""
    servers = ["127.0.0.1:11211"]
    m = hashlib.sha256()
    m.update(url.encode('utf8'))
    m.update(str(postdata).encode('utf8'))
    key = m.hexdigest()
    client = Client(servers)
    c_data = client.get(key)
    if c_data:
        data = decompress(c_data)
    else:
        r = requests.post(url, postdata)
        data = r.text
        client.set(key, compress(data))
    hp = lxml.etree.HTMLParser(encoding='utf-8')
    root = lxml.html.fromstring(data, parser=hp)
    return root

def _get_cached_url(url, timeout=DEFAULT_CACHE_TIMEOUT):
    """Returns url data from url or from local memcached"""
    servers = ["127.0.0.1:11211"]
    m = hashlib.sha256()
    m.update(url.encode('utf8'))
    key = m.hexdigest()
    client = Client(servers)
    c_data = client.get(key)
    if c_data:
        data = decompress(c_data)
    else:
        o = urlopen(url)
        rurl = o.geturl()
        data = o.read()
        client.set(key, compress(data))
    hp = lxml.etree.HTMLParser(encoding='utf-8')
    root = lxml.html.fromstring(data, parser=hp)
    return root

def __table_to_dict(node, strip_lf=True):
    """Extracts data from table"""
    data = []
    rows = node.xpath('./tbody/tr')
    if len(rows) == 0:
        rows = node.xpath('./tr')
    for row in rows:
        cells = []
        for cell in row.xpath('./td'):
            inner_tables = cell.xpath('./table')
            if len(inner_tables) < 1:
#                for k in cell.itertext(): print(k.encode('utf8').decode('utf8'))
                text = u' '.join(cell.itertext()) #cell.text_content()
                if strip_lf:
                    text = text.replace(u'\r',u' ').replace(u'\n', u' ').strip()
                cells.append(text)
            else:
                cells.append([__table_to_dict(node, strip_lf) for t in inner_tables])
        data.append(cells)
    return data


def __taglist_to_dict(tags, fields, strip_lf=True):
    """Converts list of tags into dict"""
    has_text = TEXT_FIELD in fields
    has_tag = TAG_FIELD in fields
    finfields = fields.copy()
    data = []
    if has_text: finfields.remove(TEXT_FIELD)
    if has_tag: finfields.remove(TAG_FIELD)
    for t in tags:
        item = {}
        if has_tag:
            item[TAG_FIELD] = t.tag
        if has_text:
#            print(t)
#            print(type(t))
            item[TEXT_FIELD] = ' '.join(t.itertext()).strip()
            if strip_lf:
                item[TEXT_FIELD] = (' '.join(item[TEXT_FIELD].split())).strip()
        for f in finfields:
            item[f] = t.attrib[f].strip() if f in t.attrib.keys() else ""
        data.append(item)
    return data


def pattern_extract_simpleul(tree, nodeclass, nodeid, fields):
    """Simple UL lists extractor pattern"""
    if nodeclass:
        xfilter = "//ul[@class='%s']/li//a" % (nodeclass)
    elif nodeid:
        xfilter = "//ul[@id='%s']/li//a" % (nodeid)
    else:
        xfilter = '//ul/li//a'
    tags = tree.xpath(xfilter)
    data = __taglist_to_dict(tags, fields)
    return data

def pattern_extract_simpleoptions(tree, nodeclass, nodeid, fields):
    """Simple SELECT / OPTION  extractor pattern"""
    if nodeclass:
        xfilter = "//select[@class='%s']/option" % (nodeclass)
    elif nodeid:
        xfilter = "//select[@id='%s']/option" % (nodeid)
    else:
        xfilter = '//select/option'
    tags = tree.xpath(xfilter)
    data = __taglist_to_dict(tags, fields)
    return data

def pattern_extract_exturls(tree, nodeclass, nodeid, fields):
    """Pattern to extract external urls"""
    if nodeclass:
        xfilter = "//a[@class='%s']" % (nodeclass)
    elif nodeid:
        xfilter = "//a[@id='%s']" % (nodeid)
    else:
        xfilter = '//a'
    tags = tree.xpath(xfilter)
    filtered = []
    for t in tags:
        if 'href' in t.attrib.keys():
            if t.attrib['href'][:6] in ['http:/', 'https:']:
                filtered.append(t)
    data = __taglist_to_dict(filtered, fields)
    return data


def pattern_extract_forms(tree, nodeclass, nodeid, fields):
    """Extracts web forms from page"""
    res = []
    formattrlist = ['name', 'id', 'action', 'class', 'method']
    inputattrlist = ['name', 'id', 'type', 'class', 'value', 'src', 'size']
    textarealist = ['name', 'id', 'size', 'class']
    buttonlist = ['name', 'id', 'value', 'class']
    selectlist = ['name', 'id', 'multiple', 'size', 'class']
    optionlist = ['value', 'selected', 'class']
    tagnames = [('input', inputattrlist), ('textarea', textarealist), ('button', buttonlist), ('select', selectlist)]
    allforms = tree.xpath('//form')
    for form in allforms:
        fkey = {}
        for k in formattrlist:
            if form.attrib.has_key(k):
                fkey[k] = form.attrib[k]#
        for tag in form.iterdescendants():
            if not hasattr(tag, 'tag'): continue
            for tagname, tlist in tagnames:
                if tag.tag == tagname:
                    if not tagname in fkey.keys():   fkey[tagname] = []
                    tval = {'text' : tag.text}
                    for k in tlist:
                        if tag.attrib.has_key(k):
                            tval[k] = tag.attrib[k]
                    if tag.tag == 'select':
                        tval['options'] = []
                        options = tag.xpath('option')
                        for o in options:
                            optionval = {'text' : o.text}
#                            print o.text
                            for k in optionlist:
                                if o.attrib.has_key(k):
                                    optionval[k] = o.attrib[k]
                            tval['options'].append(optionval)
                    fkey[tagname].append(tval)
        res.append(fkey)
    return {'total' : len(res), 'list' : res}

PATTERNS = {
'simpleul' : {'func' : pattern_extract_simpleul, 'deffields' : DEFAULT_URL_FIELDS, 'json_only' : False },
'simpleopt' : {'func' : pattern_extract_simpleoptions, 'deffields' : DEFAULT_SELECT_FIELDS , 'json_only' : False },
'exturls' : {'func' : pattern_extract_exturls, 'deffields' : DEFAULT_URL_FIELDS, 'json_only' : False },
'getforms' : {'func' : pattern_extract_forms, 'deffields' : None, 'json_only' : True },
}



@click.group()
def cli1():
    pass

@cli1.command()
@click.option('--url', default='url', help='URL to parse')
@click.option('--xpath', default='//a', help='Xpath')
@click.option('--fieldnames', default=None, help='Fieldnames. If not set, default names used')
@click.option('--absolutize', default=False, help='Absolutize urls')
@click.option('--post', default=False, help='Use post request')
@click.option('--pagekey', default=False, help='Pagination url/post parameter')
@click.option('--pagerange', default=False, help='Pagination range as start,end,step, like "1,24,1"')
@click.option('--format', default='text', help='Output format')
@click.option('--output', default=None, help='Output filename')
def extract(url, xpath, fieldnames, absolutize, post, pagekey, pagerange, format, output):
    """Extract data with xpath"""
    fields = fieldnames.split(',') if fieldnames else DEFAULT_FIELDS
    data = []
    if pagekey is False:
        if post:
            root = _get_cached_post(url)
        else:
            root = _get_cached_url(url)
        tree = root.getroottree()
        tags = tree.xpath(xpath)
        data = __taglist_to_dict(tags, fields)
    else:
        start, end, step, pagesize = map(int, pagerange.split(','))
#        for i in range(start, end, step):
        current = start
        while True:
            anurl = url + '?%s=%d' % (pagekey,current)
            logging.info('Processing url %s' % (anurl))
            if post:
                root = _get_cached_post(anurl, {pagekey : str(current)})
            else:
                root = _get_cached_url(anurl)
            tree = root.getroottree()
            tags = tree.xpath(xpath)
#            print(tags)
            items = __taglist_to_dict(tags, fields)
            data.extend(items)
            current += 1
            if pagesize != -1 and len(items) < pagesize:
                logging.info('Breaking loop. %d vs %d' % (len(items), pagesize))
                break
            if end != -1 and current == end+1:
                logging.info('Breaking loop. %d vs %d' % (len(items), pagesize))
                break


    has_urltagtype = False
    for tagtype in URL_TAG_TYPES:
        if tagtype in fields:
            has_urltagtype = True
    if absolutize and has_urltagtype:
        for i in range(0, len(data)):
            for tagtype in URL_TAG_TYPES:
                if tagtype not in data[i].keys(): continue
                if data[i][tagtype][:6] not in ['http:/', 'https:'] and len(data[i][tagtype]) > 0:
                    data[i][tagtype] = urljoin(url, data[i][tagtype])
    if output:
        io = open(output, 'w', encoding='utf8')
    else:
        io =  open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
    if format == 'text':
        writer = csv.DictWriter(io, fieldnames=fields)
        writer.writeheader()
        for item in data:
            writer.writerow(item)
    elif format == 'csv':
        writer = csv.DictWriter(io, fieldnames=fields)
        writer.writeheader()
        for item in data:
            writer.writerow(item)
    elif format == 'json':
        io.write(json.dumps(data, indent=4 ))
    pass


@click.group()
def cli2():
    pass

@cli2.command()
@click.option('--url', default='url', help='URL to parse')
@click.option('--pattern', default='simpleul', help='Scraper pattern')
@click.option('--nodeid', default=None, help='Node id in html')
@click.option('--nodeclass', default=None, help='Node "class" in html')
@click.option('--fieldnames', default=None, help='Fieldnames. If not set, default names used')
@click.option('--absolutize', default=False, help='Absolutize urls')
@click.option('--format', default='text', help='Output format')
@click.option('--pagekey', default=False, help='Pagination url parameter')
@click.option('--pagerange', default=False, help='Pagination range as start,end,step, like "1,24,1"')
@click.option('--output', default=None, help='Output filename')
def use(url, pattern, nodeid, nodeclass, fieldnames, absolutize, format, pagekey, pagerange, output):
    """Uses predefined pattern to extract page data"""

    findata = []
    pat = PATTERNS[pattern]
    fields = fieldnames.split(',') if fieldnames else pat['deffields']

    if pagekey is False:
        root = _get_cached_url(url)
        tree = root.getroottree()
        findata = PATTERNS[pattern]['func'](tree, nodeclass, nodeid, fields)
    else:
        start, end, step = map(int, pagerange.split(','))
        for i in range(start, end, step):
            anurl = url + '?%s=%d' % (pagekey,i)
            print('Processing url %s' % (anurl))
            root = _get_cached_url(url)
            tree = root.getroottree()
            findata.extend(PATTERNS[pattern]['func'](tree, nodeclass, nodeid, fields))

    has_urltagtype = False
    if fields is not None:
        for tagtype in URL_TAG_TYPES:
            if tagtype in fields:
                has_urltagtype = True
    if absolutize and has_urltagtype:
        for i in range(0, len(data)):
            for tagtype in URL_TAG_TYPES:
                if tagtype not in data[i].keys(): continue
                if findata[i][tagtype][:6] not in ['http:/', 'https:'] and len(data[i][tagtype]) > 0:
                    findata[i][tagtype] = urljoin(url, data[i][tagtype])
    # Instead error let's force json output if it's the only way
    if pat['json_only']: format = 'json'

    if output:
        io = open(output, 'w', encoding='utf8')
    else:
        io =  open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
    if format == 'text':
        writer = csv.DictWriter(io, fieldnames=fields)
        writer.writeheader()
        for item in findata:
            writer.writerow(item)
    elif format == 'csv':
        writer = csv.DictWriter(io, fieldnames=fields)
        writer.writeheader()
        for item in findata:
            writer.writerow(item)
    elif format == 'json':
        io.write(json.dumps(findata, indent=4 ))
    pass


@click.group()
def cli3():
    pass

@cli3.command()
@click.option('--url', default='url', help='URL to parse')
@click.option('--nodeid', default=None, help='Node id in html')
@click.option('--nodeclass', default=None, help='Node "class" in html')
@click.option('--fieldnames', default=None, help='Fieldnames. If not set, default names used')
@click.option('--format', default='text', help='Output format')
@click.option('--pagekey', default=False, help='Pagination url parameter')
@click.option('--pagerange', default=False, help='Pagination range as start,end,step, like "1,24,1"')
@click.option('--output', default=None, help='Output filename')
def gettable(url, nodeid, nodeclass, fieldnames, format, pagekey, pagerange, output):
    """Extracts table with data from html"""
    if pagekey is False:
        root = _get_cached_url(url)
        tree = root.getroottree()
        if nodeclass:
            xfilter = "//table[@class='%s']" % (nodeclass)
        elif nodeid:
            xfilter = "//table[@id='%s']" % (nodeid)
        else:
            xfilter = '//table'
        tags = tree.xpath(xfilter)
        if len(tags) > 0:
            findata = __table_to_dict(tags[0], strip_lf=True)
        else:
            findata = []
    else:
        findata = []
        start, end, step, pagesize = map(int, pagerange.split(','))
#        for i in range(start, end, step):
        current = start
        while True:
            anurl = url + '?%s=%d' % (pagekey,current)
            logging.info('Crawling url %s' % (anurl))
            root = _get_cached_url(anurl)
            logging.info('Got url %s' % (anurl))
            tree = root.getroottree()
            if nodeclass:
                xfilter = "//table[@class='%s']" % (nodeclass)
            elif nodeid:
                xfilter = "//table[@id='%s']" % (nodeid)
            else:
                xfilter = '//table'
            tags = tree.xpath(xfilter)
            if len(tags) > 0:
                items = __table_to_dict(tags[0], strip_lf=True)
                findata.extend(items)
            else:
                items = []

            current += 1
            if pagesize != -1 and len(items) < pagesize:
                logging.info('Breaking loop. %d vs %d' % (len(items), pagesize))
                break
            if end != -1 and current == end+1:
                logging.info('Breaking loop. %d vs %d' % (len(items), pagesize))
                break

    if output:
        io = open(output, 'w', encoding='utf8')
    else:
        io =  open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
    if format == 'text':
        writer = csv.writer(io)
        if fieldnames:
            writer.writerow(fieldnames.split(','))
        for item in findata:
            writer.writerow(item)
    elif format == 'csv':
        writer = csv.writer(io)
        if fieldnames:
            writer.writerow(fieldnames.split(','))
        for item in findata:
            writer.writerow(item)
    elif format == 'json':
        io.write(json.dumps(findata, sort_keys=True, indent=4 ))
    pass


cli = click.CommandCollection(sources=[cli1, cli2, cli3])

if __name__ == '__main__':
    cli()
