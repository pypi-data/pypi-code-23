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
        ["http", "http://39.137.83.130:8080"],
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
import six
import json
import logging
import datetime
import time
import random
import platform
import hashlib
import uuid
import traceback
from collections import OrderedDict
import scrapy
from scrapy import signals
from scrapy.spiders import Spider, CrawlSpider, CSVFeedSpider, SitemapSpider, XMLFeedSpider
from scrapy.spiders import Rule
from scrapy.http.request.form import FormRequest, Request
from scrapy.http.response.html import HtmlResponse
from scrapy.http.response.xml import XmlResponse
from scrapy.http.response.text import TextResponse
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url
from scrapy.exceptions import DropItem
from scrapy.contrib.loader.processor import Join, MapCompose, TakeFirst
from scrapy.contrib.loader import ItemLoader
from w3lib.html import remove_tags

from selenium import webdriver
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException, NoSuchElementException
from bs4 import BeautifulSoup
from urlparse import urlparse, urljoin, parse_qs, parse_qsl

from .mixin import BaseMixin
from . import utils

UA_FIREFOX = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0"
UA_SAFARI = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/604.4.7 (KHTML, like Gecko) Version/11.0.2 Safari/604.4.7"
UA_PHANTOMJS = "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/538.1 (KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1"


class AbstractSpider(BaseMixin, Spider):
    name = None
    allowed_domains = []
    start_urls = []

    DEFAULT_UA = UA_FIREFOX
    TIME_TO_WAIT = 30

    _driver = None
    _proxy = None

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
                spider.auto_setup(config)
                spider.log(u"CONFIG sid:[{sid}] sname:[{sname}] version: [{version}]".format(sid=spider.sid, sname=spider.sname, version=spider.version), level=logging.INFO)
                spider.log(u"CONFIG spider_id:[{spider_id}] spider_name:[{spider_name}]".format(spider_id=spider.spider_id, spider_name=spider.spider_name), level=logging.INFO)
                spider.log(u"CONFIG config: {config}".format(config=json.dumps(spider.config, ensure_ascii=False, indent=2)), level=logging.INFO)
                spider.log(u"SPIDER spider_config: {config}".format(config=json.dumps(spider.spider_config, ensure_ascii=False, indent=2)), level=logging.INFO)
        except ValueError as e:
            spider.log(e, level=logging.ERROR)
            raise e
        except Exception as e:
            spider.log(e, level=logging.ERROR)
            traceback.print_exc()
        return spider

    @staticmethod
    def close(spider, reason):
        if isinstance(spider, AbstractSpider):
            spider._close_browser()
        return super(AbstractSpider, spider).close(spider, reason)

    def _get_capabilities(self, capabilities=None, proxy=None):
        if proxy:
            result = urlparse(proxy)
            scheme = result.scheme
            netloc = result.netloc
            webproxy = webdriver.Proxy()
            webproxy.proxy_type = ProxyType.MANUAL
            if scheme == "http":
                webproxy.http_proxy = netloc
            elif scheme == "https":
                webproxy.sslProxy = netloc
            webproxy.add_to_capabilities(capabilities)
        return capabilities

    def _get_webdriver(self, proxy=None, **kwargs):
        userAgent = kwargs.pop("userAgent", self.DEFAULT_UA)
        system = platform.system()

        if system == "Darwin":
            capabilities = webdriver.DesiredCapabilities.PHANTOMJS
            capabilities["phantomjs.page.settings.userAgent"] = userAgent
            capabilities["phantomjs.page.customHeaders.User-Agent"] = userAgent
            capabilities = self._get_capabilities(capabilities=capabilities, proxy=proxy)
            driver = webdriver.PhantomJS(desired_capabilities=capabilities)

            # capabilities = webdriver.DesiredCapabilities.SAFARI
            # capabilities = self._get_capabilities(capabilities=capabilities, proxy=proxy)
            # driver = webdriver.Safari(desired_capabilities=capabilities)

            # capabilities = webdriver.DesiredCapabilities.FIREFOX
            # capabilities = self._get_capabilities(capabilities=capabilities, proxy=proxy)
            # driver = webdriver.Firefox(executable_path=path, capabilities=capabilities)
        else:
            capabilities = webdriver.DesiredCapabilities.PHANTOMJS
            capabilities["phantomjs.page.settings.userAgent"] = userAgent
            capabilities["phantomjs.page.customHeaders.User-Agent"] = userAgent
            capabilities = self._get_capabilities(capabilities=capabilities, proxy=proxy)
            driver = webdriver.PhantomJS(desired_capabilities=capabilities, **kwargs)
        # driver.maximize_window()
        driver.implicitly_wait(self.TIME_TO_WAIT)
        driver.set_script_timeout(self.TIME_TO_WAIT)
        driver.set_page_load_timeout(self.TIME_TO_WAIT)
        return driver, proxy

    def _close_browser(self):
        try:
            if self._driver:
                self._driver.quit()
            self._driver = None
            self._proxy = None
        except Exception as e:
            self.log(e, level=logging.ERROR)
            self._driver = None
            self._proxy = None

    def get_browser(self, proxy=None, **kwargs):
        try:
            if self._driver and self._proxy == proxy:
                return self._driver
            if self._driver:
                self._close_browser()
            self._driver, self._proxy = self._get_webdriver(proxy=proxy, **kwargs)
        except SessionNotCreatedException as e:
            self.log(e, level=logging.ERROR)
            self._close_browser()
            time.sleep(2)
            self._driver, self._proxy = self._get_webdriver(proxy=proxy, **kwargs)
        return self._driver

    def get_base_url(self, response):
        return get_base_url(response=response)

    def get_queryparam(self, query=None):
        try:
            return parse_qs(query)
        except Exception as e:
            self.log(e, level=logging.ERROR)
            return {}

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

    def auto_clean(self):
        if self.spider_clean_all:
            self.clean_all()
        elif self.spider_clean_urls and isinstance(self.spider_clean_urls, (list, tuple,)) and len(self.spider_clean_urls) > 0:
            uids = []
            for uid, url in self.spider_clean_urls:
                uids.append(uid)
                self.clean_url(url=url)
            if uids:
                self.clean_db(uids=uids)

