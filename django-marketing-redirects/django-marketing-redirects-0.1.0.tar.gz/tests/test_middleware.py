from django.test import TestCase
from django.test import modify_settings
from django.test import override_settings

from collections import OrderedDict

from django.conf import settings
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site

from django_marketing_redirects import models

try:
    # python 2
    import urlparse
except ModuleNotFoundError:
    # python 3
    import urllib.parse as urlparse


OLD_PATH = '/a/'
NEW_PATH_BASE = '/b/'
NEW_PATH = NEW_PATH_BASE + '?x=specified'

REQUESTS = dict(
    no_params=OLD_PATH,
    x_only=OLD_PATH + '?x=requested',
    y_only=OLD_PATH + '?y=requested',
    x_and_y=OLD_PATH + '?x=requested&y=requested'
)


class BaseMiddlewareTest(TestCase):

    def setUp(self, behavior):
        self.site = Site.objects.get(pk=settings.SITE_ID)
        self.redirect = Redirect.objects.create(site=self.site, old_path=OLD_PATH, new_path=NEW_PATH)
        self.item = models.RedirectWithQueryParams.objects.create(
            redirect=self.redirect,
            query_param_behavior=behavior,
        )

    def confirm_redirect(self, response, x=None, y=None):
        expected_params = OrderedDict()
        expected_url = NEW_PATH_BASE
        if x:
            expected_params['x'] = x
        if y:
            expected_params['y'] = y
        if len(expected_params) > 0:
            expected_url += '?' + urlparse.urlencode(expected_params)
        received_url = urlparse.urlsplit(response.url)
        if received_url.query:
            received_params = OrderedDict(sorted(urlparse.parse_qsl(received_url.query)))
            received_url = received_url.path + '?' + urlparse.urlencode(received_params)
        self.assertEqual(received_url, expected_url)
        self.assertRedirects(response, response.url, status_code=301, target_status_code=404)


@modify_settings(MIDDLEWARE={'append': 'django_marketing_redirects.middleware.RedirectFallbackMiddleware'})
@override_settings(APPEND_SLASH=False, ROOT_URLCONF='tests.urls', SITE_ID=1)
class RedirectRemoveQueryParamsTest(BaseMiddlewareTest):

    def setUp(self):
        super(RedirectRemoveQueryParamsTest, self).setUp(behavior='REMOVE')

    def test_no_params(self):
        response = self.client.get(REQUESTS['no_params'])
        self.confirm_redirect(response, x='specified')

    def test_x_only(self):
        response = self.client.get(REQUESTS['x_only'])
        self.confirm_redirect(response, x='specified')

    def test_y_only(self):
        response = self.client.get(REQUESTS['y_only'])
        self.confirm_redirect(response, x='specified')

    def test_x_and_y(self):
        response = self.client.get(REQUESTS['x_and_y'])
        self.confirm_redirect(response, x='specified')


@modify_settings(MIDDLEWARE={'append': 'django_marketing_redirects.middleware.RedirectFallbackMiddleware'})
@override_settings(APPEND_SLASH=False, ROOT_URLCONF='tests.urls', SITE_ID=1)
class RedirectRedirectWinsQueryParamsTest(BaseMiddlewareTest):

    def setUp(self):
        super(RedirectRedirectWinsQueryParamsTest, self).setUp(behavior='REDIRECT_WINS')

    def test_no_params(self):
        response = self.client.get(REQUESTS['no_params'])
        self.confirm_redirect(response, x='specified')

    def test_x_only(self):
        response = self.client.get(REQUESTS['x_only'])
        self.confirm_redirect(response, x='specified')

    def test_y_only(self):
        response = self.client.get(REQUESTS['y_only'])
        self.confirm_redirect(response, x='specified', y='requested')

    def test_x_and_y(self):
        response = self.client.get(REQUESTS['x_and_y'])
        self.confirm_redirect(response, x='specified', y='requested')


@modify_settings(MIDDLEWARE={'append': 'django_marketing_redirects.middleware.RedirectFallbackMiddleware'})
@override_settings(APPEND_SLASH=False, ROOT_URLCONF='tests.urls', SITE_ID=1)
class RedirectUserWinsQueryParamsTest(BaseMiddlewareTest):

    def setUp(self):
        super(RedirectUserWinsQueryParamsTest, self).setUp(behavior='QUERY_WINS')

    def test_no_params(self):
        response = self.client.get(REQUESTS['no_params'])
        self.confirm_redirect(response, x='specified')

    def test_x_only(self):
        response = self.client.get(REQUESTS['x_only'])
        self.confirm_redirect(response, x='requested')

    def test_y_only(self):
        response = self.client.get(REQUESTS['y_only'])
        self.confirm_redirect(response, x='specified', y='requested')

    def test_x_and_y(self):
        response = self.client.get(REQUESTS['x_and_y'])
        self.confirm_redirect(response, x='requested', y='requested')
