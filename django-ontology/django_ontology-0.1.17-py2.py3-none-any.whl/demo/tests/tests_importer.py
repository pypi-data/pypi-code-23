from itertools import zip_longest

from django.test import TestCase
from django.utils import translation

from demo.models import Concept, Expression
from django_ontology.api.importer import ApiRow, OntologyApiActions, OntologyImporter, ConceptNotFound
from django_ontology.models import Language, ExpressionField


def get_tree_details(nodes):
    """
    Creates pertinent tree details for the given list of nodes.
    The fields are:
        id  parent_id  tree_id  level  left  right
    """
    if hasattr(nodes, 'order_by'):
        nodes = list(nodes.order_by('tree_id', 'lft', 'pk'))
    nodes = list(nodes)
    opts = nodes[0]._mptt_meta
    return '\n'.join(['%s %s %s %s %s %s' %
                      (n.pk, getattr(n, '%s_id' % opts.parent_attr) or '-',
                       getattr(n, opts.tree_id_attr), getattr(n, opts.level_attr),
                       getattr(n, opts.left_attr), getattr(n, opts.right_attr))
                      for n in nodes])

class ImporterTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.language, created = Language.objects.get_or_create(key="en", name="English")
        Language.objects.update_or_create(key="sv", defaults={"name": "Svenska"})

        cls.model = Concept

    @classmethod
    def tearDownClass(cls):
        Language.objects.all().delete()
        Concept.translate.all().delete()
        Expression.objects.all().delete()

    def assertImport(self, delete=None, create=None, update=None, ignored=None, noop=None, success=True, model=None,
                     language=None, rows=None, row=None, exceptions=None):
        rows = ([row] if row else []) + (rows or [])

        result = OntologyImporter(
            model=model or self.model,
            language=language or self.language,
            rows=rows
        ).result

        if exceptions:
            success = False

        if success:
            self.assertTrue(
                result.success,
                msg="The import failed with the following errors %s" % list(str(e) for e in result.exceptions)
            )
            self.assertEqual(len(result.delete), delete or 0)
            self.assertEqual(len(result.create), create or 0)
            self.assertEqual(len(result.update), update or 0)
            self.assertEqual(len(result.ignored_rows), ignored or 0)
            self.assertEqual(len(result.noop), noop or 0)
        else:
            if exceptions:
                for exception, expected in zip_longest(result.exceptions, exceptions):
                    if isinstance(expected, Exception):
                        self.assertEqual(exception, expected)
                    else:
                        self.assertTrue(isinstance(exception, expected))

            self.assertFalse(result.success)

    def assertRowConcept(self, row, concept, model=None):
        if row.parent != OntologyApiActions.noop:
            self.assertEqual(row.parent, concept.parent_id)

        for expression_type in (model or self.model).expression_types:
            row_expression = row.get_expression(expression_type)
            if row_expression != OntologyApiActions.noop:
                self.assertEqual(row_expression, concept.get_expression(expression_type).raw)

    def setUp(self):
        translation.activate("en")

    def test_create_root(self):
        row = ApiRow(
            action=OntologyApiActions.create,
            key="add_root",
            parent=None,
            short="Add root test"
        )
        self.assertImport(row=row, create=1)
        self.assertRowConcept(row, Concept.translate.get(key="add_root"))

    def test_create_child(self):
        parent = Concept.translate.create(key="parent")
        row = ApiRow(
            action=OntologyApiActions.create,
            key="child",
            parent="parent",
            short="Add child test"
        )
        self.assertImport(row=row, create=1)
        child = Concept.translate.get(key="child")
        self.assertRowConcept(row, child)
        self.assertEqual(parent, child.parent)

    def test_create_parent_and_child(self):
        parent_row = ApiRow(
            action=OntologyApiActions.create,
            key="parent",
            parent=None,
            short="Add parent"
        )
        child_row = ApiRow(
            action=OntologyApiActions.create,
            key="child",
            parent="parent",
            short="Add child"
        )
        self.assertImport(create=2, rows=[parent_row, child_row])
        self.assertRowConcept(parent_row, Concept.translate.get(key="parent"))
        self.assertRowConcept(child_row, Concept.translate.get(key="child"))

    def test_create_parent_child_wrong_order(self):
        parent_row = ApiRow(
            action=OntologyApiActions.create,
            key="parent",
            parent=None,
            short="Add parent"
        )
        child_row = ApiRow(
            action=OntologyApiActions.create,
            key="child",
            parent="parent",
            short="Add child"
        )
        self.assertImport(success=False, rows=[child_row, parent_row])
        self.assertEqual(Concept.translate.count(), 0)

    def test_create_duplicate_key_noop(self):
        concept = Concept.translate.create(key="duplicated_key")
        row = ApiRow(
            action=OntologyApiActions.create,
            key="duplicated_key",
        )
        self.assertImport(row=row, noop=1)
        self.assertRowConcept(row, concept)

    def test_create_duplicate_key_update(self):
        Concept.translate.create(key="duplicated_key")
        row = ApiRow(
            action=OntologyApiActions.create,
            key="duplicated_key",
            short="short update"
        )
        self.assertImport(row=row, update=1)
        concept = Concept.translate.get(key="duplicated_key")
        self.assertRowConcept(row, concept)

    def test_update(self):
        Concept.translate.create(key="parent")
        Concept.translate.create(key="child")

        row = ApiRow(
            action=OntologyApiActions.update,
            key="child",
            short="child short",
            parent="parent"
        )
        self.assertImport(row=row, update=1)
        self.assertRowConcept(row, Concept.translate.get(key="child"))

    def test_update_does_not_exist(self):
        row = ApiRow(
            action=OntologyApiActions.update,
            key="concept",
            short="concept short",
            parent=None
        )
        self.assertImport(row=row, exceptions=(Concept.DoesNotExist,))
        # self.assertRowConcept(row, Concept.objects.get(key="child"))

    def test_update_parent_does_not_exist(self):
        Concept.translate.create(key="child")

        row = ApiRow(
            action=OntologyApiActions.update,
            key="child",
            short="child short",
            parent="parent"
        )
        self.assertImport(row=row, exceptions=(Concept.DoesNotExist,))

    def test_delete(self):
        Concept.translate.create(key="child")

        row = ApiRow(
            action=OntologyApiActions.delete,
            key="child",
            short="child short",
            parent="parent"
        )
        self.assertImport(row=row, delete=1)
        self.assertFalse(Concept.translate.filter(key="child").exists())

    def test_create_delete(self):
        create = ApiRow(
            action=OntologyApiActions.create,
            key="child",
            parent=None,
            short="Add child test"
        )
        delete = ApiRow(
            action=OntologyApiActions.delete,
            key="child",
            parent="parent",
            short="Add child test"
        )
        self.assertImport(rows=[create, delete], create=1, delete=1)
        self.assertFalse(Concept.translate.filter(key="child").exists())

    def test_delete_does_not_exist(self):
        delete = ApiRow(
            action=OntologyApiActions.delete,
            key="child",
            parent="parent",
            short="Add child test"
        )
        self.assertImport(rows=[delete], noop=1)

    def test_create_tripple(self):
        rows = [
            ApiRow(
                action=OntologyApiActions.create,
                key="root",
            ),
            ApiRow(
                action=OntologyApiActions.create,
                key="node",
                parent="root"
            ),
            ApiRow(
                action=OntologyApiActions.create,
                key="leaf1",
                parent="node"
            ),
            ApiRow(
                action=OntologyApiActions.create,
                key="leaf2",
                parent="node"
            ),
            ApiRow(
                action=OntologyApiActions.create,
                key="leaf3",
                parent="node"
            ),
            ApiRow(
                action=OntologyApiActions.create,
                key="leaf4",
                parent="node"
            ),
            ApiRow(
                action=OntologyApiActions.create,
                key="node2",
                parent="root"
            ),
            ApiRow(
                action=OntologyApiActions.create,
                key="root2"
            )
        ]
        self.assertImport(rows=rows, create=8)
        before = get_tree_details(Concept.objects.all())
        Concept.objects.rebuild()
        after = get_tree_details(Concept.objects.all())


