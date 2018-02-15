###############################################################################
#
# Copyright (c) 2014 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""Testing

$Id: testing.py 4241 2015-05-18 09:38:13Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import os.path

import zope.schema.interfaces
import zope.pagetemplate.interfaces

import z3c.form.interfaces
import z3c.form.testing
import z3c.form.widget

import p01.schema.interfaces

import j01.form.layer
import j01.form.interfaces
import j01.form.widget
import j01.form.widget.dictionary
import j01.form.widget.multi
import j01.form.widget.password
import j01.form.widget.radio
import j01.form.widget.select
import j01.form.widget.text
import j01.form.widget.textarea


def getPath(fName):
    return os.path.join(os.path.dirname(j01.form.widget.__file__), fName)


def provideWidgetTemplate(fName, iface, mode=z3c.form.interfaces.INPUT_MODE):
    fPath = getPath(fName)
    template = z3c.form.widget.WidgetTemplateFactory(fPath, 'text/html')
    zope.interface.directlyProvides(template,
        zope.pagetemplate.interfaces.IPageTemplate)
    zope.component.provideAdapter(template,
        (None, j01.form.layer.IFormLayer, None, None, iface),
        zope.pagetemplate.interfaces.IPageTemplate, name=mode)


def setupFormDefaults():
    # z3c.form widget setup
    z3c.form.testing.setupFormDefaults()

    # checkbox
    provideWidgetTemplate('checkbox_input.pt',
        j01.form.interfaces.ICheckBoxWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('checkbox_display.pt',
        j01.form.interfaces.ICheckBoxWidget,
        z3c.form.interfaces.DISPLAY_MODE)
    provideWidgetTemplate('checkbox_hidden.pt',
        j01.form.interfaces.ICheckBoxWidget,
        z3c.form.interfaces.HIDDEN_MODE)

    provideWidgetTemplate('checkbox_inline_input.pt',
        j01.form.interfaces.ICheckBoxInlineWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('checkbox_input.pt',
        j01.form.interfaces.ISingleCheckBoxWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('checkbox_inline_input.pt',
        j01.form.interfaces.ISingleCheckBoxInlineWidget,
        z3c.form.interfaces.INPUT_MODE)

    provideWidgetTemplate('checkbox_picker_input.pt',
        j01.form.interfaces.ICheckBoxPickerWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('checkbox_inline_picker_input.pt',
        j01.form.interfaces.ICheckBoxInlinePickerWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('checkbox_picker_input.pt',
        j01.form.interfaces.ISingleCheckBoxPickerWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('checkbox_inline_picker_input.pt',
        j01.form.interfaces.ISingleCheckBoxInlinePickerWidget,
        z3c.form.interfaces.INPUT_MODE)
    # dictionary
    zope.component.provideAdapter(
        j01.form.widget.dictionary.DictKeyValueConverter)

    # file
    provideWidgetTemplate('file_input.pt',
        j01.form.interfaces.IFileWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('file_display.pt',
        j01.form.interfaces.IFileWidget,
        z3c.form.interfaces.DISPLAY_MODE)

    # multi widget
    zope.component.provideAdapter(
        j01.form.widget.multi.getMultiFieldWidget,
        [zope.schema.interfaces.IDict,
         zope.schema.interfaces.IField,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.multi.getMultiFieldWidgetDispatcher,
        [zope.schema.interfaces.IList,
         zope.schema.interfaces.IField,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.multi.getMultiFieldWidgetDispatcher,
        [zope.schema.interfaces.ITuple,
         zope.schema.interfaces.IField,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    provideWidgetTemplate('multi_input.pt',
        j01.form.interfaces.IMultiWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('multi_display.pt',
        j01.form.interfaces.IMultiWidget,
        z3c.form.interfaces.DISPLAY_MODE)
    provideWidgetTemplate('multi_hidden.pt',
        j01.form.interfaces.IMultiWidget,
        z3c.form.interfaces.HIDDEN_MODE)

    # password
    zope.component.provideAdapter(
        j01.form.widget.password.PasswordConfirmationDataConverter)
    zope.component.provideAdapter(
        j01.form.widget.password.getPasswordWidget,
        [zope.schema.interfaces.IPassword,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.password.PasswordRequiredValue)
    provideWidgetTemplate('password_input.pt',
        j01.form.interfaces.IPasswordWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('password_display.pt',
        j01.form.interfaces.IPasswordWidget,
        z3c.form.interfaces.DISPLAY_MODE)
    provideWidgetTemplate('password_confirmation_input.pt',
        j01.form.interfaces.IPasswordConfirmationWidget,
        z3c.form.interfaces.INPUT_MODE)

    # radio
    zope.component.provideAdapter(
        j01.form.widget.radio.getRadioWidget,
        [zope.schema.interfaces.IBool,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    provideWidgetTemplate('radio_input.pt',
        j01.form.interfaces.IRadioWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('radio_display.pt',
        j01.form.interfaces.IRadioWidget,
        z3c.form.interfaces.DISPLAY_MODE)
    provideWidgetTemplate('radio_hidden.pt',
        j01.form.interfaces.IRadioWidget,
        z3c.form.interfaces.HIDDEN_MODE)
    provideWidgetTemplate('radio_input.pt',
        j01.form.widget.radio.RadioInlineWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('radio_picker_input.pt',
        j01.form.widget.radio.RadioPickerWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('radio_inline_picker_input.pt',
        j01.form.widget.radio.RadioInlinePickerWidget,
        z3c.form.interfaces.INPUT_MODE)

    # select
    zope.component.provideAdapter(
        j01.form.widget.select.ChoiceWidgetDispatcher)
    zope.component.provideAdapter(
        j01.form.widget.select.SelectFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.select.CollectionSelectFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.select.CollectionChoiceSelectFieldWidget)
    provideWidgetTemplate('select_input.pt',
        j01.form.interfaces.ISelectWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('select_display.pt',
        j01.form.interfaces.ISelectWidget,
        z3c.form.interfaces.DISPLAY_MODE)
    provideWidgetTemplate('select_hidden.pt',
        j01.form.interfaces.ISelectWidget,
        z3c.form.interfaces.HIDDEN_MODE)
    provideWidgetTemplate('select_optgroup_input.pt',
        j01.form.widget.select.GroupSelectWidget,
        z3c.form.interfaces.INPUT_MODE)

    # text
    zope.component.provideAdapter(
        j01.form.widget.text.getDateWidget,
        [zope.schema.interfaces.IDate,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getDatetimeWidget,
        [zope.schema.interfaces.IDatetime,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTimeWidget,
        [zope.schema.interfaces.ITime,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getURLWidget,
        [zope.schema.interfaces.IURI,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTextWidget,
        [zope.schema.interfaces.IBytesLine,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTextWidget,
        [zope.schema.interfaces.IASCIILine,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTextWidget,
        [zope.schema.interfaces.ITextLine,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTextWidget,
        [zope.schema.interfaces.IId,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTextWidget,
        [zope.schema.interfaces.IInt,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTextWidget,
        [zope.schema.interfaces.IFloat,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTextWidget,
        [zope.schema.interfaces.IDecimal,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTextWidget,
        [zope.schema.interfaces.ITimedelta,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getColorWidget,
        [p01.schema.interfaces.IColor,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getDateWidget,
        [p01.schema.interfaces.IDate,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getDatetimeWidget,
        [p01.schema.interfaces.IDatetime,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getDatetimeLocalWidget,
        [p01.schema.interfaces.IDatetimeLocal,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getDatetimeLocalWidget,
        [p01.schema.interfaces.IDatetimeLocal,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getEMailWidget,
        [p01.schema.interfaces.IEMail,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getMonthWidget,
        [p01.schema.interfaces.IMonth,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getNumberWidget,
        [p01.schema.interfaces.INumber,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getSearchWidget,
        [p01.schema.interfaces.ISearch,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTelWidget,
        [p01.schema.interfaces.ITel,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getTimeWidget,
        [p01.schema.interfaces.ITime,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getURLWidget,
        [p01.schema.interfaces.IURL,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.text.getWeekWidget,
        [p01.schema.interfaces.IWeek,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)

    provideWidgetTemplate('text_input.pt',
        j01.form.interfaces.ITextWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('text_display.pt',
        j01.form.interfaces.ITextWidget,
        z3c.form.interfaces.DISPLAY_MODE)
    provideWidgetTemplate('text_hidden.pt',
        j01.form.interfaces.ITextWidget,
        z3c.form.interfaces.HIDDEN_MODE)

    # textarea
    zope.component.provideAdapter(
        j01.form.widget.textarea.getTextAreaWidget,
        [zope.schema.interfaces.IASCII,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    zope.component.provideAdapter(
        j01.form.widget.textarea.getTextAreaWidget,
        [zope.schema.interfaces.IText,
         j01.form.layer.IFormLayer], z3c.form.interfaces.IFieldWidget)
    provideWidgetTemplate('textarea_input.pt',
        j01.form.interfaces.ITextAreaWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('textarea_display.pt',
        j01.form.interfaces.ITextAreaWidget,
        z3c.form.interfaces.DISPLAY_MODE)
    provideWidgetTemplate('textarea_hidden.pt',
        j01.form.interfaces.ITextAreaWidget,
        z3c.form.interfaces.HIDDEN_MODE)

    # textlines
    provideWidgetTemplate('textlines_input.pt',
        j01.form.interfaces.ITextLinesWidget,
        z3c.form.interfaces.INPUT_MODE)
    provideWidgetTemplate('textlines_display.pt',
        j01.form.interfaces.ITextLinesWidget,
        z3c.form.interfaces.DISPLAY_MODE)

    # widget ayout
    fPath = getPath('widget_layout_display.pt')
    layout = z3c.form.widget.WidgetLayoutFactory(fPath, 'text/html')
    zope.interface.directlyProvides(layout,
        z3c.form.interfaces.IWidgetLayoutTemplate)
    zope.component.provideAdapter(layout,
        (None, j01.form.layer.IFormLayer, None, None,
         j01.form.interfaces.IWidget),
        z3c.form.interfaces.IWidgetLayoutTemplate,
        name=z3c.form.interfaces.DISPLAY_MODE)
    fPath = getPath('widget_layout_input.pt')
    layout = z3c.form.widget.WidgetLayoutFactory(fPath, 'text/html')
    zope.interface.directlyProvides(layout,
        z3c.form.interfaces.IWidgetLayoutTemplate)
    zope.component.provideAdapter(layout,
        (None, j01.form.layer.IFormLayer, None, None,
         j01.form.interfaces.IWidget),
        z3c.form.interfaces.IWidgetLayoutTemplate,
        name=z3c.form.interfaces.INPUT_MODE)


def setUp(test=None):
    z3c.form.testing.setUp(test)
    setupFormDefaults()


def tearDown(test=None):
    z3c.form.testing.tearDown(test)
