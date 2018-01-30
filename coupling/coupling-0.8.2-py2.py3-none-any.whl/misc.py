# coding: utf-8

import re
import inspect
import pkgutil
import importlib
import ctypes

import six
from abc import ABCMeta, abstractmethod


import logging
logger = logging.getLogger(__name__)


def rreload(module, pattern):
    imp_loader = pkgutil.get_loader(module)
    if imp_loader.is_package(module.__name__):
        for module_loader, sub_module_name, is_pkg in pkgutil.iter_modules(path=module.__path__):
            if is_pkg or (not is_pkg and re.match(pattern, sub_module_name)):
                sub_module = importlib.import_module(module.__name__ + "." + sub_module_name)
                rreload(sub_module, pattern)
    else:
        logger.debug("reload %s", module)
        six.moves.reload_module(module)


@six.add_metaclass(ABCMeta)
class ClosingContextManager(object):
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        if exc_info != (None, None, None):
            logger.exception("")
        self.close()

    @abstractmethod
    def close(self):
        pass


_STRING_BOOLEAN_MAPPING = {
    '1': True, 'yes': True, 'true': True, 'on': True,
    '0': False, 'no': False, 'false': False, 'off': False
}


def get_boolean_from_string(s):
    if s.lower() not in _STRING_BOOLEAN_MAPPING:
        raise ValueError('Not a boolean: %s' % s)
    return _STRING_BOOLEAN_MAPPING[s.lower()]


def is_inherited_from_base_classes(cls, method_name, ignore_abstract=False):
    inherited = False
    for mro in cls.__mro__[1:]:
        if ignore_abstract and inspect.isabstract(mro):
            continue

        if hasattr(mro, method_name):
            inherited = True
            break
    return inherited


def ctypes_structure_to_dict(obj, recursive=True):
    d = {}
    for field in getattr(obj, "_fields_"):
        name = field[0]
        value = getattr(obj, name)
        if isinstance(value, ctypes.Structure) and recursive:
            value = ctypes_structure_to_dict(value)
        d[name] = value
    return d


def evaluate(s, global_context=None, local_context=None):
    import re
    import pydoc
    context = local_context or locals()
    try:
        return eval(s, global_context or globals(), context)
    except NameError as err:
        message = str(err)
        logger.debug(message)
        match = re.search(r"name '(\w+)' is not defined", message)
        if match:
            name = match.group(1)
            value = pydoc.locate(name)
            context[name] = value
            logger.debug("add (%s, %s) into context and re-evaluate.", name, value)
            return evaluate(s, global_context, context)

