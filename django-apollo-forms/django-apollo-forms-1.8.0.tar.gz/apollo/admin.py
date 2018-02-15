from django.contrib import admin
from apollo import models


class APIUserAdmin(admin.ModelAdmin):
    fields = ['service_name', 'auth_user']


class ExternalWebhookAdmin(admin.ModelAdmin):
    fields = ['form', 'url', 'for_event', 'service']
    list_display = ['form', 'url', 'service']


admin.site.register(models.APIUser, APIUserAdmin)
admin.site.register(models.ExternalWebhook, ExternalWebhookAdmin)