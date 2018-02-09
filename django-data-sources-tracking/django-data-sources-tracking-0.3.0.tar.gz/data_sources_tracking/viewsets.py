# -*- coding: utf-8 -*-
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from . import filters, models, serializers


class FileViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Files."""

    queryset = models.File.objects.all()
    serializer_class = serializers.FileSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_class = filters.FileFilter
    search_fields = (
        'name',
        'description',
        'url',
        'path',
    )
