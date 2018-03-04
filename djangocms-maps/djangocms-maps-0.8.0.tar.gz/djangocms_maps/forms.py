# coding: utf-8
import json
import re

from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Maps

CSS_WIDTH_RE = re.compile(r'^\d+(?:px|em|%)$')
CSS_HEIGHT_RE = re.compile(r'^\d+(?:px|em)$')


class MapsForm(ModelForm):
    class Meta:
        model = Maps
        fields = '__all__'

    def clean(self):
        cleaned_data = super(MapsForm, self).clean()
        width = cleaned_data.get('width', '')
        height = cleaned_data.get('height', '')
        if width or height:
            if width and not CSS_WIDTH_RE.match(width):
                self._errors['width'] = self.error_class([
                    _(u'Must be a positive integer followed by'
                      u' “px”, “em” or “%”.')])
            if height and not CSS_HEIGHT_RE.match(height):
                self._errors['height'] = self.error_class([
                    _(u'Must be a positive integer followed by'
                      u' “px”, “em”.')])
        return cleaned_data

    def clean_style(self):
        style = self.cleaned_data.get('style', '').strip()
        if style:
            try:
                json.loads(style)
            except ValueError:
                raise ValidationError('Has to be valid JSON', code='invalid')
        return style
