# coding=utf-8
import hashlib
import re


def gen_md5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()


def get_links(html):
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)

