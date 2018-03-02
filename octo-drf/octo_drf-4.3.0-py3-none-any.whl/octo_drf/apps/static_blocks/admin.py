# -*- coding: utf-8 -*-

from django import forms
from trumbowyg.widgets import TrumbowygWidget
from django.contrib.contenttypes.admin import GenericStackedInline
from django.forms.widgets import Textarea
from sorl.thumbnail.admin import AdminImageMixin

from .models import StaticBlock


class StaticBlocForm(forms.ModelForm):

    class Meta:
        widgets = {
            'content': TrumbowygWidget(),
            'announce': Textarea(attrs={'rows': 5, 'cols': 35})
        }


class StaticBlockStackedInline(AdminImageMixin, GenericStackedInline):

    model = StaticBlock
    form = StaticBlocForm
    extra = 0
    fields = ('title', 'content', 'announce',
              'image1', 'image2', 'image3', 'image4',
              'order', 'is_published'
              )