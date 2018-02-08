#


""" Writer implementation """


import os

import bs4
import docutils.nodes
import docutils.writers.html5_polyglot


class Writer(docutils.writers.html5_polyglot.Writer):
    """ Writer for docutils """

    def __init__(self):
        super().__init__()
        self.translator_class = _Translator
        return

    def translate(self):
        super().translate()
        soup = bs4.BeautifulSoup(self.output, 'html5lib')
        self.output = soup.prettify()
        return


class _Translator(docutils.writers.html5_polyglot.HTMLTranslator):

    embedded_stylesheet = '<style>\n\n%s\n</style>\n'

    def unimplemented_visit(self, node):
        super().unimplemented_visit(node)
        return

    def visit_document(self, node):
        title = (
            node.get('title', '') or
            os.path.basename(node['source']) or
            'docutils document without title'
        )
        self.head.append('<title>%s</title>\n' % self.encode(title))

    def depart_document(self, node):
        self.head_prefix.extend([self.doctype,
                                 self.head_prefix_template %
                                 {'lang': self.settings.language_code}])
        self.html_prolog.append(self.doctype)
        self.meta.insert(0, self.content_type % self.settings.output_encoding)
        self.head.insert(0, self.content_type % self.settings.output_encoding)
        if self.math_header:
            if self.math_output == 'mathjax':
                self.head.extend(self.math_header)
            else:
                self.stylesheet.extend(self.math_header)
        # skip content-type meta tag with interpolated charset value:
        self.html_head.extend(self.head[1:])
        self.body_prefix.append(self.starttag(node, 'main'))
        self.body_suffix.insert(0, '</main>\n')
        self.fragment.extend(self.body)  # self.fragment is the "naked" body
        self.html_body.extend(
            self.body_prefix[1:] +
            self.body_pre_docinfo +
            self.docinfo +
            self.body +
            self.body_suffix[:-1]
        )
        assert not self.context, 'len(context) = %s' % len(self.context)

    def visit_footer(self, node):
        self.context.append(len(self.body))
        return

    def depart_footer(self, node):
        start = self.context.pop()
        footer = []
        footer.append(self.starttag(node, 'footer'))
        footer.extend(self.body[start:])
        footer.append('</footer>\n')
        self.footer.extend(footer)
        self.body_suffix[:0] = footer
        del self.body[start:]
        return

    def visit_header(self, node):
        self.context.append(len(self.body))
        return

    def depart_header(self, node):
        start = self.context.pop()
        header = []
        header.append(self.starttag(node, 'header'))
        header.extend(self.body[start:])
        header.append('</header>\n')
        self.body_prefix.extend(header)
        self.header.extend(header)
        del self.body[start:]
        return

    def visit_section(self, node):
        self.section_level += 1
        self.body.append(
            self.starttag(node, 'section'),
        )
        return

    def depart_section(self, node):
        self.section_level -= 1
        self.body.append('</section>\n')
        return


# EOF
