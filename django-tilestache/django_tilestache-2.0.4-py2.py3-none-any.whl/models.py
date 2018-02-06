# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models
from jsonfield import JSONField


class Layer(models.Model):
    """
    Represents a tilestache layer
    """
    name = models.CharField(
        max_length=64,
        verbose_name=_(u'Name'),
        unique=True
    )

    provider = JSONField(
        verbose_name=_(u'Provider'),
        default=dict
    )

    projection = models.CharField(
        max_length=128,
        verbose_name=_(u'Projection'),
        null=True,
        blank=True
    )

    metatile = JSONField(
        verbose_name=_(u'Metatile'),
        null=True
    )

    state_lock_timeout = models.PositiveIntegerField(
        verbose_name=_(u'State Lock Timeout'),
        null=True
    )

    cache_lifespan = models.PositiveIntegerField(
        verbose_name=_(u'State Lock Timeout'),
        null=True
    )

    write_cache = models.NullBooleanField(
        verbose_name=_(u'Write Cache?'),
        null=True,
    )

    bounds = JSONField(
        verbose_name=_(u'Bounds'),
        null=True,
    )

    allowed_origin = models.CharField(
        max_length=256,
        verbose_name=_(u'Allowed Origin'),
        null=True
    )

    preview = JSONField(
        verbose_name=_(u'Preview'),
        null=True,
    )

    max_cache_age = models.PositiveIntegerField(
        verbose_name=_(u'Max Cache Age (seconds)'),
        null=True,
    )

    redirects = JSONField(
        verbose_name=_(u'Redirects'),
        null=True
    )

    tile_height = models.PositiveIntegerField(
        verbose_name=_(u'Tile Height'),
        null=True
    )

    def __unicode__(self):
        return self.name

    class Meta:

        verbose_name = _(u'Layer')
        verbose_name_plural = _('Layers')
