# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- Visitor pattern revisited
# :Created:   mer 23 nov 2016 22:45:46 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016, 2017 Arstecnica s.r.l.
# :Copyright: © 2018 Lele Gaifax
#

import sys

from .ast import SpanStyle, ListStyle


class Visitor(object):
    "Abstract AST visitor."

    def visit(self, node):
        """Visit the given `node`.

        If the instance has a ``accept_<nodename>`` method, where
        ``<nodename>`` is the class name of the `node`, and it does not return
        ``False``, then if it implements a ``visit_<nodename>`` method call it
        passing the `node` as the single argument.
        """

        cname = node.__class__.__name__.lower()
        accept = getattr(self, 'accept_%s' % cname, None)
        if accept is not None and accept(node) is not False:
            visit = getattr(self, 'visit_%s' % cname, None)
            if visit is not None:
                visit(node)

    def visit_children(self, node):
        """Visit `node` children."""

        for child in node.children:
            self.visit(child)


class SynopsisPrinter(Visitor):
    """Visitor that prints out just the plain text, for a quick preview."""

    def __init__(self, max_length=80, where=sys.stdout):
        self.max_length = max_length
        self.where = where
        self.lists_stack = []

    def visit_children(self, node):
        """Visit `node` children."""

        for child in node.children:
            if self.max_length > 0:
                self.visit(child)

    def emit(self, line):
        length = len(line)
        if self.max_length < length:
            length = self.max_length
            line = line[:length]
            end = '…'
        else:
            end = ''
        print(line, end=end, file=self.where)
        self.max_length -= length

    def accept_text(self, node):
        pass

    def visit_text(self, node):
        self.visit_children(node)

    def accept_paragraph(self, node):
        pass

    def visit_paragraph(self, node):
        self.visit_children(node)

    def accept_span(self, node):
        pass

    def visit_span(self, node):
        self.emit(node.text)

    def accept_list(self, node):
        if node.style == ListStyle.DOTTED:
            self.lists_stack.append(lambda x: '- ')
        else:
            self.lists_stack.append(lambda n: '%d. '
                                    % (getattr(n, 'index', 0) or 0))

    def visit_list(self, node):
        self.emit(' ')
        self.visit_children(node)
        self.lists_stack.pop()

    def accept_item(self, node):
        marker = self.lists_stack[-1](node)
        self.emit(marker)

    def visit_item(self, node):
        self.visit_children(node)


class BaseIndentingPrinter(Visitor):
    """Abstract visitor able to keep track of current indentation.

    :param where: a file-like object where the output is written, by default
                  ``sys.stdout``
    """

    def __init__(self, where=sys.stdout):
        self.indent = 0
        self.where = where

    def visit_children(self, node, indent=True):
        if indent:
            self.indent += 2
        super().visit_children(node)
        if indent:
            self.indent -= 2

    def emit(self, line, indent=True, sep='', end='\n'):
        if indent:
            print(" "*self.indent, end='', file=self.where)
        print(line, sep=sep, end=end, file=self.where)


class ASTPrinter(BaseIndentingPrinter):
    """Visitor used by the tests, that emits the AST as a readable stream."""

    def accept_text(self, node):
        self.emit("<text>")

    def visit_text(self, node):
        self.visit_children(node)
        self.emit("</text>")

    def accept_paragraph(self, node):
        self.emit("<paragraph>")

    def visit_paragraph(self, node):
        self.emit("  ", end='')
        self.visit_children(node)
        self.emit("", indent=False)
        self.emit("</paragraph>")

    def accept_span(self, node):
        style = ('' if node.style == SpanStyle.PLAIN
                 else ' style="%s"' % node.style.name.lower())
        self.emit('<span%s>' % style, indent=False, end='')

    def visit_span(self, node):
        self.emit(node.text, end='', indent=False)
        self.emit("</span>", end='', indent=False)

    def accept_list(self, node):
        self.emit('<list style="%s">'
                  % ('dotted' if node.style == ListStyle.DOTTED
                     else 'numeric'))

    def visit_list(self, node):
        self.visit_children(node)
        self.emit("</list>")

    def accept_item(self, node):
        index = '' if node.index is None else (' index="%d"' % node.index)
        self.emit("<item%s>" % index)

    def visit_item(self, node):
        self.visit_children(node)
        self.emit("</item>")


