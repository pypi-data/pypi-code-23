from lunch_spider import LunchSpider
import scrapy
from scrapy.crawler import CrawlerProcess

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'LOG_ENABLED': False
})

def lunchboy():
    print("in lunchboy")

def lunch():
    process.crawl(LunchSpider)
    process.start()

def menu():
    process.crawl(LunchSpider, include_menu=True)
    process.start()
