# cronster tests
import os


def test_import_crawler():
    from cronster.crawler import CronsterCrawler
    crawler = CronsterCrawler(
        root=os.getcwd(),
        cache_host='localhost',
        cache_port=6379,
        interval=2)
    assert crawler
