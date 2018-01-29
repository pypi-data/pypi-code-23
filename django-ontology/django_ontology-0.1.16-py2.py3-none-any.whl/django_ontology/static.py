from fortnum import Fortnum, class_property

from django_ontology.models import get_language


class AbstractConcept(Exception):
    pass


class ConceptCache:
    languages = None

    def __init__(self, model):
        self.model = model
        self.languages = {}

    def get(self, key, language=None):
        language, cache = self._language_cache(language)

        try:
            return cache[key]
        except KeyError:
            raise self.model.DoesNotExist(key)

    def set(self, key, concept, language=None):
        language, cache = self._language_cache(language)
        cache[key] = concept

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, item):
        language, cache = self._language_cache()
        return item in cache

    def _language_cache(self, language=None):
        language = get_language()

        if language not in self.languages:
            self.languages[language] = {}

        return language, self.languages[language]


class BaseStaticConcept(Fortnum):
    model = None
    do_not_call_in_templates = True

    @class_property
    def concept(cls):
        if cls.abstract:
            raise AbstractConcept("Abstract StaticConcepts have no translations.")

        if not cls.is_loaded:
            cls.root().load()

        return cls.cache[cls]

    @class_property
    def is_loaded(cls):
        return bool(cls in cls.cache)

    @classmethod
    def load(cls):
        if cls.is_loaded or cls.abstract:
            return

        cache = cls.cache

        concept, change = cls.model.translate.get_or_create(key=cls.key, translate=False)
        concepts = {c.key: c for c in concept.get_descendants(include_self=True, translate=True)}

        for fortnum in cls.descendants(include_self=True):
            if fortnum.abstract:
                continue

            try:
                c = concepts[fortnum.key]
            except KeyError:
                change = True
                c, created = cls.model.translate.get_or_create(key=fortnum.key)

            if not c.static:
                change = True
                c.static = True
                c.save()

            parent = fortnum.parent
            if parent:
                if c.parent_id != parent.key:
                    change = True
                    parent_concept, created = cls.model.translate.get_or_create(key=parent.key, translate=False)
                    c.move_to(parent_concept)
                if not c.static_parent:
                    change = True
                    c.static_parent = True
                    c.save()

        if change:
            concept = cls.model.translate.get(key=cls.key, translate=False)
            concepts = {c.key: c for c in concept.get_descendants(include_self=True, translate=True)}

        for fortnum in cls.descendants(include_self=True):
            if fortnum.abstract:
                continue

            cache[fortnum] = concepts[fortnum.key]

        cls.model.static_cache = cache

    @class_property
    def cache(cls):
        if not cls.model.static_cache:
            cls.model.static_cache = ConceptCache(cls.model)
        return cls.model.static_cache

    def __str__(self):
        return str(self.concept)

    @class_property
    def key(cls):
        return cls.__name__





