from django.test import TestCase


class SimpleTest(TestCase):
    def test_load_cz(self):
        from django_nuts.loaders import load_lau, load_nuts, load_other_nuts
        from django_nuts.cz_nuts4 import load_cz_nuts4
        from django_nuts.models import LAU, NUTS
        load_nuts('CZ', 'SK')
        load_lau('CZ', 'SK')
        load_cz_nuts4()
        load_other_nuts('AL')
        self.assertTrue(NUTS.objects.count() > 20)
        self.assertTrue(LAU.objects.count() > 5000)
        load_nuts()
        load_other_nuts()
        load_lau()
