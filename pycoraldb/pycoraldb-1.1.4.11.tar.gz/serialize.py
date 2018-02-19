#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import base64

import dill as pickle


def loads(b64):
    try:
        return pickle.loads(base64.b64decode(b64))
    except BaseException, e:
        raise Exception('decode obj failed: %s' % e)


def dumps(obj):
    faked = __fake()
    try:
        return base64.b64encode(pickle.dumps(obj, recurse=True))
    except BaseException, e:
        raise Exception('encode obj failed: %s' % e)
    finally:
        pass
        #__unfake(faked)


# ---------------------------------------------------------------------
# set classes's module in current directory modules to __main__, fake dill to serialize them.

__globals = {}


def set_main_globals(d):
    global __globals
    __globals = d


def __fake():
    cur_dir = os.path.abspath(os.curdir)
    modules_in_cur_dir = {}
    faked = []
    for m in __globals.values():
        __module = '%s' % type(m)
        if __module == "<type 'module'>":
            if getattr(m, '__file__', '').startswith(cur_dir):
                modules_in_cur_dir[m.__name__] = None
        elif __module == "<type 'instance'>":
            for module in modules_in_cur_dir:
                if str(m.__class__).startswith(module):
                    faked.append((m.__class__, m.__class__.__module__))  # backup
                    m.__class__.__module__ = '__main__'
                    break
    return faked


def __unfake(faked):
    for m, v in faked:
        m.__module__ = v


if __name__ == '__main__':
    args = [1]
    b64 = dumps(args)
    print b64
    obj = loads(b64)
    print obj