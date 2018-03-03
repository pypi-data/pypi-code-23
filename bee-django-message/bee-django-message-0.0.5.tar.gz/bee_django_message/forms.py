#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import Message


# ===== course contract======
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['name', "info", "is_user_show", "is_admin_show"]
