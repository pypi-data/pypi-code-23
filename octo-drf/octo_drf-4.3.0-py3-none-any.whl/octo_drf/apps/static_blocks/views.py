# -*- coding: utf-8 -*-

from rest_framework import views, viewsets, mixins
from rest_framework.response import Response

from .serializers import StaticBlockSerializer
from .models import StaticBlock

class StaticBlockView(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = StaticBlock.objects.all()
    serializer_class = StaticBlockSerializer
