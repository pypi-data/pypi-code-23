# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import viewsets, filters
from .models import Location, City, State, Country, CountryCode
from .serializers import LocationSerializer, CitySerializer, StateSerializer, CountrySerializer, CountryCodeSerializer

# Create your views here.


class CityViewSet(viewsets.ModelViewSet):
    model = City
    queryset = model.objects.all()
    serializer_class = CitySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('language', 'slug', 'state__id', 'state__code')
    http_method_names = ['get', ]


class StateViewSet(viewsets.ModelViewSet):
    model = State
    queryset = model.objects.all()
    serializer_class = StateSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('language', 'slug', 'country__id', 'country__code__code')
    ordering_fields = ('name',)
    http_method_names = ['get', ]


class CountryViewSet(viewsets.ModelViewSet):
    model = Country
    queryset = model.objects.all()
    serializer_class = CountrySerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('language', 'slug', 'code__code')
    ordering_fields = ('name',)
    http_method_names = ['get', ]


class CountryCodeViewSet(viewsets.ModelViewSet):
    model = CountryCode
    queryset = model.objects.all()
    serializer_class = CountryCodeSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('language',)
    ordering_fields = ('name',)
    http_method_names = ['get', ]


class LocationViewSet(viewsets.ModelViewSet):
    model = Location
    serializer_class = LocationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = (
        'neighborhood',
        'postal_code',
        'address',
        'complement',
        'city__id',
        'city__state__id',
        'city__state__code',
        'city__state__country__id',
        'city__state__country__code__code'
    )
    ordering_fields = ('address',)
    http_method_names = ['get', ]

