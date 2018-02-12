from django.test import TestCase


class SimpleTest(TestCase):
    def test_load_cz(self):
        from django_nuts.loaders import load_lau, load_nuts
        from django_nuts.cz_nuts4 import load_cz_nuts4
        from django_nuts.models import LAU, NUTS
        load_nuts('CZ', 'SK')
        load_lau('CZ', 'SK')
        load_cz_nuts4()
        self.assertTrue(NUTS.objects.count() > 10)
        self.assertTrue(LAU.objects.count() > 1000)
