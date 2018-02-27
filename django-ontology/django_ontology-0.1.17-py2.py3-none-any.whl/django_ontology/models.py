from collections import OrderedDict

import re

from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.
from django.db.models import CASCADE
from django.db.models.query import ModelIterable
from django.http import Http404
from django.utils.translation import get_language as django_get_language
from django.conf import settings
from fortnum import class_property
from model_utils.models import TimeStampedModel
from mptt.fields import TreeForeignKey
from mptt.managers import TreeManager
from mptt.models import MPTTModel

from django_ontology.utils import snake_case


class LanguageManager(models.Manager.from_queryset(models.query.QuerySet)):
    def delete(self, **kwargs):
        self.model.cache.clear()
        super().delete(**kwargs)


class LanguageCache:
    def __init__(self):
        self._cache = None

    def all(self):
        return self.cache.values()

    def get(self, key):
        try:
            if isinstance(key, Language):
                return key

            # print("get from cache", self.cache[key], self.cache[key].pk)

            return self.cache[key]
        except KeyError:
            raise Language.DoesNotExist(key)

    def get_or_create(self, key):
        if key not in self.cache:
            Language.objects.create(key=key)
        return self.get(key)

    def __contains__(self, key):
        return key in self.cache

    @property
    def active(self):
        return self.get(django_get_language())

    @property
    def cache(self):
        if self._cache is None:
            cache = OrderedDict((l.key, l) for l in Language.objects.all())

            for key, name in settings.LANGUAGES:
                if key not in cache:
                    l = Language(key=key, name=name)
                    l.save()
                    cache[key] = l

            self._cache = cache

        return self._cache

    def clear(self):
        self._cache = None

    def __bool__(self):
        return self._cache is not None


class Language(TimeStampedModel):
    objects = LanguageManager()
    cache = LanguageCache()

    key = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=True, unique=True)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name or self.key

    def save(self, **kwargs):
        self.cache.clear()
        return super().save(**kwargs)

    def delete(self, **kwargs):
        self.cache.clear()
        return super().delete(**kwargs)

    class Meta:
        ordering = ("-created",)

    @property
    def is_active(self):
        return self.key == django_get_language()

    @classmethod
    def get_active(cls):
        return cls.cache.get(django_get_language())


def get_language(value=None, raise_404=False):
    if not value:
        return Language.get_active()

    if isinstance(value, Language):
        return value

    try:
        return Language.cache.get(value)
    except Language.DoesNotExist:
        if raise_404:
            raise Http404("Language '%s' does not exist" % value)
        else:
            raise


class OntologyQuerySet(models.query.QuerySet):
    language = None
    translate = True

    def _clone(self, **kwargs):
        clone = super()._clone(**kwargs)
        clone.language = self.language
        clone.translate = self.translate
        return clone

    def _fetch_all(self):
        if self._result_cache is None:
            # Use subquery to avoid nasty in comparisons with 1000s of keys.
            # Exclude values querysets
            if not self._iterable_class == ModelIterable:
                return super()._fetch_all()

            expressions = self.model.expression_model.objects.filter(
                concept__in=self,
                language=self.language
            )

            super()._fetch_all()

            if not self.language:
                raise ValueError("Query language not set")

            concepts = {}
            for concept in self._result_cache:
                concept._language = self.language
                concept.translated = self.translate
                concepts[concept.key] = concept
                # if self.translate:
                #     concept._tree_manager = self.model.translate

            if self.translate:
                for expression in expressions:
                    try:
                        setattr(concepts[expression.concept_id], expression.type, expression)
                    except KeyError as e:
                        pass

    def create(self, **kwargs):
        concept = super().create(**kwargs)
        concept._language = self.language
        return concept

    def delete(self):
        self.model.clear_static_cache()
        return super().delete()


class OntologyManager(models.Manager.from_queryset(OntologyQuerySet), TreeManager):
    language = None
    use_for_related_fields = True

    def __init__(self, translate=True):
        super().__init__()
        self.translate = translate

    def get_queryset(self, language=None, translate=None):
        language = get_language(language or self.language)
        translate = translate if translate is not None else self.translate
        # queryset = super().get_queryset()
        queryset = super().get_queryset()
        queryset.language = language
        queryset.translate = translate
        return queryset

    def all(self, language=None, translate=None):
        return self.get_queryset(language=language, translate=translate)

    def filter(self, *args, language=None, translate=None, **kwargs):
        return self.get_queryset(language=language, translate=translate).filter(*args, **kwargs)

    def get(self, *args, language=None, translate=None, **kwargs):
        return self.get_queryset(language=language, translate=translate).get(*args, **kwargs)

    def create(self, *args, language=None, translate=None, **kwargs):
        return self.get_queryset(language=language, translate=translate).create(
            *args,
            language=language,
            **kwargs
        )

    def get_or_create(self, defaults=None, language=None, translate=None, **kwargs):
        return self.get_queryset(language=language, translate=translate).get_or_create(
            defaults=defaults,
            **kwargs
        )


