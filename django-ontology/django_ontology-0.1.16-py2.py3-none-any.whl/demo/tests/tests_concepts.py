from django.test import TestCase
from django.utils import translation

from demo.models import Article, Definition, Concept, Expression
from django_ontology.models import ontology_models, Language, get_language, NotTranslated


class ConceptTypeTests(TestCase):
    def test_discover_ontology_models(self):
        self.assertEqual(
            {Concept, Article, Definition},
            set(ontology_models())
        )

    def test_discover_expression_types(self):
        self.assertEqual(
            ["short"],
            list(t.type for t in Concept.expression_types)
        )

        self.assertEqual(
            ["short", "medium", "long"],
            list(t.type for t in Article.expression_types)
        )

        self.assertEqual(
            ["name", "text"],
            list(t.type for t in Definition.expression_types)
        )

#     TODO: def if definition has short descriptor, in that case remove it

    def test_filer_concepts_on_type_count(self):
        Concept(key="concept1").save()
        Concept(key="concept2").save()

        Article(key="article1").save()

        self.assertEqual(2, Concept.translate.count())
        self.assertEqual(1, Article.translate.count())
        self.assertEqual(0, Definition.translate.count())

    def test_filer_concepts_on_type_get(self):
        Concept(key="concept1").save()
        Concept(key="concept2").save()

        Article(key="article1").save()

        self.assertTrue(bool(Concept.translate.get(key="concept2")))
        self.assertTrue(bool(Article.translate.get(key="article1")))
        with self.assertRaises(Definition.DoesNotExist):
            Definition.translate.get(key="concept2")

    def test_filter_concepts_on_type_exists(self):
        Concept(key="concept1").save()
        self.assertFalse(Article.translate.filter(key="concept1").exists())


class ConceptLanguageTestCase(TestCase):
    def test_language_set_on_init(self):
        translation.activate("sv")
        c = Concept()
        self.assertEqual(c.language, get_language("sv"))

    def test_language_set_on_get(self):
        translation.activate("sv")
        Concept(key="concept1").save()

        c = Concept.translate.get(key="concept1")
        self.assertEqual(c.language, get_language("sv"))

    def test_language_set_on_all(self):
        translation.activate("sv")
        Concept(key="concept1").save()
        Concept(key="concept2").save()

        for c in Concept.translate.all():
            self.assertEqual(c.language, get_language("sv"))

    def test_set_language_explicitly_get(self):
        translation.activate("sv")
        Concept(key="concept1").save()

        c = Concept.translate.get(key="concept1", language="en")
        self.assertEqual(c.language, get_language("en"))

    def test_set_language_explicitly_init(self):
        translation.activate("sv")
        c = Concept(language="en")
        self.assertEqual(c.language, get_language("en"))

    def test_set_language_explicitly_all(self):
        translation.activate("sv")
        Concept(key="concept1").save()
        Concept(key="concept2").save()

        for c in Concept.translate.all(language="en"):
            self.assertEqual(c.language, get_language("en"))

    def test_delete_language_does_not_cascade_concepts(self):
        translation.activate("sv")
        Concept(key="concept1").save()
        Concept(key="concept2").save()

        self.assertEqual(Concept.translate.count(), 2)
        get_language("sv").delete()
        self.assertEqual(Concept.translate.count(), 2)

    # # TODO: fix
    # def test_language_inherited_by_related_concepts(self):
    #     translation.activate("sv")
    #
    #     c1 = Concept(key="concept1")
    #     c1.save()
    #     c2 = Concept(key="concept2", parent=c1)
    #     c2.save()
    #
    #     c2 = Concept.objects.get(key="concept2", language="en")
    #     self.assertEqual(c2.language, get_language("en"))
    #     self.assertEqual(c2.parent.language, get_language("en"))


