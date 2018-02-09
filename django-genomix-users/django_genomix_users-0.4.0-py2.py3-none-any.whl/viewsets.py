# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import SearchFilter

from . import filters, models, serializers


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """A simple ViewSet for viewing Users."""

    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_class = filters.UserFilter
    lookup_field = 'username__iexact'
    search_fields = ('user__username', )


class ProfileViewSet(viewsets.ModelViewSet):
    """A simple ViewSet for viewing User Profiles."""

    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = (permissions.IsAuthenticated, )
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_class = filters.ProfileFilter
    lookup_field = 'user__username__iexact'
    search_fields = ('user__username', 'title')
    http_method_names = ['get', 'put', 'patch', 'options', 'head']
