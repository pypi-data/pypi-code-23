"""Soft delete managers."""
__all__ = [
    "SoftDeleteQuerySet",
    "SoftDeleteManager",
]

from django.db.models import Manager, QuerySet
from django.utils import timezone


class SoftDeleteQuerySet(QuerySet):
    """Soft delete queryset.

    Overrides the default delete behavior to soft delete instances.
    """

    def delete(self, *, hard=False):
        """Soft delete all instances in the queryset.

        Parameters
        ----------
        hard : bool
            Hard delete the items if True.
            Must be passed as a kwarg.

        Returns
        _______
        None
            Return value should not be relied on.

        """
        if hard:
            return super().delete()
        return super().update(deleted_on=timezone.now())


class SoftDeleteManager(Manager):
    """Soft delete model manager.

    Attributes
    ----------
    show_deleted : bool
        Whether to return soft deleted items.

    """

    def __init__(self, show_deleted=False, *args, **kwargs):
        self.show_deleted = show_deleted
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        """Get soft delete queryset."""
        qs = SoftDeleteQuerySet(self.model)
        if not self.show_deleted:
            qs = qs.filter(deleted_on=None)
        return qs

    def delete(self, *, hard=False):
        """Override delete to do soft deletions by default.

        Parameters
        ----------
        hard : bool
            Hard delete the items if True.
            Must be passed as a kwarg.

        """
        return self.get_queryset().delete(hard=hard)
