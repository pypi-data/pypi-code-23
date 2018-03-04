from django.db import models

from octo_drf.apps.base.catalog_models import AbstractItem, AbstractCategory


class CatalogCategory(AbstractCategory):
    pass


class CatalogItem(AbstractItem):

    category = models.ForeignKey(on_delete=models.CASCADE, to=CatalogCategory, related_name='catalog_items')


class Post(models.Model):
    txt = models.CharField(
        'Txt field',
        max_length=255,
    )

