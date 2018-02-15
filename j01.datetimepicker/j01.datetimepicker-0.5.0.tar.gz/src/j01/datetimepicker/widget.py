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
$Id: widget.py 4753 2018-02-15 04:53:17Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import datetime

import zope.interface
import zope.component
import zope.i18n
import zope.i18nmessageid
import zope.i18n.format

import z3c.form.interfaces
import z3c.form.converter
import z3c.form.widget
import z3c.form.browser.widget

from j01.datetimepicker import UTC
from j01.datetimepicker import interfaces


_ = zope.i18nmessageid.MessageFactory('p01')


_marker = object()


##############################################################################
#
# i18n

TOOLTIPS = {
    'today': _('Go to today'),
    'clear': _('Clear selection'),
    'close': _('Close the picker'),
    'selectMonth': _('Select Month'),
    'prevMonth': _('Previous Month'),
    'nextMonth': _('Next Month'),
    'selectYear': _('Select Year'),
    'prevYear': _('Previous Year'),
    'nextYear': _('Next Year'),
    'selectDecade': _('Select Decade'),
    'prevDecade': _('Previous Decade'),
    'nextDecade': _('Next Decade'),
    'prevCentury': _('Previous Century'),
    'nextCentury': _('Next Century'),
    'incrementHour': _('Increment Hour'),
    'pickHour': _('Pick Hour'),
    'decrementHour': 'Decrement Hour',
    'incrementMinute': _('Increment Minute'),
    'pickMinute': _('Pick Minute'),
    'decrementMinute': 'Decrement Minute',
    'incrementSecond': _('Increment Second'),
    'pickSecond': _('Pick Second'),
    'decrementSecond': _('Decrement Second'),
    }


##############################################################################
#
# l10n

# known patterns
I18N_PATTERN_MESSAGES = {
    # python format: i18n label
    # de, medium
    _('dd.MM.yyyy HH:mm:ss'),
    # fr medium
    _('d MMM yy HH:mm:ss'),
    # it medium
    _('dd/MMM/yy HH:mm:ss'),
    # en medium
    _('MMM d, yyyy h:mm:ss a'),
}
I18N_PATTERNS = {}
for msgid in I18N_PATTERN_MESSAGES:
    I18N_PATTERNS[str(msgid)] = msgid


##############################################################################
#
# defaults

class DateTimePickerDefaults(object):
    """DateTimePicker default values"""

    # datetimepicker options
    format = False
    dayViewHeaderFormat = 'MMMM YYYY'
    extraFormats = None
    stepping = 1
    minDate = False
    maxDate = False
    useCurrent = True
    collapse = True
    locale = None
    defaultDate = False
    disabledDates = False
    enabledDates = False
    icons = {
        'time': 'glyphicon glyphicon-time',
        'date': 'glyphicon glyphicon-calendar',
        'up': 'glyphicon glyphicon-chevron-up',
        'down': 'glyphicon glyphicon-chevron-down',
        'previous': 'glyphicon glyphicon-chevron-left',
        'next': 'glyphicon glyphicon-chevron-right',
        'today': 'glyphicon glyphicon-screenshot',
        'clear': 'glyphicon glyphicon-trash',
        'close': 'glyphicon glyphicon-remove',
    }
    useStrict = False
    sideBySide = False
    daysOfWeekDisabled = []
    calendarWeeks = False
    viewMode = 'days'
    toolbarPlacement = 'default'
    showTodayButton = False
    showClear = False
    showClose = False
    widgetPositioning = {
        'horizontal': 'auto',
        'vertical': 'auto',
    }
    widgetParent = None
    keepOpen = False
    inline = False
    keepInvalid = False
    # keyBinds = None # not defined, use custom javascript if you need this
    debug = False
    ignoreReadonly = False
    disabledTimeIntervals = False
    allowInputToggle = False
    focusOnShow = True
    enabledHours = False
    disabledHours = False
    viewDate = False
    tooltips = TOOLTIPS


##############################################################################
#
# javascript

J01_DATEPICKER_JAVASCRIPT = """
<script type="text/javascript">
    $("%(expression)s").datetimepicker({%(settings)s});
</script>
"""


def j01DateTimePickerJavaScript(j01DateTimePickerExpression, data):
    """DateTimePicker JavaScript generator"""
    # settings
    lines = []
    append = lines.append
    for key, value in data.items():

        default = getattr(DateTimePickerDefaults, key, _marker)
        if value is _marker or value == default:
            continue

        if key in ['dates']:
            # skip locale and dates
            continue

        # complex values
        elif key == 'daysOfWeekDisabled':
            l = ["\"%s\"" % v for v in value]
            if l:
                append("\n    daysOfWeekDisabled: [%s]" % ','.join(l))
        elif key in ['icons', 'widgetPositioning', 'tooltips']:
            l = ["%s: \"%s\"" % v for v in value.items()]
            if l:
                v = "\n    %s: {" % key
                v += "\n         %s" % ','.join(l)
                v += "\n    }"
                append(v)
        # generic values
        elif value is True:
            append("\n    %s: true" % key)
        elif value is False:
            append("\n    %s: false" % key)
        elif value is None:
            append("\n    %s: null" % key)
        elif isinstance(value, int):
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, (str, unicode)):
            append("\n    %s: \"%s\"" % (key, value))
        else:
            append("\n    %s: %s" % (key, value))
    settings = ','.join(lines)

    return J01_DATEPICKER_JAVASCRIPT % ({
        'expression': j01DateTimePickerExpression,
        'settings': settings,
        })


##############################################################################
#
# datetime widget