class NotTranslated(Exception):
    def __init__(self, instance):
        super().__init__("%s '%s' has not been loaded with translations, reload from the database "
                         "to use translated features" % (type(instance).__name__, instance.key))


class ExpressionField:
    formatter = None

    # Intentionally shared attributes
    registry = {}
    sort = 0

    def __init__(self, formatter=None, excel_column=None, rest_serializer=None):
        self.type = None  # set by contribute to class
        self.model = None  # set by contribute to class
        self.formatter = formatter
        self.excel_column = excel_column
        self.rest_serializer = rest_serializer

        # Global declaration order
        self.sort = ExpressionField.sort + 1
        ExpressionField.sort = self.sort

    def __get__(self, instance, owner):
        if instance is None:
            return self

        self.translated_check(instance)

        try:
            return instance.__dict__[self.attr]
        except KeyError:
            expression = self.expression_model(
                type=self.type,
                language=instance.language,
                concept_id=instance.key
            )
            # expression.save()
            instance.__dict__[self.attr] = expression
            return expression

    def __set__(self, instance, value):
        self.translated_check(instance)

        if isinstance(value, self.expression_model):
            instance.__dict__[self.attr] = value
        else:
            expression = self.__get__(instance, None)

            if not value:
                if expression.pk:
                    expression.delete()
                del instance.__dict__[self.attr]
            else:
                if expression.raw != value:
                    expression.raw = value
                    if self.is_formatted:
                        expression.formatted = self.formatter(value)
                    else:
                        expression.formatted = None
                    expression.save()

    def contribute_to_class(self, model, field_name):
        # print(self, model, field_name)

        self.model = model
        self.type = field_name

        if model not in self.registry:
            expression_types = []
            self.registry[model] = expression_types
            model.expression_types = expression_types
        else:
            expression_types = self.registry[model]

        expression_types.append(self)
        expression_types.sort(key=lambda ex: ex.sort)

        setattr(model, field_name, self)

    @property
    def attr(self):
        return "_%s" % self.type

    @property
    def is_formatted(self):
        return bool(self.formatter)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.type or ""

    @staticmethod
    def translated_check(instance):
        if not instance.translated:
            raise NotTranslated(instance)

    @property
    def expression_model(self):
        return self.model.expression_model

    def reformat_expressions(self):
        if not self.is_formatted:
            return 0

        count = 0
        for expression in self.model.expression_model.objects.filter(type=self.type):
            formatted = self.formatter(expression.raw)
            if formatted != expression.formatted:
                expression.formatted = formatted
                expression.save()
                count += 1

        return count


ONTOLOGY_KEY_REGEX = r"^([a-zA-Z0-9_]{1,64})$"
_ONTOLOGY_KEY_REGEX = re.compile(ONTOLOGY_KEY_REGEX)


def key_validator(key):
    if not _ONTOLOGY_KEY_REGEX.match(key):
        raise ValidationError("Invalid ontology key '%s'" % key)

# Make sure that expression_types are explicitly declared but not overriding result of contribute_to_class in
# ExpressionField
class ExpressionTypeMixin:
    expression_types = None


