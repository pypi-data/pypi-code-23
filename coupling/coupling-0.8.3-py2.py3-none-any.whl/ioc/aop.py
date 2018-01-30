# -*- coding: utf-8 -*-

import six
from abc import ABCMeta, abstractmethod

from .base import ObjectDef, ReferenceValueDef, NamespaceHandler, BaseParser, ListValueDef
from .objects import XmlObjectDefParser
from lxml import etree
import logging
logger = logging.getLogger(__name__)


class XmlAopNamespaceHandler(NamespaceHandler):
    NAMESPACE = "coupling/aop"

    def __init__(self):
        self.register_parser("config", XmlConfigParser())


class XmlConfigParser(BaseParser):
    def parse(self, element, context):
        v = []
        for sub_element in list(element):
            if etree.QName(sub_element).localname == "proxy":
                proxy_def = self.parse_proxy_element(sub_element, context)
                v.append(proxy_def)
        return ListValueDef(v)

    @classmethod
    def parse_proxy_element(cls, element, context):
        target = element.get("target")
        l = []
        for sub_element in list(element):
            if etree.QName(sub_element).localname == "intercept":
                method = sub_element.get("method")
                list_def = XmlObjectDefParser.get_value_def(sub_element)
                for obj_def in list_def.value:
                    if not isinstance(obj_def, ObjectDef):
                        raise ValueError("")
                    obj_def.props["method"] = method
                    l.append(obj_def)
        proxy_def = ObjectDef(target, AopProxy)
        proxy_def.args.append(ReferenceValueDef(target))
        proxy_def.args.append(ListValueDef(l))
        context.proxy_defines[target] = proxy_def
        return proxy_def


@six.add_metaclass(ABCMeta)
class MethodInterceptor(object):
    def __init__(self, method=None):
        self.method = method

    @abstractmethod
    def invoke(self, invocation):
        pass


class MethodInvocation(object):
    def __init__(self, instance, method_name, args, kwargs, interceptors):
        self.instance = instance
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs
        self.interceptors = interceptors
        self.iterator = iter(self.interceptors)

    def proceed(self):
        # proceed -> interceptor.invoke -> proceed -> ...
        try:
            interceptor = next(self.iterator)
            logger.debug("Calling %s.%s(%s, %s)" % (interceptor.__class__.__name__, self.method_name, self.args, self.kwargs))
            return interceptor.invoke(self)
        except StopIteration:
            return getattr(self.instance, self.method_name)(*self.args, **self.kwargs)


class AopProxy(object):
    def __init__(self, target, interceptors):
        self.target = target
        self.interceptors = interceptors

    # def __getattr__(self, name):
    #     attr = getattr(self.target, name)
    #     if not callable(attr):
    #         return attr
    #
    #     def dispatch(*args, **kwargs):
    #         invocation = MethodInvocation(self.target, name, args, kwargs, self.interceptors)
    #         return invocation.proceed()
    #     return dispatch

    def __getattr__(self, name):
        attr = getattr(self.target, name)
        if not callable(attr):
            return attr
        else:
            interceptors = []
            for interceptor in self.interceptors:
                if interceptor.method is not None:
                    if name == interceptor.method:
                        interceptors.append(interceptor)
                else:
                    interceptors.append(interceptor)

            if interceptors:
                def dispatch(*args, **kwargs):
                    invocation = MethodInvocation(self.target, name, args, kwargs, interceptors)
                    return invocation.proceed()
                return dispatch
            else:
                return attr
