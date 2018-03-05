"""Publishable managers and querysets."""
__all__ = [
    'PublishExpireQuerySet',
]

from django.db import models
from django.utils import timezone


class PublishExpireQuerySet(models.QuerySet):
    """Publish expire queryset."""

    def expired(self):
        """Instances past their expiry date."""
        return self.filter(expiry_dt__lt=timezone.now())

    def published(self):
        """Instances that are not expired or pending."""
        now = timezone.now()
        after_publish_date_q = models.Q(publish_dt__lt=now)
        before_expiry_q = models.Q(expiry_dt__gt=now) | models.Q(expiry_dt=None)
        return self.filter(after_publish_date_q & before_expiry_q)

    def pending(self):
        """Instances that are awaiting to be published."""
        return self.filter(publish_dt__gt=timezone.now())


class PublishExpireManager(models.Manager):
    """Publish expire model manager."""

    def get_queryset(self):
        """Get publish expire queryset."""
        return PublishExpireQuerySet(self.model)

    def expired(self):
        return self.get_queryset().expired()

    def published(self):
        return self.get_queryset().published()

    def pending(self):
        return self.get_queryset().pending()
