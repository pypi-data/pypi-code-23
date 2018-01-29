from django.test import TestCase

from demo.models import Article, StaticConcept
from demo.static import Root


class StaticArticleTestCase(TestCase):
    def setUp(self):
        Article.clear_static_cache()

    def test_load(self):
        Root.load()

        self.assertEqual(Article.translate.count(), 6)

        Article.static_cache = None

        with self.assertNumQueries(3):
            Root.load()

        self.assertTrue(Article.translate.get(key="child1", parent_id="Parent1"))

        with self.assertNumQueries(0):
            self.assertTrue(Root.Parent2.child3.concept)

    def test_save_model_clears_cache(self):
        Root.load()

        self.assertTrue(Root.is_loaded)
        Article(key="new_concept").save()
        self.assertFalse(Root.is_loaded)

    def test_delete_model_clears_cache_get(self):
        Root.load()

        self.assertTrue(Root.is_loaded)
        c = Article.translate.get(key="Root")
        c.delete()
        self.assertFalse(Root.is_loaded)

    def test_delete_model_clears_cache_filter(self):
        Root.load()

        self.assertTrue(Root.is_loaded)
        Article.translate.filter(key="Root").delete()
        self.assertFalse(Root.is_loaded)


class StaticTestX(StaticConcept):
    key = "test_replace_key"

