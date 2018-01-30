# coding: utf-8

import logging
logger = logging.getLogger(__name__)


class AttrDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as err:
            raise AttributeError(err)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as err:
            raise AttributeError(err)

    def __str__(self):
        return '<AttrDict %s>' % dict.__str__(self)
