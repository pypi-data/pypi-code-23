from django.contrib import admin

from .models import Ticket


class TicketAdmin(admin.ModelAdmin):
    list_filter = ['status']
    list_display = ['subject', 'created', 'status', 'assignee']
    readonly_fields = ['user', 'email', 'subject', 'text', 'meta']
    search_fields = ['subject']

    def has_module_permission(self, request):
        """ Only available to superusers """
        return request.user.is_superuser


admin.site.register(Ticket, TicketAdmin)
