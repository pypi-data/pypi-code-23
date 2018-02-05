# coding: utf-8
from rest_framework import viewsets
from .models import Entrepreneur
from .filters import EntrepreneurFilter
from .serializers import EntrepreneurAutoCompleteSerializer


class EntrepreneurAutoCompleteViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Entrepreneur.objects.all()
    serializer_class = EntrepreneurAutoCompleteSerializer
    filter_class = EntrepreneurFilter
    search_fields = (
        'id',
        'name'
    )
