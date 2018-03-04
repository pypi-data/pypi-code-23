# -*- coding:utf-8 -*-
from rest_framework.decorators import list_route, detail_route
from rest_framework.serializers import ModelSerializer

from django_szuprefix.api.mixins import UserApiMixin
from django_szuprefix.saas.mixins import PartyMixin, PartySerializerMixin
from .apps import Config
from rest_framework.response import Response

__author__ = 'denishuang'
from . import models
from rest_framework import serializers, viewsets
from django_szuprefix.api import register
from rest_framework import status


class PaperSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Paper
        fields = ('title', 'content', 'content_object', 'is_active', 'create_time', 'id')


class PaperViewSet(PartyMixin, UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Paper.objects.all()
    serializer_class = PaperSerializer

    @detail_route(['post'])
    def answer(self, request, pk=None):
        paper = self.get_object()
        serializer = AnswerSerializer(data=request.data, party=self.party)
        if serializer.is_valid():
            serializer.save(user=self.request.user, paper=paper)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @detail_route(['get'])
    def stat(self, request, pk=None):
        paper = self.get_object()
        if paper.stat:
            serializer = StatSerializer(instance=paper.stat)
            return Response(serializer.data)
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)


register(Config.label, 'paper', PaperViewSet)


class AnswerSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Answer
        fields = ('detail', 'performance', 'seconds')


class AnswerViewSet(PartyMixin, UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Answer.objects.all()
    serializer_class = AnswerSerializer
    filter_fields = ('paper',)


register(Config.label, 'answer', AnswerViewSet)


class StatSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Stat
        fields = ('detail',)


# class StatViewSet(PartyMixin, UserApiMixin, viewsets.ReadOnlyModelViewSet):
#     queryset = models.Stat.objects.all()
#     serializer_class = StatSerializer
#     filter_fields = ('paper',)
#
#
# register(Config.label, 'stat', StatViewSet)


class PerformanceSerializer(PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Performance
        fields = ('paper_id', 'score', 'detail')


class PerformanceViewSet(PartyMixin, UserApiMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Performance.objects.all()
    serializer_class = PerformanceSerializer
    filter_fields = ('paper',)

    def filter_queryset(self, queryset):
        qset = super(PerformanceViewSet, self).filter_queryset(queryset)
        ids = self.request.GET.get("papers")
        # qset = qset.filter(user=self.request.user)
        if ids:
            qset = qset.filter(paper_id__in=[int(id) for id in ids.split(",")])
        return qset


register(Config.label, 'performance', PerformanceViewSet)
