from __future__ import absolute_import, print_function, unicode_literals

from django.contrib import admin
from .models import DBFile


class DBFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'content_type')

admin.site.register(DBFile, DBFileAdmin)
