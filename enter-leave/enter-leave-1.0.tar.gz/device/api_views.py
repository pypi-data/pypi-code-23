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

class DeviceMobilityListView(generics.ListCreateAPIView):
    queryset = models.DeviceMobility.objects.all()
    serializer_class = serializers.DeviceMobilitySerializer
    pagination_class = StandardPagination
    filter_backends = (OrderingFilter, CustomSearchFilter1)
    ordering_fields = ('created_on', 'end_on')
    search_params = [
        {'project_pk': 'project__pk__in'},
        {'project_code': 'project__code__in'},
        {'project_unit_pk': 'project_unit__pk__in'},
        {'project_unit_code': 'project_unit__code__in'},
        {'created_year': 'created_on__year__in'},
        {'created_month': 'created_on__month__in'},
        {'created_date': 'created_on__date__in'},
        {'source': 'source__in'},
        {'manufacturer_name': 'manufacturer__name__in'}
    ]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.DeviceMobilityDetailSerializer
        else:
            return serializers.DeviceMobilitySerializer

    def get_queryset(self):
        queryset = super(DeviceMobilityListView, self).get_queryset()
        search_key = self.request.GET.get('keyword')
        is_ground = self.request.GET.get('ground')
        if is_ground:
            queryset = queryset.filter(is_ground__exact=is_ground)
        if search_key:
            queryset = queryset.filter(Q(device_name__name__contains=search_key) \
                |Q(device_spec__contains=search_key) \
                |Q(device_type__contains=search_key))
        return queryset

class DeviceMobilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.DeviceMobility.objects.all()
    serializer_class = serializers.DeviceMobilitySerializer
    # permission_classes = (permissions.IsAuthenticated,)
    # perms_map = {
    #     'GET': ['accounts.appmeta.MANAGE.NEWS.READ'],
    #     'PUT': ['accounts.appmeta.MANAGE.NEWS.CREATE'],
    #     'DELETE': ['accounts.appmeta.MANAGE.NEWS.DELETE'],
    # }

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.DeviceMobilityDetailSerializer
        else:
            return serializers.DeviceMobilitySerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        if serializer.validated_data.get('is_ground') is not True:
            if serializer.validated_data.get('end_on') is None:
                instance.end_on = datetime.datetime.now()
                instance.save()

class DeviceListView(generics.ListCreateAPIView):
    queryset = models.Device.objects.all()
    serializer_class = serializers.DeviceSerializer

class DeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Device.objects.all()
    serializer_class = serializers.DeviceSerializer
