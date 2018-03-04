from rest_framework import serializers

from octo_drf.apps.base.serializers import BaseModelSerializer
from .models import CatalogItem, CatalogCategory


class CatalogItemSerializer(BaseModelSerializer):

    class Meta:
        model = CatalogItem
        fields = CatalogItem.get_serializer_fields()


class CatalogCategorySerializer(BaseModelSerializer):

    class Meta:
        model = CatalogCategory
        fields = CatalogCategory.get_serializer_fields()