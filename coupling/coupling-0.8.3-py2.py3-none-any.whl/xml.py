# -*- coding: utf-8 -*-

from lxml import etree
import logging
logger = logging.getLogger(__name__)


def set_namespaces(element, nsmap):
    new_root = etree.Element(element.tag, nsmap=nsmap)
    for k, v in element.attrib.items():
        new_root.set(k, v)
    new_root[:] = element[:]
    new_root = etree.fromstring(etree.tostring(new_root))
    return new_root
