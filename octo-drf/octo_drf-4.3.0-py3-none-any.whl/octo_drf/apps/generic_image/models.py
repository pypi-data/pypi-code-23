from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
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
    
    

class GalleryBaseAbstractModel(BaseAbstractModel):
    gallery = GenericRelation(
        GenericImage,
        blank=True
    )

    def get_count_gallery(self):
        content_type = ContentType.objects.get_for_model(self)
        qs = self.__class__.objects.filter(gallery__content_type__pk=content_type.id, gallery__object_id=self.id)
        if qs:
            return qs.count()
        
        return 0

    class Meta:
        abstract = True


class GalleryBaseAbstractMixin(models.Model):
    gallery = GenericRelation(
        GenericImage,
        blank=True
    )

    def get_count_gallery(self):
        content_type = ContentType.objects.get_for_model(self)
        qs = self.__class__.objects.filter(gallery__content_type__pk=content_type.id, gallery__object_id=self.id)
        if qs:
            return qs.count()
        
        return 0

    class Meta:
        abstract = True