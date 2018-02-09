from django import forms
from wagtail.wagtailcore.blocks import ChooserBlock
from .models import Form


class FormChooserBlock(ChooserBlock):
    target_model = Form
    widget = forms.Select

    def value_for_form(self, value):
        if isinstance(value, self.target_model):
            return value.pk
        else:
            return value

# class FormChooserBlock(ChooserBlock):
#     @cached_property
#     def target_model(self):
#         return Form
#
#     @cached_property
#     def widget(self):
#         from wagtail.documents.widgets import AdminDocumentChooser
#         return AdminDocumentChooser
#
#     def render_basic(self, value, context=None):
#         if value:
#             return format_html('<a href="{0}">{1}</a>', value.url, value.title)
#         else:
#             return ''
#
#     class Meta:
#         icon = "doc-empty"
