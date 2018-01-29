from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from fortnum.utils import OrderedSet
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl_templates.exceptions import OpenpyxlTemplateException

from django_ontology.api.excel.workbook import OntologyWorkbook
from django_ontology.api.importer import OntologyImporter, OntologyImportException
from django_ontology.models import Language, get_language, ontology_models


class WorkbookResponse(HttpResponse):
    def __init__(self, filename, templated_workbook):
        super().__init__(
            status=200,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            content=save_virtual_workbook(templated_workbook.workbook)
        )
        self['Content-Disposition'] = 'attachment; filename="%s"' % templated_workbook.timestamp_filename(filename)


def excel_api_view_name(model):
    return "django-ontology-excel-%s" % model.slug


class ExcelApiIndex(TemplateView):
    template_name = "django_ontology/api/excel/excel_index.html"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(
            request,
            *args,
            models=[
                dict(
                    name=model.__name__,
                    url=reverse(excel_api_view_name(model)),
                    model=model
                ) for model in ontology_models()
            ],
            languages=Language.cache.all(),
            active_language=Language.cache.active,
            **kwargs
        )


class ExcelApiView(View):
    model = None
    workbook_template_class = None
    url_name = None
    _class_registry = {}

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            languages = OrderedSet(get_language(key) for key in request.GET.getlist("language"))
            if not languages:
                languages = (get_language(),)
        except Language.DoesNotExist as e:
            return HttpResponseBadRequest("Language '%s' does not exists" % str(e))

        templated_workbook = self.workbook_template_class()
        for language in languages:
            templated_workbook.write_concepts(
                language,
                self.model.translate.all(language=language),
                title=None,
                description=None,
            )
        templated_workbook.sort_worksheets()

        return WorkbookResponse("%s.xlsx" % self.model.slug, templated_workbook)

    def post(self, request, *args, **kwargs):
        if "file" in request.FILES:
            file = request.FILES["file"]
            language = get_language(request.POST.get("language", None), raise_404=True)

            templated_workbook = self.get_workbook(file)
            if language not in templated_workbook.languages:
                return HttpResponseBadRequest("Language '%s' not found in '%s'" % (language, file))
            try:
                rows = list(templated_workbook.languages[language].read())
            except OpenpyxlTemplateException as e:
                return HttpResponseBadRequest(str(e))

            try:
                importer = OntologyImporter(self.model, rows, language)
            except OntologyImportException as e:
                return HttpResponseBadRequest(str(e))

            result = importer.result
            if not result.success:
                return JsonResponse(status=400, data={"errors": [str(e) for e in importer.result.exceptions]})

            return JsonResponse(data=importer.result.dict)
        else:
            return HttpResponseBadRequest("No file supplied.")

    def get_workbook(self, file=None):
        return self.workbook_template_class(file)

    @classmethod
    def from_model(cls, model):
        if model not in cls._class_registry:
            cls._class_registry[model] = type(
                "%s%s" % (model.__name__, cls.__name__),
                (cls,),
                {
                    "model": model,
                    "workbook_template_class": OntologyWorkbook.from_model(model),
                    "url_name": "django_ontology-excel-%s" % model.slug
                }
            )
        return cls._class_registry[model]
