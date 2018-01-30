# -*- coding: utf-8 -*-

import pydoc
import six
from abc import ABCMeta, abstractmethod, abstractproperty
from enum import Enum
from ..misc import get_boolean_from_string, evaluate
from lxml import etree


def is_expression(value):
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("#{"):
            if s.endswith("}"):
                return True
            else:
                raise ValueError("Expression should starts with '#{' and ends with '}'")
    return False


class Scope(Enum):
    PROTOTYPE = "prototype"
    SINGLETON = "singleton"

    @classmethod
    def value_of(cls, s):
        if s == "prototype":
            return cls.PROTOTYPE
        elif s == "singleton":
            return cls.SINGLETON
        else:
            raise AttributeError


class InvalidObjectScope(Exception):
    pass


@six.add_metaclass(ABCMeta)
class BaseParser(object):
    NAMESPACE = None

    @abstractmethod
    def parse(self, element, container):
        pass


@six.add_metaclass(ABCMeta)
class NamespaceHandler(object):
    parsers = {}

    @abstractproperty
    def NAMESPACE(self):
        pass

    def parse(self, element, container):
        return self.find_parser(element).parse(element, container)

    def find_parser(self, element):
        parser = self.parsers.get(etree.QName(element).localname)
        if parser is None:
            msg = "Can't find parser for %s." % element
            raise KeyError(msg)
        return parser

    def register_parser(self, element_name, parser):
        self.parsers[element_name] = parser


@six.add_metaclass(ABCMeta)
class BaseDef(object):
    @abstractmethod
    def get_actual_value(self, container, extra_map=None):
        raise NotImplementedError


class ValueDef(BaseDef):
    def __init__(self, value):
        self.value = value

    def get_actual_value(self, container, extra_map=None):
        return self.value


class ObjectDef(BaseDef):
    def __init__(self, id, cls, scope=Scope.SINGLETON, lazy_init=False):
        super(ObjectDef, self).__init__()
        self.id = id
        self.cls = cls
        self.scope = scope
        self.lazy_init = lazy_init
        self.args = []
        self.kwargs = {}
        self.props = {}
        self.value = None   # will be set when scope is SINGLETON.

    def get_actual_value(self, container, extra_map=None):
        if self.id is None:
            if self.scope == Scope.SINGLETON:
                value = getattr(self, "value", None)
                if value is None:
                    value = container.create_object(self)
                    self.value = value
                return value
            elif self.scope == Scope.PROTOTYPE:
                value = container.create_object(self)
                return value
            else:
                raise InvalidObjectScope
        return container.get_object(self.id)

    def __repr__(self):
        return "<ObjectDef(id:%s, class:%s, scope:%s, lazy_init=%s)>" % (self.id, self.cls, self.scope, self.lazy_init)


class BasicValueDef(ValueDef):
    def __init__(self, value, type):
        if type not in (str, int, float, bool):
            raise ValueError
        super(BasicValueDef, self).__init__(value)
        self.type = type

    def get_actual_value(self, container, extra_map=None):
        if self.value is None:
            return None

        if self.type is str:
            return self.value
        elif self.type is bool:
            return get_boolean_from_string(self.value)
        else:
            return self.type(self.value)


class CallableValueDef(ValueDef):
    def get_actual_value(self, container, extra_map=None):
        return pydoc.locate(self.value)


class ExpressionValueDef(ValueDef):
    def get_actual_value(self, container, extra_map=None):
        extra_map = extra_map or {}
        s = self.value.strip()[2:-1]
        local_context = dict()
        local_context.update(container.objects)
        local_context.update(extra_map)
        return evaluate(s, globals(), local_context)


class ReferenceValueDef(ValueDef):
    def get_actual_value(self, container, extra_map=None):
        if extra_map is not None and self.value in extra_map:
            return extra_map[self.value]
        return container.get_object(self.value)


class ListValueDef(ValueDef):
    def get_actual_value(self, container, extra_map=None):
        for i in list(range(len(self.value))):
            if isinstance(self.value[i], BaseDef):
                self.value[i] = self.value[i].get_actual_value(container, extra_map)
        return self.value


class DictValueDef(ValueDef):
    def get_actual_value(self, container, extra_map=None):
        for k in self.value.keys():
            v = self.value[k]
            if isinstance(v, BaseDef):
                value = v.get_actual_value(container, extra_map)
            elif isinstance(v, list):
                value = ListValueDef(v).get_actual_value(container, extra_map)
            elif isinstance(v, dict):
                value = DictValueDef(v).get_actual_value(container, extra_map)
            elif is_expression(v):
                value = ExpressionValueDef(v).get_actual_value(container, extra_map)
            else:
                value = v
            self.value[k] = value
        return self.value
