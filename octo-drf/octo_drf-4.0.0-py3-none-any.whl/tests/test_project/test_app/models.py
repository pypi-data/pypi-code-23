


from django.db import models

from octo_drf.apps.base.catalog_models import AbstractItem, AbstractCategory


class CatalogCategory(AbstractCategory):
    pass


class CatalogItem(AbstractItem):

    category = models.ForeignKey(CatalogCategory, related_name='catalog_items')