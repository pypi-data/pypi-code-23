# -*- coding: utf-8 -*-
from eea.facetednavigation import EEAMessageFactory as EEAMF
from eea.facetednavigation.widgets.widget import Widget as AbstractWidget
from eea.facetednavigation.widgets.daterange import widget
from Products.Archetypes.public import Schema
from Products.Archetypes.public import StringField
from Products.Archetypes.public import SelectionWidget

import logging

from collective.faceted.datewidget import _


logger = logging.getLogger('collective.faceted.datewidget.daterange')

EditSchema = Schema((
    StringField(
        'index',
        schemata="default",
        required=True,
        vocabulary_factory='eea.faceted.vocabularies.DateRangeCatalogIndexes',
        widget=SelectionWidget(
            format='select',
            label=_(u'Catalog index (begin date)'),
            description=EEAMF(u'Catalog index to use for search'),
            i18n_domain='collective.faceted.datewidget',
        )
    ),
    StringField(
        'index_end',
        schemata="default",
        required=True,
        vocabulary_factory='eea.faceted.vocabularies.DateRangeCatalogIndexes',
        widget=SelectionWidget(
            format='select',
            label=_(u'Catalog index (end date)'),
            description=EEAMF(u'Catalog index to use for search'),
            i18n_domain='collective.faceted.datewidget',
        )
    ),
))


class Widget(widget.Widget):
    """
    Date Range Custom widget
    """
    # Widget properties
    widget_type = 'daterangecustom'
    widget_label = _('Date range (begin/end)')

    edit_schema = AbstractWidget.edit_schema.copy() + widget.EditSchema.copy() + EditSchema.copy()  # NOQA

    @property
    def css_class(self):
        """
        Override of css_class property to inherit from daterange widget CSS
        """
        css = super(Widget, self).css_class
        return 'faceted-daterange-widget {0}'.format(css)

    def query(self, form):
        query = {}
        index_begin = self.get_index('index')
        index_end = self.get_index('index_end')
        if not (index_begin and index_end):
            return query

        if self.hidden:
            start, end = self.default
        else:
            value = form.get(self.data.getId(), ())
            if not value or len(value) != 2:
                return query
            start, end = value
        start, end = start.replace('/', '-'), end.replace('/', '-')
        # be sure years are 0padded & 4 digits
        # this to allow very old years to be entered up
        bounds = {'start': start, 'end': end}
        for sbound in bounds:
            bound = bounds[sbound]
            parts = bound.split('-')
            if len(parts) == 3:
                year, month, day = parts
                ypadding = 4 - len(year)
                mpadding = 2 - len(month)
                dpadding = 2 - len(day)
                bounds[sbound] = '%s-%s-%s' % (
                    '0' * ypadding + year,
                    '0' * mpadding + month,
                    '0' * dpadding + day,
                )

        start, end = bounds['start'], bounds['end']

        if not (start and end):
            return query

        try:
            # give datetime.datetime to allow very old or big years
            # not to be transformed in current years (eg: 0001 -> 1901)
            start = widget.formated_time(start)
            end = widget.formated_time(end)
        except Exception, err:
            logger.exception(err)
            return query

        start = start - 1
        start = start.latestTime()
        end = end.latestTime()

        query[index_begin] = {
            'query': end,
            'range': 'max'
        }
        query[index_end] = {
            'query': start,
            'range': 'min'
        }

        return query

    def get_index(self, indexname):
        return self.data.get(indexname, '').encode('utf-8', 'replace')
