


from rest_framework import viewsets

from octo_drf.apps.base.views import BaseReadOnlyModelViewSet
from .models import CatalogItem, CatalogCategory
from .serializers import CatalogItemSerializer, CatalogCategorySerializer


class CatalogItemViewSet(BaseReadOnlyModelViewSet):

    queryset = CatalogItem.objects.all()
    serializer_class = CatalogItemSerializer


class CatalogCategoryViewSet(BaseReadOnlyModelViewSet):

    queryset = CatalogCategory.objects.all()
    serializer_class = CatalogCategorySerializer
