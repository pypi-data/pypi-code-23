"""
An example crawler that extracts modules info from the Python documentation.

The results are reported to stdout with yellow (logged with warning level) and
written in a ``pymodules.jsonl`` file in the current directory.
"""

import pprint

from crawlster import Crawlster, start, Configuration
from crawlster.handlers.jsonl import JsonLinesHandler
from crawlster.handlers.log_handler import LogItemHandler


class PythonOrgCrawler(Crawlster):
    """
    This is an example crawler used to crawl info about all the Python modules
    """
    item_handler = [LogItemHandler(),
                    JsonLinesHandler('items.jsonl')]

    @start
    def step_start(self, url):
        data = self.http.get(url)
        if not data:
            return
        self.urls.mark_seen(url)
        hrefs = self.extract.css(data.body, 'a', attr='href')
        full_links = self.urls.multi_join(url, hrefs)
        for link in full_links:
            if '#' in link:
                continue
            self.schedule(self.process_page, link)

    def process_page(self, url):
        if not self.urls.can_crawl(url):
            return
        resp = self.http.get(url)
        self.urls.mark_seen(url)
        if not self.looks_like_module_page(resp.body):
            return
        module_name = self.extract.css(resp.body,
                                       'h1 a.reference.internal code span',
                                       content=True)
        if not module_name:
            return
        self.submit_item({'name': module_name[0], 'url': url})

    def looks_like_module_page(self, page_content):
        return b'Source code:' in page_content


if __name__ == '__main__':
    crawler = PythonOrgCrawler(Configuration({
        "core.start_urls": ["https://docs.python.org/3/library/index.html"],
        "pool.workers": 3,
    }))
    crawler.start()
    pprint.pprint(crawler.stats.dump())
