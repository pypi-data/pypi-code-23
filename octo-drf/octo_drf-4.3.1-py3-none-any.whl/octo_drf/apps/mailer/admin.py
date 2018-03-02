


from django.contrib import admin
from django import forms

from trumbowyg.widgets import TrumbowygWidget

from .models import UserTemplate, AdminTemplate


class MailerTemplateForm(forms.ModelForm):

    class Meta:
        widgets = {
            'content': TrumbowygWidget(),
            'footer': TrumbowygWidget()
        }


@admin.register(UserTemplate)
class MailerTemplateAdmin(admin.ModelAdmin):

    list_display = ('name', 'template')
    fields = ('name', 'template', 'admin_template', 'from_email', 'title', 'content', 'footer')
    readonly_fields = ('template', )
    form = MailerTemplateForm


@admin.register(AdminTemplate)
class MailerTemplateAdmin(admin.ModelAdmin):

    list_display = ('name', 'template', )
    fields = ('name', 'template', 'title', 'from_email', 'admin_url', 'content', 'footer', 'subscribers')
    filter_horizontal = ('subscribers', )
    readonly_fields = ('template', )
    form = MailerTemplateForm
