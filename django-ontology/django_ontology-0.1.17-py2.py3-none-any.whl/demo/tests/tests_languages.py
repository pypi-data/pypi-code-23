from django.test import TestCase, modify_settings, override_settings
from django.utils import translation

from django_ontology.models import Language, get_language

LANGUAGE_SETTINGS = {
    "LANGUAGES": (("en", "English"), ("sv", "Svenska")),
    "LANGUAGE": "sv"
}


class CreateLanguageTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Language.objects.all().delete()

    def setUp(self):
        Language.cache.clear()

    @override_settings(**LANGUAGE_SETTINGS)
    def test_automatically_created(self):
        self.assertEqual(0, Language.objects.count())

        keys = list(l.key for l in Language.cache.all())

        self.assertEqual(2, Language.objects.count())

        self.assertIn("sv", keys)
        self.assertIn("en", keys)

    @override_settings(**LANGUAGE_SETTINGS)
    def test_languages_cached(self):
        # muliple queries when creates
        languages = list(Language.cache.all())
        Language.cache.clear()

        with self.assertNumQueries(1):
            languages = list(Language.cache.all())

        with self.assertNumQueries(0):
            languages = list(Language.cache.all())
            sv = Language.cache.get(key="sv")

    @override_settings(**LANGUAGE_SETTINGS)
    def test_cache_cleared_on_save(self):
        languages = list(Language.cache.all())
        self.assertTrue(Language.cache)

        languages[0].save()

        self.assertFalse(Language.cache)

    @override_settings(**LANGUAGE_SETTINGS)
    def test_languages_not_loaded_by_default(self):
        self.assertFalse(Language.cache)

    @override_settings(**LANGUAGE_SETTINGS)
    def test_get_language_none(self):
        translation.activate("sv")
        self.assertEqual(Language.cache.get(key="sv"), get_language(None))

    @override_settings(**LANGUAGE_SETTINGS)
    def test_get_language_code(self):
        self.assertEqual(Language.cache.get(key="en"), get_language("en"))

    @override_settings(**LANGUAGE_SETTINGS)
    def test_get_language_language_instance(self):
        self.assertEqual(Language.cache.get(key="en"), get_language(Language.cache.get(key="en")))

    @override_settings(**LANGUAGE_SETTINGS)
    def test_get_language_does_not_exists(self):
        with self.assertRaises(Language.DoesNotExist):
            get_language("de")

    def test_clear_cache_on_delete(self):
        # TODO
        pass





