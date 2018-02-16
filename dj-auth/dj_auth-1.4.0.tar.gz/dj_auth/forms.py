# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models import Q

from .settings import DEFAULT
from .models import ObjectFilter
from .widgets import ObjectFilterValuesWidget


class ObjectFilterFormMixin(object):

    class Meta:
        model = ObjectFilter
        fields = ('users', 'filter_type', 'content_type', 'filter_values')
        widgets = {'filter_values': ObjectFilterValuesWidget(),
                   }

    class Media:
        js = ('js/dj_auth.js', )

    def __init__(self, *args, **kwargs):
        DJ_AUTH = getattr(settings, 'DJ_AUTH', DEFAULT)

        super(ObjectFilterFormMixin, self).__init__(*args, **kwargs)

        content_type_queryset = self.fields['content_type'].queryset
        for record in DJ_AUTH['content_type_exclude']:
            app_label, model = record.split('.')
            content_type_queryset = content_type_queryset.exclude(app_label=app_label, model=model)

        filter_query = ''
        for record in DJ_AUTH['content_type_include']:
            app_label, model = record.split('.')
            filter_query += "Q(**{'app_label': '%s', 'model': '%s'}) |" % (app_label, model)

        if filter_query.endswith('|'):
            filter_query = filter_query[:-1]

        if filter_query:
            content_type_queryset = content_type_queryset.filter(eval(filter_query))

        self.fields['content_type'].queryset = content_type_queryset
        self.fields['content_type'].widget.attrs = {"id": 'dj_auth_content_type',
                                                    "onchange": 'refreshObjectFilterValuesWidget()', }

        if self.instance.pk:
            # Update
            self.fields['filter_values'].widget.attrs['content_type'] = self.instance.content_type.id

        self.fields['filter_values'].help_text = _('Hold down "Control", or "Command" on a Mac, to select more than one.')

    def clean(self):
        cleaned_data = super(ObjectFilterFormMixin, self).clean()
        return cleaned_data

    def clean_filter_values(self):
        data = self.cleaned_data['filter_values']
        if data:
            data = list(map(int, eval(data)))
        else:
            data = []
        return data
