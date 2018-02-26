# coding=utf-8
from lxml import etree


def get_node_text(node):
    return node.xpath('string(.)').strip()


def node_to_text(node):
    return etree.tostring(node, pretty_print=True)
