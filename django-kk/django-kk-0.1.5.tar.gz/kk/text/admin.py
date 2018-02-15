from django.contrib import admin

class SimpleTextAdmin(admin.ModelAdmin):
    list_display = ['codename', 'status', 'note']
    list_per_page = 80
    ordering = ['codename']
    fields = ['status', 'codename', 'note', 'content']
