"""Created updated util models."""
__all__ = [
    "CreatedUpdatedMixin",
]

from django.db import models
from django.utils.translation import ugettext_lazy as _


class CreatedUpdatedMixin(models.Model):
    """Mixin to add created, edited timestamp and creator/editor name.

    Created by and updated by is not a foreign key to a user object, just a
    ``django.db.models.CharField`.

    Ensuring that ``created_by`` is not edited after instance creation is the
    developers responsibility.

    """
    created_dt = models.DateTimeField(
        verbose_name=_("Created"),
        auto_now_add=True)
    created_by = models.CharField(
        verbose_name=_("Created by"),
        max_length=225,)
    updated_dt = models.DateTimeField(
        verbose_name=_("Updated"),
        auto_now=True)
    updated_by = models.CharField(
        verbose_name=_("Updated by"),
        max_length=225,)

    class Meta:
        abstract = True
