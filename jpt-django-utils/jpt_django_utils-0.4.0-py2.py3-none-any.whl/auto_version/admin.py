"""Auto version admin."""
from django.contrib import admin


class AutoIntVersionAdmin(admin.ModelAdmin):
    """Add version into list_display and as readonly."""

    def get_list_display(self, request):
        list_display = list(super().get_list_display(request)) + [
            'version',
        ]
        return list_display

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj)) + [
            'version',
        ]
        return readonly_fields
