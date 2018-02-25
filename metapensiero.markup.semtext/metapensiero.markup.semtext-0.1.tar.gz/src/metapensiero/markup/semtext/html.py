# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- HTML parser
# :Created:   sab 01 apr 2017 14:00:33 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Arstecnica s.r.l.
# :Copyright: © 2018 Lele Gaifax
#

from io import StringIO
from itertools import chain
from re import compile

from lxml.html import fragment_fromstring

from .ast import Item, List, ListStyle, Paragraph, Span, SpanStyle, Text
from .exc import UnparsableError
from .text import parse_text
from .visitor import HTMLPrinter, SEMPrinter


SPACES_RX = compile(r'\s+')

def squash_ws(text, empty=None):
    "Squash consecutive whitespaces to a single space."

    if not text:
        return None
    elif text.isspace():
        return empty
    else:
        return SPACES_RX.sub(" ", text)


class Parser:
    "HTML parser based on ``lxml``."

    def __init__(self, top_element, **options):
        self.top_element = top_element
        self.options = options
        self.lists_style_stack = []

    def __call__(self, children):
        handle = self.handle
        elts = []
        for c in children:
            elts.extend(handle(c))
        return self.top_element(elts, **self.options)

    def handle(self, element):
        handler = getattr(self, 'handle_' + element.tag)
        return handler(element)

    def make_paragraph(self, element):
        elts = []

        spans = []
        handle = self.handle

        text = squash_ws(element.text)
        if text:
            spans.append(Span(text))

        partial = False

        children = element.iterchildren()
        for elt in children:
            if elt.tag == 'br':
                tail = squash_ws(elt.tail, " ")
                if tail:
                    elts.append(Paragraph(spans))
                    if spans:
                        ss = spans[-1].style
                        spans = [Span(tail, ss)]
            else:
                if elt.tag not in ('b', 'em', 'i', 'strong'):
                    partial = True
                    break

                spans.extend(handle(elt))

        tail = squash_ws(element.tail, " ")
        if spans and tail:
            spans.append(Span(tail))

        if spans:
            elts.append(Paragraph(spans))

        remaining = chain((elt,), children) if partial else None

        return elts, remaining

    def handle_p(self, element):
        elts, remaining = self.make_paragraph(element)
        assert remaining is None
        return elts

    handle_div = handle_p

    def handle_strong(self, element):
        elts = []
        text = squash_ws(element.text)
        if text:
            elts.append(Span(text, SpanStyle.BOLD))
        tail = squash_ws(element.tail, " ")
        if tail:
            elts.append(Span(tail))
        return elts

    handle_b = handle_strong

    def handle_em(self, element):
        elts = []
        text = squash_ws(element.text)
        if text:
            elts.append(Span(text, SpanStyle.ITALIC))
        tail = squash_ws(element.tail, " ")
        if tail:
            elts.append(Span(tail))
        return elts

    handle_i = handle_em

    def handle_ul(self, element):
        self.lists_style_stack.append(ListStyle.DOTTED)
        items = []
        handle = self.handle
        for elt in element.iterchildren():
            items.extend(handle(elt))
        self.lists_style_stack.pop()
        return [List(items)]

    def handle_ol(self, element):
        self.lists_style_stack.append(ListStyle.NUMERIC)
        items = []
        handle = self.handle
        for elt in element.iterchildren():
            items.extend(handle(elt))
        self.lists_style_stack.pop()
        index = 0
        for item in items:
            if item.index is None:
                index += 1
                item.index = index
            else:
                index = item.index
        return [List(items, ListStyle.NUMERIC)]

    def handle_li(self, element):
        elts, remaining = self.make_paragraph(element)
        if remaining is not None:
            handle = self.handle
            for r in remaining:
                elts.extend(handle(r))
        index = None
        if self.lists_style_stack[-1] == ListStyle.NUMERIC:
            values = element.values()
            if values:
                try:
                    index = int(values[0])
                except ValueError:
                    pass
        return [Item(elts, index=index)]


def parse_html(html):
    """Parse `html` and return a :class:`.ast.Text` with the equivalent *AST*.

    If any kind of error happens, wrap the whole original `html` within a
    single :class:`.ast.Span` and return that.
    """

    fragment = fragment_fromstring(html, 'text')
    outer_div = fragment.find('div')
    if outer_div is not None:
        outer_div.drop_tag()
    parser = Parser(Text)
    return parser(fragment.iterchildren())


def html_to_text(html):
    """Parse `html` and return an equivalent *semtext*."""

    if squash_ws(html):
        parsed = parse_html(html)
        stream = StringIO()
        SEMPrinter(where=stream).visit(parsed)
        return stream.getvalue() or html


def text_to_html(text):
    """Parse `text` and return an equivalent ``HTML`` representation."""

    if squash_ws(text):
        parsed = parse_text(text)
        stream = StringIO()
        HTMLPrinter(where=stream).visit(parsed)
        return stream.getvalue() or text
