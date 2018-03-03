#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import CoinType


# ===== course contract======
class CoinTypeForm(forms.ModelForm):
    class Meta:
        model = CoinType
        fields = ['name',"identity", "coin", "info"]