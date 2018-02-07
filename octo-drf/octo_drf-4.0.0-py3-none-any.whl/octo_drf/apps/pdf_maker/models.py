


import os

from django.db import models
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from octo_drf.apps.base.models import DynamicModelFieldsMixin


class PDFTemplate(DynamicModelFieldsMixin, models.Model):

    name = models.SlugField(
        'Название шаблона',
        max_length=255,
        unique=True
    )
    template = models.CharField(
        'HTML шаблон',
        help_text='Название HTML шаблона. Создается автоматически, на основе имени'
                  'Если одноименного шаблона нету в папке, он будет создан автомачески',
        max_length=255,
        editable=False,
    )
    title = models.CharField(
        'Заголовок',
        max_length=255,
        blank=True
    )
    content = models.TextField(
        'Контент',
        blank=True
    )
    footer = models.TextField(
        'Футер',
        blank=True
    )

    class Meta:
        verbose_name = 'PDF шаблон'
        verbose_name_plural = 'PDF шаблоны'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        template_name = 'pdf_templates/{}.html'.format(self.name)
        try:
            self.template = get_template(template_name).template.name
        except TemplateDoesNotExist:
            path = os.path.join(settings.BASE_DIR, 'templates/{}'.format(template_name))
            open(path, 'a').close()
            self.template = template_name
        return super().save(*args, **kwargs)
