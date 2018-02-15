from django.db import models

from sorl.thumbnail.fields import ImageField
from sorl.thumbnail import get_thumbnail

from ..base import models as base


class GalleryBase(base.Ordered):
    original_image = models.ImageField(
        'Изображение',
        upload_to = 'images'
    )

    def thumb(self):
        return get_thumbnail(self.image, '80x60', crop = 'center')

    class Meta:
        abstract = True


class SimpleGallery(GalleryBase):

    caption = models.TextField(
        'Описание',
        null = True,
        blank = True
    )

    class Meta:
        abstract = True
        verbose_name = 'слайд'
        verbose_name_plural = 'галерея'


class SimpleBanner(GalleryBase):
    text = models.CharField(
        'текст',
        help_text="<em>Максимум 140 знаков</em>",
        max_length = 140,
        null = True,
        blank = True
    )

    class Meta:
        abstract = True
        verbose_name = 'баннер'
        verbose_name_plural = 'баннеры'
