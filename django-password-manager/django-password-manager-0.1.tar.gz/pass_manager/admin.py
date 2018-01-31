#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

# future
from __future__ import unicode_literals

# Django
from django.contrib import admin
from pass_manager import models


class PasswordHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'password', 'timestamp', )
    list_display_links = ('id', 'user', )
    search_fields = ('user', )
    raw_id_fields = ('user', )
    list_per_page = 20
    ordering = ('-id', )

admin.site.register(models.PasswordHistory, PasswordHistoryAdmin)
