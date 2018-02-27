from collections import OrderedDict

from openpyxl_templates import TemplatedWorkbook

from django_ontology.api.excel.worksheet import OntologySheet
from django_ontology.models import Language


class OntologyWorkbook(TemplatedWorkbook):
    model = None
    sheet_class = None
    _class_registry = {}

    def __init__(self, file=None, **kwargs):
        super().__init__(file=file, **kwargs)

        if not file:
            self.remove_all_sheets()

        self.languages = OrderedDict()

        self.identify_language_sheets()

    def identify_language_sheets(self):
        languages = {}
        for language in Language.cache.all():
            languages[language.key] = language
            if language.name:
                languages[language.name] = language

        for sheetname in self.sheetnames:
            if sheetname in languages:
                print(sheetname, languages)
                language = languages[sheetname]

                self.add_ontology_sheet(language, sheetname)

    def add_ontology_sheet(self, language, sheetname):
        if language in self.languages:
            raise Exception("Duplicate language '%s'", language)

        sheet = self.sheet_class(language)
        self.languages[language] = sheet
        self.add_templated_sheet(
            sheet,
            sheetname=sheetname
        )
        return sheet

    def write_concepts(self, language, concepts, title=None, description=None):
        sheet = self.add_ontology_sheet(language, sheetname=language.name or language.key)
        sheet.write(
            concepts,
            title=title or str(language),
            description=description
        )
        return sheet

    @classmethod
    def from_model(cls, model):
        if model not in cls._class_registry:
            cls._class_registry[model] = type(
                "%sWorkbook" % model.__name__,
                (cls,),
                {
                    "model": model,
                    "sheet_class": OntologySheet.from_model(model)
                }
            )
        return cls._class_registry[model]



