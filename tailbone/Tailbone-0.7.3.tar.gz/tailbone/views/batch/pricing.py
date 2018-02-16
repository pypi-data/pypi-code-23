# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Views for pricing batches
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from webhelpers2.html import tags

from tailbone.views.batch import BatchMasterView


class PricingBatchView(BatchMasterView):
    """
    Master view for pricing batches.
    """
    model_class = model.PricingBatch
    model_row_class = model.PricingBatchRow
    default_handler_spec = 'rattail.batch.pricing:PricingBatchHandler'
    model_title_plural = "Pricing Batches"
    route_prefix = 'batch.pricing'
    url_prefix = '/batches/pricing'
    template_prefix = '/batch/pricing'
    creatable = False
    bulk_deletable = True
    rows_editable = True
    rows_bulk_deletable = True

    grid_columns = [
        'id',
        'description',
        'created',
        'created_by',
        'rowcount',
        # 'status_code',
        # 'complete',
        'executed',
        'executed_by',
    ]

    form_fields = [
        'id',
        'description',
        'min_diff_threshold',
        'calculate_for_manual',
        'notes',
        'created',
        'created_by',
        'rowcount',
        'executed',
        'executed_by',
    ]

    row_labels = {
        'upc': "UPC",
    }

    row_grid_columns = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'discounted_unit_cost',
        'old_price',
        'new_price',
        'price_margin',
        'price_diff',
        'manually_priced',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'product',
        'upc',
        'brand_name',
        'description',
        'size',
        'department_number',
        'department_name',
        'vendor',
        'regular_unit_cost',
        'discounted_unit_cost',
        'old_price',
        'new_price',
        'price_diff',
        'price_margin',
        'price_markup',
        'status_code',
        'status_text',
    ]

    def configure_row_grid(self, g):
        super(PricingBatchView, self).configure_row_grid(g)

        g.set_type('old_price', 'currency')
        g.set_type('new_price', 'currency')
        g.set_type('price_diff', 'currency')

        g.set_label('upc', "UPC")
        g.set_label('brand_name', "Brand")
        g.set_label('regular_unit_cost', "Reg. Cost")
        g.set_label('price_margin', "Margin")
        g.set_label('price_markup', "Markup")
        g.set_label('price_diff', "Diff")
        g.set_label('manually_priced', "Manual")

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_CANNOT_CALCULATE_PRICE:
            return 'warning'
        if row.status_code in (row.STATUS_PRICE_INCREASE, row.STATUS_PRICE_DECREASE):
            return 'notice'

    def configure_row_form(self, f):
        super(PricingBatchView, self).configure_row_form(f)

        # currency fields
        f.set_type('old_price', 'currency')
        f.set_type('new_price', 'currency')
        f.set_type('price_diff', 'currency')

        # vendor
        f.set_renderer('vendor', self.render_vendor)

    def render_vendor(self, row, field):
        vendor = row.vendor
        if not vendor:
            return ""
        text = "({}) {}".format(vendor.id, vendor.name)
        url = self.request.route_url('vendors.view', uuid=vendor.uuid)
        return tags.link_to(text, url)


def includeme(config):
    PricingBatchView.defaults(config)
