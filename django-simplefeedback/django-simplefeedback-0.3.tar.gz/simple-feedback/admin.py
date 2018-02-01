from django.contrib import admin

from .models import Ticket


class TicketAdmin(admin.ModelAdmin):
    list_filter = ['status']
    list_display = ['subject', 'created', 'status', 'assignee']
    readonly_fields = ['user', 'email', 'subject', 'text', 'meta']
    search_fields = ['subject']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super(TicketAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
        if db_field.name == 'assignee':
            field.label_from_instance = lambda u: '{} <{}>'.format(u.get_full_name(), u.email)
        return field

    def has_module_permission(self, request):
        """ Only available to superusers """
        return request.user.is_superuser


admin.site.register(Ticket, TicketAdmin)
