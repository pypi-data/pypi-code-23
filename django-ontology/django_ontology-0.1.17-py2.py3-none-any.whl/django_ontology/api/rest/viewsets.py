from django.http import Http404
from mptt.utils import get_cached_trees
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from django_ontology.api.rest.serializers import RestSerializer
from django_ontology.models import get_language


class OntologyViewSet(ModelViewSet):
    model = None
    permission_classes = (IsAdminUser,)
    _class_registry = {}

    def get_queryset(self):
        queryset = self.model.translate.all(language=self.language)
        levels = self.levels
        if levels:
            queryset = queryset.filter(level__lt=levels)

        return queryset

    def get_object(self):
        lookup_kwargs = {self.lookup_field: self.kwargs[self.lookup_url_kwarg or self.lookup_field]}
        try:
            concept = self.model.translate.get(translate=True, **lookup_kwargs)

            queryset = concept.get_descendants(
                language=self.language,
                translate=True,
                include_self=True
            )

            levels = self.levels
            if levels:
                levels = concept.level + levels
                queryset = queryset.filter(level__lt=levels)

            obj = get_cached_trees(queryset)[0]
        except self.model.DoesNotExist:
            raise Http404()

        self.check_object_permissions(self.request, obj)

        return obj

    def filter_queryset(self, queryset):
        return get_cached_trees(super().filter_queryset(queryset))

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, language=self.language, **kwargs)

    @classmethod
    def from_model(cls, model):
        if model not in cls._class_registry:
            cls._class_registry[model] = type(
                "%s%s" % (model.__name__, cls.__name__),
                (cls,),
                {
                    "model": model,
                    "serializer_class": RestSerializer.from_model(model)
                }
            )

        return cls._class_registry[model]

    @property
    def levels(self):
        levels = self.request.query_params.get("levels", None)
        if levels:
            try:
                levels = int(levels)
            except ValueError:
                raise Http404("Unknown levels")
        return levels

    @property
    def language(self):
        return get_language(
            self.request.query_params.get("language", None),
            raise_404=True
        )



