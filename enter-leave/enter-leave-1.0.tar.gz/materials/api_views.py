#-*- coding:utf-8 -*-
from __future__ import unicode_literals
import datetime, calendar, requests
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import OrderingFilter
from . import models
from . import serializers
from comm.pagination import StandardPagination
from comm.filter import CustomSearchFilter, CustomSearchFilter1
from comm import permissions



class MaterialListView(generics.ListCreateAPIView):
    queryset = models.Material.objects.all()
    serializer_class = serializers.MaterialSerializer
    # permission_classes = (IsAuthenticated,)
    # permission_classes = (permissions.IsAuthenticated,)
    # perms_map = {
    #     'GET': ['accounts.appmeta.MANAGE.NEWS.READ'],
    #     'POST': ['accounts.appmeta.MANAGE.NEWS.WRITE'],
    # }

class MaterialDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Material.objects.all()
    serializer_class = serializers.MaterialSerializer
    # permission_classes = (permissions.IsAuthenticated,)
    # perms_map = {
    #     'GET': ['accounts.appmeta.MANAGE.NEWS.READ'],
    #     'PUT': ['accounts.appmeta.MANAGE.NEWS.CREATE'],
    #     'DELETE': ['accounts.appmeta.MANAGE.NEWS.DELETE'],
    # }


class MaterialSpecificationListView(generics.ListCreateAPIView):
    queryset = models.MaterialSpecification.objects.all()
    serializer_class = serializers.MaterialSpecificationSerializer
    # permission_classes = (IsAuthenticated,)
    # permission_classes = (permissions.IsAuthenticated,)
    # perms_map = {
    #     'GET': ['accounts.appmeta.MANAGE.NEWS.READ'],
    #     'POST': ['accounts.appmeta.MANAGE.NEWS.WRITE'],
    # }

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.MaterialSpecificationSerializer
        else:
            return serializers.MaterialSpecificationSerializerEdit

    def get_queryset(self):
        queryset = super(MaterialSpecificationListView, self).get_queryset()
        material_code = self.request.GET.get('material_code')
        if material_code:
            queryset = queryset.filter(material__code=material_code)
            return queryset
        return queryset


class MaterialSpecificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.MaterialSpecification.objects.all()
    serializer_class = serializers.MaterialSpecificationSerializer
    # permission_classes = (IsAuthenticated,)
    # permission_classes = (permissions.IsAuthenticated,)
    # perms_map = {
    #     'GET': ['accounts.appmeta.MANAGE.NEWS.READ'],
    #     'PUT': ['accounts.appmeta.MANAGE.NEWS.CREATE'],
    #     'DELETE': ['accounts.appmeta.MANAGE.NEWS.DELETE'],
    # }


    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.MaterialSpecificationSerializer
        else:
            return serializers.MaterialSpecificationSerializerEdit

class MaterialEntryListView(generics.ListCreateAPIView):
    queryset = models.MaterialsEntry.objects.all()
    serializer_class = serializers.MaterialsEntrySerializer
    pagination_class = StandardPagination
    # permission_classes = (IsAuthenticated,)
    # permission_classes = (permissions.IsAuthenticated,)
    # perms_map = {
    #     'GET': ['accounts.appmeta.MANAGE.NEWS.READ'],
    #     'POST': ['accounts.appmeta.MANAGE.NEWS.WRITE'],
    # }
    filter_backends = (OrderingFilter, CustomSearchFilter1)
    ordering_fileds = ('create_on')
    search_params = [
        {'project_pk': 'project__pk__in'},
        {'project_code': 'project__code__in'},
        {'project_unit_pk': 'project_unit__pk__in'},
        {'project_unit_code': 'project_unit__code__in'},
        {'producer': 'producer__name__in'},
        {'created_year': 'create_on__year__in'},
        {'created_month': 'create_on__month__in'},
        {'created_date': 'create_on__date__in'},
        {'delivery_order': 'delivery_order__in'},
        {'lot_number': 'lot_number__in'}

    ]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.MaterialsEntrySerializer
        else:
            return serializers.MaterialsEntrySerializerEdit

    def get_queryset(self):
        queryset = super(MaterialEntryListView, self).get_queryset()
        search_key = self.request.GET.get('keyword')

        if search_key:
            queryset = queryset.filter(Q(material__name__contains=search_key) \
                | Q(material__code__contains=search_key) \
                | Q(material_spec__code__contains = search_key) \
                | Q(material_spec__name__contains=search_key))
        return queryset

    def perform_create(self, serializer):
        material_spec = serializer.validated_data['material_spec']
        serializer.validated_data['material']['name'] = material_spec.material.name
        serializer.validated_data['material']['code'] = material_spec.material.code
        serializer.validated_data['material']['unit'] = material_spec.material.unit
        serializer.save()




class MaterialEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.MaterialsEntry.objects.all()
    serializer_class = serializers.MaterialsEntrySerializer

    # permission_classes = (IsAdminUser,)
    # permission_classes = (permissions.IsAuthenticated,)
    # perms_map = {
    #     'GET': ['accounts.appmeta.MANAGE.NEWS.READ'],
    #     'PUT': ['accounts.appmeta.MANAGE.NEWS.CREATE'],
    #     'DELETE': ['accounts.appmeta.MANAGE.NEWS.DELETE'],
    # }

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.MaterialsEntrySerializer
        else:
            return serializers.MaterialsEntrySerializerEdit

    def perform_update(self, serializer):
        material_spec = serializer.validated_data['material_spec']
        if material_spec:
            serializer.validated_data['material']['name'] = material_spec.material.name
            serializer.validated_data['material']['code'] = material_spec.material.code
            serializer.validated_data['material']['unit'] = material_spec.material.unit
        serializer.save()

