#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import base64

try:
    import dill as pickle
except ImportError:
    import pickle


def loads(b64):
    return pickle.loads(base64.b64decode(b64))


def dumps(obj):
    return base64.b64encode(pickle.dumps(obj, recurse=True, ))


if __name__ == '__main__':
    args = [1]
    b64 = dumps(args)
    print b64
    obj = loads(b64)
    print obj