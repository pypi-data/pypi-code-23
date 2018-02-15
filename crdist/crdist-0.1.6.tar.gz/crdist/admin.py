from django.contrib import admin

# Register your models here.

from crdist.models import District, Canton, Province
from crdist.widgets import DistrictSelect
from django import forms

admin.site.register([District, Canton, Province])

