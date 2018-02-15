###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Select ordered widget
$Id:$
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.component
import zope.schema.interfaces
import zope.i18n
import zope.i18nmessageid

import z3c.form.interfaces
import z3c.form.widget

import j01.selectordered.widget

import j01.form.layer
from j01.form import interfaces
from j01.form.widget.widget import WidgetMixin

_ = zope.i18nmessageid.MessageFactory('p01')


class OrderedSelectWidget(WidgetMixin,
    j01.selectordered.widget.OrderedSelectWidget):
    """Ordered-Select widget implementation with JQuery template."""

    zope.interface.implementsOnly(interfaces.IOrderedSelectWidget)

    klass = u'select-ordered-control form-control'
    css = u'select-ordered'

    # btn labels
    @property
    def btnAddLabel(self):
        return zope.i18n.translate(_(u'add'), context=self.request)

    @property
    def btnRemoveLabel(self):
        return zope.i18n.translate(_(u'remove'), context=self.request)

    @property
    def btnUpLabel(self):
        return zope.i18n.translate(_(u'up'), context=self.request)

    @property
    def btnDownLabel(self):
        return zope.i18n.translate(_(u'down'), context=self.request)


# ordered select widget
@zope.component.adapter(zope.schema.interfaces.ISequence,
                        j01.form.layer.IFormLayer)
@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def OrderedSelectFieldWidget(field, request):
    """IFieldWidget factory for OrderedSelectWidget."""
    return z3c.form.widget.FieldWidget(field, OrderedSelectWidget(request))


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def SequenceChoiceSelectFieldWidget(field, value_type, request):
    """IFieldWidget factory for OrderedSelectWidget."""
    return OrderedSelectFieldWidget(field, request)


# get
def getOrderedSelectWidget(field, request):
    """IFieldWidget factory for SelectWidget."""
    return z3c.form.widget.FieldWidget(field, OrderedSelectWidget(request))
