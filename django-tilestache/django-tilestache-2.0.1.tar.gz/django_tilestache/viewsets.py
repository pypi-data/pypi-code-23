# coding: utf-8
from rest_framework import viewsets
from django_tilestache.models import Layer
from django_tilestache.serializers import LayerSerializer


class LayerViewSet(viewsets.ModelViewSet):

    serializer_class = LayerSerializer
    queryset = Layer.objects.all()
