from django.db import models
from django.utils.translation import ugettext_lazy as _


class MC2PConfig(models.Model):
    """
    MyChoice2Pay Configuration
    """
    key = models.CharField(max_length=32, verbose_name=_('Key'))
    secret_key = models.CharField(max_length=32, verbose_name=_('Secret Key'))

    class Meta:
        verbose_name = _('MyChoice2Pay Configuration')
        verbose_name_plural = _('MyChoice2Pay Configuration')
