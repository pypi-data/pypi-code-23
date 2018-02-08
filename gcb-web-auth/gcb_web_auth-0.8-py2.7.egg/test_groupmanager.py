from django.test import TestCase
from gcb_web_auth.groupmanager import make_users_groups_url, get_users_group_names, user_belongs_to_group
    #, user_belongs_to_group, get_users_group_names
from gcb_web_auth.models import GroupManagerConnection
from mock import patch, MagicMock


class GroupManagerFuncsTestCase(TestCase):
    def setUp(self):
        self.group_manager_connection = GroupManagerConnection.objects.create(
            base_url='https://fakegroupmanager.com',
            account_id='123',
            password='secret'
        )

    def test_make_users_groups_url(self):
        url = make_users_groups_url('https://stuff.com', duke_unique_id='123')
        self.assertEqual(url, 'https://stuff.com/subjects/123/groups',
                         "make_users_groups_url can build the correct url for fetching a users groups")

    @patch('gcb_web_auth.groupmanager.requests')
    def test_get_users_group_names(self, mock_requests):
        response = MagicMock()
        response.json.return_value = {
            'WsGetGroupsLiteResult': {
                'wsGroups': [{'name': 'duke:group1'}, {'name': 'duke:group2'}]
            }
        }
        mock_requests.get.return_value = response
        group_names = get_users_group_names(self.group_manager_connection, '123')
        self.assertEqual(group_names, ['duke:group1', 'duke:group2'],
                         "get_users_group_names pulls out group names from json response")

    @patch('gcb_web_auth.groupmanager.get_users_group_names')
    def test_user_belongs_to_group(self, mock_get_users_group_names):
        mock_get_users_group_names.return_value = ['group1', 'group2']
        self.assertTrue(user_belongs_to_group(self.group_manager_connection, '123', 'group1'),
                        "user_belongs_to_group returns True for groups in a users list")
        self.assertFalse(user_belongs_to_group(self.group_manager_connection, '123', 'group3'),
                         "user_belongs_to_group returns False for groups NOT in a users list")

