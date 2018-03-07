import unittest

from django.contrib.redirects.models import Redirect

from django_marketing_redirects import models


class RedirectWithQueryParamsTest(unittest.TestCase):

    def setUp(self):
        self.redirect = Redirect(site_id=1, old_path='abc', new_path='cba')
        self.item = models.RedirectWithQueryParams(redirect=self.redirect)

    def test_fields_exist(self):
        self.assertIsNotNone(self.item.redirect)
        self.assertIsNotNone(self.item.query_param_behavior)

    def test_query_param_choices(self):
        choice_dbvals = [c[0] for c in models.QUERY_PARAM_CHOICES]
        self.assertEqual(len(choice_dbvals), 3)
        self.assertIn('REMOVE', choice_dbvals)
        self.assertIn('REDIRECT_WINS', choice_dbvals)
        self.assertIn('QUERY_WINS', choice_dbvals)
