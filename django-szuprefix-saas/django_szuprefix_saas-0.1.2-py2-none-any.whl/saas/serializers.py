# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from . import models, mixins
from rest_framework import serializers
from django_szuprefix.auth.serializers import UserSerializer

class PartySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Party
        fields = ('name', 'worker_count', 'status', 'url')


class WorkerSerializer(mixins.PartySerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Worker
        fields = ('name', 'number', 'profile', 'position', 'url')


class CurrentWorkerSerializer(mixins.PartySerializerMixin, serializers.ModelSerializer):
    party = PartySerializer()
    user = UserSerializer()

    class Meta:
        model = models.Worker
        fields = ('name', 'number', 'position', 'party', 'user')

