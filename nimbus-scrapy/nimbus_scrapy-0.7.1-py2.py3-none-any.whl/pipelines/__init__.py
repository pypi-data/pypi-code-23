# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from scrapy.exceptions import DropItem
from ..exceptions import CrawledItemError, ScrapItemError
from ..items import CrawledItem, ScrapItem


class NimbusPipeline(object):

    def process_item(self, item, spider, **kwargs):
        func = getattr(spider, "process_item", None)
        if callable(func):
            try:
                item = func(item=item, spider=spider, **kwargs)
                if isinstance(item, CrawledItem):
                    raise DropItem(u"Crawled item found: %s" % item['url'])
                elif isinstance(item, ScrapItem):
                    raise DropItem(u"Scrap item found: %s" % item['url'])
            except CrawledItemError as e:
                spider.log(e, level=logging.INFO)
                raise DropItem(e)
            except ScrapItemError as e:
                spider.log(e, level=logging.INFO)
                raise DropItem(e)
        return item

