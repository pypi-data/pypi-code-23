# --
# Copyright (c) 2008-2018 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
# --

"""Generate the content to return to the browser"""

from lxml import etree

import peak.rules
import lxml.html

from nagare.namespaces import xml, xhtml_base


@peak.rules.abstract
def serialize(output, content_type, doctype, declaration):
    """Generic method to generate the content for the browser

    In:
      - ``output`` -- the rendered content
      - ``content_type`` -- the rendered content type
      - ``doctype`` -- the (optional) doctype
      - ``declaration`` -- is the XML declaration to be outputed?

    Return:
      - a tuple (content_type, content)
    """
    return content_type, str(output)


@peak.rules.when(serialize, (xhtml_base._HTMLTag,))
def serialize(next_method, output, content_type, doctype, declaration):
    """Generic method to generate a (X)HTML text from a tree

    In:
      - ``output`` -- the rendered content
      - ``content_type`` -- the rendered content type
      - ``doctype`` -- the (optional) doctype
      - ``declaration`` -- is the XML declaration to be outputed?

    Return:
      - a tuple (content_type, content)
    """
    if 'xmlns' in output.attrib:
        # Let ``lxml`` generate the correct namespaces
        del output.attrib['xmlns']

    if content_type == 'application/xhtml+xml':
        # The browser accepts XHTML
        output = next_method(output, content_type, doctype, declaration)[1]
    else:
        # The browser only accepts HTML
        lxml.html.xhtml_to_html(output)

        output = output.write_htmlstring(pretty_print=True, doctype=doctype if declaration else None)

    return content_type, output


@peak.rules.when(serialize, (xml._Tag,))
def serialize(next_method, output, content_type, doctype, declaration):
    """Generic method to generate a XML text from a tree

    In:
      - ``output`` -- the rendered content
      - ``content_type`` -- the rendered content type
      - ``doctype`` -- the (optional) doctype
      - ``declaration`` -- is the XML declaration to be outputed?

    Return:
      - a tuple (content_type, content)
    """
    if content_type == 'text/html':
        output = next_method(output, content_type, doctype, declaration)[1]
    else:
        output = output.write_xmlstring(xml_declaration=declaration, doctype=doctype if declaration else None)

    return content_type, output


@peak.rules.when(serialize, (etree._Element,))
def serialize(output, content_type, doctype, declaration):
    """Generic method to generate a XML text from a tree

    In:
      - ``output`` -- the rendered content
      - ``content_type`` -- the rendered content type
      - ``doctype`` -- the (optional) doctype
      - ``declaration`` -- is the XML declaration to be outputed?

    Return:
      - a tuple (content_type, content)
    """
    if content_type == 'text/html':
        lxml.html.xhtml_to_html(output)
        method = 'html'
        pretty_print = True
    else:
        method = 'xml'
        pretty_print = False

    return (
        content_type,
        etree.tostring(
            output, encoding='utf-8', method=method, pretty_print=pretty_print,
            xml_declaration=declaration, doctype=doctype if declaration else None
        )
    )


@peak.rules.when(serialize, (str,))
def serialize(output, content_type, doctype, declaration):
    """Generic method to generate a text (or a binary content)

    In:
      - ``output`` -- the rendered content
      - ``content_type`` -- the rendered content type
      - ``doctype`` -- the (optional) doctype
      - ``declaration`` -- is the XML declaration to be outputed?

    Return:
      - a tuple (content_type, content)
    """
    return content_type or 'text/plain', output


@peak.rules.when(serialize, (unicode,))
def serialize(output, content_type, doctype, declaration):
    """Generic method to generate a text from unicode

    In:
      - ``output`` -- the rendered content
      - ``content_type`` -- the rendered content type
      - ``doctype`` -- the (optional) doctype
      - ``declaration`` -- is the XML declaration to be outputed?

    Return:
      - a tuple (content_type, content)
    """
    return serialize(output.encode('utf-8'), content_type, doctype, declaration)


@peak.rules.when(serialize, ((list, tuple),))
def serialize(output, content_type, doctype, declaration):
    """Generic method to generate a text from a list or a tuple

    In:
      - ``output`` -- the rendered content
      - ``content_type`` -- the rendered content type
      - ``doctype`` -- the (optional) doctype
      - ``declaration`` -- is the XML declaration to be outputed?

    Return:
      - a tuple (content_type, content)
    """
    if not output:
        return content_type, ''

    first = serialize(output[0], content_type, doctype, declaration)[1]
    second = ''.join(serialize(e, content_type, doctype, False)[1] for e in output[1:])

    return content_type, first + second
