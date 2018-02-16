# -*- coding: utf-8 -*-
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string


class ObjectFilterValuesWidget(forms.SelectMultiple):

    def render(self, name, value, *args, **kwargs):
        option_list = []
        values = value
        try:
            values = eval(values)
        except:
            values = []

        if 'content_type' in self.attrs:
            content_type_id = self.attrs['content_type']
        else:
            content_type_id = None

        if isinstance(values, list):
            if content_type_id:
                cnt_type = ContentType.objects.get(pk=content_type_id)
                model_class = cnt_type.model_class()
                if hasattr(model_class, 'dj_auth_objects'):
                    option_list = [(o.id, o.__str__()) for o in model_class.dj_auth_objects.all()]
                else:
                    option_list = [(o.id, o.__str__()) for o in model_class._default_manager.distinct()]
        else:
            option_list.insert(0, ('0', ''))
            values = '0'

        return render_to_string("object_filter_values_widget.html", {'option_list': option_list, 'selected': values})
