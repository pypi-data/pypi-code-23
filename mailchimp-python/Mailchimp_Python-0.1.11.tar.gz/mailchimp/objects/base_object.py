# coding=utf-8
from dateutil import parser


class BaseObject(object):
    item_url = None
    valid_search_params = ['offset', 'count', 'fields', 'exclude_fields']

    def _parse_date(self, date_string):
        return parser.parse(date_string)

    def __str__(self):
        if hasattr(self, 'id'):
            return "%s" % self.id
        else:
            return ""

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.__str__())
