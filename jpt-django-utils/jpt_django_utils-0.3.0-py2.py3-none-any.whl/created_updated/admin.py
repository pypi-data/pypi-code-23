"""Created updated admin."""
from django.contrib import admin


class CreatedUpdatedAdmin(admin.ModelAdmin):
    """Add created updated fields into list_display and as readonly."""

    def get_list_display(self, request):
        list_display = list(super().get_list_display(request)) + [
            'created_by',
            'updated_by',
            'updated_dt',
        ]
        return list_display

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj)) + [
            'created_dt',
            'updated_dt',
            'created_by',
            'updated_by',
        ]
        return readonly_fields