class DateTimePickerWidget(DateTimePickerDefaults,
    z3c.form.browser.widget.HTMLTextInputWidget, z3c.form.widget.Widget):
    """Upload widget implementation."""

    zope.interface.implementsOnly(interfaces.IDateTimePickerWidget)

    formatter = None
    value = u''

    klass = u'j01DateTimePickerWidget'
    css = u'j01-datetimepicker'

    _label = None
    showLabel = True
    showClose = True

    # converter formatter length
    formatterLength = 'medium'
    appendLabelDateTimePattern = True

    # fontawasome icons
    icons = {
        'time': 'far fa-clock',
        'date': 'far fa-calendar-alt',
        'up': 'fas fa-chevron-up',
        'down': 'fas fa-chevron-down',
        'previous': 'fas fa-chevron-left',
        'next': 'fas fa-chevron-right',
        'today': 'far fa-calendar-times',
        'clear': 'fas fa-trash',
        'close': 'far fa-minus-square',
    }

    @property
    def locale(self):
        lang = self.request.locale.id.language
        return lang and lang or 'en'

    # converter helper
    def setUpFormatter(self):
        self.formatter = self.request.locale.dates.getFormatter(
            'dateTime', self.formatterLength)
        self.pattern = self.formatter.getPattern()


    def getWidgetPattern(self, pattern):
        """Replace python pattern to widget (moment.js) pattern.

        See: http://momentjs.com/docs/#/parsing/ for pattern info.
        """
        # yyyy -> YYYY
        pattern = pattern.replace('y', 'Y')
        # dd -> DD
        pattern = pattern.replace('dd', 'DD')
        # d -> DD, can't set single day, use DD
        pattern = pattern.replace('d', 'DD')
        return pattern

    @property
    def format(self):
        """Formatter pattern"""
        return self.getWidgetPattern(self.pattern)

    @property
    def tzinfo(self):
        """Timzone info

        NOTE: implement your own timezone lookup concept based on ITZInfo
        adapter, member timezone or other request based lookup.
        """
        return UTC

    # converter methods
    def getWidgetValue(self, value):
        # format based on the widgets settings
        return self.formatter.format(value, self.pattern)

    def getTimezoneAwareValue(self, value):
        """Adjust timezone for given datetime value"""
        try:
            # as timezone if teimzone aware datetime
            return value.astimezone(self.tzinfo)
        except ValueError:
            # naive datetime, set UTC and then replace with given timezone
            value = value.replace(tzinfo=UTC)
            return value.replace(tzinfo=self.tzinfo)

    def getFieldValue(self, value):
        if value is not None:
            # convert am, pm to uppercase
            value = value.replace('am', 'AM')
            value = value.replace('pm', 'PM')
        try:
            # parse based on the widgets settings
            dt = self.formatter.parse(value, pattern=self.pattern)
            return self.getTimezoneAwareValue(dt)
        except zope.i18n.format.DateTimeParseError, err:
            try:
                self.formatter.format(value, self.pattern)
            except zope.i18n.format.DateTimeParseError, err:
                raise z3c.form.converter.FormatterValidationError(err.args[0],
                    value)

    # widget rendering
    def getWidgetLabelPattern(self, pattern):
        """Generic pattern translation"""
        try:
            msg = I18N_PATTERNS[pattern]
            pattern = zope.i18n.translate(msg, context=self.request)
        except KeyError:
            pass
        return pattern

    def getWidgetLabel(self):
        if self.appendLabelDateTimePattern:
            # translate and append date pattern to label
            label = zope.i18n.translate(self._label, context=self.request)
            pattern = self.getWidgetLabelPattern(self.pattern)
            return '%s (%s)' % (label, pattern)
        else:
            # return plain label
            return self._label

    @apply
    def label():
        def fget(self):
            return self.getWidgetLabel()
        def fset(self, value):
            # set plain field title as value
            self._label = value
        return property(fget, fset)

    # javascript
    @property
    def j01DateTimePickerExpression(self):
        return '#%s' % self.id.replace('.', '\\\.')

    @property
    def javascript(self):
        data = {
            'format': self.format,
            'dayViewHeaderFormat': self.dayViewHeaderFormat,
            'extraFormats': self.extraFormats,
            'stepping': self.stepping,
            'minDate': self.minDate,
            'maxDate': self.maxDate,
            'useCurrent': self.useCurrent,
            'collapse': self.collapse,
            'locale': self. locale,
            'defaultDate': self.defaultDate,
            'disabledDates': self.disabledDates,
            'enabledDates': self.enabledDates,
            'icons': self.icons,
            'useStrict': self.useStrict,
            'sideBySide': self.sideBySide,
            'daysOfWeekDisabled': self.daysOfWeekDisabled,
            'calendarWeeks': self.calendarWeeks,
            'viewMode': self.viewMode,
            'toolbarPlacement': self.toolbarPlacement,
            'showTodayButton': self.showTodayButton,
            'showClear': self.showClear,
            'showClose': self.showClose,
            'widgetPositioning': self.widgetPositioning,
            'widgetParent': self.widgetParent,
            'keepOpen': self.keepOpen,
            'inline': self.inline,
            'keepInvalid': self.keepInvalid,
            'debug': self.debug,
            'ignoreReadonly': self.ignoreReadonly,
            'disabledTimeIntervals': self.disabledTimeIntervals,
            'allowInputToggle': self.allowInputToggle,
            'focusOnShow': self.focusOnShow,
            'enabledHours': self.enabledHours,
            'disabledHours': self.disabledHours,
            'viewDate': self.viewDate,
            'tooltips': self.tooltips,
        }
        return j01DateTimePickerJavaScript(self.j01DateTimePickerExpression, data)

    def update(self):
        self.setUpFormatter()
        super(DateTimePickerWidget, self).update()


def getDateTimePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    return z3c.form.widget.FieldWidget(field, DateTimePickerWidget(request))
