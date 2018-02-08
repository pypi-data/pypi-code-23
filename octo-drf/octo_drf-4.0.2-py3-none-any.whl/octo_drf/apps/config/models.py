import os

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from octo_drf.apps.base.models import BaseAbstractModel
from .decorators import register_config, config_types


class AbstractConfig(BaseAbstractModel):

    name = models.CharField(
        'Название',
        max_length=255,
        unique=True
    )
    config_type = models.CharField(
        max_length=255
    )
    description = models.TextField(
        'Описание',
        blank=True
    )
    content = models.TextField(
        'Контент'
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def call_action(self):
        config_cls = config_types[self.config_type]
        config_cls.func(self)

    def save(self, *args, **kwargs):
        #TODO: Обработать валидацию в админке. Добавить опциональное отлючение из save
        config_cls = config_types[self.config_type]
        existed_objects = self.__class__.objects.filter(config_type=self.config_type).count()
        if config_cls.is_unique and existed_objects and not self.pk:
            raise ValidationError('Может быть только одна модель с типом {}'.format(self.config_type))

        self.call_action()
        return super().save(*args, **kwargs)
