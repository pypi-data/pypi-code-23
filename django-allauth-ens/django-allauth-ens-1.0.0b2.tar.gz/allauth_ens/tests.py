import re

import django
from django.contrib.auth import HASH_SESSION_KEY, get_user_model
from django.contrib.sites.models import Site
from django.core import mail
from django.test import TestCase, override_settings

if django.VERSION >= (1, 10):
    from django.urls import reverse
else:
    from django.core.urlresolvers import reverse

User = get_user_model()


def prevent_logout_pwd_change(client, user):
    """
    Updating a user's password logs out all sessions for the user.
    By calling this function this behavior will be prevented.

    See this link, and the source code of `update_session_auth_hash`:
    https://docs.djangoproject.com/en/dev/topics/auth/default/#session-invalidation-on-password-change
    """
    if hasattr(user, 'get_session_auth_hash'):
        session = client.session
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.save()


class ViewsTests(TestCase):
    """
    Checks (barely) that templates do not contain errors.
    """
    def setUp(self):
        self.u = User.objects.create_user('user', 'user@mail.net', 'user')

        Site.objects.filter(pk=1).update(domain='testserver')

    def _login(self, client=None):
        if client is None:
            client = self.client
        client.login(username='user', password='user')

    def _get_confirm_email_link(self, email_msg):
        m = re.search(
            r'http://testserver(/accounts/confirm-email/.*/)',
            email_msg.body,
        )
        return m.group(1)

    def _get_reset_password_link(self, email_msg):
        m = re.search(
            r'http://testserver(/accounts/password/reset/key/.*/)',
            email_msg.body,
        )
        return m.group(1)

    def test_account_signup(self):
        r = self.client.get(reverse('account_signup'))
        self.assertEqual(r.status_code, 200)

    @override_settings(
        ACCOUNT_ADAPTER='tests.adapter.ClosedSignupAccountAdapter',
    )
    def test_account_closed_signup(self):
        r = self.client.get(reverse('account_signup'))
        self.assertEqual(r.status_code, 200)

    def test_account_login(self):
        r = self.client.get(reverse('account_login'))
        self.assertEqual(r.status_code, 200)

    def test_account_logout(self):
        self._login()
        r = self.client.get(reverse('account_logout'))
        self.assertEqual(r.status_code, 200)

    def test_account_change_password(self):
        self._login()
        r = self.client.get(reverse('account_change_password'))
        self.assertEqual(r.status_code, 200)

    def test_account_set_password(self):
        self._login()
        self.u.set_unusable_password()
        self.u.save()
        prevent_logout_pwd_change(self.client, self.u)

        r = self.client.get(reverse('account_set_password'))
        self.assertEqual(r.status_code, 200)

    def test_account_inactive(self):
        r = self.client.get(reverse('account_inactive'))
        self.assertEqual(r.status_code, 200)

    def test_account_email(self):
        self._login()
        r = self.client.get(reverse('account_email'))
        self.assertEqual(r.status_code, 200)

    def test_account_email_verification_sent(self):
        self._login()
        r = self.client.get(reverse('account_email_verification_sent'))
        self.assertEqual(r.status_code, 200)

    def test_account_confirm_email(self):
        self._login()
        self.client.post(reverse('account_email'), {
            'action_add': '',
            'email': 'test@mail.net',
        })
        confirm_url = self._get_confirm_email_link(mail.outbox[0])

        r = self.client.get(confirm_url)
        self.assertEqual(r.status_code, 200)

    def test_account_reset_password(self):
        r = self.client.get(reverse('account_reset_password'))
        self.assertEqual(r.status_code, 200)

    def test_account_reset_password_done(self):
        r = self.client.get(reverse('account_reset_password_done'))
        self.assertEqual(r.status_code, 200)

    def test_account_reset_password_from_key(self):
        self.client.post(reverse('account_reset_password'), {
            'email': 'user@mail.net',
        })
        reset_url = self._get_reset_password_link(mail.outbox[0])

        r = self.client.get(reset_url, follow=True)
        self.assertEqual(r.status_code, 200)

    def test_account_reset_password_from_key_done(self):
        r = self.client.get(reverse('account_reset_password_from_key_done'))
        self.assertEqual(r.status_code, 200)
