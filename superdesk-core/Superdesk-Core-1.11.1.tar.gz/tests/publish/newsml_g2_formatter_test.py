# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
from unittest import mock


from superdesk.tests import TestCase
from superdesk.publish.formatters.newsml_g2_formatter import NewsMLG2Formatter
from superdesk.publish import init_app
from superdesk.publish.formatters import Formatter
from superdesk.publish.subscribers import SubscribersService
from lxml import etree
import datetime

NOW = datetime.datetime.now(datetime.timezone.utc)
ARTICLE = {
    '_id': 'urn:localhost.abc',
    'guid': 'urn:localhost.abc',
    'versioncreated': NOW,
    'firstcreated': NOW,
    'source': 'AAP',
    'anpa_category': [{'qcode': 'a', 'name': 'Australian General News'}],
    'headline': 'This is a test headline',
    'byline': 'joe',
    'slugline': 'slugline',
    'subject': [{'qcode': '02011001', 'name':'test'}, {'qcode': '02011002', 'name':'test'}],
    'anpa_take_key': 'take_key',
    'unique_id': '1',
    'body_html': '<p><h1>The story body</h1><h3/>empty element on purpose<br/><strong>test</strong><em/><br/>'
                 'other test</p>',
    'type': 'text',
    'word_count': '1',
    'priority': 1,
    '_current_version': 5,
    'state': 'published',
    'urgency': 2,
    'pubstatus': 'usable',
    'dateline': {
        'source': 'AAP',
        'text': 'sample dateline',
        'located': {
            'alt_name': '',
            'state': 'California',
            'city_code': 'Los Angeles',
            'city': 'Los Angeles',
            'dateline': 'city',
            'country_code': 'US',
            'country': 'USA',
            'tz': 'America/Los_Angeles',
            'state_code': 'CA'
        }
    },
    'keywords': ['traffic'],
    'abstract': 'sample abstract',
    'place': [
        {'qcode': 'NSW', 'name': 'NSW', 'state': 'New South Wales',
         'country': 'Australia', 'world_region': 'Oceania'}
    ],
    'ednote': '',
    'body_footer': '',
    'company_codes': [{'name': 'YANCOAL AUSTRALIA LIMITED', 'qcode': 'YAL', 'security_exchange': 'ASX'}]
}


class NewsMLG2FormatterTest(TestCase):
    article = None

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def setUp(self):
        self.formatter = NewsMLG2Formatter()
        self.base_formatter = Formatter()
        init_app(self.app)
        if self.article is None:
            self.article = ARTICLE
            # formatting is done once for all tests to save time
            # as long as used attributes are not modified, it's fine
            self.formatter_output = self.formatter.format(self.article, {'name': 'Test NewsMLG2'})
            self.doc = self.formatter_output[0][1]
            self.doc_xml = etree.fromstring(self.doc.encode('utf-8'))

    def test_html_void(self):
        import ipdb
        ipdb.set_trace()
