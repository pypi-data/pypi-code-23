from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
#from ckeditor.fields import RichTextField

from ..base import models as base

class SimpleText(base.Base):
    codename = models.CharField(
        'Кодовое имя',
        help_text="<em>Латинскими буквами</em>",
        max_length = 128,
        unique = True
    )

    note = models.CharField(
        'Заметка',
#        default = 'noname',
        max_length = 128,
        null = True,
        blank = True
    )

    content = RichTextUploadingField(
        'Содержимое',
        blank=True
    )

    def __str__(self):
        return self.codename

    class Meta:
        abstract = True
        verbose_name = 'Текстовый блок'
        verbose_name_plural = 'Текстовые блоки'
