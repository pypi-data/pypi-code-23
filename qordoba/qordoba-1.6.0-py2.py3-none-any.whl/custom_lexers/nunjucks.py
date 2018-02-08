# -*- coding: utf-8 -*-
"""
    pygments.lexers.html
    ~~~~~~~~~~~~~~~~~~~~

    Lexers for HTML, XML and related markup.

    :copyright: Copyright 2006-2017 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re
import threading

from pygments.lexer import RegexLexer, ExtendedRegexLexer, include, bygroups, \
    default, using
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Punctuation
from pygments.util import looks_like_xml, html_doctype_matches

from pygments.lexers.javascript import JavascriptLexer
from pygments.lexers.jvm import ScalaLexer
from pygments.lexers.css import CssLexer, _indentation, _starts_block
from pygments.lexers.ruby import RubyLexer

__all__ = ['nunjucks']


class HtmlLexer(RegexLexer):
    """
    For HTML 4 and XHTML 1 markup. Nested JavaScript and CSS is highlighted
    by the appropriate lexer.
    """

    name = 'HTML'
    aliases = ['html']
    filenames = ['*.html', '*.htm', '*.xhtml', '*.xslt']
    mimetypes = ['text/html', 'application/xhtml+xml']

    flags = re.IGNORECASE | re.DOTALL
    tokens = {
        'root': [
            ('[^<&]+', Text),
            (r'&\S*?;', Name.Entity),
            (r'\<\!\[CDATA\[.*?\]\]\>', Comment.Preproc),
            ('<!--', Comment, 'comment'),
            (r'<\?.*?\?>', Comment.Preproc),
            ('<![^>]*>', Comment.Preproc),
            (r'(<)(\s*)(script)(\s*)',
             bygroups(Punctuation, Text, Name.Tag, Text),
             ('script-content', 'tag')),
            (r'(<)(\s*)(style)(\s*)',
             bygroups(Punctuation, Text, Name.Tag, Text),
             ('style-content', 'tag')),
            # note: this allows tag names not used in HTML like <x:with-dash>,
            # this is to support yet-unknown template engines and the like
            (r'(<)(\s*)([\w:.-]+)',
             bygroups(Punctuation, Text, Name.Tag), 'tag'),
            (r'(<)(\s*)(/)(\s*)([\w:.-]+)(\s*)(>)',
             bygroups(Punctuation, Text, Punctuation, Text, Name.Tag, Text,
                      Punctuation)),
        ],
        'comment': [
            ('[^-]+', Comment),
            ('-->', Comment, '#pop'),
            ('-', Comment),
        ],
        'tag': [
            (r'\s+', Text),
            (r'([\w:-]+\s*)(=)(\s*)', bygroups(Name.Attribute, Operator, Text),
             'attr'),
            (r'[\w:-]+', Name.Attribute),
            (r'(/?)(\s*)(>)', bygroups(Punctuation, Text, Punctuation), '#pop'),
        ],
        'script-content': [
            (r'(<)(\s*)(/)(\s*)(script)(\s*)(>)',
             bygroups(Punctuation, Text, Punctuation, Text, Name.Tag, Text,
                      Punctuation), '#pop'),
            (r'.+?(?=<\s*/\s*script\s*>)', using(JavascriptLexer)),
        ],
        'style-content': [
            (r'(<)(\s*)(/)(\s*)(style)(\s*)(>)',
             bygroups(Punctuation, Text, Punctuation, Text, Name.Tag, Text,
                      Punctuation), '#pop'),
            (r'.+?(?=<\s*/\s*style\s*>)', using(CssLexer)),
        ],
        'attr': [
            ('".*?"', String, '#pop'),
            ("'.*?'", String, '#pop'),
            (r'[^\s>]+', String, '#pop'),
        ],
    }

    def analyse_text(text):
        if html_doctype_matches(text):
            return 0.5


class nunjucks(HtmlLexer):
    """
    A lexer for XSLT.

    .. versionadded:: 0.10
    """

    name = 'nunjucks'

    # aliases = ['xslt']
    # filenames = ['*.xsl', '*.xslt', '*.xpl']  # xpl is XProc
    # mimetypes = ['application/xsl+xml', 'application/xslt+xml']
    # def MyThread1(index, nunjucks_list):
    #     for string in nunjucks_list:
    #         yield index, "nunjucks", string

    # def MyThread2(index, token, filtered_str):
    #     for string in filtered_str:
    #         yield index, token, string

    def get_tokens_unprocessed(self, text):
        for index, token, value in HtmlLexer.get_tokens_unprocessed(self, text):
            value = value.strip()
            if re.match('{%/?([^}]*)/?%}?', value):

                nunjucks_list = re.findall('{%/?([^}]*)/?%}?', value)
                filtered_str = [s.split('}')[-1] for s in value.split('{%')]
                max_len = max(len(nunjucks_list), len(filtered_str))
                try:
                    for i in range(max_len):
                        yield index, "nunjucks", nunjucks_list[i]
                        yield index, "Token.Text.nunjucks", filtered_str[i]
                except IndexError:
                    pass

                # t1 = threading.Thread(target=MyThread1, args=[index, token, nunjucks_list])
                # t2 = threading.Thread(target=MyThread2, args=[index, token, filtered_str])

                # # start threads
                # threads = [t1, t2]
                # for t in threads:
                #     t.start()

                # #wait for threads to finish
                # for t in threads:
                #     t.join()

            else:
                yield index, token, value

    # def analyse_text(text):
    #     if looks_like_xml(text) and '<xsl' in text:
    #         return 0.8