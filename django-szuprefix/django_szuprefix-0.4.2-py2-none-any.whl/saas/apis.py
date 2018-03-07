# -*- coding:utf-8 -*-
import django_filters

from .apps import Config

__author__ = 'denishuang'
from . import models, mixins
from rest_framework import serializers, viewsets, permissions
from django_szuprefix.api import register


class PartySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Party
        fields = ('name', 'worker_count', 'status', 'url')


class PartyViewSet(viewsets.ModelViewSet):
    queryset = models.Party.objects.all()
    serializer_class = PartySerializer
    permission_classes = [permissions.IsAdminUser]


register(Config.label, 'party', PartyViewSet)


class WorkerSerializer(mixins.PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Worker
        fields = ('name', 'number', 'profile', 'url')


class WorkerViewSet(mixins.PartyMixin, viewsets.ModelViewSet):
    queryset = models.Worker.objects.all()
    serializer_class = WorkerSerializer
    # permission_classes = [permissions.IsAdminUser]


register(Config.label, 'worker', WorkerViewSet)
