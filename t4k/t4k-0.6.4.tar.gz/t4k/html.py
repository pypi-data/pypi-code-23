import types
import re
from xml.dom import minidom

xml_declaration = re.compile(r'<\?xml[^>]*?>')
html_declaration = '<!DOCTYPE html>'
def HtmlDocument():
    dom = minidom.Document()
    def toprettyhtml(self, *args):
        html = self.toprettyxml(*args)
        return html_declaration + xml_declaration.split(html, 1)[1]
    dom.toprettyhtml = types.MethodType(toprettyhtml, dom, minidom.Document)
    return dom


# This provisional dom is used as an element factory
DOM = HtmlDocument()

def new_document():
    new_dom = HtmlDocument()
    html = new_dom.appendChild(element('html', attributes={'lang':'en'}))
    head = html.appendChild(element('head'))
    head.appendChild(meta(attributes={
        'http-equiv':'Content-Type', 'content':'text/html', 'charset':'utf-8'
    }))
    body = html.appendChild(element('body'))

    return new_dom, html, head, body


def element(tag_name, text_content=None, attributes={}):
    elm = DOM.createElement(tag_name)
    bind_attributes(elm, attributes)
    if text_content is not None:
        elm.appendChild(text(text_content))
    return elm 

def bind_attributes(element, attributes):
    for attribute in attributes:
        element.setAttribute(attribute, attributes[attribute])
    return element

def meta(attributes={}):
    return element('meta', '', attributes)

def script(src=None, attributes={}):
    if src is not None:
        attributes['src'] = src
    return element('script', '', attributes)

def a(text_content=None, href=None, attributes={}):
    if href is not None:
        attributes['href'] = href
    return element('a', text_content, attributes)

def ol(text_content=None, attributes={}):
    return element('ol', text_content, attributes)

def ul(text_content=None, attributes={}):
    return element('ul', text_content, attributes)

def li(text_content=None, attributes={}):
    return element('li', text_content, attributes)

def div(text_content=None, attributes={}):
    return element('div', text_content, attributes)

def span(text_content=None, attributes={}):
    return element('span', text_content, attributes)

def br(attributes={}):
    return element('br', None, attributes)

def text(text_content):
    return DOM.createTextNode(str(text_content))

def table(attributes={}):
    return element('table', None, attributes)

def tr(attributes={}):
    return element('tr', None, attributes)

def td(text_content=None, attributes={}):
    return element('td', text_content, attributes)

def th(text_content=None, attributes={}):
    return element('th', text_content, attributes)

def h1(text_content=None, attributes={}):
    return element('h1', text_content, attributes)

def h2(text_content=None, attributes={}):
    return element('h2', text_content, attributes)

def h3(text_content=None, attributes={}):
    return element('h3', text_content, attributes)

def h4(text_content=None, attributes={}):
    return element('h4', text_content, attributes)

def build_table(fields):
    table_elm = table({'class': 'performance'})
    first_row = True
    for row in fields:
        if first_row:
            tr_elm = table_elm.appendChild(tr({'class': 'first-row'}))
            first_row = False
        else:
            tr_elm = table_elm.appendChild(tr())
                
        first_cell = True
        for cell in row:
            if first_cell:
                td_elm = tr_elm.appendChild(td({'class': 'first-cell'}))
                first_cell = False
            else:
                td_elm = tr_elm.appendChild(td())
            td_elm.appendChild(text(cell))

    return table_elm


class Styler(dict):

    def as_element(self):
        style_element = DOM.createElement('style')
        style_element.appendChild(text('\n' + self.serialize()))
        return style_element

    def serialize(self):
        string = ''
        for rule in self:

            # Open the style rule
            string += '%s {\n' % rule

            # Write each directive
            for directive in self[rule]:
                string += '\t%s: %s;\n' % (directive, self[rule][directive])

            # Close the style rule
            string += '}\n'

        return string
