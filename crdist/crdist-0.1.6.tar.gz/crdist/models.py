# -*- coding: utf-8  -*-

from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.db import models


@python_2_unicode_compatible
class Province(models.Model):
    code = models.CharField(unique=True, max_length=16, verbose_name=_('Code'))
    name = models.CharField(max_length=64, verbose_name=_('Name'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Province")
        verbose_name_plural = _("Provinces")


@python_2_unicode_compatible
class Region(models.Model):
    name = models.CharField(unique=True, max_length=64, verbose_name=_('Name'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")


@python_2_unicode_compatible
class Canton(models.Model):
    code = models.CharField(unique=True, max_length=16, verbose_name=_('Code'))
    name = models.CharField(max_length=64, verbose_name=_('Name'))
    province = models.ForeignKey('Province', verbose_name=_('Province'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Canton")
        verbose_name_plural = _("Cantons")


@python_2_unicode_compatible
class District(models.Model):
    code = models.CharField(unique=True, max_length=16, verbose_name=_('Code'))
    name = models.CharField(max_length=64, verbose_name=_('Name'))
    canton = models.ForeignKey(Canton, verbose_name=_('Canton'))
    region = models.ForeignKey(Region, null=True, verbose_name=_('Region'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("District")
        verbose_name_plural = _("Districts")



