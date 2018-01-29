import json
from collections import OrderedDict
from itertools import chain

from django.db import transaction, IntegrityError
from fortnum import Fortnum

# from django_ontology.models import Concept


class OntologyApiAction(Fortnum):
    pass


class OntologyApiActions(Fortnum):
    # item_class = OntologyApiAction

    noop = OntologyApiAction("noop")
    create = OntologyApiAction("create")
    update = OntologyApiAction("update")
    delete = OntologyApiAction("delete")


class ApiRow:
    model = None
    expression_types = None
    _class_registry = {}

    def __init__(self, action=None, key=None, parent=None, **expressions):
        self.action = action or OntologyApiActions.noop
        self.key = key
        self.parent = parent
        self._expressions = expressions

    def __str__(self):
        return "(%s)" % ", ".join(str(v) for v in (self.action, self.key, self.parent, self._expressions))

    def __repr__(self):
        return str(self)

    @classmethod
    def from_model(cls, model):
        if model not in cls._class_registry:
            cls._class_registry[model] = type(
                "%sRow" % model.__class__.__name__,
                (cls, ),
                {
                    "model": model,
                    "expression_types": model.expression_types
                }
            )

        return cls._class_registry[model]

    def get_expression(self, expression_type):
        try:
            return self._expressions[expression_type.type]
        except KeyError:
            return OntologyApiActions.noop


class OntologyImportException(Exception):
    pass


class ParentDoesNotExist(OntologyImportException):
    def __init__(self, parent_key):
        super().__init__("Parent with key '%s' not found." % parent_key)


class Rollback(Exception):
    pass


class ConceptNotFound(OntologyImportException):
    def __init__(self, model, key):
        super().__init__("%s with key '%s' does not exists." % (model.__name__, key))


class ImportResult:
    def __init__(self, model, rows, language):
        self.model = model
        self.rows = rows
        self.language = language

        self.update = []
        self.delete = []
        self.create = []
        self.noop = []
        self.ignored_rows = []
        self.exceptions = []

    @property
    def success(self):
        return not self.exceptions

    @property
    def concepts(self):
        return sorted(
            chain(self.update, self.delete, self.create, self.noop),
            key=lambda concept: concept.modified
        )

    @property
    def dict(self):
        return OrderedDict((
            ("created", len(self.create)),
            ("updated", len(self.update)),
            ("deleted", len(self.delete)),
            ("noop", len(self.noop)),
            ("ignored", len(self.ignored_rows)),
        ))

    @property
    def json(self):
        return json.dumps(self.dict)

    def __str__(self):
        return self.json


class OntologyImporter:
    def __init__(self, model, rows, language, concepts=None):
        self.model = model
        self.expression_types = model.expression_types
        self.rows = rows
        self.language = language

        self.concepts = {m.key: m for m in concepts or model.translate.all(language=self.language)}
        self.result = ImportResult(model, rows, language)

        actions = {
            OntologyApiActions.update: self.update,
            OntologyApiActions.delete: self.delete,
            OntologyApiActions.create: self.create,
            OntologyApiActions.noop: self.noop
        }

        try:
            with transaction.atomic():
                for row in self.rows:
                    try:
                        actions[row.action](row)
                    except OntologyImportException as e:
                        self.result.exceptions.append(e)
                    except IntegrityError as e:
                        self.result.exceptions.append(e)
                    except self.model.DoesNotExist as e:
                        self.result.exceptions.append(e)
                if not self.result.success:
                    raise Rollback()
        except Rollback:
            pass

    def update(self, row):
        concept = self.get_concept(row.key)
        if self.is_equal(row, concept):
            self.result.noop.append(concept)
            return

        if row.parent != concept.parent_id and row.parent != OntologyApiActions.noop:
            try:
                concept.move_to(self.model.translate.get(key=row.parent, translate=False) if row.parent is not None else None)
            except self.model.DoesNotExist:
                raise ParentDoesNotExist(row.parent)

        for expression_type in self.expression_types:
            expression = row.get_expression(expression_type)
            if expression == OntologyApiActions.noop:
                continue
            concept.set_expression(expression_type, expression)

        self.result.update.append(concept)

    def delete(self, row):
        try:
            concept = self.get_concept(row.key)
            concept.delete()
            self.result.delete.append(concept)
        except self.model.DoesNotExist:
            self.result.noop.append(row)

    def create(self, row):
        if row.key in self.concepts:
            return self.update(row)
        try:
            concept = self.model(
                key=row.key,
                parent=self.model.translate.get(key=row.parent, translate=False) if row.parent else None,
                language=self.language
            )
        except self.model.DoesNotExist:
            raise ParentDoesNotExist(row.parent)

        concept.save()
        for expression_type in self.expression_types:
            expression = row.get_expression(expression_type)
            if expression == OntologyApiActions.noop:
                continue
            concept.set_expression(expression_type, expression)

        self.concepts[concept.key] = concept
        self.result.create.append(concept)

    def noop(self, row):
        try:
            concept = self.get_concept(row.key)
            self.result.noop.append(concept)
        except ConceptNotFound:
            self.result.ignored_rows.append(row)

    def get_concept(self, key):
        try:
            return self.concepts[key]
        except KeyError:
            raise self.model.DoesNotExist("Concept '%s' does not exists." % key)

    def is_equal(self, row, concept):
        if row.parent != concept.parent and row.parent != OntologyApiActions.noop:
            return False

        for expression_type in self.expression_types:
            expression = row.get_expression(expression_type)
            if expression != OntologyApiActions.noop and expression != concept.get_expression(expression_type).raw:
                return False

        return True



