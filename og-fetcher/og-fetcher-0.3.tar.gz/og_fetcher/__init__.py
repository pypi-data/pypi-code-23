from urllib.request import urlopen
from html.parser import HTMLParser

class OGHTMLParser(HTMLParser):
    og_tags = []
    def handle_starttag(self, tag, attrs):
        if not tag == 'meta':
            return
        og_tag = {}
        is_og = False
        for attr in attrs:
            if attr[0] == 'property' and attr[1].startswith('og:'):
                is_og = True
        if is_og:
            for attr in attrs:
                og_tag[attr[0]] = attr[1]
            self.og_tags.append(og_tag)
