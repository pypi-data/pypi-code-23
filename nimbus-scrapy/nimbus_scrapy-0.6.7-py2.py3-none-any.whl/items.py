# -*- coding: utf-8 -*-
from __future__ import absolute_import
import scrapy
from scrapy.contrib.loader import ItemLoader


class CrawledItem(scrapy.Item):
    url = scrapy.Field()


class ScrapItem(scrapy.Item):
    url = scrapy.Field()


