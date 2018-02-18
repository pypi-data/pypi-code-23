# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from djangoplus.db.models import CharField, FieldPlus
from enderecos.forms import fields


class CepField(CharField, FieldPlus):
    def formfield(self, **kwargs):
        kwargs.setdefault('form_class', fields.CepField)
        return super(CepField, self).formfield(**kwargs)