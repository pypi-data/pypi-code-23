from django.conf.urls import url, include
from django.views.i18n import set_language

from django_ontology.models import ontology_models
from django_ontology.views import OntologyRebuildView

urlpatterns = [
    url("rest/", include("django_ontology.api.rest.urls")),
    url("excel/", include("django_ontology.api.excel.urls")),
    url(r'^setlang/$', set_language, name='set_language'),
    url(
        r'^rebuild/(?:(?P<slug>%s)/)?$' % "|".join(model.slug for model in ontology_models()),
        OntologyRebuildView.as_view(), name="ontology-rebuild"
    )
]