"""Publishable models.

Models that are dynamically displayed and hidden.
"""
__all__ = [
    'PublishExpireMixin',
]

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .managers import PublishExpireQuerySet


class PublishExpireMixin(models.Model):
    """A time framed model that can be published at a future date and expired.

    Attributes
    ----------
    publish_dt : models.DateTimeField
        Instance will be displayed after the time specified.
        Defaults to the current date and time.
    expiry_dt : models.DateTimeField
        Instance will be hidden after the time specified.
        Value of ``None`` means the instance will never expire.

    Notes
    -----
    ``expiry_dt`` should be more than ``publish_dt``, validation is not handled
    by this mixin.

    """
    objects = PublishExpireQuerySet.as_manager()

    publish_dt = models.DateTimeField(
        verbose_name=_("Publish date"),
        help_text=_("Will only be visible after this time."),
        default=timezone.now,
        blank=True)
    expiry_dt = models.DateTimeField(
        verbose_name=_("Expiry date"),
        help_text=_("Will be hidden after this time. Will not expire if left blank"),
        default=None,
        blank=True,
        null=True)

    class Meta:
        abstract = True
