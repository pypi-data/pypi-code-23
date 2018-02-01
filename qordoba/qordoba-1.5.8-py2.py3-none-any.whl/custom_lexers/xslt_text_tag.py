# -*- coding: utf-8 -*-
"""
    pygments.lexers.html
    ~~~~~~~~~~~~~~~~~~~~

    Lexers for HTML, XML and related markup.

    :copyright: Copyright 2006-2017 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer, ExtendedRegexLexer, include, bygroups, \
    default, using
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Punctuation
from pygments.util import looks_like_xml, html_doctype_matches

from pygments.lexers.javascript import JavascriptLexer
from pygments.lexers.jvm import ScalaLexer
from pygments.lexers.css import CssLexer, _indentation, _starts_block
from pygments.lexers.ruby import RubyLexer

__all__ = ['HtmlLexer', 'DtdLexer', 'XmlLexer', 'XsltLexer', 'HamlLexer',
           'ScamlLexer', 'PugLexer']


class XmlLexer(RegexLexer):
    """
    Generic lexer for XML (eXtensible Markup Language).
    """

    flags = re.MULTILINE | re.DOTALL | re.UNICODE

    name = 'XML'
    aliases = ['xml']
    filenames = ['*.xml', '*.xsl', '*.rss', '*.xslt', '*.xsd',
                 '*.wsdl', '*.wsf']
    mimetypes = ['text/xml', 'application/xml', 'image/svg+xml',
                 'application/rss+xml', 'application/atom+xml']

    tokens = {
        'root': [
            ('[^<&]+', Text),
            (r'&\S*?;', Name.Entity),
            (r'\<\!\[CDATA\[.*?\]\]\>', Comment.Preproc),
            ('<!--', Comment, 'comment'),
            (r'<\?.*?\?>', Comment.Preproc),
            ('<![^>]*>', Comment.Preproc),
            (r'<\s*[\w:.-]+', Name.Tag, 'tag'),
            (r'<\s*/\s*[\w:.-]+\s*>', Name.Tag),
        ],
        'comment': [
            ('[^-]+', Comment),
            ('-->', Comment, '#pop'),
            ('-', Comment),
        ],
        'tag': [
            (r'\s+', Text),
            (r'[\w.:-]+\s*=', Name.Attribute, 'attr'),
            (r'/?\s*>', Name.Tag, '#pop'),
        ],
        'attr': [
            ('\s+', Text),
            ('".*?"', String, '#pop'),
            ("'.*?'", String, '#pop'),
            (r'[^\s>]+', String, '#pop'),
        ],
    }

    def analyse_text(text):
        if looks_like_xml(text):
            return 0.45  # less than HTML


class xslt_text_tag(XmlLexer):
    """
    A lexer for XSLT.

    .. versionadded:: 0.10
    """

    name = 'xslt_text_tag'
    aliases = ['xslt']
    filenames = ['*.xsl', '*.xslt', '*.xpl']  # xpl is XProc
    mimetypes = ['application/xsl+xml', 'application/xslt+xml']

    EXTRA_KEYWORDS = set((
        'apply-imports', 'apply-templates', 'attribute',
        'attribute-set', 'call-template', 'choose', 'comment',
        'copy', 'copy-of', 'decimal-format', 'element', 'fallback',
        'for-each', 'if', 'import', 'include', 'key', 'message',
        'namespace-alias', 'number', 'otherwise', 'output', 'param',
        'preserve-space', 'processing-instruction', 'sort',
        'strip-space', 'stylesheet', 'template', 'text', 'transform',
        'value-of', 'variable', 'when', 'with-param'
    ))

    def get_tokens_unprocessed(self, text):
        text_tag = False
        end_tag = False
        count = 0
        for index, token, value in XmlLexer.get_tokens_unprocessed(self, text):

            m = re.match('</?xsl:([^>]*)/?>?', value)
            try:
                if m.group(0) in "<xsl:text>":
                    text_tag = True
            except AttributeError:
                pass
            if token is Name.Tag and m and m.group(1) in self.EXTRA_KEYWORDS:
                yield index, Keyword, value
            else:
                if text_tag and value == '>':
                    end_tag = True
                    count += 1
                try:
                    if text_tag and end_tag and token != Name.Tag:
                        text_tag = False
                        end_tag = False
                        yield index, "Text.Tag", value
                except AttributeError:
                    pass

            yield index, token, value

    def analyse_text(text):
        if looks_like_xml(text) and '<xsl' in text:
            return 0.8