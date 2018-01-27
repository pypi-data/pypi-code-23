# -*- coding: utf-8 -*-
from __future__ import absolute_import
from dateutil.parser import parse
import scrapy
from scrapy.loader.processors import Join, MapCompose, TakeFirst, Identity
from scrapy.loader.processors import Compose, SelectJmes, MergeDict
from w3lib.html import remove_tags
from scrapy.contrib.loader import ItemLoader


class CrawledItem(scrapy.Item):
    url = scrapy.Field()


class ScrapItem(scrapy.Item):
    url = scrapy.Field()


