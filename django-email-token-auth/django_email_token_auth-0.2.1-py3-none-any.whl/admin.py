# -*- coding: utf-8 -*-
u"Admin autoconfig for Django"

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from emailuser.models import EmailUser, UserOption

class EmailUserInline(admin.StackedInline):
    """Inline for standart Django admin user"""
    model = EmailUser
    can_delete = False
    verbose_name_plural = 'Email Users'

# Define a new User admin
class UserAdmin(UserAdmin):
    """New user-admin"""
    inlines = (EmailUserInline, )

class UserOptionAdmin(admin.ModelAdmin):
    """email user options"""
    list_display = ('user', 'name', 'value')
    search_fields = ("name", 'value')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(UserOption, UserOptionAdmin)

