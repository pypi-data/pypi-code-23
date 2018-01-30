# coding: utf-8
from django import forms
from .models import FonteExterna


class FonteExternaForm(forms.ModelForm):
    class Meta:
        model = FonteExterna
        fields = ('nome',
                  'tipo',
                  'url_sincronia',
                  'formato',
                  'descricao',
                  'srid',
                  'encoding', )