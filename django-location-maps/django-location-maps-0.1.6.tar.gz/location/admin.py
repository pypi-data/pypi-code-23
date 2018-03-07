# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.conf.urls import url
from django.core import serializers
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from .models import *
from .forms import LocationForm, CountryCodeForm, CountryForm, CityForm, StateForm


class CityAdmin(admin.ModelAdmin):
    form = CityForm
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(City, CityAdmin)


class StateAdmin(admin.ModelAdmin):
    form = StateForm
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(State, StateAdmin)


class CountryAdmin(admin.ModelAdmin):
    form = CountryForm
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Country, CountryAdmin)


class CountryCodeAdmin(admin.ModelAdmin):
    form = CountryCodeForm
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(CountryCode, CountryCodeAdmin)


class LocationAdmin(admin.ModelAdmin):
    form = LocationForm
    model = Location
    prepopulated_fields = {"slug": ("address",)}
    fieldsets = (
        (
            _('Location'), {
                'fields': (
                    'map',
                    'field1',
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
        super(LocationAdmin, self).__init__(model, admin_site)

    def get_urls(self):
        urls = super(LocationAdmin, self).get_urls()
        my_urls = [
            url(r'^cities/', self.admin_site.admin_view(self.cities), name='city'),
            url(r'^states/', self.admin_site.admin_view(self.states), name='state'),
        ]
        return my_urls + urls

    def cities(self, request):
        data = serializers.serialize('json', City.objects.filter(state=request.GET.get('state')).all())
        return HttpResponse(data, content_type='application/json')

    def states(self, request):
        data = serializers.serialize('json', State.objects.filter(country=request.GET.get('country')).all())
        return HttpResponse(data, content_type='application/json')

