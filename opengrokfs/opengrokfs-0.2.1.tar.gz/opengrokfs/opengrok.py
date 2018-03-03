import threading
import urllib.parse

import requests
import dateparser
import attr
from lxml import etree


@attr.s
class File(object):
    name = attr.ib()
    date = attr.ib()
    size = attr.ib()
    dir = attr.ib(False)


@attr.s
class Result(object):
    path = attr.ib()
    function = attr.ib(None)
    line = attr.ib(0)
    text = attr.ib(None)


class OpenGrok(object):
    def __init__(self, url, projects=None, strip=None):
        if not url.endswith('/'):
            url += '/'
        self.url = url
        self.base = urllib.parse.urlparse(self.url).path
        self.htmlparser = etree.HTMLParser()
        self.lock = threading.Lock()

        self.params = {'n': 10000}
        self.projects = projects
        if projects:
            self.params['project'] = projects

        self.strip = strip

    def single_project(self):
        return self.projects and len(self.projects) == 1 and self.projects[0]

    def _text(self, item):
        return ''.join(item.itertext())

    def search(self, query):
        params = dict(self.params)
        params.update(query)

        page = requests.get(self.url + '/search', params)

        tree = etree.fromstring(page.text.encode('utf-8'), self.htmlparser)

        if '<title>Search Error</title>' in page.text:
            msgp = tree.find('.//div[@id="results"]/p')
            msg = msgp.text if msgp is not None else 'Search Error'
            raise Exception(msg)

        results = []
        for tr in tree.findall('.//div[@id="results"]//tr'):
            if tr.get('class') == 'dir':
                continue

            try:
                href = tr.find('./td[@class="f"]/a').get('href')
            except AttributeError:
                # If a file is missing, then OpenGrok inserts an entire HTML
                # document (headers and all) inside the table.  Ignore this.
                continue

            path = href.replace(self.base, '').replace('xref', '')

            if self.strip and path.startswith(self.strip):
                path = path[len(self.strip):]

            anchors = tr.findall('./td/tt/a[@class="s"]')
            for a in anchors:
                line = int(a[0].text)
                text = ''.join(a.itertext())
                text = text.replace('%d ' % line, '')

                results.append(Result(path=path, line=line, text=text))

            if not anchors:
                results.append(Result(path=path))

        return results

    def get(self, path):
        page = requests.get(self.url + '/raw/' + path)
        return page.text

    def parse_size(self, sizetext):
        size = float(sizetext.split(' ')[0])
        if 'KiB' in sizetext:
            # Precision has been lost due to rounding, so just try to
            # increase the size and hope nothing breaks
            size += 0.1
            size *= 1024

        return int(size)

    def list(self, path='/'):
        page = requests.get(self.url + '/xref/' + path + '/')
        tree = etree.fromstring(page.text.encode('utf-8'), self.htmlparser)

        tbl = tree.find('.//table[@id="dirlist"]')
        colmap = dict([(col.text, i)
                       for i, col
                       in enumerate(tbl.findall('.//th'))
                       if col.text])

        files = []
        for tr in tbl.findall('./tbody/tr'):
            tds = tr.findall('./td')

            name = self._text(tds[colmap['Name']])
            if name.endswith('/'):
                name = name[:-1]
                directory = True
            elif name == '..':
                directory = True
            else:
                directory = False

            # Empty directories are folded in newer versions
            name = name.split('/')[0]

            with self.lock:
                # dateparser uses a single instance of FreshnessDataParser
                # whose self.now value usage is not thread-safe.
                date = dateparser.parse(self._text(tds[colmap['Date']]))
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)

            sizetext = self._text(tds[colmap['Size']])
            # &nbsp; seems to be converted to \xa0
            sizetext = sizetext.replace(',', '.').replace('\xa0', '')
            size = self.parse_size(sizetext)

            files.append(File(name=name, date=date, size=size, dir=directory))

        return files
