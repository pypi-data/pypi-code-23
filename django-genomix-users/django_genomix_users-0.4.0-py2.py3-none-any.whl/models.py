# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

from .conf import settings


class Profile(TimeStampedModel):
    """User Profile"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        verbose_name=_("user"),
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('users:profile-detail', kwargs={'user__username__iexact': str(self.user)})
