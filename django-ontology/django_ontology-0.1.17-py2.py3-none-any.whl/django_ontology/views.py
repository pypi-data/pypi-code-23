from timeit import default_timer as timer
from collections import OrderedDict

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views import View

from django_ontology.models import ontology_models


class OntologyRebuildView(View):
    def dispatch(self, request, *args, slug=None, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied()

        start = timer()
        for model in ontology_models():
            if slug is None or model.slug == slug:
                print("Rebuilding '%s' " % model.slug)
                model.objects.rebuild()
                print("    Done")
        end = timer()

        return JsonResponse(OrderedDict((
            ("success", True),
            ("message", "Rebuilt!"),
            ("time", round((end-start), 2)),
        )))
