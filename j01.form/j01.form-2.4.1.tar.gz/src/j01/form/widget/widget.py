###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Widget layout and setup
$Id: widget.py 4275 2015-07-25 13:28:27Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import zope.i18n
import zope.interface
import zope.component
from zope.schema.fieldproperty import FieldProperty

import z3c.form.field
import z3c.form.widget
import z3c.form.interfaces

from j01.form import interfaces


class WidgetMixin(object):
    """Enhanced widget layout mixin class supporting widget addons"""

    _showLabel = None
    _showRequired = None
    _showError = None
    _showDescription = None

    # description and addon set by updateWidget in j01 forms
    description = FieldProperty(interfaces.IWidget['description'])
    addOnBefore = FieldProperty(interfaces.IWidget['addOnBefore'])
    addOnAfter = FieldProperty(interfaces.IWidget['addOnAfter'])
    addOnWrapper = FieldProperty(interfaces.IWidget['addOnWrapper'])

    @apply
    def showLabel():
        """Show label condition

        Allows to disable the label for single (sequence) checkbox widgets
        override this in your widget if needed.
        """
        def fget(self):
            if self._showLabel is not None:
                # return overriden value
                return self._showLabel
            else:
                # depends on label
                return self.label is not None
        def fset(self, value):
            self._showLabel = value
        return property(fget, fset)

    @apply
    def showRequired():
        def fget(self):
            if self._showRequired is not None:
                # return overriden value
                return self._showRequired
            else:
                # depends on required marker
                return self.required is True
        def fset(self, value):
            self._showRequired = value
        return property(fget, fset)

    @apply
    def showError():
        def fget(self):
            if self._showError is not None:
                # return overriden value
                return self._showError
            else:
                # depends on error
                return self.error is not None
        def fset(self, value):
            self._showError = value
        return property(fget, fset)

    @apply
    def showDescription():
        def fget(self):
            if self._showDescription is not None:
                # return overriden value
                return self._showDescription
            else:
                # depends on description
                return self.description is not None
        def fset(self, value):
            self._showDescription = value
        return property(fget, fset)

    def render(self):
        """Render the plain widget without additional layout"""
        widget = super(WidgetMixin, self).render()
        classes = ['input-group']
        if self.addOnBefore is not None:
            widget = '%s\n%s' % (self.addOnBefore, widget)
            classes.append('input-group-before')
        if self.addOnAfter is not None:
            widget = '%s\n%s' % (widget, self.addOnAfter)
            classes.append('input-group-after')
        if self.addOnWrapper:
            # don't use if None or an empty string
            widget = self.addOnWrapper % {'widget': widget,
                                          'class': ' '.join(classes)}
        return widget
