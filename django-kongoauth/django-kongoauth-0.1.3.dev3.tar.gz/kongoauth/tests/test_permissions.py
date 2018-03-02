from django.contrib.auth.models import User, Permission, ContentType
from rest_framework.test import APIRequestFactory
from ..permissions import KongOAuthPermission
from unittest import TestCase
from mock import MagicMock
from faker import Faker


def mock_has_perm(permission):
    if permission == 'all':
        return True
    return False


class KongOAuthPermissionTestCase(TestCase):

    def setUp(self):
        f = Faker()
        self.rf = APIRequestFactory()
        self.permission = KongOAuthPermission()
        self.request = MagicMock(user=MagicMock())
        self.view = MagicMock()
        self.request.user = User.objects.create_user(username=f.first_name())

    def test_has_group_permission(self):
        self.view.permission_list = ['.all']
        self.content_type = ContentType.objects.create(
            app_label='', model='unused')
        permission = Permission.objects.create(codename='all',
                                               name='all',
                                               content_type=self.content_type)
        self.request.user.user_permissions.add(permission)
        self.assertTrue(self.permission.has_permission(self.request,
                                                       self.view),
                        msg='Permission Failed')
        ContentType.delete(self.content_type)

    def test_has_obj_permission(self):
        self.view.permissions_map = {'list': ['.add_user', 'other_group']}
        self.content_type = ContentType.objects.create(
            app_label='', model='unused')
        self.request.method = 'GET'
        permission = Permission.objects.create(codename='add_user',
                                               name='add_user',
                                               content_type=self.content_type)
        obj = User.objects.create_user(username='test_object_user')
        self.request.user.user_permissions.add(permission)
        self.assertTrue(self.permission.has_object_permission(self.request,
                                                              self.view,
                                                              obj),
                        msg='Permission Failed')
        ContentType.delete(self.content_type)
