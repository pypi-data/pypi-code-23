"""Publishable managers and querysets."""
__all__ = [
    'PublishExpireQuerySet',
]

from django.db import models
from django.utils import timezone


class PublishExpireQuerySet(models.QuerySet):
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
