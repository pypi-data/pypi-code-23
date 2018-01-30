# -*- coding: utf-8 -*-

import os
import collections
from lxml import etree

from .objects import XmlObjectsNamespaceHandler
from .aop import XmlAopNamespaceHandler

import logging
logger = logging.getLogger(__name__)


class XmlConfig(object):
    xsd_file = os.path.join(os.path.dirname(__file__), "schema", "objects.xsd")

    def __init__(self, xml, validate=True):
        if etree.iselement(xml):
            self.root = xml
        else:
            self.root = etree.parse(xml, parser=etree.XMLParser(remove_comments=True)).getroot()

        if validate:
            self.validate()
        self._ns_handlers = {}

        obj_handler = XmlObjectsNamespaceHandler()
        aop_handler = XmlAopNamespaceHandler()

        self.add_namespace_handler(obj_handler.NAMESPACE, obj_handler)
        self.add_namespace_handler(aop_handler.NAMESPACE, aop_handler)

    def add_namespace_handler(self, namespace, handler):
        self._ns_handlers[namespace] = handler

    def validate(self):
        xsd = etree.XMLSchema(file=self.xsd_file)
        xsd.assertValid(self.root)

    def read_object_defines(self, container):
        defines = collections.OrderedDict()
        for sub_element in list(self.root):
            ns = etree.QName(sub_element).namespace
            try:
                handler = self._ns_handlers[ns]
            except KeyError:
                logger.warn("Don't find handler for %s", sub_element)
            else:
                define = handler.parse(sub_element, container)
                logger.debug("Parse %r -> %s", sub_element, define)
                if hasattr(define, "id"):
                    defines[define.id] = define
        return defines
