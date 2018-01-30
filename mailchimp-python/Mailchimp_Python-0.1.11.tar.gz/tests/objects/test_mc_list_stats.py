# coding=utf-8
import datetime
from dateutil.tz import tzutc
import unittest
from mailchimp.objects import MCListStats


class TestMCListStats(unittest.TestCase):
    def get_list_stat(self):
        return {
            'member_count': 10,
            'unsubscribe_count': 10,
            'cleaned_count': 10,
            'member_count_since_send': 4,
            'unsubscribe_count_since_send': 4,
            'cleaned_count_since_send': 4,
            'campaign_count': 1,
            'campaign_last_sent': '2015-09-15T17:27:16+00:00',
            'merge_field_count': 0,
            'avg_sub_rate': 1,
            'avg_unsub_rate': 1,
            'target_sub_rate': 2,
            'open_rate': 2,
            'click_rate': 3,
            'last_sub_date': '2015-09-15T17:27:16+00:00',
            'last_unsub_date': '2015-09-15T17:27:16+00:00',
        }

    def test_item_url(self):
        list_stat = MCListStats()
        self.assertIsNone(list_stat.item_url)

    def test_valid_search_params(self):
        list_stat = MCListStats()
        self.assertEqual(['offset', 'count', 'fields', 'exclude_fields'],
                         list_stat.valid_search_params)

    def test_none_init(self):
        list_stat = MCListStats(None)

        for prop in ['member_count', 'unsubscribe_count', 'cleaned_count', 'member_count_since_send',
                     'unsubscribe_count_since_send', 'cleaned_count_since_send', 'campaign_count',
                     'campaign_last_sent', 'merge_field_count', 'avg_sub_rate', 'avg_unsub_rate', 'target_sub_rate',
                     'open_rate', 'click_rate', 'last_sub_date', 'last_unsub_date']:
            self.assertIsNone(getattr(list_stat, prop))

    def test_empty_init(self):
        list_stat = MCListStats()

        for prop in ['member_count', 'unsubscribe_count', 'cleaned_count', 'member_count_since_send',
                     'unsubscribe_count_since_send', 'cleaned_count_since_send', 'campaign_count',
                     'campaign_last_sent', 'merge_field_count', 'avg_sub_rate', 'avg_unsub_rate', 'target_sub_rate',
                     'open_rate', 'click_rate', 'last_sub_date', 'last_unsub_date']:
            self.assertIsNone(getattr(list_stat, prop))

    def test_init(self):
        list_stat = MCListStats(self.get_list_stat())

        self.assertEqual(10, list_stat.member_count)
        self.assertEqual(10, list_stat.unsubscribe_count)
        self.assertEqual(10, list_stat.cleaned_count)
        self.assertEqual(4, list_stat.member_count_since_send)
        self.assertEqual(4, list_stat.unsubscribe_count_since_send)
        self.assertEqual(4, list_stat.cleaned_count_since_send)
        self.assertEqual(1, list_stat.campaign_count)
        self.assertEqual(datetime.datetime(2015, 9, 15, 17, 27, 16).replace(tzinfo=tzutc()),
                         list_stat.campaign_last_sent)
        self.assertEqual(0, list_stat.merge_field_count)
        self.assertEqual(1, list_stat.avg_sub_rate)
        self.assertEqual(1, list_stat.avg_unsub_rate)
        self.assertEqual(2, list_stat.target_sub_rate)
        self.assertEqual(2, list_stat.open_rate)
        self.assertEqual(3, list_stat.click_rate)
        self.assertEqual(datetime.datetime(2015, 9, 15, 17, 27, 16).replace(tzinfo=tzutc()), list_stat.last_sub_date)
        self.assertEqual(datetime.datetime(2015, 9, 15, 17, 27, 16).replace(tzinfo=tzutc()), list_stat.last_unsub_date)

    def test_to_str(self):
        list_stat = MCListStats(self.get_list_stat())
        self.assertEqual('', str(list_stat))

    def test_repr(self):
        list_stat = MCListStats(self.get_list_stat())
        self.assertEqual('<MCListStats: >', str(repr(list_stat)))
