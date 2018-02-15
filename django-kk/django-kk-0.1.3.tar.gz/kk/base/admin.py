from django.contrib import admin
from django.db import models
from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html

class BaseAdmin(admin.ModelAdmin):
    list_per_page = 80

class OrderedAdmin(BaseAdmin):
    list_display = ('position', 'status')
#    ordering = ('-is_unordered', 'position', )

    fields = ('status', 'position', )

    def get_queryset(self, request):
        qs = super(OrderedAdmin, self).get_queryset(request)
        qs = qs.annotate(is_unordered = models.Count('position'))
        return qs

    def is_unordered(self, obj):
        return obj.is_unordered
    is_unordered.admin_order_field = 'is_unordered'


class InlinesBeforeCreatingObjectAdminMixin(admin.ModelAdmin):

    def get_inline_instances(self, request, obj = None):
        if obj:
            return [
                inline(self.model, self.admin_site) for inline in self.inlines
            ]
        else:
            return []
