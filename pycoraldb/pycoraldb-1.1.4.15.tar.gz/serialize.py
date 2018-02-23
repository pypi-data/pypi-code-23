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
__modules = None


def register_main_globals(d):
    global __globals
    __globals = d


def register_custom_modules(dir):
    modules = __get_non_main_modules()
    d = __search_modules(dir)
    modules.update(d)


def __get_non_main_modules():
    global __modules
    if __modules is None:
        __modules = {}
        d = __search_modules(os.curdir)
        __modules.update(d)
    return __modules


def __search_modules(base_dir):
    modules = {}
    abs_base_dir = os.path.abspath(base_dir)
    for root, dirs, files in os.walk(abs_base_dir, followlinks=True):
        if abs_base_dir != root and '__init__.py' not in files:
            continue
        for filename in files:
            l_name = filename.lower()
            if not l_name.endswith('.py'):
                continue
            dirname = root[len(abs_base_dir) + 1:]
            s = dirname if l_name == '__init__.py' else os.path.join(dirname, filename[:-3])
            s = s.replace(os.path.sep, '.')
            if s:
                modules[s] = True
    return modules


def __fake():
    modules = __get_non_main_modules()
    faked = []
    for m in __globals.values():
        module_type = '%s' % type(m)
        # if module_type == "<type 'module'>":
        #     filename = getattr(m, '__file__', '')
        #     print 'filename=', filename
        #     if filename:
        #         for dir in __pythonpaths:
        #             if filename.startswith(dir):
        #                 modules[m.__name__] = None
        #                 print 'fake module: [%s]' % (m.__name__)
        #                 break
        if module_type == "<type 'instance'>":
            for module_name in modules:
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
    # print __search_modules('.')
    args = [1]
    b64 = dumps(args)
    print b64
    obj = loads(b64)
    print obj