class BaseConcept(ExpressionTypeMixin, TimeStampedModel, MPTTModel):
    objects = TreeManager()
    translate = OntologyManager(translate=True)
    _language = None
    _translated = None
    static_cache = None

    rest_viewset = True
    excel_view = True

    key = models.CharField(
        max_length=64,
        primary_key=True
    )

    parent = TreeForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="children",
        null=True
    )

    static = models.BooleanField(default=False)
    static_parent = models.BooleanField(default=False)
    used_in_template = models.BooleanField(default=False)

    def __init__(self, *args, language=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._language = get_language(language)

    def __repr__(self):
        return str(self)

    def __str__(self):
        if not self.translated:
            return "[%s]" % self.key
        return str(self.short) or "[%s]" % self.key

    @property
    def language(self):
        if not self._language:
            raise ValueError("Language not set")
        return self._language

    @language.setter
    def language(self, value):
        raise ValueError("To change language reload from the database.")

    @property
    def translated(self):
        if self._translated is None:
            return True
        return self._translated

    @translated.setter
    def translated(self, value):
        self._translated = value

    def save(self, **kwargs):
        key_validator(self.key)
        self.clear_static_cache()
        return super().save(**kwargs)

    def delete(self, *args, **kwargs):
        self.clear_static_cache()
        return super().delete(*args, **kwargs)

    @class_property
    def slug(cls):
        return snake_case(cls.__name__)

    @classmethod
    def get_model_slugs(cls):
        slugs = list((model, model.slug) for model in cls.models())

        if len(slugs) != len(set(slug for model, slug in slugs)):
            raise Exception("Model slugs not unique, rename one of the conflicting models.")

        return slugs

    def get_expression(self, expression_type):
        return getattr(self, expression_type.type, None)

    def set_expression(self, expression_type, raw):
        setattr(self, expression_type.type, raw)

    # Add translation kwargs to tree methods
    def get_descendants(self, include_self=False, language=None, translate=None):
        self._tree_manager = self.__class__.translate
        qs = self._queryset_kwargs(super().get_descendants(include_self), language=language, translate=translate)
        return qs

    def get_ancestors(self, ascending=False, include_self=False, language=None, translate=None):
        self._tree_manager = self.__class__.translate
        return self._queryset_kwargs(super().get_ancestors(
            ascending=ascending,
            include_self=include_self
        ), language=language, translate=translate)

    def get_children(self, language=None, translate=None):
        self._tree_manager = self.__class__.translate
        return self._queryset_kwargs(super().get_children(), language=language, translate=translate)

    def get_family(self, language=None, translate=None):
        self._tree_manager = self.__class__.translate
        return self._queryset_kwargs(super().get_family(), language=language, translate=translate)

    def get_root(self, language=None, translate=None):
        self._tree_manager = self.__class__.translate
        return self._queryset_kwargs(super().get_root(), language=language, translate=translate)

    def _queryset_kwargs(self, queryset, language=None, translate=None):
        queryset.language = language if language is not None else self._language
        queryset.translate = translate if translate is not None else self.translated
        return queryset

    @classmethod
    def clear_static_cache(cls):
        cls.static_cache = None

    @classmethod
    def get_rest_viewset(cls):
        if not cls.rest_viewset:
            return None

        if cls.rest_viewset is True:
            from django_ontology.api.rest.viewsets import OntologyViewSet
            cls.rest_viewset = OntologyViewSet.from_model(cls)

        return cls.rest_viewset

    @classmethod
    def get_excel_view(cls):
        if not cls.excel_view:
            return None

        if cls.excel_view is True:
            from django_ontology.api.excel.views import ExcelApiView
            cls.excel_view = ExcelApiView.from_model(cls)

        return cls.excel_view

    @classmethod
    def reformat_expressions(cls):
        count = 0
        for expression_field in cls.expression_types:
            count += expression_field.reformat_expressions()
        return count

    def change_key(self, new_key):
        new_concept = type(self)(
            key=new_key,
            static=self.static,
            static_parent=self.static_parent,
            used_in_template=self.used_in_template
        )
        new_concept.save()
        parent = self.parent
        if parent:
            new_concept.parent = parent
            new_concept.move_to(parent)
            new_concept.save()

        self.expression_model.objects.filter(concept_id=self.key).update(concept_id=new_key)

        for child in type(self).objects.filter(parent_id=self.key):
            child.move_to(new_concept)

        self.delete()

        return type(self).translate.get(key=new_key)

    @classmethod
    def additional_rest_fields(cls):
        return OrderedDict()

    class Meta:
        abstract = True


def ontology_models():
    return BaseConcept.__subclasses__()


def default_ontology_model():
    return ontology_models()[0]


class OntologyForeignKey(models.ForeignKey):
    def __init__(self, *args, **kwargs):
        kwargs.update(dict(
            related_name="expressions",
            db_index=True,
            null=False,
            on_delete=CASCADE,
        ))
        super().__init__(*args, **kwargs)


class BaseExpression(TimeStampedModel):
    concept = None

    language = models.ForeignKey(
        Language,
        db_index=True,
        null=False
    )

    type = models.CharField(
        max_length=32,
        null=False,
    )

    raw = models.TextField(null=True, blank=False)

    formatted = models.TextField(null=True, blank=False)

    def save(self, **kwargs):
        super().save(**kwargs)

    def __str__(self):
        return self.formatted or self.raw or ""

    def __bool__(self):
        return bool(str(self))

    class Meta:
        unique_together = ("concept", "language", "type")
        abstract = True

