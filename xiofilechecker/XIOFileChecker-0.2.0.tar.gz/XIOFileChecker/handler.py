#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :platform: Unix
    :synopsis: Class to handle filename for XIOFileChecker.

"""

import re
from utils.constants import *
from utils.custom_exceptions import *


class Filename(object):
    """
    Handler providing methods to deal with filename patterns.

    """
    def __init__(self, filename, filters):
        # Reformat filename pattern
        self.filename = filename
        self.filename = re.sub('%start_date%', 'startdate', self.filename)
        self.filename = re.sub('%end_date%', 'enddate', self.filename)
        if not self.filename.endswith('.nc'):
            self.filename += '.nc'
        # Filename attributes as dict(): {institute: 'IPSL', project : 'CMIP5', ...}
        try:
            self.attributes = re.search(CMIP6_FILENAME_PATTERN, self.filename).groupdict()
        except:
            raise ExpressionNotMatch(self.filename, CMIP6_FILENAME_PATTERN)
        # Facet filters as dict(): {institute: 'REGEX', project : 'REGEX', ...}
        self.filters = dict.fromkeys(self.attributes)
        if filters:
            for k in self.filters.keys():
                if filters.has_key(k):
                    self.filters[k] = filters[k]


    def get_attrs(self):
        return self.attributes


    def in_scope(self):
        scope = dict.fromkeys(self.attributes)
        for k, v in self.attributes.items():
            if self.filters[k]:
                if re.search(self.filters[k], v):
                    scope[k] = True
                else:
                    scope[k] = False
            else:
                # Default: None = True as no filter
                scope[k] = True
        return True if all(scope.values()) else False

    def mask(self, facets):
        for facet in facets:
            del(self.attributes[facet])
        return self.get_attrs()