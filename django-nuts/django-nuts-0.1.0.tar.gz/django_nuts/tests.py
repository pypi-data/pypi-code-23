from django.test import TestCase


class SimpleTest(TestCase):
    def test_load(self):
        from django_nuts import load_lau, load_nuts
        from django_nuts.models import LAU, NUTS
        load_nuts('CZ')
        load_lau('CZ')
        self.assertTrue(NUTS.objects.count() > 10)
        self.assertTrue(LAU.objects.count() > 1000)
