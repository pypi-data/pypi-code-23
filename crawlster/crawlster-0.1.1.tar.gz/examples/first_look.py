import crawlster
from crawlster.core import start
from crawlster.handlers import JsonLinesHandler


class MyCrawler(crawlster.Crawlster):
    # items will be saved to items.jsonl
    item_handler = JsonLinesHandler('items.jsonl')

    @start
    def step_start(self, url):
        resp = self.http.get(url)
        # we select elements with the expression and we are interested
        # only in the 'href' attribute. Also, we get only the first result
        # for this example
        events_uri = self.extract.css(
            resp.body_str, '#events > a', attr='href')[0]
        # we specify what method should be called next
        self.schedule(self.step_events_page, self.urls.join(url, events_uri))

    def step_events_page(self, url):
        resp = self.http.get(url)
        # We extract the content/text of all the selected titles
        events = self.extract.css(resp.body_str, 'h3.event-title a',
                                  content=True)
        for event_name in events:
            # submitting items to be processed by the item handler
            self.submit_item({'event': event_name})


if __name__ == '__main__':
    # starting the crawler
    cfg = {
        # the start pages
        'core.start_urls': ['https://www.python.org/'],
        # to see in-depth what happens
        'log.level': 'debug'
    }
    crawler = MyCrawler(crawlster.Configuration(cfg))
    # this will block until everything finishes
    crawler.start()
    # printing some run stats, such as the number of requests, how many items
    # were submitted, etc.
    print(crawler.stats.dump())
