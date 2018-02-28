# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Form Widgets
"""

from __future__ import unicode_literals, absolute_import

import json
import datetime

import six

import colander
from deform import widget as dfwidget
from webhelpers2.html import tags, HTML


class ReadonlyWidget(dfwidget.HiddenWidget):

    readonly = True

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ''
        # TODO: is this hacky?
        text = kw.get('text')
        if not text:
            text = field.parent.tailbone_form.render_field_value(field.name)
        return HTML.tag('span', text) + tags.hidden(field.name, value=cstruct, id=field.oid)


class NumberInputWidget(dfwidget.TextInputWidget):
    template = 'numberinput'
    autocomplete = 'off'


class PlainSelectWidget(dfwidget.SelectWidget):
    template = 'select_plain'


class JQuerySelectWidget(dfwidget.SelectWidget):
    template = 'select_jquery'


class JQueryDateWidget(dfwidget.DateInputWidget):
    """
    Uses the jQuery datepicker UI widget, instead of whatever it is deform uses
    by default.
    """
    template = 'date_jquery'
    type_name = 'text'
    requirements = None

    default_options = (
        ('changeMonth', True),
        ('changeYear', True),
        ('dateFormat', 'yy-mm-dd'),
    )

    def serialize(self, field, cstruct, **kw):
        if cstruct in (colander.null, None):
            cstruct = ''
        readonly = kw.get('readonly', self.readonly)
        template = readonly and self.readonly_template or self.template
        options = dict(
            kw.get('options') or self.options or self.default_options
        )
        options.update(kw.get('extra_options', {}))
        kw.setdefault('options_json', json.dumps(options))
        kw.setdefault('selected_callback', None)
        values = self.get_template_values(field, cstruct, kw)
        return field.renderer(template, **values)


class JQueryTimeWidget(dfwidget.TimeInputWidget):
    """
    Uses the jQuery datepicker UI widget, instead of whatever it is deform uses
    by default.
    """
    template = 'time_jquery'
    type_name = 'text'
    requirements = None
    default_options = (
        ('showPeriod', True),
    )


class JQueryAutocompleteWidget(dfwidget.AutocompleteInputWidget):
    """ 
    Uses the jQuery autocomplete plugin, instead of whatever it is deform uses
    by default.
    """
    template = 'autocomplete_jquery'
    requirements = None
    field_display = ""
    service_url = None
    cleared_callback = None
    selected_callback = None

    default_options = (
        ('autoFocus', True),
    )
    options = None

    def serialize(self, field, cstruct, **kw):
        if 'delay' in kw or getattr(self, 'delay', None):
            raise ValueError(
                'AutocompleteWidget does not support *delay* parameter '
                'any longer.'
            )
        if cstruct in (colander.null, None):
            cstruct = ''
        self.values = self.values or []
        readonly = kw.get('readonly', self.readonly)

        options = dict(
            kw.get('options') or self.options or self.default_options
        )
        options['source'] = self.service_url

        kw['options'] = json.dumps(options)
        kw['field_display'] = self.field_display
        kw['cleared_callback'] = self.cleared_callback
        kw.setdefault('selected_callback', self.selected_callback)
        tmpl_values = self.get_template_values(field, cstruct, kw)
        template = readonly and self.readonly_template or self.template
        return field.renderer(template, **tmpl_values)
