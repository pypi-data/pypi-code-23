"""Util model mixins."""
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .fields import AutoIntVersionField


class AutoIntVersionMixin(models.Model):
    """Adds an autoincrement on save int field, ``version``.

    Version will update on every save regardless whether field values actually
    change or note.

    If you need to save without incrementing the version field either pass
    ``.save(update_version=False)`` or set ``update_version=False`` directly
    on the instance.

    Attributes
    ----------
    version : AutoIntVersionField
        Check ``AutoIntVersionField`` for default values.

    """
    version = AutoIntVersionField(verbose_name=_("Version"))

    class Meta:
        abstract = True

    def save(self, **kwargs):
        """Detect if update_version is either passed as kwargs or as a prop on model."""
        self.update_version = kwargs.pop('update_version', getattr(self, 'update_version', True))
        super().save(**kwargs)
