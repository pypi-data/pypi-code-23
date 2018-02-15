import scrapy
import datetime
import string
from datetime import date
import calendar
import re
import requests
import os

# scrapy runspider --nolog lunch_spider.py
class LunchSpider(scrapy.Spider):
    name = "lunch"

    def __init__(self, include_menu=False, *args, **kwargs):
        super(LunchSpider, self).__init__(*args, **kwargs)
        self.include_menu = include_menu

    def start_requests(self):
        print("Yay lunch")
        print("")
        yield scrapy.Request(url="https://www.fooda.com/braze", callback=self.parse)

    def parse(self, response):
        if self.include_menu:
            self.print_menu(response)

    def print_menu(self, response):
        img_urls = response.xpath("//div[contains(@class, 'myfooda-event')]/child::img/@src").extract()
        data = {'requests': []}

        for img_url in img_urls:
            data['requests'].append({
                'image':{
                    'source':{
                        'imageUri': img_url
                    }
                },
                'features':[
                    {
                        'type':"TEXT_DETECTION"
                    }
                ]
            })

        r = requests.post("https://vision.googleapis.com/v1/images:annotate?key=%s" % os.environ.get('GCM_KEY'), json=data)
        menu_no = 1
        for response in r.json()["responses"]:
            self.print_spacer("Menu " + str(menu_no))
            menu_no = menu_no + 1
            print response["textAnnotations"][0]["description"]

    def print_spacer(self, message):
        print("")
        print("--------------- " + message + " ----------------")
        print("")
