from django.conf.urls import url

from django_ontology.api.excel.views import ExcelApiView, ExcelApiIndex, excel_api_view_name
from django_ontology.models import ontology_models

urlpatterns = [
    url("^$", ExcelApiIndex.as_view(), name="django_ontology-excel-index")
]

for model in ontology_models():
    excel_view = model.get_excel_view()

    if excel_view:
        urlpatterns.append(url(
            "^%s/$" % model.slug,
            excel_view.as_view(),
            name=excel_api_view_name(model)
        ))
