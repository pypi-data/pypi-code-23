# -*- coding: utf-8 -*-
"""
Package Description

Configuration
=================================================================================
{
    "id": "user spider's id",
    "name": "user spider's name",
    "sid": "spider's id",
    "sname": "spider's name",
    "db": {
        "db_uri": "{dialect}{user}:{password}@{host}:{port}/{db}",
        "dialect": "postgresql://",
        "host": "xxx.xxx.xxx.xxx",
        "port": "5432",
        "db": "xxx",
        "user": "xxx",
        "password": "xxx"
    },
    "redis": {
        "host": '127.0.0.1',
        "port": 6379,
        "db": 0,
        "password": None
    },
    "proxy": [
        "http://123.234.234.2:8000",
    ],
    "spider": {
        "max_pages": 2,
        "clean_urls": [[uid, url], ],
        "date": {
            "period": "days",
            "every": 5,
        },
        "keywords": ["KEY1", "KEY2", ]
    }
}

"""
import os
import sys
import json
import logging
import datetime
import time
import urlparse
import random
import platform
import hashlib
import uuid
import traceback
import scrapy
from scrapy import signals
from scrapy.spiders import Spider, CrawlSpider, CSVFeedSpider, SitemapSpider, XMLFeedSpider
from scrapy.spiders import Rule
from scrapy.http.request.form import FormRequest, Request
from scrapy.http.response.html import HtmlResponse
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from bs4 import BeautifulSoup

from .mixin import BaseMixin
from . import utils


class AbstractSpider(BaseMixin, Spider):
    name = None
    allowed_domains = []
    start_urls = []

    def start_requests(self):
        return super(AbstractSpider, self).start_requests()

    def parse(self, response):
        raise NotImplementedError

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        config = kwargs.pop("config", None)
        spider = super(AbstractSpider, cls).from_crawler(crawler, *args, **kwargs)
        try:
            spider.log(message=u"NAME: {}".format(spider.name), level=logging.INFO)
            if config is None:
                spider.log(message="config is None", level=logging.ERROR)
            else:
                spider.log(message=config, level=logging.DEBUG)
                spider.setup(config)
                spider.log(u"CONFIG sid:[{sid}] sname:[{sname}] version: [{version}]".format(sid=spider.sid, sname=spider.sname, version=spider.version), level=logging.INFO)
                spider.log(u"CONFIG spider_id:[{spider_id}] spider_name:[{spider_name}]".format(spider_id=spider.spider_id, spider_name=spider.spider_name), level=logging.INFO)
                spider.log(u"CONFIG config: {config}".format(config=json.dumps(spider.config, ensure_ascii=False, indent=2)), level=logging.INFO)
                spider.log(u"SPIDER spider_config: {config}".format(config=json.dumps(spider.spider_config, ensure_ascii=False, indent=2)), level=logging.INFO)
                spider.clean_auto()
        except ValueError as e:
            spider.log(e, level=logging.ERROR)
            raise e
        except Exception as e:
            spider.log(e, level=logging.ERROR)
            traceback.print_exc()
        return spider

    def get_browser(self, proxy=None, path=None, **kwargs):
        if path:
            browser = webdriver.PhantomJS(path, **kwargs)
            capabilities = webdriver.DesiredCapabilities.PHANTOMJS
        elif platform.system() == "Linux":
            browser = webdriver.PhantomJS(**kwargs)
            capabilities = webdriver.DesiredCapabilities.PHANTOMJS
        elif platform.system() == "Windows":
            browser = webdriver.PhantomJS(**kwargs)
            capabilities = webdriver.DesiredCapabilities.PHANTOMJS
        else:
            path = os.path.expanduser("~/dev/phantomjs/bin/phantomjs")
            browser = webdriver.PhantomJS(path)
            capabilities = webdriver.DesiredCapabilities.PHANTOMJS
            # browser = webdriver.Safari()
            # capabilities = webdriver.DesiredCapabilities.SAFARI
        if proxy:
            webproxy = webdriver.Proxy()
            webproxy.proxy_type = ProxyType.MANUAL
            webproxy.http_proxy = proxy
            webproxy.add_to_capabilities(capabilities)
            browser.start_session(capabilities)
        return browser

    def get_md5(self, data=None):
        m = hashlib.md5()
        m.update(data)
        return m.hexdigest()

    def get_crawled(self):
        redis = self.get_redis()
        if self.spider_id and redis:
            keys = redis.keys(u'{spider_id}*'.format(spider_id=self.spider_id))
        else:
            keys = []
        return keys

    def get_url_id(self, url=None):
        if self.spider_id and url:
            return u"{}_{}".format(self.spider_id, self.get_md5(url))
        return None

    def is_crawled(self, url=None):
        url_id = self.get_url_id(url=url)
        redis = self.get_redis()
        if redis and url_id:
            return redis.exists(url_id)
        return False

    def set_crawled(self, url=None):
        url_id = self.get_url_id(url=url)
        redis = self.get_redis()
        if redis and url_id:
            return redis.set(url_id, url)
        return False

    def generate_uid(self):
        return uuid.uuid4().hex

    def trim_value(self, value, index=0):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, (tuple, list)) and len(value) > index:
            return value[index]
        elif isinstance(value, (int, long, float)):
            return value

    def clean_all(self):
        redis = self.get_redis()
        if redis:
            keys = redis.keys(u'{spider_id}*'.format(spider_id=self.spider_id))
            for key in keys:
                redis.delete(key)

    def clean_url(self, url=None):
        key = self.get_url_id(url=url)
        redis = self.get_redis()
        if key and redis:
            redis.delete(key)

    def clean_key(self, key=None):
        redis = self.get_redis()
        if key and redis:
            redis.delete(key)

    def clean_db(self, uids=None):
        raise NotImplementedError

    def clean_db_all(self):
        raise NotImplementedError

    def clean_auto(self):
        if self.spider_clean_all:
            self.clean_all()
        elif self.spider_clean_urls and isinstance(self.spider_clean_urls, (list, tuple,)) and len(self.spider_clean_urls) > 0:
            uids = []
            for uid, url in self.spider_clean_urls:
                uids.append(uid)
                self.clean_url(url=url)
            if uids:
                self.clean_db(uids=uids)

