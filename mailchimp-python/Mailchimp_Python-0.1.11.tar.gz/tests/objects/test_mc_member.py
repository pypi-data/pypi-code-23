# coding=utf-8
import datetime
from dateutil.tz import tzutc
import responses
import unittest
from mailchimp.config import mailchimp_config
from mailchimp.exceptions import MCMemberNotFound
from mailchimp.objects import MCMember, MCLocation


class TestMCMember(unittest.TestCase):
    def setUp(self):
        mailchimp_config.api_key = 'a65a65a65a65a65a56a5a6-us1'

    def get_member_1(self):
        return {
            "id": "852aaa9532cb36adfb5e9fef7a4206a9",
            "email_address": "urist.mcvankab+3@freddiesjokes.com",
            "unique_email_id": "fab20fa03d",
            "email_type": "html",
            "status": "subscribed",
            "status_if_new": "",
            "merge_fields": {
                "FNAME": "",
                "LNAME": ""
            },
            "interests": {
                "9143cf3bd1": False,
                "3a2a927344": False,
                "f9c8f5f0ff": False,
                "f231b09abc": False,
                "bd6e66465f": False
            },
            "stats": {
                "avg_open_rate": 0,
                "avg_click_rate": 0
            },
            "ip_signup": "",
            "timestamp_signup": "",
            "ip_opt": "198.2.191.34",
            "timestamp_opt": "2015-09-15T17:27:16+00:00",
            "member_rating": 2,
            "last_changed": "2015-09-15T17:27:16+00:00",
            "language": "",
            "vip": False,
            "email_client": "",
            "location": {
                "latitude": 0,
                "longitude": 0,
                "gmtoff": 0,
                "dstoff": 0,
                "country_code": "",
                "timezone": ""
            },
            "list_id": "57afe96172",
            "_links": [
                {
                    "rel": "self",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Instance.json"
                },
                {
                    "rel": "parent",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Members.json"
                },
                {
                    "rel": "update",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9",
                    "method": "PATCH",
                    "schema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Instance.json"
                },
                {
                    "rel": "upsert",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9",
                    "method": "PUT",
                    "schema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Instance.json"
                },
                {
                    "rel": "delete",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9",
                    "method": "DELETE"
                },
                {
                    "rel": "activity",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9/activity",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Activity/Collection.json"
                },
                {
                    "rel": "goals",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9/goals",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Goals/Collection.json"
                },
                {
                    "rel": "notes",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9/notes",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Notes/Collection.json"
                }
            ]
        }

    def get_updated_member_1(self):
        return {
            "id": "852aaa9532cb36adfb5e9fef7a4206a9",
            "email_address": "urist.mcvankab+3@freddiesjokes.com",
            "unique_email_id": "fab20fa03d",
            "email_type": "html",
            "status": "unsubscribed",
            "status_if_new": "",
            "merge_fields": {
                "FNAME": "Firstname",
                "LNAME": "Surname"
            },
            "interests": {
                "9143cf3bd1": False,
                "3a2a927344": False,
                "f9c8f5f0ff": False,
                "f231b09abc": False,
                "bd6e66465f": False
            },
            "stats": {
                "avg_open_rate": 0,
                "avg_click_rate": 0
            },
            "ip_signup": "",
            "timestamp_signup": "",
            "ip_opt": "198.2.191.34",
            "timestamp_opt": "2015-09-15T17:27:16+00:00",
            "member_rating": 2,
            "last_changed": "2016-09-15T17:27:16+00:00",
            "language": "",
            "vip": False,
            "email_client": "",
            "location": {
                "latitude": 0,
                "longitude": 0,
                "gmtoff": 0,
                "dstoff": 0,
                "country_code": "",
                "timezone": ""
            },
            "list_id": "57afe96172",
            "_links": [
                {
                    "rel": "self",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Instance.json"
                },
                {
                    "rel": "parent",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Members.json"
                },
                {
                    "rel": "update",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9",
                    "method": "PATCH",
                    "schema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Instance.json"
                },
                {
                    "rel": "upsert",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9",
                    "method": "PUT",
                    "schema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Instance.json"
                },
                {
                    "rel": "delete",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9",
                    "method": "DELETE"
                },
                {
                    "rel": "activity",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9/activity",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Activity/Collection.json"
                },
                {
                    "rel": "goals",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9/goals",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Goals/Collection.json"
                },
                {
                    "rel": "notes",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/852aaa9532cb36adfb5e9fef7a4206a9/notes",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Notes/Collection.json"
                }
            ]
        }

    def get_member_2(self):
        return {
            "id": "3de9374357fa55432c8e395935b806df",
            "email_address": "urist.mcvankab+3@freddiesjokes.se",
            "unique_email_id": "fab20fa03e",
            "email_type": "html",
            "status": "subscribed",
            "status_if_new": "",
            "merge_fields": {
                "FNAME": "",
                "LNAME": ""
            },
            "interests": {
                "9143cf3bd1": False,
                "3a2a927344": False,
                "f9c8f5f0ff": False,
                "f231b09abc": False,
                "bd6e66465f": False
            },
            "stats": {
                "avg_open_rate": 0,
                "avg_click_rate": 0
            },
            "ip_signup": "",
            "timestamp_signup": "",
            "ip_opt": "198.2.191.34",
            "timestamp_opt": "2015-09-15T17:27:16+00:00",
            "member_rating": 2,
            "last_changed": "2015-09-15T17:27:16+00:00",
            "language": "",
            "vip": False,
            "email_client": "",
            "location": {
                "latitude": 0,
                "longitude": 0,
                "gmtoff": 0,
                "dstoff": 0,
                "country_code": "",
                "timezone": ""
            },
            "list_id": "57afe96172",
            "_links": [
                {
                    "rel": "self",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/3de9374357fa55432c8e395935b806df",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Instance.json"
                },
                {
                    "rel": "parent",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Collection.json",
                    "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Members.json"
                },
                {
                    "rel": "update",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/3de9374357fa55432c8e395935b806df",
                    "method": "PATCH",
                    "schema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Instance.json"
                },
                {
                    "rel": "upsert",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/3de9374357fa55432c8e395935b806df",
                    "method": "PUT",
                    "schema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Instance.json"
                },
                {
                    "rel": "delete",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/3de9374357fa55432c8e395935b806df",
                    "method": "DELETE"
                },
                {
                    "rel": "activity",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/3de9374357fa55432c8e395935b806df/activity",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Activity/Collection.json"
                },
                {
                    "rel": "goals",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/3de9374357fa55432c8e395935b806df/goals",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Goals/Collection.json"
                },
                {
                    "rel": "notes",
                    "href": "https://us1.api.mailchimp.com/3.0/lists/57afe96172/members/3de9374357fa55432c8e395935b806df/notes",
                    "method": "GET",
                    "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Notes/Collection.json"
                }
            ]
        }

    def check_member_1(self, member):
        self.assertEqual(member.id, '852aaa9532cb36adfb5e9fef7a4206a9')
        self.assertEqual(member.email_address, 'urist.mcvankab+3@freddiesjokes.com')
        self.assertEqual(member.unique_email_id, 'fab20fa03d')
        self.assertEqual(member.email_type, 'html')
        self.assertEqual(member.status, 'subscribed')
        self.assertEqual(member.status_if_new, '')
        self.assertEqual(member.merge_fields, {
            "FNAME": "",
            "LNAME": ""
        })
        self.assertEqual(member.interests, {
            "9143cf3bd1": False,
            "3a2a927344": False,
            "f9c8f5f0ff": False,
            "f231b09abc": False,
            "bd6e66465f": False
        })
        self.assertEqual(member.stats, {
            "avg_open_rate": 0,
            "avg_click_rate": 0
        })
        self.assertEqual(member.ip_signup, "")
        self.assertIsNone(member.timestamp_signup)
        self.assertEqual(member.ip_opt, "198.2.191.34")
        self.assertEqual(member.timestamp_opt, datetime.datetime(2015, 9, 15, 17, 27, 16).replace(tzinfo=tzutc()))
        self.assertEqual(member.member_rating, 2)
        self.assertEqual(member.last_changed, datetime.datetime(2015, 9, 15, 17, 27, 16).replace(tzinfo=tzutc()))
        self.assertEqual(member.language, "")
        self.assertFalse(member.vip)
        self.assertEqual(member.email_client, "")
        self.assertTrue(isinstance(member.location, MCLocation))
        self.assertEqual(member.location.longitude, 0)
        self.assertEqual(member.location.latitude, 0)
        self.assertEqual(member.location.gmtoff, 0)
        self.assertEqual(member.location.dstoff, 0)
        self.assertEqual(member.location.country_code, "")
        self.assertEqual(member.location.timezone, "")
        self.assertEqual(member.list_id, "57afe96172")
        self.assertEqual(len(member.links), 8)

    def check_member_2(self, member):
        self.assertEqual(member.id, '3de9374357fa55432c8e395935b806df')
        self.assertEqual(member.email_address, 'urist.mcvankab+3@freddiesjokes.se')
        self.assertEqual(member.unique_email_id, 'fab20fa03e')
        self.assertEqual(member.email_type, 'html')
        self.assertEqual(member.status, 'subscribed')
        self.assertEqual(member.status_if_new, '')
        self.assertEqual(member.merge_fields, {
            "FNAME": "",
            "LNAME": ""
        })
        self.assertEqual(member.interests, {
            "9143cf3bd1": False,
            "3a2a927344": False,
            "f9c8f5f0ff": False,
            "f231b09abc": False,
            "bd6e66465f": False
        })
        self.assertEqual(member.stats, {
            "avg_open_rate": 0,
            "avg_click_rate": 0
        })
        self.assertEqual(member.ip_signup, "")
        self.assertIsNone(member.timestamp_signup)
        self.assertEqual(member.ip_opt, "198.2.191.34")
        self.assertEqual(member.timestamp_opt, datetime.datetime(2015, 9, 15, 17, 27, 16).replace(tzinfo=tzutc()))
        self.assertEqual(member.member_rating, 2)
        self.assertEqual(member.last_changed, datetime.datetime(2015, 9, 15, 17, 27, 16).replace(tzinfo=tzutc()))
        self.assertEqual(member.language, "")
        self.assertFalse(member.vip)
        self.assertEqual(member.email_client, "")
        self.assertTrue(isinstance(member.location, MCLocation))
        self.assertEqual(member.location.longitude, 0)
        self.assertEqual(member.location.latitude, 0)
        self.assertEqual(member.location.gmtoff, 0)
        self.assertEqual(member.location.dstoff, 0)
        self.assertEqual(member.location.country_code, "")
        self.assertEqual(member.location.timezone, "")
        self.assertEqual(member.list_id, "57afe96172")
        self.assertEqual(len(member.links), 8)

    def test_item_url(self):
        member = MCMember()
        self.assertEqual('/lists/{list_id}/members', member.item_url)

    def test_get_list_url(self):
        self.assertEqual('/lists/57afe96172/members', MCMember.get_list_url('57afe96172'))

    def test_to_dict_without_id(self):
        member = MCMember(self.get_member_1())
        member.id = None
        self.assertEqual({
            'email_type': member.email_type,
            'status': member.status,
            'merge_fields': member.merge_fields,
            'interests': member.interests,
            'language': member.language,
            'vip': member.vip,
            'location': member.location.to_dict(),
            'email_address': member.email_address,
            'status_if_new': member.status_if_new
        }, member.to_dict())

    def test_to_dict_with_id(self):
        member = MCMember(self.get_member_1())
        self.assertEqual({
            'email_type': member.email_type,
            'status': member.status,
            'merge_fields': member.merge_fields,
            'interests': member.interests,
            'language': member.language,
            'vip': member.vip,
            'location': member.location.to_dict(),
            'id': member.id
        }, member.to_dict())

    def test_valid_search_params(self):
        member = MCMember()
        self.assertEqual(['offset', 'count', 'fields', 'exclude_fields'],
                         member.valid_search_params)

    def test_empty_init(self):
        member = MCMember()

        for prop in ['id', 'email_address', 'unique_email_id', 'email_type', 'status', 'status_if_new', 'merge_fields',
                     'interests', 'stats', 'ip_signup', 'timestamp_signup', 'ip_opt', 'timestamp_opt', 'member_rating',
                     'last_changed', 'language', 'vip', 'email_client', 'list_id']:
            self.assertIsNone(getattr(member, prop))

        self.assertTrue(isinstance(member.location, MCLocation))
        self.assertEqual(member.links, [])

    def test_init(self):
        member = MCMember(self.get_member_1())

        self.check_member_1(member)

    def test_to_str(self):
        member = MCMember(self.get_member_1())
        self.assertEqual('852aaa9532cb36adfb5e9fef7a4206a9', str(member))

    def test_repr(self):
        member = MCMember(self.get_member_1())
        self.assertEqual('<MCMember: 852aaa9532cb36adfb5e9fef7a4206a9>', str(repr(member)))

    def test_get(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, 'https://us1.api.mailchimp.com/3.0/lists/57afe96172/'
                                    'members/852aaa9532cb36adfb5e9fef7a4206a9',
                     json=self.get_member_1(), status=200, content_type='application/json')

            mc_member = MCMember.get('57afe96172', '852aaa9532cb36adfb5e9fef7a4206a9')
            self.assertEqual(1, len(rsps.calls))
            self.assertEqual('https://us1.api.mailchimp.com/3.0/lists/57afe96172/'
                             'members/852aaa9532cb36adfb5e9fef7a4206a9', rsps.calls[0].request.url)
            self.assertEqual('GET', rsps.calls[0].request.method)
            self.assertEqual("application/json", rsps.calls[0].request.headers['Accept'])
            self.assertEqual("application/json", rsps.calls[0].request.headers['Content-Type'])
            self.assertEqual("Basic dXNlcm5hbWU6YTY1YTY1YTY1YTY1YTY1YTU2YTVhNi11czE=",
                             rsps.calls[0].request.headers['Authorization'])

            self.check_member_1(mc_member)

    def test_get_nonexistent_member(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, 'https://us1.api.mailchimp.com/3.0/lists/57afe96172/'
                                    'members/852aaa9532cb36adfb5e9fef7a4206a9',
                     json={'error': 'non existent list'}, status=404, content_type='application/json')

            with self.assertRaises(MCMemberNotFound):
                MCMember.get('57afe96172', '852aaa9532cb36adfb5e9fef7a4206a9')

    def test_list(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, 'https://us1.api.mailchimp.com/3.0/lists/57afe96172/members',
                     json={
                         'members': [self.get_member_1(), self.get_member_2()],
                         "list_id": "57afe96172",
                         "_links": [
                             {
                                 "rel": "self",
                                 "href": "https://usX.api.mailchimp.com/3.0/lists/57afe96172/members",
                                 "method": "GET",
                                 "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Collection.json",
                                 "schema": "https://api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Members.json"
                             },
                             {
                                 "rel": "parent",
                                 "href": "https://usX.api.mailchimp.com/3.0/lists/57afe96172",
                                 "method": "GET",
                                 "targetSchema": "https://api.mailchimp.com/schema/3.0/Lists/Instance.json"
                             },
                             {
                                 "rel": "create",
                                 "href": "https://usX.api.mailchimp.com/3.0/lists/57afe96172/members",
                                 "method": "POST",
                                 "schema": "https://api.mailchimp.com/schema/3.0/Lists/Members/Instance.json"
                             }
                         ],
                         "total_items": 2
                     }, status=200, content_type='application/json')

            mc_members = MCMember.list('57afe96172')
            self.assertEqual(1, len(rsps.calls))
            self.assertEqual('https://us1.api.mailchimp.com/3.0/lists/57afe96172/members', rsps.calls[0].request.url)
            self.assertEqual('GET', rsps.calls[0].request.method)
            self.assertEqual("application/json", rsps.calls[0].request.headers['Accept'])
            self.assertEqual("application/json", rsps.calls[0].request.headers['Content-Type'])
            self.assertEqual("Basic dXNlcm5hbWU6YTY1YTY1YTY1YTY1YTY1YTU2YTVhNi11czE=",
                             rsps.calls[0].request.headers['Authorization'])

            self.check_member_1(mc_members[0])
            self.check_member_2(mc_members[1])

    def test_delete(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.DELETE, 'https://us1.api.mailchimp.com/3.0/lists/57afe96172/'
                                       'members/852aaa9532cb36adfb5e9fef7a4206a9',
                     json={}, status=204, content_type='application/json')

            mc_member = MCMember(self.get_member_1())
            mc_member.delete()

            self.assertEqual(1, len(rsps.calls))
            self.assertEqual('https://us1.api.mailchimp.com/3.0/lists/57afe96172/'
                             'members/852aaa9532cb36adfb5e9fef7a4206a9', rsps.calls[0].request.url)
            self.assertEqual('DELETE', rsps.calls[0].request.method)
            self.assertEqual("application/json", rsps.calls[0].request.headers['Accept'])
            self.assertEqual("application/json", rsps.calls[0].request.headers['Content-Type'])
            self.assertEqual("Basic dXNlcm5hbWU6YTY1YTY1YTY1YTY1YTY1YTU2YTVhNi11czE=",
                             rsps.calls[0].request.headers['Authorization'])

    def test_save(self):
        with responses.RequestsMock() as rsps:
            rsps.add(responses.PUT, 'https://us1.api.mailchimp.com/3.0/lists/57afe96172/'
                                    'members/852aaa9532cb36adfb5e9fef7a4206a9',
                     json=self.get_updated_member_1(), status=200, content_type='application/json')

            mc_member = MCMember(self.get_member_1())
            mc_member.status = 'unsubscribed'
            mc_member.merge_fields = {
                "FNAME": "Firstname",
                "LNAME": "Surname"
            }
            mc_member.save()

            self.assertEqual(1, len(rsps.calls))
            self.assertEqual('https://us1.api.mailchimp.com/3.0/lists/57afe96172/'
                             'members/852aaa9532cb36adfb5e9fef7a4206a9', rsps.calls[0].request.url)
            self.assertEqual('PUT', rsps.calls[0].request.method)
            self.assertEqual("application/json", rsps.calls[0].request.headers['Accept'])
            self.assertEqual("application/json", rsps.calls[0].request.headers['Content-Type'])
            self.assertEqual("Basic dXNlcm5hbWU6YTY1YTY1YTY1YTY1YTY1YTU2YTVhNi11czE=",
                             rsps.calls[0].request.headers['Authorization'])

            self.assertEqual(mc_member.last_changed, datetime.datetime(2016, 9, 15, 17, 27, 16).replace(tzinfo=tzutc()))
