# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

from . import choices


class File(TimeStampedModel):
    """Model File that stores data relevant.

    Notes:
        - Trying to follow GA4GH data models
        (Specifically https://github.com/ga4gh/task-execution-schemas)
        - Following inputs model
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    type = models.SmallIntegerField(
        choices=choices.FILE_TYPES,
    )

    active = models.BooleanField(default=True)
    relative_path = models.BooleanField(default=True)
    comments = GenericRelation('user_activities.Comment')

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        unique_together = (
            ('name', 'path'),
            ('name', 'url'),
        )

    def __str__(self):
        return self.name
