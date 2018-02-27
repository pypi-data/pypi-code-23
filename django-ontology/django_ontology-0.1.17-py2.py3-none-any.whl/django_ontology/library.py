from django_ontology.models import get_language, ontology_models
from fortnum import Fortnum


class LibraryLoadLevels(Fortnum):
    self = Fortnum("self")
    kids = Fortnum("kids")  # Cannot use children
    brood = Fortnum("brood")  # Cannot use descendants/family


class OntologyLibrary:
    def __init__(self, model=None, language=None):
        self.model = model or ontology_models()[0]
        self.language = get_language(language)

        self.concepts = {}
        self.concept_load_level = {}

    def load_self(self, *keys, load_level=None):
        keys = [key for key in keys if key not in self.concepts]

        for concept in self.model.translate.filter(key__in=keys, language=self.language):
            self.concepts[concept.key] = concept
            self.concept_load_level[concept.key] = load_level or LibraryLoadLevels.self

    def load_children(self, *keys):
        keys = [
            key for key in keys if not(
                key in self.concepts and
                self.concept_load_level[key] >= LibraryLoadLevels.kids
            )
        ]
        self.load_self(*keys, load_level=LibraryLoadLevels.kids)

        for concept in self.model.translate.filter(parent_id__in=keys, language=self.language):
            if concept not in self.concepts:
                self.concepts[concept.key] = concept
                self.concept_load_level[concept.key] = LibraryLoadLevels.self

    def load_family(self, *keys):
        keys = [
            key for key in keys if
            key not in self.concepts or
            self.concept_load_level[key] != LibraryLoadLevels.brood
        ]
        if not keys:
            return

        self.load_self(*keys)

        for key in keys:
            for concept in self[key].get_family(language=self.language):
                self.concepts[concept.key] = concept
                self.concept_load_level[concept.key] = LibraryLoadLevels.brood

    def __getitem__(self, item):
        return self.concepts[item]

    def get_or_create(self, key, default_parent=None):
        if key not in self.concepts:
            concept, created = self.model.translate.get_or_create(key=key)

            if created:
                concept.move_to(self.model.translate.get_or_create(key=default_parent))
                concept.save()

            print("Warning: '{key}' not loaded".format(key=key))

            self.concepts[key] = concept
            self.concept_load_level[key] = LibraryLoadLevels.self

        return self[key]



