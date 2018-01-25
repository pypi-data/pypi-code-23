from django.contrib.auth import get_user_model

from allauth_cas.test.testcases import CASTestCase, CASViewTestCase

User = get_user_model()


class ClipperProviderTests(CASTestCase):

    def setUp(self):
        self.u = User.objects.create_user('user', 'user@mail.net', 'user')

    def test_auto_signup(self):
        self.client_cas_login(
            self.client, provider_id='clipper', username='clipper_uid')

        u = User.objects.get(username='clipper_uid')
        self.assertEqual(u.email, 'clipper_uid@clipper.ens.fr')


class ClipperViewsTests(CASViewTestCase):

    def test_login_view(self):
        r = self.client.get('/accounts/clipper/login/')
        expected = (
            "https://cas.eleves.ens.fr/login?service=http%3A%2F%2Ftestserver"
            "%2Faccounts%2Fclipper%2Flogin%2Fcallback%2F"
        )
        self.assertRedirects(
            r, expected,
            fetch_redirect_response=False,
        )

    def test_callback_view(self):
        # Required to initialize a SocialLogin.
        r = self.client.get('/accounts/clipper/login/')

        # Tests.
        self.patch_cas_response(valid_ticket='__all__')
        r = self.client.get('/accounts/clipper/login/callback/', {
            'ticket': '123456',
        })
        self.assertLoginSuccess(r)

    def test_logout_view(self):
        r = self.client.get('/accounts/clipper/logout/')
        expected = (
            "https://cas.eleves.ens.fr/logout?service=http%3A%2F%2Ftestserver"
            "%2F"
        )
        self.assertRedirects(
            r, expected,
            fetch_redirect_response=False,
        )
