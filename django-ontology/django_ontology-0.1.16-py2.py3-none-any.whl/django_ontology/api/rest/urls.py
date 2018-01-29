from rest_framework import routers

from django_ontology.api.rest.viewsets import OntologyViewSet
from django_ontology.models import ontology_models

ontology_router = routers.DefaultRouter()

for model in ontology_models():
    slug = model.slug
    viewset = model.get_rest_viewset()

    if viewset:
        ontology_router.register(
            "%s" % slug,
            viewset,
            base_name="django-ontology-rest-%s" % slug
        )

urlpatterns = ontology_router.urls