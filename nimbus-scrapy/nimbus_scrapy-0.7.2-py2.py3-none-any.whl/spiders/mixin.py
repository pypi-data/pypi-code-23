# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys
import json
import datetime
import time
import urlparse
import random
import platform
import copy
import scrapy
from scrapy import signals
from scrapy.spiders import Spider, CrawlSpider, CSVFeedSpider, SitemapSpider, XMLFeedSpider
from scrapy.spiders import Rule, BaseSpider
from scrapy.exceptions import DropItem
from scrapy.exceptions import NotConfigured, IgnoreRequest
from scrapy.http.request.form import FormRequest, Request
from scrapy.http.response.html import HtmlResponse
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url

__all__ = ["BaseMixin", ]


class BaseMixin(object):
    config = None
    version = None
    sid = None
    sname = None
    spider_id = None
    spider_name = None
    spider_config = {}

    _db = None
    _redis = None
    _proxy = None
    
    _spider_max_pages = 10
    _spider_clean_urls = []
    _spider_clean_all = False

    BIN_PATHS = [
        (0, "~/dev/phantomjs-2.1.1-macosx/bin/"),
        (-1, "~/dev/geckodriver/"),
        (-1, "~/dev/"),
        (-1, "~/bin/"),
    ]

    def auto_setup(self, config=None):
        if config is None:
            self.config = None
        elif isinstance(config, basestring):
            self.config = json.loads(config)
        elif isinstance(config, dict):
            self.config = copy.deepcopy(config)
        else:
            raise NotImplementedError
        if self.config is None:
            return
        self.version = self.config.get("version", 0)
        self.sid = self.config.pop("sid", None)
        self.sname = self.config.pop("sname", None)
        self.spider_id = self.config.pop("id", None) or self.config.pop("spider_id", "default")
        self.spider_name = self.config.pop("name", None) or self.config.pop("spider_name", self.name)
        for key, value in self.config.iteritems():
            func = getattr(self, u"_setup_{}".format(key), None) or getattr(self, u"setup_{}".format(key), None)
            if func and callable(func):
                v = func(self.spider_id, value)
                setattr(self, u"_{}".format(key), v)
            elif value:
                setattr(self, key, value)
        self._init_env()
        self.auto_clean()

    def _init_env(self):
        paths = os.environ.get("PATH", "")
        paths = paths.split(os.pathsep)
        for i, p in self.BIN_PATHS:
            paths.insert(i, os.path.expanduser(p))
        os.environ["PATH"] = os.pathsep.join(paths)

    def _setup_db(self, spider_id=None, config=None):
        from ..data import dbclient
        if not isinstance(config, dict):
            raise ValueError(u"ERROR db:{}".format(config))
        dbclient.init(name=spider_id, **config)
        return dbclient.get_session(name=spider_id)

    def _setup_redis(self, spider_id=None, config=None):
        from ..data import redisclient
        if not isinstance(config, dict):
            raise ValueError(u"ERROR redis:{}".format(config))
        connection = redisclient.init(name=spider_id, **config)
        return connection

    def _setup_spider(self, spider_id=None, config=None):
        if not isinstance(config, dict):
            raise ValueError(u"ERROR spider:{}".format(config))
        self.spider_config = copy.deepcopy(config)
        self.spider_max_pages = int(self.spider_config.get("max_pages", self._spider_max_pages)) + 1
        self.spider_clean_urls = self.spider_config.get("clean_urls", self._spider_clean_urls)
        self.spider_clean_all = self.spider_config.get("clean_all", self._spider_clean_all)
        return self.spider_config

    def _setup_spider_config(self, spider_id=None, config=None):
        return self._setup_spider(spider_id=spider_id, config=config)

    def _setup_proxy(self, spider_id=None, config=None):
        if config is None:
            raise ValueError(u"ERROR proxy:{}".format(config))
        return copy.deepcopy(config)

    def get_db(self):
        return self._db

    def get_redis(self):
        return self._redis

    def get_proxy(self):
        return self._proxy

    def get_last_proxy(self):
        if self._proxy and len(self._proxy) > 0:
            return self._proxy[0]
        return None

    def pop_proxy(self):
        if self._proxy and isinstance(self._proxy, list) and len(self._proxy) >= 1:
            count = len(self._proxy) - 1
            index = random.randint(0, count)
            return self._proxy.pop(index)
        return None

    def pop_proxy_url(self):
        proxy = self.pop_proxy()
        if proxy and isinstance(proxy, list) and len(proxy) >= 1:
            return proxy[-1]
        return None

    @property
    def spider_max_pages(self):
        return self._spider_max_pages

    @spider_max_pages.setter
    def spider_max_pages(self, value):
        try:
            if isinstance(value, basestring):
                value = int(value)
            else:
                value = int(value)
        except Exception as e:
            value = None
            pass
        if not isinstance(value, int):
            raise ValueError('max_pages must be an integer !')
        if value <= 0 or value > 100:
            raise ValueError('max_pages must between 0 ~ 100 !')
        self._spider_max_pages = value
        
    @property
    def spider_clean_urls(self):
        return self._spider_clean_urls

    @spider_clean_urls.setter
    def spider_clean_urls(self, value):
        if not isinstance(value, (tuple, list)):
            raise ValueError('clean_urls must be list !')
        self._spider_clean_urls = value

    @property
    def spider_clean_all(self):
        return self._spider_clean_all

    @spider_clean_all.setter
    def spider_clean_all(self, value):
        if not isinstance(value, bool):
            raise ValueError('clean_all must be bool !')
        self._spider_clean_all = value

    def auto_clean(self):
        pass

    def process_item(self, item, spider, **kwargs):
        raise NotImplementedError


