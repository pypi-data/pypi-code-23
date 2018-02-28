from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from django.apps import apps
from django import forms
from sorl.thumbnail.admin import AdminImageMixin

from octo_drf.apps.base.admin import BaseAdmin
from .models import FormMeta, FormFieldMeta


class MetaFormset(BaseInlineFormSet):
    """
    Формсет для FormFieldMeta, передает класс FormMeta в форму инлайна
    """
    def get_form_kwargs(self, index):
        kwargs = self.form_kwargs.copy()
        kwargs.update({'parent': self.instance})
        return kwargs


class FormMetaForm(forms.ModelForm):
    """
    Форма для MetaForm, заменяет поле `form_name` на ChoiceField
    Варианты для ChoiceField предсталяют собой все модели форм из mail_forms.models
    """
    def _get_forms(self):
        models = apps.get_app_config('mail_forms').get_models()
        choices = tuple([(m._meta.model_name, m._meta.verbose_name) for m in models])
        return choices

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['form_name'] = forms.ChoiceField(choices=self._get_forms(), label='Название формы')


class FormFieldMetaForm(forms.ModelForm):
    """
    Форма для FormFieldMeta, заменяет поле `field_name` на ChoiceField
    Варианты для ChoiceField предсталяют собой все поля родительской модели FormMeta
    """

    def _get_form_fields(self, parent):
        choices = []
        if parent.form_name:
            form_name = parent.form_name
            model = apps.get_app_config('mail_forms').get_model(form_name)
            choices = tuple([(field, field) for field in model._get_model_fields()])
        return choices

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop('parent')
        super().__init__(*args, **kwargs)
        choices = self._get_form_fields(parent)
        self.fields['field_name'] = forms.ChoiceField(choices=choices, label='Название поля')


class FormFieldMetaInline(AdminImageMixin, admin.StackedInline):

    model = FormFieldMeta
    fields = ('field_name', 'title', 'placeholder', 'image', 'error_message')
    extra = 0
    form = FormFieldMetaForm
    formset = MetaFormset


@admin.register(FormMeta)
class FormMetaAdmin(BaseAdmin):

    list_display = ('form_name', )
    form = FormMetaForm
    inlines = (FormFieldMetaInline, )
