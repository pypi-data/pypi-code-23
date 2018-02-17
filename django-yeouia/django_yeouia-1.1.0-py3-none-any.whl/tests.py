from django.contrib.auth.models import User
from django.test import TestCase


class YummyEmailOrUsernameInsensitiveAuthTests(TestCase):
    def setUp(self):
        User.objects.create_user('foo', email='foo@example.org', password='foo')
        User.objects.create_user('bar', email='bar@example.org', password='bar', is_active=False)
        User.objects.create_user('@nn@', email='anna@example.org', password='@nn@')
        User.objects.create_user('@NN@', email='anna@example.fr', password='@NN@')

    def test_login(self):
        self.assertTrue(self.client.login(username='foo', password='foo'))
        self.assertFalse(self.client.login(username='bar', password='bar'))
        self.assertTrue(self.client.login(username='fOo', password='foo'))
        self.assertTrue(self.client.login(username='foo@example.org', password='foo'))
        self.assertTrue(self.client.login(username='@nn@', password='@nn@'))
        self.assertFalse(self.client.login(username='@Nn@', password='@nn@'))
        self.assertFalse(self.client.login(username='@NN@', password='@nn@'))
        self.assertFalse(self.client.login(username='@nn@', password='@NN@'))
        self.assertTrue(self.client.login(username='ANNA@example.org', password='@nn@'))
        self.assertFalse(self.client.login(username='ofo', password='foo'))
        self.assertFalse(self.client.login(username='foo', password='fOo'))
