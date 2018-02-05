from html.parser import HTMLParser

from . import OGHTMLParser

def parse(html):
    parser = OGHTMLParser()
    parser.feed(html)
    return parser.og_tags
