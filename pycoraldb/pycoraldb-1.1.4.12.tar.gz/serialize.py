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
        __unfake(faked)


# ---------------------------------------------------------------------
# set classes's module in current directory modules to __main__, fake dill to serialize them.

__globals = {}
__pythonpaths = [os.path.abspath(os.curdir)]


def set_main_globals(d):
    global __globals
    __globals = d


def set_python_path(dir):
    global __pythonpaths
    __pythonpaths[dir] = None


def __fake():
    module_names = {}
    faked = []
    for m in __globals.values():
        module_type = '%s' % type(m)
        if module_type == "<type 'module'>":
            filename = getattr(m, '__file__', '')
            if filename:
                for dir in __pythonpaths:
                    if filename.startswith(dir):
                        module_names[m.__name__] = None
                        break
        elif module_type == "<type 'instance'>":
            for module_name in module_names:
                if str(m.__class__).startswith(module_name):
                    faked.append((m.__class__, m.__class__.__module__))  # backup
                    m.__class__.__module__ = '__main__'
                    break
    return faked


def __unfake(faked):
    # restore module name is unnecessary
    # for m, v in faked:
    #     m.__module__ = v
    return


if __name__ == '__main__':
    args = [1]
    b64 = dumps(args)
    print b64
    obj = loads(b64)
    print obj