class SEMPrinter(BaseIndentingPrinter):
    "Visitor that turns an AST back to the equivalent SEM text."

    def __init__(self, where=sys.stdout):
        super().__init__(where)
        self.lists_stack = []

    def accept_text(self, node):
        pass

    def visit_text(self, node):
        self.visit_children(node, indent=False)

    def accept_paragraph(self, node):
        pass

    def visit_paragraph(self, node):
        self.visit_children(node)
        self.emit("", indent=False)
        self.emit("", indent=False)
        self.emit("", end='')

    def accept_span(self, node):
        if node.style == SpanStyle.BOLD:
            self.emit('*', end='', indent=False)
        elif node.style == SpanStyle.ITALIC:
            self.emit('/', end='', indent=False)

    def visit_span(self, node):
        self.emit(node.text, end='', indent=False)
        if node.style == SpanStyle.BOLD:
            self.emit('*', end='', indent=False)
        elif node.style == SpanStyle.ITALIC:
            self.emit('/', end='', indent=False)

    def accept_list(self, node):
        if node.style == ListStyle.DOTTED:
            self.lists_stack.append(lambda x: '- ')
        else:
            self.lists_stack.append(lambda n: '%d. ' % n.index)
        self.emit("", indent=False)

    def visit_list(self, node):
        self.visit_children(node, indent=False)
        self.lists_stack.pop()

    def accept_item(self, node):
        marker = self.lists_stack[-1](node)
        self.emit(marker, end='')
        if len(marker) != 2:
            self.indent += len(marker) - 2

    def visit_item(self, node):
        self.visit_children(node)
        self.emit("", indent=False)
        marker = self.lists_stack[-1](node)
        if len(marker) != 2:
            self.indent -= len(marker) - 2


class HTMLPrinter(BaseIndentingPrinter):
    "Visitor that turns an AST to the equivalent HTML text."

    def __init__(self, where=sys.stdout):
        super().__init__(where)
        self.lists_stack = []
        self.first_item_child = False

    def accept_text(self, node):
        pass

    def visit_text(self, node):
        self.visit_children(node, indent=False)

    def accept_paragraph(self, node):
        pass

    def visit_paragraph(self, node):
        self.emit("" if self.first_item_child else "<p>", end='')
        self.visit_children(node)
        if not self.first_item_child:
            self.emit("</p>")
        else:
            self.emit("", indent=False)
            self.first_item_child = False

    def accept_span(self, node):
        if node.style == SpanStyle.BOLD:
            self.emit('<strong>', end='', indent=False)
        elif node.style == SpanStyle.ITALIC:
            self.emit('<em>', end='', indent=False)

    def visit_span(self, node):
        self.emit(node.text, end='', indent=False)
        if node.style == SpanStyle.BOLD:
            self.emit('</strong>', end='', indent=False)
        elif node.style == SpanStyle.ITALIC:
            self.emit('</em>', end='', indent=False)

    def accept_list(self, node):
        if node.style == ListStyle.DOTTED:
            self.emit('<ul>')
            self.lists_stack.append(lambda x: '<li>')
        else:
            self.emit('<ol>')
            self.lists_stack.append(lambda n: '<li value="%d">' % n.index)

    def visit_list(self, node):
        self.visit_children(node)
        self.lists_stack.pop()
        if node.style == ListStyle.DOTTED:
            self.emit('</ul>')
        else:
            self.emit('</ol>')

    def accept_item(self, node):
        marker = self.lists_stack[-1](node)
        self.emit(marker)

    def visit_item(self, node):
        self.first_item_child = True
        self.visit_children(node)
        self.emit("</li>")
        marker = self.lists_stack[-1](node)
