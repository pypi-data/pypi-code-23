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
$Id: converter.py 4753 2018-02-15 04:53:17Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.i18n.format
import zope.component
import zope.schema.interfaces

import z3c.form.converter

from j01.datetimepicker import interfaces


class DateTimePickerConverter(z3c.form.converter.BaseDataConverter):
    """DateTimePicker date for datetime converter."""
    zope.component.adapts(
        zope.schema.interfaces.IDatetime, interfaces.IDateTimePickerWidget)

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return u''
        return self.widget.getWidgetValue(value)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value == u'':
            return self.field.missing_value
        return self.widget.getFieldValue(value)
