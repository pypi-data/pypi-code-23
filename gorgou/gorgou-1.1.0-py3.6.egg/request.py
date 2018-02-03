#!/usr/bin/env python
# -*- coding: utf8 -*-


import os
import sys
import io
import time
import requests
from lxml import etree

'''
//div[@id=\"list\"]/ul/li
a/@href
div/text()

attrib
text
'''
dire = os.path.dirname(os.path.abspath(__file__))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
t = time.strftime('%Y%m%d', time.localtime())


def writefile(filename, content):
    fi = os.path.join(dire, filename + '.txt')
    with open(fi, 'w', encoding='utf8') as f:
        f.write(content)


def downloadImage(imgUrl, local_filename, fold):
    r = requests.get(imgUrl, stream=True)
    if not os.path.exists(fold):
        os.mkdir(fold)
    path = os.path.join(fold, local_filename)
    with open(path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
        f.close()
    return local_filename


def get_pageitems_by_xpath(url, xpath, fileenc=None, htmldec=None):
    r = requests.get(url)
    if fileenc:
        r.encoding = fileenc
    if r.status_code == 200:
        html = r.text
        return get_htmlitems_by_xpath(html, xpath, htmldec)


def get_htmlitems_by_xpath(html, xpath, htmldec=None):
    if htmldec:
        html = html.decode(htmldec)
    page = etree.HTML(html)
    rows = page.xpath(xpath)
    return rows
