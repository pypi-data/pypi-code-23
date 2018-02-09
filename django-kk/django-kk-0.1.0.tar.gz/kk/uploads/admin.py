from django.contrib import admin

class SimpleUploadAdmin(admin.ModelAdmin):
    list_display = ['codename', 'status', 'file']
    list_per_page = 80
    ordering = ['codename']

    fields = ['status', 'codename', 'file']
