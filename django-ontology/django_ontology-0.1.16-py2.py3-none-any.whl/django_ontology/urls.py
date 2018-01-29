from django.conf.urls import url, include
from django.views.i18n import set_language

urlpatterns = [
    url("rest/", include("django_ontology.api.rest.urls")),
    url("excel/", include("django_ontology.api.excel.urls")),
    url(r'^setlang/$', set_language, name = 'set_language')
]