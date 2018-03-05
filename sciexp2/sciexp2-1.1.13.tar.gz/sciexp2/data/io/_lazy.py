#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Lazy function evaluation.

If possible, loads file from disk, otherwise computes the function and saves it
to disk.

"""

from __future__ import print_function
from __future__ import absolute_import

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2013-2018, Lluís Vilanova"
__license__ = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__ = "llvilanovag@gmail.com"


import collections
import hashlib
import inspect
import os
import pickle
import six
import struct
import sys
import warnings

from sciexp2.common import compat
import sciexp2.data.io


##################################################
# Timestamp retrieval

def __timestamp_none(obj):
    return 0


def __timestamp_find_files(obj):
    source = obj._Result__result()
    times = [0]
    for s in source:
        st = 0
        sf = s["FILE"]
        if six.PY3:
            import io
            file = io.IOBase
        if isinstance(sf, six.string_types) and os.path.exists(sf):
            st = _timestamp_path(sf)
        elif isinstance(sf, file) and os.path.exists(sf):
            st = _timestamp_path(sf.name)
        else:
            st = 0
        times.append(st)
    return max(times)


def _timestamp_path(path):
    if not os.path.exists(path):
        return 0
    return os.stat(path).st_mtime


def __timestamp_sequence(elems):
    if len(elems) == 0:
        return 0
    return max([_timestamp(elem) for elem in elems])


def _timestamp(elem):
    if isinstance(elem, tuple):
        return __timestamp_sequence(elem)
    elif isinstance(elem, set):
        return __timestamp_sequence(elem)
    elif isinstance(elem, dict):
        return max([__timestamp_sequence(elem.keys()),
                    __timestamp_sequence(elem.values())])
    elif isinstance(elem, list):
        return __timestamp_sequence(elem)
    elif isinstance(elem, Result):
        return elem._Result__timestamp()
    elif isinstance(elem, six.string_types):
        return 0
    elif isinstance(elem, collections.Iterable):
        return __timestamp_sequence(elem)
    else:
        return 0


##################################################
# Versioning control

def _version_write(fobj, version):
    fobj.write(struct.pack("I", len(version)))
    fobj.write(version.encode("utf8"))


def _version_read(fobj):
    len_fmt = "I"
    len_size = struct.calcsize(len_fmt)
    version_len = struct.unpack(len_fmt, fobj.read(len_size))[0]
    version = fobj.read(version_len)
    return version


def _version_skip(fobj):
    _version_read(fobj)


def __version_sequence(elems):
    return [_version(elem) for elem in elems]


def _version(elem):
    if isinstance(elem, tuple):
        res = __version_sequence(elem)
        return "tuple([%s])" % ", ".join(res)
    elif isinstance(elem, set):
        res = __version_sequence(elem)
        return "set([%s])" % ", ".join(res)
    elif isinstance(elem, dict):
        res = __version_sequence(six.iteritems(elem))
        return "{%s}" % ", ".join(res)
    elif isinstance(elem, list):
        res = __version_sequence(elem)
        return "[%s]" % ", ".join(res)
    elif isinstance(elem, Result):
        elem._Result__version()
        return elem._Result__version_str
    elif isinstance(elem, six.string_types):
        return repr(elem)
    elif isinstance(elem, collections.Iterable):
        res = __version_sequence(elem)
        return "[%s]" % ", ".join(res)
    elif inspect.isfunction(elem):
        source = inspect.getsource(elem)
        return hashlib.md5(source).hexdigest()
    else:
        return repr(elem)


##################################################
# Function-specific information

def __function_arg_is_lazy(obj):
    if isinstance(obj, dict):
        return any(__function_arg_is_lazy(key) or __function_arg_is_lazy(value)
                   for key, value in six.iteritems(obj))
    elif isinstance(obj, six.string_types):
        return False
    elif isinstance(obj, collections.Iterable):
        return any(__function_arg_is_lazy(i) for i in obj)
    else:
        return isinstance(obj, Result) or isinstance(obj, Method)


def __function_wrap_find_files(arg):
    return sciexp2.data.io._as_find_files(arg)[0]


def _function_parse(func, args, kwargs):
    fargs = compat.InspectBind(func, *args, **kwargs)

    type_ = None
    timestamp = __timestamp_none

    if func == sciexp2.data.io.find_files or \
       func == __function_wrap_find_files:
        type_ = sciexp2.common.instance.InstanceGroup
        timestamp = __timestamp_find_files
    elif (func == sciexp2.data.io.extract_txt or
          func == sciexp2.data.io.extract_regex or
          func == sciexp2.data.io.extract_func):
        type_ = sciexp2.data.Data
        source = Result(__function_wrap_find_files,
                        [fargs.arguments["source"]], {})
        if "source" in kwargs:
            kwargs.pop("source")
            args = [source] + args
        else:
            args = list(args)
            args[0] = source

    return type_, args, kwargs, timestamp


##################################################
# Lazy function / method invocation

class LazySaveError (Exception):
    pass


def _lazy_result(obj):
    if isinstance(obj, Result):
        return obj._Result__result()
    elif isinstance(obj, dict):
        for key, value in six.iteritems(obj):
            obj[_lazy_result(key)] = _lazy_result(value)
        return obj
    elif isinstance(obj, tuple):
        return tuple([_lazy_result(i) for i in obj])
    elif isinstance(obj, list):
        return [_lazy_result(i) for i in obj]
    elif isinstance(obj, six.string_types):
        return obj
    else:
        return obj


def _lazy_outdated(obj):
    if isinstance(obj, Result):
        return obj._Result__outdated()
    elif isinstance(obj, dict):
        return any(_lazy_outdated(key) or _lazy_outdated(value)
                   for key, value in six.iteritems(obj))
    elif isinstance(obj, six.string_types):
        return False
    elif isinstance(obj, collections.Iterable):
        return any(_lazy_outdated(i) for i in obj)
    else:
        return False


class Result (object):

    def __init__(self, func, args, kwargs):
        if not callable(func):
            raise TypeError("Cannot lazily invoke a non-callable")
        self.__func = func

        self.__type, self.__args, self.__kwargs, self.__timestamp_func \
            = _function_parse(func, args, kwargs)

        self.__path = None
        self.__timestamp_num = None
        self.__version_str = None
        self.__version_num = None
        self.__res = None

    def __repr__(self):
        res = "lazy(%s" % self.__func
        if len(self.__args) > 0:
            res += ", " + ", ".join([repr(a) for a in self.__args])
        if len(self.__kwargs) > 0:
            res += ", " + ", ".join(["%s=%s" % (k, repr(v))
                                     for k, v in self.__kwargs.items()])
        res += ")"
        return res

    def __timestamp(self):
        if self.__timestamp_num is None:
            self.__timestamp_num = max(_timestamp(self.__args),
                                       _timestamp(self.__kwargs),
                                       self.__timestamp_func(self))
        return self.__timestamp_num

    def __version(self):
        if self.__version_num is None:
            # track function name and arguments
            ver_args = [_version(a) for a in self.__args]
            ver_kwargs = ["%s=%s" % (k, _version(v))
                          for k, v in six.iteritems(self.__kwargs)]
            ver_all = ", ".join(ver_args + ver_kwargs)
            self.__version_str = "%s.%s(%s)" % (
                self.__func.__module__, self.__func.__name__, ver_all)
            # track function source code
            if inspect.isfunction(self.__func):
                self.__version_str += ": {%s}" % inspect.getsource(self.__func)
            self.__version_num = hashlib.md5(self.__version_str.encode("utf8")).hexdigest()
        return self.__version_num

    def __outdated(self):
        if self.__path is not None and not os.path.exists(self.__path):
            return True
        res = _lazy_outdated(self.__args) or _lazy_outdated(self.__kwargs)
        if self.__path is not None and os.path.exists(self.__path):
            res |= self.__timestamp() >= _timestamp_path(self.__path)
            with open(self.__path, "rb") as fobj:
                res |= self.__version() != _version_read(fobj)
        return res

    ###########################################################
    # Result computation

    def __result_compute(self):
        self.__res = self.__func(*_lazy_result(self.__args),
                                 **_lazy_result(self.__kwargs))

    def __result_save(self):
        assert self.__path is not None
        version = self.__version()
        try:
            with open(self.__path, "wb") as fobj:
                _version_write(fobj, version)
                pickle.dump(self.__res, fobj)
        except Exception as e:
            os.unlink(self.__path)
            _, _, exc_traceback = sys.exc_info()
            new_e = LazySaveError("Cannot save: %s"
                                  "\n  [was] %s: %s" % (
                                      self, e.__class__.__name__, str(e)))
            six.reraise(new_e.__class__, new_e, exc_traceback)

    def __result_load(self):
        with open(self.__path, "rb") as fobj:
            _version_skip(fobj)
            self.__res = pickle.load(fobj)

    def __result(self):
        if self.__res is None:
            if self.__path is not None:
                if self.__outdated():
                    self.__result_compute()
                    self.__result_save()
                else:
                    self.__result_load()
            else:
                self.__result_compute()
        return self.__res

    ##################################################
    # Realization

    def checkpoint(self, path):
        self.__path = path
        return self

    def realize(self, path=None):
        self.__path = path
        return self.__result()

    def __getattr__(self, attr):
        return Method(self, attr)


def _method(obj, func, *args, **kwargs):
    func_obj = getattr(obj, func)
    if not callable(func_obj):
        raise TypeError("Non-callable lazy attribute: %s" % func)
    return func_obj(*args, **kwargs)


class Method:

    def __init__(self, object, func):
        self.__object = object
        self.__func = func

    def __call__(self, *args, **kwargs):
        return Result(_method,
                      [self.__object, self.__func] + list(args),
                      kwargs)

    def __getattr__(self, attr):
        raise Exception("Unsupported nested implicit lazy calls")
