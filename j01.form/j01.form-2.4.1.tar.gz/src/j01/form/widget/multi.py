##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Multi Widget Implementation

$Id: select.py 78513 2007-07-31 23:03:47Z srichter $
"""
__docformat__ = "reStructuredText"
from operator import attrgetter

import zope.component
import zope.interface
import zope.i18nmessageid

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.widget

_ = zope.i18nmessageid.MessageFactory('p01')

from j01.form import btn
from j01.form import interfaces
from j01.form.widget.widget import WidgetMixin


@zope.interface.implementer(z3c.form.interfaces.IButtonForm,
    z3c.form.interfaces.IHandlerForm)
class FormMixin(object):
    pass


class IMultiFormButtons(zope.interface.Interface):
    """Multi form buttons"""

    add = btn.Button(
        title=_(u"Add"),
        css='btn btn-add-multi',
        )

    remove = btn.Button(
        title=_(u"Remove"),
        css='btn btn-remove-multi',
        )


@zope.interface.implementer(interfaces.IMultiWidget)
class MultiWidget(WidgetMixin, z3c.form.browser.widget.HTMLFormElement,
    z3c.form.widget.MultiWidget, FormMixin):
    """Multi widget implementation."""

    buttons = btn.Buttons()

    prefix = 'widget'
    klass = u'multi-control' # no form-control, that's a form
    css = u'multi'
    items = ()

    # show labels
    showLabel = True
    # show labels for key widgets
    showKeyWidgetLabel = False
    # show labels for value widgets
    showWidgetLabel = False

    # Internal attributes
    _adapterValueAttributes = ('label', 'name', 'required', 'title',
        'showLabel')

    def updateActions(self):
        self.updateAllowAddRemove()
        if self.name is not None:
            self.prefix = self.name
        self.actions = zope.component.getMultiAdapter(
            (self, self.request, self), z3c.form.interfaces.IActions)
        self.actions.update()

    @btn.buttonAndHandler(IMultiFormButtons['add'],
        condition=attrgetter('allowAdding'))
    def handleAdd(self, action):
        self.appendAddingWidget()

    @btn.buttonAndHandler(IMultiFormButtons['remove'],
        condition=attrgetter('allowRemoving'))
    def handleRemove(self, action):
        self.removeWidgets([widget.name for widget in self.widgets
                            if ('%s.remove' % (widget.name)) in self.request])

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        super(MultiWidget, self).update()
        self.updateActions()
        self.actions.execute()
        # Update again, as conditions may change
        self.updateActions()
        try:
            # force to disable sub widget labels
            for widget in self.key_widgets:
                if widget is not None:
                    widget.showLabel = self.showKeyWidgetLabel
            # show label
            for widget in self.widgets:
                widget.showLabel = self.showWidgetLabel
        except AttributeError:
            pass


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getMultiFieldWidget(field, request):
    """IFieldWidget factory for MultiWidget."""
    widget = MultiWidget(request)
    return z3c.form.widget.FieldWidget(field, widget)


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def getMultiFieldWidgetDispatcher(field, value_type, request):
    """IFieldWidget factory for MultiWidget."""
    return getMultiFieldWidget(field, request)
