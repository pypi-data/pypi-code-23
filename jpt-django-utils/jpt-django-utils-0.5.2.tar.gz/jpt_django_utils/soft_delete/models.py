"""Soft delete model mixins."""
__all__ = [
    "SoftDeleteMixin",
]

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from .managers import SoftDeleteManager


class SoftDeleteMixin(models.Model):
    """Adds soft deletion to a model.

    Override default delete behavior to soft delete.
    Hard deletes can be done by passing in ``hard=True`` as a kwarg.
    Default manager will not return soft deleted items.

    Soft deletion does not handle any cascading behavior with children.
    This behavior will have to be handled by further overriding the delete
    method.

    Attributes
    ----------
    objects : SoftDeleteManager
        Overrides the default manager to exclude 'deleted' items.
    all_objects : SoftDeleteManager
        Manager that returns all items.
    deleted_on : django.db.models.DateTimeField
        Field used to track soft deleted models.
        Null/None value means model has not been deleted.
        A datetime value indicates when the item was soft deleted.

    Notes
    -----
    May want to look into auto handling cascading soft delete events.
    Especially if children also extend the ``SoftDeleteMixin``.

    """
    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager(show_deleted=True)

    deleted_on = models.DateTimeField(
        verbose_name=_("Deleted on"),
        null=True,
        default=None,
        editable=False)

    class Meta:
        abstract = True

    def delete(self, using=None, *args, hard=False, **kwargs):
        """Override to do soft deletions by default.

        Parameters
        ----------
        hard : bool
            Hard deletes the instance.
            Can only be passed as a kwarg.

        Returns
        -------
        None
            On hard deletes, the usual dict for deletions are returned.
            But soft deletions do not return anything.
            Should not rely on the return value when deleting.

        """
        if hard:
            return super().delete(using=using, *args, **kwargs)

        self.deleted_on = timezone.now()
        self.save(using=using)
