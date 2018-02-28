# -*- coding:utf-8 -*-
from .apps import Config

from . import models, mixins, serializers
from rest_framework import viewsets, permissions, decorators, response
from django_szuprefix.api import register, mixins as api_mixins
__author__ = 'denishuang'


class PartyViewSet(viewsets.ModelViewSet):
    queryset = models.Party.objects.all()
    serializer_class = serializers.PartySerializer
    permission_classes = [permissions.IsAdminUser]


register(Config.label, 'party', PartyViewSet)


class WorkerViewSet(api_mixins.BatchCreateModelMixin, mixins.PartyMixin, viewsets.ModelViewSet):
    queryset = models.Worker.objects.all()
    serializer_class = serializers.WorkerSerializer

    # permission_classes = [permissions.IsAdminUser]

    @decorators.list_route(['get'])
    def current(self, request):
        serializer = serializers.CurrentWorkerSerializer(self.worker, context={'request': request})
        return response.Response(serializer.data)


register(Config.label, 'worker', WorkerViewSet)
