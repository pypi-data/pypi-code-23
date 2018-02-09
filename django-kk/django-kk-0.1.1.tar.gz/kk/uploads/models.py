import datetime
from django.db import models

from ..base import models as base


class UploadBase(base.Ordered):
    upload_date = models.DateTimeField(
        'Время загрузки',
        default = datetime.datetime.now
    )

    class Meta:
        abstract = True
        ordering = ['-upload_date']



class Upload(UploadBase):
    file = models.FileField(
        'Файл',
        upload_to = 'uploads'
    )

    class Meta:
        abstract = True



class SimpleUpload(Upload):
    codename = models.CharField(
        'Кодовое имя',
        help_text="<em>Латинскими буквами</em>",
#        default = 'noname',
        max_length = 128,
        unique = True
    )

    def __str__(self):
        return self.codename

    class Meta:
        abstract = True
        verbose_name = 'файл'
        verbose_name_plural = 'Файлы'
