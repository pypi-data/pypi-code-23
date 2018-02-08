from django.contrib import admin

from .models import MC2PConfig


class MC2PConfigAdmin(admin.ModelAdmin):
    list_display = ['key', 'secret_key']

    def has_add_permission(self, request):
        return not self.model.objects.count() and super(MC2PConfigAdmin, self).has_add_permission(request)

admin.site.register(MC2PConfig, MC2PConfigAdmin)
