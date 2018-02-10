from django.contrib import admin

from .models import LAU, NUTS


class LAUAdmin(admin.ModelAdmin):
    list_display = ('nuts', 'code', 'name', 'local_name')
    search_fields = ('nuts__code', 'code', 'name', 'local_name')


class NUTSAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level')
    list_filter = ('level',)
    search_fields = ('code', 'name')


admin.site.register(LAU, LAUAdmin)
admin.site.register(NUTS, NUTSAdmin)
