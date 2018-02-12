from django.contrib import admin

from .models import LAU, NUTS


class LAUAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'local_name', 'nuts1', 'nuts2', 'nuts3', 'nuts4')
    search_fields = ('nuts__code', 'code', 'name', 'local_name')


class NUTSAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level')
    list_filter = ('level',)
    search_fields = ('code', 'name')


admin.site.register(LAU, LAUAdmin)
admin.site.register(NUTS, NUTSAdmin)
