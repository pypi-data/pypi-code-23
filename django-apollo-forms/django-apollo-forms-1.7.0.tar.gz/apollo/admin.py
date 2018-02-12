from django.contrib import admin
from apollo import models


class APIUserAdmin(admin.ModelAdmin):
    fields = ['service_name', 'auth_user']


admin.site.register(models.APIUser, APIUserAdmin)