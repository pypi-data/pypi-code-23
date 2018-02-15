##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: datetimepicker.py 4754 2018-02-15 04:53:32Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.interface

import z3c.form.widget

import j01.datetimepicker.widget

from j01.form import interfaces
from j01.form.widget.widget import WidgetMixin


# datetime widget
class DateTimePickerWidget(WidgetMixin,
    j01.datetimepicker.widget.DateTimePickerWidget):
    """DateTimePicker widget implementation."""

    zope.interface.implementsOnly(interfaces.IDateTimePickerWidget)

    klass = u'datetimepicker-control form-control'
    # prefix datetimepicker class and use bootstrap-datetimepicker.
    # This prevents to essup with the div.datepicker box
    css = u'bootstrap-datetimepicker'


def getDateTimePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    return z3c.form.widget.FieldWidget(field, DateTimePickerWidget(request))
