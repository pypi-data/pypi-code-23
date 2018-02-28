from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from octo_drf.apps.base.models import BaseAbstractModel
from .fields import SorlImageField
from .mixin import ResizeImagesMixin

class GenericImage(ResizeImagesMixin, BaseAbstractModel):

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    object_id = models.PositiveIntegerField(
        blank=True,
        null=True,
        db_index=True
    )
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )
    image = SorlImageField(
        'Изображение',
        lookup_name='image'
    )

    title = models.CharField(
        'Тег Title',
        max_length=255,
        blank=True
    )

    def __str__(self):
        return 'image № {}'.format(self.pk)
    
    

    