class ConceptTranslateTestCase(TestCase):
    def setUp(self):
        super().setUp()

        # Language.cache.clear()

    def test_is_translated_by_default_init(self):
        c = Concept()
        self.assertTrue(c.translated)

    def test_is_translated_by_default_get(self):
        Concept(key="concept1").save()
        c = Concept.translate.get(key="concept1")
        self.assertTrue(c.translated)

    def test_disable_translation(self):
        Concept(key="concept1").save()
        c = Concept.translate.get(key="concept1", translate=False)
        self.assertFalse(c.translated)

    def test_single_query_when_translation_disabled_get(self):
        Concept(key="concept1").save()
        with self.assertNumQueries(1):
            c = Concept.translate.get(key="concept1", translate=False)

    def test_single_query_when_translation_disabled_all(self):
        Concept(key="concept1").save()
        Concept(key="concept2").save()
        with self.assertNumQueries(1):
            c = list(Concept.translate.all(translate=False))

    def test_not_translated_error_set_expression(self):
        Concept(key="concept1").save()
        c = Concept.translate.get(key="concept1", translate=False)
        with self.assertRaises(NotTranslated):
            c.short = "raise exception"

    def test_not_translated_error_get_expression(self):
        Concept(key="concept1").save()
        c = Concept.translate.get(key="concept1", translate=False)
        with self.assertRaises(NotTranslated):
            s = str(c.short)


class ConceptExpressionTestCase(TestCase):
    def setUp(self):
        self.root = Concept.translate.create(key="root")
        self.parent = Concept.translate.create(key="parent", parent=self.root)
        self.child1 = Concept.translate.create(key="child1", parent=self.parent)
        self.child2 = Concept.translate.create(key="child2", parent=self.parent)

        for concept in (self.root, self.parent, self.child1, self.child2):
            for language in Language.cache.all():
                Expression.objects.create(
                    concept_id=concept.key,
                    language=language,
                    type="short",
                    raw="%s_%s" % (concept.key, language.key)
                )

    def test_num_queries_get(self):
        translation.activate("sv")

        with self.assertNumQueries(2):
            c = Concept.translate.get(key="parent")
            self.assertEqual(str(c.short), "parent_sv")

    def test_num_queries_all(self):
        translation.activate("en")

        with self.assertNumQueries(2):
            for c in Concept.translate.all():
                self.assertEqual(str(c.short), "%s_en" % c.key)

    def test_num_queries_get_family(self):
        translation.activate("sv")
        with self.assertNumQueries(3):
            parent = Concept.translate.get(key="parent", translate=False)
            for c in parent.get_family(translate=True):
                self.assertEqual(str(c.short), "%s_sv" % c.key)

    def test_multiple_languages(self):
        en = Concept.translate.get(key="parent", language="en")
        sv = Concept.translate.get(key="parent", language="sv")

        self.assertEqual(str(en.short), "parent_en")
        self.assertEqual(str(sv.short), "parent_sv")

    def test_expression_field_set_create(self):
        translation.activate("sv")
        c = Concept(key="test")
        c.save()
        self.assertEqual(0, c.expressions.count())

        c.short = "create"
        self.assertEqual(1, c.expressions.count())
        self.assertEqual("create", Expression.objects.get(concept=c, language="sv", type="short").raw)

    def test_expression_field_update(self):
        translation.activate("sv")
        c = Concept.translate.get(key="root")
        self.assertEqual(str(c.short), "root_sv")

        c.short = "update"
        c = Concept.translate.get(key="root")
        self.assertEqual(str(c.short), "update")

    def test_expression_field_set_none(self):
        translation.activate("sv")
        c = Concept.translate.get(key="root")

        self.assertTrue(Expression.objects.filter(concept=c, language="sv", type="short").exists())
        c.short = None
        self.assertFalse(Expression.objects.filter(concept=c, language="sv", type="short").exists())

    def test_expression_field_set_empty_string(self):
        translation.activate("sv")
        c = Concept.translate.get(key="root")

        self.assertTrue(Expression.objects.filter(concept=c, language="sv", type="short").exists())
        c.short = ""
        self.assertFalse(Expression.objects.filter(concept=c, language="sv", type="short").exists())

    def test_delete_concept_cascade_expressions(self):
        c = Concept.translate.create(key="delete_me")
        c.short = "me_to!"
        expression_pk = c.short.pk

        c.delete()
        self.assertFalse(Expression.objects.filter(id=expression_pk).exists())

    def test_delete_language_cascade_expressions(self):
        en = get_language("en")
        ids = list(e.pk for e in Expression.objects.filter(language=en))
        en.delete()
        self.assertFalse(Expression.objects.filter(id__in=ids).exists())

    def test_formatted_empty_when_unformatted(self):
        self.assertIsNone(Concept.translate.get(key="root").short.formatted)

    def test_formatter(self):
        d = Definition(key="d1")
        d.save()
        d.name = "lower"
        self.assertEqual(str(d.name), "LOWER")

    def test_delete_parent_does_not_delete_children(self):
        Concept.translate.get(key="parent").delete()
        self.assertTrue(Concept.translate.filter(key="child1").exists())






















