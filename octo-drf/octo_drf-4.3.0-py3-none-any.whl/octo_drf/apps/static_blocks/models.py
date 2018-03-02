from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from octo_drf.apps.base.models import BaseAbstractModel
from octo_drf.apps.generic_image.fields import SorlImageField


class StaticBlock(BaseAbstractModel):

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
    title = models.CharField(
        'Заголовок',
        max_length=255,
        blank=True
    )
    announce = models.TextField(
        'Сноска',
        blank=True
    )
    content = models.TextField(
        'Контент',
        blank=True
    )
    image1 = SorlImageField(
        'Изображение 1',
        lookup_name='image1',
        blank=True
    )
    image2 = SorlImageField(
        'Изображение 2',
        lookup_name='image2',
        blank=True
    )
    image3 = SorlImageField(
        'Изображение 3',
        lookup_name='image3',
        blank=True
    )
    image4 = SorlImageField(
        'Изображение 4',
        lookup_name='image4',
        blank=True
    )

    class Meta:
        ordering = ['order']
        verbose_name = 'Блок'
        verbose_name_plural = 'Блоки'

    def __str__(self):
        return 'Блок'

class StaticBlockBaseAbstractModel(BaseAbstractModel):

    static_block = GenericRelation(
        StaticBlock,
        blank=True
    )

    def get_count_static_blocks(self):
        content_type = ContentType.objects.get_for_model(self)
        qs = self.__class__.objects.filter(static_block__content_type__pk=content_type.id, static_block__object_id=self.id)
        if qs:
            return qs.count()
        
        return 0

    class Meta:
        abstract = True


class StaticBlockBaseAbstractMixin(models.Model):
    static_block = GenericRelation(
        StaticBlock,
        blank=True
    )

    def get_count_static_blocks(self):
        content_type = ContentType.objects.get_for_model(self)
        qs = self.__class__.objects.filter(static_block__content_type__pk=content_type.id, static_block__object_id=self.id)
        if qs:
            return qs.count()
        
        return 0

    class Meta:
        abstract = True