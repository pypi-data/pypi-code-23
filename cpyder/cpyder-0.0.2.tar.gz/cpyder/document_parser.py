# encoding=utf8
# author=spenly
# mail=i@spenly.com

from lxml import etree, html
import json
from .utils import print_msg

"""
These are functions based on lxml.etree and it is a structured document and functions set.
But we always do not need its all functions, so these make it simpler.
"""


def document(str_doc, doc_type="html"):
    """
    build the html, xml or json to a document
    :param str_doc: string object
    :param doc_type: document type: html,xml,json
    :return: html and xml will return a document of lxml.etree, json
    """
    if len(str_doc) == 0:
        print_msg("invalid document string !")
        return None
    if not isinstance(str_doc, str):
        str_doc = str_doc.decode("utf8")
    doc_type = doc_type.lower().strip()
    if doc_type == "html":
        parser = etree.HTMLParser()
        doc = html.document_fromstring(str_doc, parser)
    elif doc_type == "xml":
        parser = etree.XMLParser()
        doc = html.document_fromstring(str_doc, parser)
    elif doc_type == "json":
        json.load(str_doc)
    else:
        raise Exception("unsupported document type: %s" % doc_type)
    return doc


def select(nodes, select_type="a"):
    """
    based on lxml.etree
    get data from xpath nodes object
    :param nodes: what xpath returns, maybe nodes or str
    :param select_type: select type: 'a' for all values matched, and 'f' just for the first
    :return: return values matched
    """
    res = ""
    if isinstance(nodes, str):
        return nodes
    if isinstance(nodes, list) and len(nodes) > 0 and select_type == "f":
        return select(nodes[0])
    for node in nodes:
        if etree.iselement(node):
            res = res + html.tostring(node, pretty_print=True, encoding='unicode')
        else:
            t_res = len(node.strip()) > 0 and res + ";" + node.strip() or res
            res = len(res.strip()) > 0 and t_res or t_res[1:]
    res = res and res or " "
    return res
