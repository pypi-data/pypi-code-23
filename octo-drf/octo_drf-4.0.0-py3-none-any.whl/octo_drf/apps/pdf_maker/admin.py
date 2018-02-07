


from django import forms
from django.contrib import admin

from octo_drf.apps.base.admin import BaseAdmin
from redactor.widgets import RedactorEditor

from .models import PDFTemplate


class PDFTemplateAdminForm(forms.ModelForm):

    class Meta:
        widgets = {
            'content': RedactorEditor(),
        }


@admin.register(PDFTemplate)
class PDFTemplateAdmin(BaseAdmin):

    form = PDFTemplateAdminForm
    list_display = ('name', 'template')
    readonly_fields = ('template', )