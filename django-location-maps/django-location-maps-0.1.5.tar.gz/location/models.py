# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings


class Control(models.Model):
    slug = models.CharField(max_length=255, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=False)
    updated_at = models.DateTimeField(auto_now=True, blank=False)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class CountryCode(Control):
    name = models.CharField(max_length=255, blank=False, unique=True)
    code = models.CharField(max_length=2, blank=False, unique=True)

    def __unicode__(self):
        return self.code.upper() + ' - (' + self.name + ')'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.code = self.code.lower()
        super(CountryCode, self).save(force_insert, force_update)


class Country(Control):
    language = models.CharField(max_length=5, choices=settings.LANGUAGES)
    name = models.CharField(max_length=50, blank=False, unique=True)
    code = models.ForeignKey(CountryCode, blank=False)
    flag = models.FileField(blank=True, null=True)

    class Meta:
        unique_together = (("language", "code"),)

    def __unicode__(self):
        return self.name


class State(Control):
    language = models.CharField(max_length=5, choices=settings.LANGUAGES)
    country = models.ForeignKey(Country, blank=False)
    name = models.CharField(max_length=50, blank=False)
    code = models.CharField(max_length=50)

    class Meta:
        unique_together = (("language", "code"),)

    def __unicode__(self):
        return self.name + ' - ' + self.country.code.code.upper()


class City(Control):
    language = models.CharField(max_length=2, choices=settings.LANGUAGES)
    state = models.ForeignKey(State, blank=False)
    name = models.CharField(max_length=50, blank=False, unique=True)

    def __unicode__(self):
        return self.name


class Location(Control):
    city = models.ForeignKey(City, verbose_name='City')
    neighborhood = models.CharField(max_length=255, blank=True, null=True, verbose_name='Neighborhood')
    postal_code = models.CharField(max_length=255, blank=True, null=True, verbose_name='Postal Code')
    address = models.CharField(max_length=255, blank=False, verbose_name='Address')
    street_number = models.CharField(max_length=255, blank=True, null=True, verbose_name='Street Number')
    complement = models.CharField(max_length=255, blank=True, null=True, verbose_name='Complement')
    latitude = models.CharField(max_length=255, verbose_name='Latitude')
    longitude = models.CharField(max_length=255, verbose_name='Longitude')
    slug = models.CharField(max_length=255, blank=False, unique=False)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.address
