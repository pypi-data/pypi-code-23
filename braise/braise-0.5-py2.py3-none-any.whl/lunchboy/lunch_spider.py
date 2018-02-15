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
        yield scrapy.Request(url="http://foodamenus.com/appboy", callback=self.parse)

    def parse(self, response):
        weekday = calendar.day_name[date.today().weekday()].lower()

        self.print_name(weekday, response)

        if self.include_menu:
            self.print_spacer()
            self.print_menu(weekday, response)

    def print_name(self, weekday, response):
        tmpl = string.Template("//h2[contains(., '$day')]")
        xpath_query_for_name = tmpl.substitute(day=weekday.capitalize())
        matches = response.xpath(xpath_query_for_name).extract()
        match = matches[0].lower()
        matcher = re.compile(weekday +': (.*)</')
        restaurant_names = matcher.findall(match)
        message = "today's lunch is %s!!!!!!!!!!!" % restaurant_names[0]
        print(message)

    def print_menu(self, weekday, response):
        img_tmpl = string.Template("//h2[contains(., '$day')]/following::img[1]/@src")
        xpath_query_for_image = img_tmpl.substitute(day=weekday.capitalize())
        img_matches = response.xpath(xpath_query_for_image).extract()
        img_url = img_matches[0]

        data = {
            'requests':[
                {
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
                }
            ]
        }
        r = requests.post("https://vision.googleapis.com/v1/images:annotate?key=%s" % os.environ.get('GCM_KEY'), json=data)
        print r.json()["responses"][0]["textAnnotations"][0]["description"]

    def print_spacer(self):
        print("")
        print("--------------- MENU ----------------")
        print("")
