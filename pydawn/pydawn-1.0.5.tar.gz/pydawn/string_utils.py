# coding=utf-8
import hashlib
import re
from urlparse import urlparse


def gen_md5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()


def refine_urls(host, seed_url, urls):
    urls = sorted(list(set(urls)))
    refined_urls = []
    seed_uri = urlparse(seed_url)
    for url in urls:
        uri = urlparse(url)
        if len(uri.netloc) == 0:
            path = seed_uri.path + url
            path = path.replace("//", "/")
            url = seed_uri.scheme + "://" + seed_uri.netloc + path
        elif url.find(host) == -1:
            continue

        refined_urls.append(url.strip())

    refined_urls = sorted(list(set(refined_urls)))
    return refined_urls


def get_links(host, seed_url, html):
    url_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return refine_urls(host, seed_url, url_regex.findall(html))

