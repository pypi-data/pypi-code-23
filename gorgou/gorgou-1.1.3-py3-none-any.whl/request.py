#!/usr/bin/env python
# -*- coding: utf8 -*-


import os
import requests
from lxml import etree

'''
//div[@id=\"list\"]/ul/li
a/@href
div/text()

attrib
text
'''


def downloadImage(imgUrl, fold, local_filename):
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
