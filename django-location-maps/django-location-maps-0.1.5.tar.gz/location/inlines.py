# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from location.forms import LocationForm
from location.models import Location


class LocationStackedInline(admin.StackedInline):
    model = Location
    form = LocationForm
    fieldsets = (
        (
            _('Location'), {
                'fields': (
                    'map',
                    'country',
                    'states',
                    'city',
                    'neighborhood',
                    'postal_code',
                    'address',
                    'street_number',
                    'complement',
                    'latitude',
                    'longitude',
                )
            }
        ),
    )

    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        super(LocationStackedInline, self).__init__(model, admin_site)
