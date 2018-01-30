# coding=utf-8
import unittest
import responses
from mailchimp.objects import MCCampaignDefaults, MCContact, MCLink, MCList, MCListStats
from mailchimp.exceptions import MCListNotFound
from mailchimp.config import mailchimp_config


class TestMCList(unittest.TestCase):
    def setUp(self):
        mailchimp_config.api_key = 'a65a65a65a65a65a56a5a6-us1'

    def get_list_1(self):
        return {
            "id": "57afe96172",
            "name": "Freddie's Jokes",
            "contact": {
                "company": "MailChimp",
                "address1": "675 Ponce De Leon Ave NE",
                "address2": "Suite 5000",
                "city": "Atlanta",
                "state": "GA",
                "zip": "30308",
                "country": "US",
                "phone": ""
            },
            "permission_reminder": "You're receiving this email because you just can't get enough of Freddie's jokes.",
            "use_archive_bar": False,
            "campaign_defaults": {
                "from_name": "Freddie",
                "from_email": "freddie@freddiesjokes.com",
                "subject": "",
                "language": "en"
            },
            "notify_on_subscribe": "",
            "notify_on_unsubscribe": "",
            "date_created": "2015-09-15T14:38:16+00:00",
            "list_rating": 3,
            "email_type_option": False,
            "subscribe_url_short": "http://eepurl.com/xxxx",
            "subscribe_url_long": "http://freddiesjokes.us1.list-manage.com/subscribe?u=8d3a3db4d97663a9074efcc16&id=xxxx",
            "beamer_address": "us1-xxxx-xxxx@inbound.mailchimp.com",
            "visibility": "prv",
            "modules": [],
            "stats": {
                "member_count": 203,
                "unsubscribe_count": 0,
                "cleaned_count": 0,
                "member_count_since_send": 0,
                "unsubscribe_count_since_send": 0,
                "cleaned_count_since_send": 0,
                "campaign_count": 3,
                "campaign_last_sent": "",
                "merge_field_count": 2,
                "avg_sub_rate": 15,
                "avg_unsub_rate": 0,
                "target_sub_rate": 0,
                "open_rate": 0,
                "click_rate": 0,
                "last_sub_date": "2015-09-15T17:27:16+00:00",
                "last_unsub_date": ""
            },
            "_links": [
                {
                    "rel": "self",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Instance.json"
                },
                {
                    "rel": "parent",
                    "href": "https://us1.api.mailchimp.com/3.0/lists",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists.json"
                },
                {
                    "rel": "update",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172",
                    "method": "PATCH",
                    "schema": "https://api.mailchimp.com/schema/3.0/Lists/Instance.json"
                },
                {
                    "rel": "delete",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172",
                    "method": "DELETE"
                },
                {
                    "rel": "abuse-reports",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/abuse-reports",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Abuse/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Abuse.json"
                },
                {
                    "rel": "activity",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/activity",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Activity/Collection.json"
                },
                {
                    "rel": "clients",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/clients",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Clients/Collection.json"
                },
                {
                    "rel": "growth-history",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/growth-history",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Growth/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Growth.json"
                },
                {
                    "rel": "interest-categories",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/interest-categories",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/InterestCategories/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/InterestCategories.json"
                },
                {
                    "rel": "members",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Members.json"
                },
                {
                    "rel": "merge-fields",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/merge-fields",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/MergeFields/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/MergeFields.json"
                },
                {
                    "rel": "segments",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/segments",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Segments/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Segments.json"
                }
            ]
        }

    def get_list_2(self):
        return {
            "id": "9617257afe",
            "name": "Freddie's New Jokes",
            "contact": {
                "company": "MailChimp 2",
                "address1": "675 Ponce De Leon Ave NE",
                "address2": "Suite 5000",
                "city": "Atlanta",
                "state": "GA",
                "zip": "30308",
                "country": "US",
                "phone": ""
            },
            "permission_reminder": "You're receiving this email because you just can't get enough of Freddie's jokes.",
            "use_archive_bar": False,
            "campaign_defaults": {
                "from_name": "Freddie",
                "from_email": "freddie@freddiesjokes.com",
                "subject": "",
                "language": "en"
            },
            "notify_on_subscribe": "",
            "notify_on_unsubscribe": "",
            "date_created": "2015-09-15T14:38:16+00:00",
            "list_rating": 3,
            "email_type_option": False,
            "subscribe_url_short": "http://eepurl.com/xxxx",
            "subscribe_url_long": "http://freddiesnewjokes.us1.list-manage.com/subscribe?u=8d3a3db4d97663a9074efcc16&id=xxxx",
            "beamer_address": "us1-xxxx-xxxx@inbound.mailchimp.com",
            "visibility": "prv",
            "modules": [],
            "stats": {
                "member_count": 205,
                "unsubscribe_count": 0,
                "cleaned_count": 0,
                "member_count_since_send": 0,
                "unsubscribe_count_since_send": 0,
                "cleaned_count_since_send": 0,
                "campaign_count": 3,
                "campaign_last_sent": "",
                "merge_field_count": 2,
                "avg_sub_rate": 15,
                "avg_unsub_rate": 0,
                "target_sub_rate": 0,
                "open_rate": 0,
                "click_rate": 0,
                "last_sub_date": "2015-09-15T17:27:16+00:00",
                "last_unsub_date": ""
            },
            "_links": [
                {
                    "rel": "self",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Instance.json"
                },
                {
                    "rel": "parent",
                    "href": "https://us1.api.mailchimp.com/3.0/lists",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists.json"
                },
                {
                    "rel": "update",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe",
                    "method": "PATCH",
                    "schema": "https://api.mailchimp.com/schema/3.0/Lists/Instance.json"
                },
                {
                    "rel": "delete",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe",
                    "method": "DELETE"
                },
                {
                    "rel": "abuse-reports",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe/abuse-reports",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Abuse/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Abuse.json"
                },
                {
                    "rel": "activity",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe/activity",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Activity/Collection.json"
                },
                {
                    "rel": "clients",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe/clients",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Clients/Collection.json"
                },
                {
                    "rel": "growth-history",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe/growth-history",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Growth/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Growth.json"
                },
                {
                    "rel": "interest-categories",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe/interest-categories",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/InterestCategories/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/InterestCategories.json"
                },
                {
                    "rel": "members",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe/members",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Members.json"
                },
                {
                    "rel": "merge-fields",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe/merge-fields",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/MergeFields/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/MergeFields.json"
                },
                {
                    "rel": "segments",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/9617257afe/segments",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Segments/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Segments.json"
                }
            ]
        }

    def test_list(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, 'https://us1.api.mailchimp.com/3.0/lists',
                     json={
                         "lists": [ self.get_list_1(), self.get_list_2() ],
                         "_links": [
                             {
                                 "rel": "self",
                                 "href": "https://us1.api.mailchimp.com/3.0/lists",
                                 "method": "GET",
                                 "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Collection.json",
                                 "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists.json"
                             },
                             {
                                 "rel": "parent",
                                 "href": "https://us1.api.mailchimp.com/3.0/",
                                 "method": "GET",
                                 "targetSchema": "https://api.mailchimp.com/schema/3.0/Root.json"
                             },
                             {
                                 "rel": "create",
                                 "href": "https://us1.api.mailchimp.com/3.0/lists",
                                 "method": "POST",
                                 "schema": "https://api.mailchimp.com/schema/3.0/Lists/Instance.json"
                             }
                         ],
                         "total_items": 2
                     }, status=200,
                     content_type='application/json')

            lists = MCList.list()
            self.assertEqual(2, len(lists))
            self.assertEqual(1, len(rsps.calls))
            self.assertEqual("https://us1.api.mailchimp.com/3.0/lists", rsps.calls[0].request.url)
            self.assertEqual('GET', rsps.calls[0].request.method)
            self.assertEqual("application/json", rsps.calls[0].request.headers['Accept'])
            self.assertEqual("application/json", rsps.calls[0].request.headers['Content-Type'])
            self.assertEqual("Basic dXNlcm5hbWU6YTY1YTY1YTY1YTY1YTY1YTU2YTVhNi11czE=",
                             rsps.calls[0].request.headers['Authorization'])

            # Check item 1
            item1 = lists[0]
            self.assertEqual('57afe96172', item1.id)
            self.assertEqual("Freddie's Jokes", item1.name)
            self.assertEqual(12, len(item1.links))
            self.assertTrue(isinstance(item1.links[0], MCLink))
            self.assertTrue(isinstance(item1.contact, MCContact))
            self.assertEqual('MailChimp', item1.contact.company)
            self.assertTrue(isinstance(item1.stats, MCListStats))
            self.assertEqual(203, item1.stats.member_count)
            self.assertTrue(isinstance(item1.campaign_defaults, MCCampaignDefaults))

            # Check item 2
            item2 = lists[1]
            self.assertEqual('9617257afe', item2.id)
            self.assertEqual("Freddie's New Jokes", item2.name)
            self.assertEqual(12, len(item2.links))
            self.assertTrue(isinstance(item2.links[0], MCLink))
            self.assertTrue(isinstance(item2.contact, MCContact))
            self.assertEqual('MailChimp 2', item2.contact.company)
            self.assertTrue(isinstance(item2.stats, MCListStats))
            self.assertEqual(205, item2.stats.member_count)
            self.assertTrue(isinstance(item2.campaign_defaults, MCCampaignDefaults))

    def test_get_list(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, 'https://us1.api.mailchimp.com/3.0/lists/57afe96172',
                     json=self.get_list_1(), status=200, content_type='application/json')

            mc_list = MCList.get('57afe96172')
            self.assertEqual(1, len(rsps.calls))
            self.assertEqual("https://us1.api.mailchimp.com/3.0/lists/57afe96172", rsps.calls[0].request.url)
            self.assertEqual('GET', rsps.calls[0].request.method)
            self.assertEqual("application/json", rsps.calls[0].request.headers['Accept'])
            self.assertEqual("application/json", rsps.calls[0].request.headers['Content-Type'])
            self.assertEqual("Basic dXNlcm5hbWU6YTY1YTY1YTY1YTY1YTY1YTU2YTVhNi11czE=",
                             rsps.calls[0].request.headers['Authorization'])

            # Check list item
            self.assertEqual('57afe96172', mc_list.id)
            self.assertEqual("Freddie's Jokes", mc_list.name)
            self.assertEqual(12, len(mc_list.links))
            self.assertTrue(isinstance(mc_list.links[0], MCLink))
            self.assertTrue(isinstance(mc_list.contact, MCContact))
            self.assertEqual('MailChimp', mc_list.contact.company)
            self.assertTrue(isinstance(mc_list.stats, MCListStats))
            self.assertEqual(203, mc_list.stats.member_count)
            self.assertTrue(isinstance(mc_list.campaign_defaults, MCCampaignDefaults))

    def test_get_nonexistent_list(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, 'https://us1.api.mailchimp.com/3.0/lists/57afe96172',
                     json={'error': 'non existent list'}, status=404, content_type='application/json')

            with self.assertRaises(MCListNotFound):
                MCList.get('57afe96172')

    def test_empty_init(self):
        mc_list = MCList()

        for prop in ['id', 'name', 'permission_reminder', 'user_archive_bar', 'notify_on_subscribe',
                     'notify_on_unsubscribe', 'date_created', 'list_rating', 'email_type_option',
                     'subscribe_url_short', 'subscribe_url_long', 'beamer_address', 'visibility', 'modules']:
            self.assertIsNone(getattr(mc_list, prop))

        self.assertEqual(mc_list.links, [])
        self.assertTrue(isinstance(mc_list.contact, MCContact))
        self.assertTrue(isinstance(mc_list.stats, MCListStats))
        self.assertTrue(isinstance(mc_list.campaign_defaults, MCCampaignDefaults))

    def test_init(self):
        mc_list = MCList(self.get_list_1())

        self.assertEqual('57afe96172', mc_list.id)
        self.assertEqual("Freddie's Jokes", mc_list.name)
        self.assertEqual(12, len(mc_list.links))
        self.assertTrue(isinstance(mc_list.links[0], MCLink))
        self.assertTrue(isinstance(mc_list.contact, MCContact))
        self.assertEqual('MailChimp', mc_list.contact.company)
        self.assertTrue(isinstance(mc_list.stats, MCListStats))
        self.assertEqual(203, mc_list.stats.member_count)
        self.assertTrue(isinstance(mc_list.campaign_defaults, MCCampaignDefaults))

    def test_to_str(self):
        mc_list = MCList(self.get_list_1())
        self.assertEqual('57afe96172', str(mc_list))

    def test_repr(self):
        mc_list = MCList(self.get_list_1())
        self.assertEqual('<MCList: 57afe96172>', str(repr(mc_list)))

    def test_valid_search_params(self):
        mc_list = MCList()
        self.assertEqual(['offset', 'count', 'fields', 'exclude_fields', 'before_date_created','since_date_created'],
                         mc_list.valid_search_params)

    def test_item_url(self):
        mc_list = MCList()
        self.assertEqual("/lists", mc_list.item_url)