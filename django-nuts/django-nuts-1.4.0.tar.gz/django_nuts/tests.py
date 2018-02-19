from django.test import TestCase


class SimpleTest(TestCase):
    def test_load_all(self):
        from django_nuts.loaders import load_lau, load_nuts, load_other_nuts
        from django_nuts.models import LAU, NUTS
        load_nuts()
        load_other_nuts()
        load_lau()
        self.assertTrue(NUTS.objects.count() > 1500)
        self.assertTrue(LAU.objects.count() > 9000)

    def test_load_cz_nuts_lau(self):
        from django_nuts.loaders.cz_nuts4_lau import load_cz_nuts4_lau
        from django_nuts.models import LAU, NUTS
        load_cz_nuts4_lau()
        self.assertTrue(NUTS.objects.count() > 20)
        self.assertTrue(LAU.objects.count() > 5000)

    def test_load_cz(self):
        from django_nuts.loaders.cz_nuts import load_cz_nuts
        from django_nuts.models import NUTS
        load_cz_nuts()
        self.assertEqual(NUTS.objects.count(), 101)

    def test_load_sk(self):
        from django_nuts.loaders.sk_nuts import load_sk_nuts
        from django_nuts.models import NUTS
        load_sk_nuts()
        self.assertEqual(NUTS.objects.count(), 93)
