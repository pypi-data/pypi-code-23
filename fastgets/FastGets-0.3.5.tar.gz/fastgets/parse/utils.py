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


def is_url(url):
    # 复制并修改自: mongoengine/fields.py URLField()

    _URL_REGEX = re.compile(
        r'^(?:[a-z0-9\.\-]*)://'  # scheme is validated separately
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    _URL_SCHEMES = ['http', 'https', 'ftp', 'ftps']

    if not url:
        return False

    scheme = url.split('://')[0].lower()
    if scheme not in _URL_SCHEMES:
        return False

    if not _URL_REGEX.match(url):
        return False

    return True


def is_email(email):
    # 复制并修改自: mongoengine/fields.py EmailField()

    EMAIL_REGEX = re.compile(
        # dot-atom
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
        # quoted-string
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'
        # domain (max length of an ICAAN TLD is 22 characters)
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|[A-Z0-9-]{2,}(?<!-))$', re.IGNORECASE
    )

    if not email:
        return False

    if not EMAIL_REGEX.match(email):
        return False

    return True
