import datetime
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

from ..base import models as kk

class BasicArticle(kk.Base):
    headline = models.CharField(
        'Заголовок',
        max_length = 255,
#        help_text="Текст: <em>Текст</em>."
    )

    content = RichTextUploadingField(
        'Содержимое',
        blank = True
    )

    pub_date = models.DateTimeField(
        'Время публикации',
        default = datetime.datetime.now
    )

    def __str__(self):
        return self.headline

    class Meta:
        abstract = True
        ordering = ['-pub_date']
        verbose_name = 'статья'
        verbose_name_plural = 'Статьи'


class ArticleAnnotationMixin(models.Model):
    annotation = models.TextField(
        'Аннотация',
        help_text = 'Заполните аннотацию и в списке статей<br />\
            будет показан этот текст, вместо основного текста статьи',
        blank = True
    )

    class Meta:
        abstract = True


class ArticleCoverMixin(models.Model):
    cover = models.ImageField(
        'Обложка',
        upload_to = 'images',
        blank = True
    )

    class Meta:
        abstract = True
