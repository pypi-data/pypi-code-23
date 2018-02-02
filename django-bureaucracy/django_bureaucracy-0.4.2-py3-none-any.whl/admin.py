from django.contrib import admin

from .models import Document


class DocumentAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.uploader = request.user
        obj.save()


admin.site.register(Document, DocumentAdmin)
