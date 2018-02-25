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
$Id:$
"""
__docformat__ = "reStructuredText"

import datetime

import zope.interface
import zope.component
import zope.i18n
import zope.i18nmessageid

import z3c.form.interfaces
import z3c.form.widget
import z3c.form.browser.widget

from j01.datepicker import UTC
from j01.datepicker import interfaces


_ = zope.i18nmessageid.MessageFactory('p01')


# i18n
DAYS = [
    _('Sunday'),
    _('Monday'),
    _('Tuesday'),
    _('Wednesday'),
    _('Thursday'),
    _('Friday'),
    _('Saturday'),
    _('Sunday'), # yes, that's correct
    ]


DAYS_SHORT = [
    _('Sun'),
    _('Mon'),
    _('Tue'),
    _('Wed'),
    _('Thu'),
    _('Fri'),
    _('Sat'),
    _('Sun'), # yes, that's correct
    ]

DAYS_MIN = [
    _('Su'),
    _('Mo'),
    _('Tu'),
    _('We'),
    _('Th'),
    _('Fr'),
    _('Sa'),
    _('Su'),
    ]

MONTHS = [
    _('January'),
    _('February'),
    _('March'),
    _('April'),
    _('May'),
    _('June'),
    _('July'),
    _('August'),
    _('September'),
    _('October'),
    _('November'),
    _('December'),
    ]

MONTHS_SHORT = [
    _('Jan'),
    _('Feb'),
    _('Mar'),
    _('Apr'),
    _('May'),
    _('Jun'),
    _('Jul'),
    _('Aug'),
    _('Sep'),
    _('Oct'),
    _('Nov'),
    _('Dec'),
    ]


# l10n
# provide date format pattern translation
defaultDateFormatPattern = u'MM.dd.yyyy'
defaultDatePickerFormatPattern = u'mm.dd.yyyy'

# suported date formats
# we will ensure that we only support and use the follwing date formats
# any other format is not supported
dateLocales = {
    'dd.MM.yyyy': _(u'dd.mm.yyyy'),
    'dd/MM/yyyy': _(u'dd/mm/yyyy'),
    'dd-MM-yyyy': _(u'dd-mm-yyyy'),
    'MM.dd.yyyy': _(u'mm.dd.yyyy'),
    'MM/dd/yyyy': _(u'mm/dd/yyyy'),
    'MM-dd-yyyy': _(u'mm-dd-yyyy'),
}


def getDateFormatPattern(pattern):
    if pattern in dateLocales:
        return pattern
    elif pattern is not None and pattern.lower().startswith('d'):
        return 'dd.MM.yyyy'
    else:
        return defaultDateFormatPattern


def getDatePickerFormatPattern(pattern):
    """Return the datepicker format based on the given pattern"""
    if pattern in dateLocales:
        pattern = pattern.replace('MM', 'mm')
    elif pattern is not None and pattern.lower().startswith('d'):
        pattern = u'dd.mm.yyyy'
    else:
        pattern = defaultDatePickerFormatPattern
    return pattern


# javascript
J01_DATEPICKER_JAVASCRIPT = """
<script type="text/javascript">
;(function($){
  	$.fn.datepicker.dates['%(language)s'] = {%(dates)s};
    $("%(expression)s").datepicker({%(settings)s});
}(jQuery));
</script>
"""


def j01DatePickerJavaScript(j01DatePickerExpression, data):
    """DatePicker JavaScript generator

    //simple date picker widget script
    ;(function($){
        $.fn.datepicker.dates['en'] = {
        daysShort: ["Sun","Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
        today: "today",
        format: "mm.dd.yyyy",
        daysMin: ["Su","Mo","Tu","We","Th","Fr","Sa","Su"],
        weekStart: "0",
        clear: "remove",
        months: ["January","February","March","April","May","..."],
        days: ["Sunday","Monday","Tuesday","Wednesday","Thursday","..."],
        monthsShort: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","..."]};
    }(jQuery));
    $(document).ready(function(){
        $("#widget\\.id").datepicker({
        startDate: -Infinity,
        endDate: Infinity,
        language: "en",
        format: "mm.dd.yyyy"});
    });

    """
    # settings
    lines = []
    append = lines.append
    for key, value in data.items():
        if key in ['dates']:
            # skip locale and dates
            continue

        # skip default values
        elif key == 'autoclose' and value is False:
            # skip default container
            continue
        elif key in ['beforeShowDay', 'beforeShowMonth', 'beforeShowYear'] and \
            value == '$.noop':
            # skip default container
            continue
        elif key == 'calendarWeeks' and value is False:
            # skip default container
            continue
        elif key == 'clearBtn' and value is False:
            # skip default container
            continue
        elif key == 'container' and value == 'body':
            # skip default container
            continue
        elif key == 'disableTouchKeyboard' and value is False:
            # skip default container
            continue
        elif key == 'defaultViewDate' and value == 'today':
            # skip default container
            continue
        elif key == 'enableOnReadonly' and value is True:
            # skip default container
            continue
        elif key == 'forceParse' and value is True:
            # skip default container
            continue
        elif key == 'immediateUpdates' and value is False:
            # skip default container
            continue
        elif key == 'keyboardNavigation' and value is True:
            # skip default container
            continue
        elif key == 'maxViewMode' and value == 2:
            # skip default container
            continue
        elif key == 'minViewMode' and value == 0:
            # skip default container
            continue
        elif key == 'multidate' and value is False:
            # skip default container
            continue
        elif key == 'multidateSeparator' and value == ',':
            # skip default container
            continue
        elif key == 'orientation' and value == 'auto':
            # skip default container
            continue
        elif key == 'rtl' and value is False:
            # skip default container
            continue
        elif key == 'showOnFocus' and value is True:
            # skip default container
            continue
        elif key == 'startView' and value == 0:
            # skip default container
            continue
        elif key == 'todayBtn' and value is False:
            # skip default container
            continue
        elif key == 'todayHighlight' and value is False:
            # skip default container
            continue
        elif key == 'title' and not value:
            # skip default container
            continue
        elif key == 'toggleActive' and value is False:
            # skip default container
            continue
        elif key == 'weekStart' and value == 0:
            # skip default container
            continue
        elif key == 'zIndexOffset' and value == 10:
            # skip default container
            continue

        # complex values
        elif key == 'datesDisabled':
            l = ["\"%s\"" % v for v in value]
            if l:
                append("\n    datesDisabled: [%s]" % ','.join(l))
        elif key in ['datesDisabled', 'daysOfWeekDisabled',
                     'daysOfWeekHighlighted']:
            l = ["\"%s\"" % v for v in value]
            if l:
                append("\n    %s: [%s]" % (key, ','.join(l)))
        elif key in ['beforeShowDay', 'beforeShowMonth', 'beforeShowYear']:
            append("\n    %s: %s" % (key, value))
        elif key in ['startDate', 'endDate']:
            if value in ['Infinity', '-Infinity']:
                append("\n    %s: %s" % (key, value))
            else:
                append("\n    %s: '%s'" % (key, value))
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
    # dates
    dates = []
    append = dates.append
    for key, value in data['dates'].items():
        if key in ['days', 'daysShort', 'daysMin', 'months', 'monthsShort']:
            l = ["\"%s\"" % v for v in value]
            append("\n    %s: [%s]" % (key, ','.join(l)))
        elif isinstance(value, int):
            append("\n    %s: \"%s\"" % (key, value))
        elif isinstance(value, (str, unicode)):
            append("\n    %s: \"%s\"" % (key, value))
        else:
            append("\n    %s: %s" % (key, value))

    return J01_DATEPICKER_JAVASCRIPT % ({
        'expression': j01DatePickerExpression,
        'language': data["language"],
        'dates': ','.join(dates),
        'settings': settings,
        })


# date widget
class DatePickerWidget(z3c.form.browser.widget.HTMLTextInputWidget,
    z3c.form.widget.Widget):
    """Upload widget implementation."""

    zope.interface.implementsOnly(interfaces.IDatePickerWidget)

    value = u''

    klass = u'j01DatePickerWidget'
    css = u'j01-datepicker'

    formatterLength = 'medium'

    # timeAppendix is only used in datetime convert for correct the appended
    # time. see: DatePickerForDatetimeConverter for more info
    # We can use startDate = '00:00:00' and endDate = '23:59:59'
    # this will make sure we have almost a full day stored between startDate
    # and endDate but at the same time we can show the same date value
    timeAppendix = '00:00:00'
    territory = None
    skipPastDates = False
    skipFutureDates = False

    # config
    autoclose = True
    beforeShowDay = '$.noop'
    beforeShowMonth = '$.noop'
    beforeShowYear = '$.noop'
    calendarWeeks = False
    clearBtn = False
    container = 'body'
    datesDisabled = []
    daysOfWeekDisabled = []
    daysOfWeekHighlighted = []
    defaultViewDate = 'today'
    disableTouchKeyboard = False
    enableOnReadonly = True
    forceParse = True
    immediateUpdates = False
    keyboardNavigation = True
    language = 'en'
    maxViewMode = 2
    minViewMode = 0
    multidate = False
    multidateSeparator = ','
    orientation = 'auto'
    showOnFocus = True
    rtl = False
    startView = 0
    todayBtn = False
    todayHighlight = True
    toggleActive = False
    weekStart = 0
    zIndexOffset = 10

    _label = None
    appendLabelDatePattern = True

    def translate(self, msg):
        return zope.i18n.translate(msg, context=self.request)

    def getLabel(self):
        if self.appendLabelDatePattern:
            # translate and append date pattern to label
            label = self.translate(self._label)
            i18n = dateLocales.get(self.dateFormatPattern)
            pattern = self.translate(i18n)
            return '%s (%s)' % (label, pattern)
        else:
            # return plain label
            return self._label

    @apply
    def label():
        def fget(self):
            return self.getLabel()
        def fset(self, value):
            # set plain field title as value
            self._label = value
        return property(fget, fset)

    @property
    def tzinfo(self):
        return UTC

    @property
    def dateFormatPattern(self):
        return getDateFormatPattern(self.pattern)

    @property
    def datePickerFormatPattern(self):
        return getDatePickerFormatPattern(self.pattern)

    # dates
    @property
    def days(self):
        return [self.translate(d) for d in DAYS]

    @property
    def daysShort(self):
        return [self.translate(d) for d in DAYS_SHORT]

    @property
    def daysMin(self):
        return [self.translate(d) for d in DAYS_MIN]

    @property
    def months(self):
        return [self.translate(d) for d in MONTHS]

    @property
    def monthsShort(self):
        return [self.translate(d) for d in MONTHS_SHORT]

    @property
    def today(self):
        return zope.i18n.translate(_(u"today"), context=self.request)

    @property
    def clear(self):
        return zope.i18n.translate(_(u"remove"), context=self.request)

    @property
    def language(self):
        # the language is not really important, it's just used as a namespace
        # for our translated date strings
        lang = self.request.locale.id.language
        return lang and lang or 'en'

    @property
    def startDate(self):
        if self.skipPastDates:
            today = datetime.date.today()
            locale = self.request.locale
            formatter = locale.dates.getFormatter('date', self.formatterLength)
            return formatter.format(today, self.dateFormatPattern)
        else:
            return '-Infinity'

    @property
    def endDate(self):
        if self.skipFutureDates:
            today = datetime.date.today()
            locale = self.request.locale
            formatter = locale.dates.getFormatter('date', self.formatterLength)
            return formatter.format(today, self.dateFormatPattern)
        else:
            return 'Infinity'

    @property
    def dates(self):
        return {
            'days': self.days,
            'daysShort': self.daysShort,
            'daysMin': self.daysMin,
            'months': self.months,
            'monthsShort': self.monthsShort,
            'today': self.today,
            'clear': self.clear,
            'weekStart': self.weekStart,
            'format': self.datePickerFormatPattern,
            }

    @property
    def j01DatePickerExpression(self):
        return '#%s' % self.id.replace('.', '\\\.')

    @property
    def javascript(self):
        data = {
            'autoclose': self.autoclose,
            'beforeShowDay': self.beforeShowDay,
            'beforeShowMonth': self.beforeShowMonth,
            'beforeShowYear': self.beforeShowYear,
            'calendarWeeks': self.calendarWeeks,
            'clearBtn': self.clearBtn,
            'container': self.container,
            'dates': self.dates,
            'datesDisabled': self.datesDisabled,
            'daysOfWeekDisabled': self.daysOfWeekDisabled,
            'daysOfWeekHighlighted': self.daysOfWeekHighlighted,
            'defaultViewDate': self.defaultViewDate,
            'disableTouchKeyboard': self.disableTouchKeyboard,
            'enableOnReadonly': self.enableOnReadonly,
            'endDate': self.endDate,
            'forceParse': self.forceParse,
            'format': self.datePickerFormatPattern,
            'immediateUpdates': self.immediateUpdates,
            'keyboardNavigation': self.keyboardNavigation,
            'language': self.language,
            'maxViewMode': self.maxViewMode,
            'minViewMode': self.minViewMode,
            'multidate': self.multidate,
            'multidateSeparator': self.multidateSeparator,
            'orientation': self.orientation,
            'showOnFocus': self.showOnFocus,
            'rtl': self.rtl,
            'startDate': self.startDate,
            'startView': self.startView,
            'todayBtn': self.todayBtn,
            'todayHighlight': self.todayHighlight,
            'toggleActive': self.toggleActive,
            'weekStart': self.weekStart,
            'zIndexOffset': self.zIndexOffset,
		    }
        return j01DatePickerJavaScript(self.j01DatePickerExpression, data)

    def update(self):
        """Will setup the script attribute."""
        # setup formatter pattern given from request via converter
        converter = zope.component.queryMultiAdapter((self.field, self),
            z3c.form.interfaces.IDataConverter)
        self.pattern = converter.formatter.getPattern()
        # update widget and converter which uses our own formatter pattern
        super(DatePickerWidget, self).update()


def getDatePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    return z3c.form.widget.FieldWidget(field, DatePickerWidget(request))


def getStartDatePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    # this widget uses the default timeAppendix settings '00:00:00'
    # and prevents selecting previous dates
    widget = DatePickerWidget(request)
    widget.skipPastDates = True
    return z3c.form.widget.FieldWidget(field, widget)


def getEndDatePickerWidget(field, request):
    """IFieldWidget factory for ItemsWidget."""
    # this widget uses the default timeAppendix settings '23:59:59'
    # and prevents selecting previous dates
    widget = DatePickerWidget(request)
    widget.timeAppendix = '23:59:59'
    widget.skipPastDates = True
    return z3c.form.widget.FieldWidget(field, widget)
