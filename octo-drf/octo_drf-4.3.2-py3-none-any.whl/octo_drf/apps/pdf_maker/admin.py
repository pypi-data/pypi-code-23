


from django import forms
from django.contrib import admin

from octo_drf.apps.base.admin import BaseAdmin
from trumbowyg.widgets import TrumbowygWidget

from .models import PDFTemplate


class PDFTemplateAdminForm(forms.ModelForm):

    class Meta:
        widgets = {
            'content': TrumbowygWidget(),
        }


@admin.register(PDFTemplate)
class PDFTemplateAdmin(BaseAdmin):

    form = PDFTemplateAdminForm
    list_display = ('name', 'template')
    readonly_fields = ('template', )