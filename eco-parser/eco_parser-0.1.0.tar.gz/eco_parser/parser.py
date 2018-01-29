import re
import requests
from lxml import etree
from eco_parser.core import get_single_element, ParseError
from eco_parser.element_parsers import ElementParserFactory


class EcoParser:

    def __init__(self, url):
        self.url = url

    def get_data(self):
        r = requests.get(self.url)
        r.raise_for_status()
        return r.content

    def parse_schedule(self):
        tree = etree.fromstring(self.get_data())
        secondary = get_single_element(tree, 'Secondary')
        schedules = get_single_element(secondary, 'Schedules')
        schedule = get_single_element(schedules, 'Schedule')
        schedule_body = get_single_element(schedule, 'ScheduleBody')
        p = ElementParserFactory.create(schedule_body)
        return p.parse()

    def parse_article(self):
        tree = etree.fromstring(self.get_data())
        secondary = get_single_element(tree, 'Secondary')
        body = get_single_element(secondary, 'Body')
        p = ElementParserFactory.create(body)
        return p.parse()

    def parse(self):
        schedule_pattern = r'http[s]?\:\/\/(www\.)?legislation\.gov\.uk\/(.)+\/schedule\/(.)+\/data\.xml'
        article_pattern  = r'http[s]?\:\/\/(www\.)?legislation\.gov\.uk\/(.)+\/article\/(.)+\/data\.xml'
        if re.match(schedule_pattern, self.url):
            return self.parse_schedule()
        elif re.match(article_pattern, self.url):
            return self.parse_article()
        else:
            raise ParseError('Could not find a suitable parser for %s' % (self.url), 0)
