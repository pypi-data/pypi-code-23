# coding: utf8

import datetime
import re
from lxml import etree, html
import urllib.parse
from ..core.errors import ParseError


INT_PATTERN = re.compile('[0-9]+')
FLOAT_PATTERN = re.compile('[0-9\.]+')


def parse_doc(page_raw):
    return html.fromstring(page_raw)


def parse_node_html(node):
    return etree.tostring(node, encoding='unicode')


def parse_node_text(node):
    texts = node.xpath('.//descendant::text()')
    texts = [
        text.strip()
        for text in texts
    ]
    return ' '.join(texts)


def parse_int(s):
    """
    >>> parse_int('jnb876nk1')
    876
    """
    s = s.strip()
    for each in INT_PATTERN.findall(s):
        try:
            return int(each)
        except ValueError:
            pass

    raise ParseError('cant parse int from {}'.format(s))


def parse_float(s):
    s = s.strip()

    for each in FLOAT_PATTERN.findall(s):
        try:
            return float(each)
        except ValueError:
            pass

    raise ParseError('cant parse float from {}'.format(s))


def parse_time(s):
    s = s.strip()

    hours_ago = re.findall('(\d+)小时前', s)
    if hours_ago:
        # 10小时前
        return datetime.datetime.now() - datetime.timedelta(hours=int(hours_ago[0]))

    if re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', s):
        # 2018-01-13 13:09:44
        return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

    if re.findall('\d{4}-\d{2}-\d{2} \d{2}:\d{2}', s):
        # 2018-01-12 01:12
        return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M')

    if re.findall('\d{4}-\d{2}-\d{2}', s):
        # 2018-01-12
        return datetime.datetime.strptime(s, '%Y-%m-%d')


def parse_url_query(url):
    """
    >>> parse_url_query('http://www.test.com?a=1&b=2')
    {'a': '1', 'b': '2'}
    """
    query_dict = {}
    query_str = url.split('?')[-1]
    query_str = query_str.split('#')[0]
    for query_item_str in query_str.split('&'):
        if len(query_item_str.split('=', 1)) != 2:
            continue
        key, val = query_item_str.split('=', 1)
        query_dict[key] = urllib.parse.unquote(val)
    return query_dict
