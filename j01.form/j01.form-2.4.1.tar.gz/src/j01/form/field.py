##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Field Implementation

$Id: field.py 4644 2017-09-17 23:14:29Z roger.ineichen $
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.location
import zope.schema.interfaces

import z3c.form.util
import z3c.form.interfaces
from z3c.form.error import MultipleErrors
from z3c.form.widget import AfterWidgetUpdateEvent

from j01.form import interfaces


@zope.interface.implementer_only(z3c.form.interfaces.IWidgets)
class J01FieldWidgets(z3c.form.util.Manager):
    """Widget manager for IFieldWidget."""

    zope.component.adapts(interfaces.IForm, z3c.form.interfaces.IFormLayer,
        zope.interface.Interface)

    prefix = 'widgets.'
    mode = z3c.form.interfaces.INPUT_MODE
    errors = ()
    hasRequiredFields = False
    ignoreContext = False
    ignoreRequest = False
    ignoreReadonly = False
    ignoreRequiredOnExtract = False
    setErrors = True

    def __init__(self, form, request, content):
        super(J01FieldWidgets, self).__init__()
        self.form = form
        self.request = request
        self.content = content

    def validate(self, data):
        """Manager validator will validate invariants

        NOTE: this validator can only use the form.ignoreContext and will
        ignore the field.ignoreContext setup
        """
        fields = self.form.fields.values()

        # Step 1: Collect the data for the various schemas
        schemaData = {}
        for field in fields:
            schema = field.interface
            if schema is None:
                continue

            fieldData = schemaData.setdefault(schema, {})
            if field.__name__ in data:
                fieldData[field.field.__name__] = data[field.__name__]

        # Step 2: Validate the individual schemas and collect errors
        errors = ()
# XXX: I guess self.content is not the right context if we use an
#      adapted context. Change and use the adapted context as content for each
#      schema.
        content = self.content
        if self.ignoreContext:
            content = None
        for schema, fieldData in schemaData.items():
            validator = zope.component.getMultiAdapter(
                (content, self.request, self.form, schema, self),
                z3c.form.interfaces.IManagerValidator)
            errors += validator.validate(fieldData)

        return errors

    def update(self):
        """See interfaces.IWidgets"""
        # Create a unique prefix.
        prefix = z3c.form.util.expandPrefix(self.form.prefix)
        prefix += z3c.form.util.expandPrefix(self.prefix)
        # Walk through each field, making a widget out of it.
        uniqueOrderedKeys = []
        for field in self.form.fields.values():
            # Step 0. Determine whether the context should be ignored.
            ignoreContext = self.ignoreContext
            if field.ignoreContext is not None:
                ignoreContext = field.ignoreContext
            # Step 1: Determine the mode of the widget.
            mode = self.mode
            if field.mode is not None:
                mode = field.mode
            elif field.field.readonly and not self.ignoreReadonly:
                mode = z3c.form.interfaces.DISPLAY_MODE
            elif not ignoreContext:
                # get data manager
                dm = zope.component.getMultiAdapter((self.content, field.field),
                    z3c.form.interfaces.IDataManager)
                if not dm.canWrite():
                    # If we do not have enough permissions to write to the
                    # attribute, then switch to display mode.
                    mode = z3c.form.interfaces.DISPLAY_MODE
            # Step 2: Get the widget for the given field.
            shortName = field.__name__
            newWidget = True
            if shortName in self._data:
                # reuse existing widget
                widget = self._data[shortName]
                newWidget = False
            elif field.widgetFactory.get(mode) is not None:
                factory = field.widgetFactory.get(mode)
                widget = factory(field.field, self.request)
            else:
                widget = zope.component.getMultiAdapter(
                    (field.field, self.request),
                    z3c.form.interfaces.IFieldWidget)
            # Step 3: Set the prefix for the widget
            widget.name = prefix + shortName
            widget.id = (prefix + shortName).replace('.', '-')
            # Step 4: Set the context
            widget.context = self.content
            # Step 5: Set the form
            widget.form = self.form
            # Optimization: Set both interfaces here, rather in step 4 and 5:
            # ``alsoProvides`` is quite slow
            zope.interface.alsoProvides(widget,
                z3c.form.interfaces.IContextAware,
                z3c.form.interfaces.IFormAware)
            # Step 6: Set some variables
            widget.ignoreContext = ignoreContext
            # override widget.required if given otherwise use existing required
            widget.required = self.form.widgetRequireds.get(shortName,
                widget.required)
            widget.ignoreRequest = self.form.widgetIgnoreRequests.get(shortName,
                self.ignoreRequest)
            if field.showDefault is not None:
                widget.showDefault = field.showDefault
            # Step 7: Set the mode of the widget
            widget.mode = mode
            # Step 8: Setup ignore on validation used during extract validation
            widget.ignoreRequiredOnValidation = \
                self.form.ignoreRequiredOnValidations.get(shortName,
                    self.ignoreRequiredOnExtract)
            # Step 9: Update the widget
            widget.update()
            zope.event.notify(AfterWidgetUpdateEvent(widget))
            # Step 10: Add the widget to the manager
            if widget.required:
                self.hasRequiredFields = True
            uniqueOrderedKeys.append(shortName)
            if newWidget:
                self._data_values.append(widget)
                self._data[shortName] = widget
                zope.location.locate(widget, self, shortName)
            # always ensure that we add all keys and keep the order given from
            # button items
            self._data_keys = uniqueOrderedKeys

    def _extract(self, returnRaw=False):
        data = {}
        errors = ()
        for name, widget in self.items():
            if widget.mode == z3c.form.interfaces.DISPLAY_MODE:
                continue
            value = widget.field.missing_value
            try:
                widget.setErrors = self.setErrors
                raw = widget.extract()
                if raw is not z3c.form.interfaces.NO_VALUE:
                    value = z3c.form.interfaces.IDataConverter(widget
                        ).toFieldValue(raw)
                # don't set ignoreRequiredOnValidation based on self, we provide
                # a per widget setup with j01.form ignoreRequiredOnValidations
                # and the update method already applied this to the widget
                # widget.ignoreRequiredOnValidation = \
                #     self.ignoreRequiredOnExtract
                zope.component.getMultiAdapter((
                    #self.content,
                    widget.context,
                    self.request,
                    self.form,
                    getattr(widget, 'field', None),
                    widget),
                    z3c.form.interfaces.IValidator).validate(value)
            except (zope.interface.Invalid,
                    ValueError, MultipleErrors) as error:
                view = zope.component.getMultiAdapter((
                    error,
                    self.request,
                    widget,
                    widget.field,
                    self.form,
                    #self.content
                    widget.context),
                    z3c.form.interfaces.IErrorViewSnippet)
                view.update()
                if self.setErrors:
                    widget.error = view
                errors += (view,)
            else:
                name = widget.__name__
                if returnRaw:
                    data[name] = raw
                else:
                    data[name] = value
        for error in self.validate(data):
            view = zope.component.getMultiAdapter((
                error,
                self.request,
                None, None,
                self.form,
                # self.content,
                widget.context),
                z3c.form.interfaces.IErrorViewSnippet)
            view.update()
            errors += (view,)
        if self.setErrors:
            self.errors = errors
        return data, errors

    def extract(self):
        """See interfaces.IWidgets"""
        return self._extract(returnRaw=False)

    def extractRaw(self):
        """See interfaces.IWidgets"""
        return self._extract(returnRaw=True)
