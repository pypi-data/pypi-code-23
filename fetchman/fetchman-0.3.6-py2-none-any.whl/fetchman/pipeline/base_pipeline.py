#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf-8')


class ItemPipeline(object):
    def process_item(self, item):
        raise NotImplementedError
