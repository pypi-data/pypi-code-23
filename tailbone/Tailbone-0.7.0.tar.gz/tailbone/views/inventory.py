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
Views for inventory batches
"""

from __future__ import unicode_literals, absolute_import

import re
import decimal

import six

from rattail import pod
from rattail.db import model, api
from rattail.time import localtime
from rattail.gpc import GPC
from rattail.util import pretty_quantity

import colander
import formencode as fe
from deform import widget as dfwidget
from webhelpers2.html import HTML, tags

from tailbone import forms, forms2, grids
from tailbone.views import MasterView
from tailbone.views.batch import BatchMasterView


class InventoryAdjustmentReasonsView(MasterView):
    """
    Master view for inventory adjustment reasons.
    """
    model_class = model.InventoryAdjustmentReason
    route_prefix = 'invadjust_reasons'
    url_prefix = '/inventory-adjustment-reasons'

    grid_columns = [
        'code',
        'description',
    ]

    def configure_form(self, f):
        super(InventoryAdjustmentReasonsView, self).configure_form(f)

        # code
        f.set_validator('code', self.unique_code)

    def unique_code(self, node, value):
        query = self.Session.query(model.InventoryAdjustmentReason)\
                            .filter(model.InventoryAdjustmentReason.code == value)
        if self.editing:
            reason = self.get_instance()
            query = query.filter(model.InventoryAdjustmentReason.uuid != reason.uuid)
        if query.count():
            raise colander.Invalid(node, "Code must be unique")


class InventoryBatchView(BatchMasterView):
    """
    Master view for inventory batches.
    """
    model_class = model.InventoryBatch
    model_title_plural = "Inventory Batches"
    default_handler_spec = 'rattail.batch.inventory:InventoryBatchHandler'
    route_prefix = 'batch.inventory'
    url_prefix = '/batch/inventory'
    index_title = "Inventory"
    creatable = False
    results_executable = True
    mobile_creatable = True
    mobile_rows_creatable = True

    labels = {
        'mode': "Count Mode",
    }

    grid_columns = [
        'id',
        'created',
        'created_by',
        'description',
        'mode',
        'rowcount',
        'total_cost',
        'executed',
        'executed_by',
    ]

    form_fields = [
        'id',
        'description',
        'created',
        'created_by',
        'handheld_batches',
        'mode',
        'reason_code',
        'total_cost',
        'rowcount',
        'complete',
        'executed',
        'executed_by',
    ]

    mobile_form_fields = [
        'mode',
        'reason_code',
        'rowcount',
        'complete',
        'executed',
        'executed_by',
    ]

    model_row_class = model.InventoryBatchRow
    rows_editable = True

    row_labels = {
        'upc': "UPC",
        'previous_units_on_hand': "Prev. On Hand",
    }

    row_grid_columns = [
        'sequence',
        'upc',
        'item_id',
        'brand_name',
        'description',
        'size',
        'previous_units_on_hand',
        'cases',
        'units',
        'unit_cost',
        'total_cost',
        'status_code',
    ]

    row_form_fields = [
        'sequence',
        'upc',
        'brand_name',
        'description',
        'size',
        'status_code',
        'previous_units_on_hand',
        'case_quantity',
        'cases',
        'units',
        'unit_cost',
        'total_cost',
    ]

    def configure_grid(self, g):
        super(InventoryBatchView, self).configure_grid(g)

        # mode
        g.set_enum('mode', self.enum.INVENTORY_MODE)
        g.filters['mode'].set_value_renderer(
            grids.filters.EnumValueRenderer(self.enum.INVENTORY_MODE))

        # total_cost
        g.set_type('total_cost', 'currency')

    def render_mobile_listitem(self, batch, i):
        return "({}) {} rows - {}, {}".format(
            batch.id_str,
            "?" if batch.rowcount is None else batch.rowcount,
            batch.created_by,
            localtime(self.request.rattail_config, batch.created, from_utc=True).strftime('%Y-%m-%d'))

    def editable_instance(self, batch):
        return True

    def mutable_batch(self, batch):
        return not batch.executed and not batch.complete and batch.mode != self.enum.INVENTORY_MODE_ZERO_ALL

    def allow_worksheet(self, batch):
        return self.mutable_batch(batch)

    def get_available_modes(self):
        permission_prefix = self.get_permission_prefix()
        modes = dict(self.enum.INVENTORY_MODE)
        if not self.request.has_perm('{}.create.replace'.format(permission_prefix)):
            if hasattr(self.enum, 'INVENTORY_MODE_REPLACE'):
                modes.pop(self.enum.INVENTORY_MODE_REPLACE, None)
            if hasattr(self.enum, 'INVENTORY_MODE_REPLACE_ADJUST'):
                modes.pop(self.enum.INVENTORY_MODE_REPLACE_ADJUST, None)
        if not self.request.has_perm('{}.create.zero'.format(permission_prefix)):
            if hasattr(self.enum, 'INVENTORY_MODE_ZERO_ALL'):
                modes.pop(self.enum.INVENTORY_MODE_ZERO_ALL, None)
        return modes

    def configure_form(self, f):
        super(InventoryBatchView, self).configure_form(f)

        # mode
        modes = self.get_available_modes()
        f.set_enum('mode', modes)
        f.set_label('mode', "Count Mode")
        if len(modes) == 1:
            f.set_readonly('mode')

        # total_cost
        if self.creating:
            f.remove_field('total_cost')
        else:
            f.set_readonly('total_cost')
            f.set_type('total_cost', 'currency')

        # handheld_batches
        f.set_readonly('handheld_batches')
        f.set_renderer('handheld_batches', self.render_handheld_batches)

    def render_handheld_batches(self, inventory_batch, field):
        items = ''
        for handheld in inventory_batch._handhelds:
            text = handheld.handheld.id_str
            url = self.request.route_url('batch.handheld.view', uuid=handheld.handheld_uuid)
            items += HTML.tag('li', c=tags.link_to(text, url))
        return HTML.tag('ul', c=items)

    def row_editable(self, row):
        return self.mutable_batch(row.batch)

    def row_deletable(self, row):
        return self.mutable_batch(row.batch)

    def save_edit_row_form(self, form):
        row = form.model_instance
        batch = row.batch
        if batch.total_cost is not None and row.total_cost is not None:
            batch.total_cost -= row.total_cost
        return super(InventoryBatchView, self).save_edit_row_form(form)

    def delete_row(self):
        row = self.Session.query(model.InventoryBatchRow).get(self.request.matchdict['uuid'])
        if not row:
            raise self.notfound()
        batch = row.batch
        if batch.total_cost is not None and row.total_cost is not None:
            batch.total_cost -= row.total_cost
        return super(InventoryBatchView, self).delete_row()

    def configure_mobile_form(self, f):
        super(InventoryBatchView, self).configure_mobile_form(f)
        batch = f.model_instance

        # mode
        modes = self.get_available_modes()
        f.set_enum('mode', modes)
        mode_values = [(k, v) for k, v in sorted(modes.items())]
        f.set_widget('mode', forms2.widgets.PlainSelectWidget(values=mode_values))

        # complete
        if self.creating or batch.executed or not batch.complete:
            f.remove_field('complete')

    # TODO: document this, maybe move it etc.
    unknown_product_creates_row = True

    # TODO: this view can create new rows, with only a GET query.  that should
    # probably be changed to require POST; for now we just require the "create
    # batch row" perm and call it good..
    def mobile_row_from_upc(self):
        """
        Locate and/or create a row within the batch, according to the given
        product UPC, then redirect to the row view page.
        """
        batch = self.get_instance()
        row = None
        upc = self.request.GET.get('upc', '').strip()
        upc = re.sub(r'\D', '', upc)
        if upc:

            if len(upc) <= 14:
                row = self.add_row_for_upc(batch, upc)
                if not row:
                    self.request.session.flash("Product not found: {}".format(upc), 'error')
                    return self.redirect(self.get_action_url('view', batch, mobile=True))

            else:
                self.request.session.flash("UPC has too many digits ({}): {}".format(len(upc), upc), 'error')
                return self.redirect(self.get_action_url('view', batch, mobile=True))

        self.Session.flush()
        return self.redirect(self.mobile_row_route_url('view', uuid=row.batch_uuid, row_uuid=row.uuid))

    def add_row_for_upc(self, batch, upc):
        """
        Add a row to the batch for the given UPC, if applicable.
        """
        # try to locate general product by UPC; add to batch either way
        provided = GPC(upc, calc_check_digit=False)
        checked = GPC(upc, calc_check_digit='upc')
        product = api.get_product_by_upc(self.Session(), provided)
        if not product:
            product = api.get_product_by_upc(self.Session(), checked)
        if product or self.unknown_product_creates_row:
            row = model.InventoryBatchRow()
            if product:
                row.product = product
                row.upc = product.upc
            else:
                row.upc = provided # TODO: why not 'checked' instead? how to choose?
                row.description = "(unknown product)"
            self.handler.add_row(batch, row)
            return row

    def template_kwargs_view_row(self, **kwargs):
        row = kwargs['instance']
        kwargs['product_image_url'] = pod.get_image_url(self.rattail_config, row.upc)
        return kwargs

    def get_batch_kwargs(self, batch, mobile=False):
        kwargs = super(InventoryBatchView, self).get_batch_kwargs(batch, mobile=False)
        kwargs['mode'] = batch.mode
        kwargs['complete'] = False
        kwargs['reason_code'] = batch.reason_code
        return kwargs

    def get_mobile_row_data(self, batch):
        # we want newest on top, for inventory batch rows
        return self.get_row_data(batch)\
                   .order_by(self.model_row_class.sequence.desc())

    # TODO: ugh, the hackiness.  needs a refactor fo sho
    def mobile_view_row(self):
        """
        Mobile view for inventory batch rows.  Note that this also handles
        updating a row...ugh.
        """
        self.viewing = True
        row = self.get_row_instance()
        parent = self.get_parent(row)
        form = self.make_mobile_row_form(row)
        context = {
            'row': row,
            'instance': row,
            'instance_title': self.get_row_instance_title(row),
            'parent_model_title': self.get_model_title(),
            'parent_title': self.get_instance_title(parent),
            'parent_url': self.get_action_url('view', parent, mobile=True),
            'product_image_url': pod.get_image_url(self.rattail_config, row.upc),
            'form': form,
        }

        if self.request.has_perm('{}.edit_row'.format(self.get_permission_prefix())):
            update_form = forms.SimpleForm(self.request, schema=InventoryForm)
            if update_form.validate():
                row = update_form.data['row']
                cases = update_form.data['cases']
                units = update_form.data['units']
                if cases:
                    row.cases = cases
                    row.units = None
                elif units:
                    row.cases = None
                    row.units = units
                self.handler.refresh_row(row)
                return self.redirect(self.request.route_url('mobile.{}.view'.format(self.get_route_prefix()), uuid=row.batch_uuid))

        return self.render_to_response('view_row', context, mobile=True)

    def get_row_instance_title(self, row):
        if row.upc:
            return row.upc.pretty()
        if row.item_id:
            return row.item_id
        return "row {}".format(row.sequence)

    def configure_row_grid(self, g):
        super(InventoryBatchView, self).configure_row_grid(g)

        # quantity fields
        g.set_type('previous_units_on_hand', 'quantity')
        g.set_type('cases', 'quantity')
        g.set_type('units', 'quantity')

        # currency fields
        g.set_type('unit_cost', 'currency')
        g.set_type('total_cost', 'currency')

        # short labels
        g.set_label('brand_name', "Brand")
        g.set_label('status_code', "Status")

        # links
        g.set_link('upc')
        g.set_link('item_id')
        g.set_link('description')

    def row_grid_extra_class(self, row, i):
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'

    def render_mobile_row_listitem(self, row, i):
        description = row.product.full_description if row.product else row.description
        unit_uom = 'LB' if row.product and row.product.weighed else 'EA'
        qty = "{} {}".format(pretty_quantity(row.cases or row.units), 'CS' if row.cases else unit_uom)
        return "({}) {} - {}".format(row.upc.pretty(), description, qty)

    def configure_row_form(self, f):
        super(InventoryBatchView, self).configure_row_form(f)

        # readonly fields
        f.set_readonly('upc')
        f.set_readonly('item_id')
        f.set_readonly('brand_name')
        f.set_readonly('description')
        f.set_readonly('size')
        f.set_readonly('previous_units_on_hand')
        f.set_readonly('case_quantity')
        f.set_readonly('unit_cost')
        f.set_readonly('total_cost')

        # quantity fields
        f.set_type('case_quantity', 'quantity')
        f.set_type('cases', 'quantity')
        f.set_type('units', 'quantity')

        # currency fields
        f.set_type('unit_cost', 'currency')
        f.set_type('total_cost', 'currency')

        # upc
        f.set_renderer('upc', self.render_upc)

    def render_upc(self, row, field):
        upc = row.upc
        if not upc:
            return ""
        text = upc.pretty()
        if row.product_uuid:
            url = self.request.route_url('products.view', uuid=row.product_uuid)
            return tags.link_to(text, url)
        return text

    @classmethod
    def defaults(cls, config):
        cls._batch_defaults(config)
        cls._defaults(config)
        cls._inventory_defaults(config)

    @classmethod
    def _inventory_defaults(cls, config):
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()

        # mobile - make new row from UPC
        config.add_route('mobile.{}.row_from_upc'.format(route_prefix), '/mobile{}/{{{}}}/row-from-upc'.format(url_prefix, model_key))
        config.add_view(cls, attr='mobile_row_from_upc', route_name='mobile.{}.row_from_upc'.format(route_prefix),
                        permission='{}.create_row'.format(permission_prefix))

        # extra perms for creating batches per "mode"
        config.add_tailbone_permission(permission_prefix, '{}.create.replace'.format(permission_prefix),
                                       "Create new {} with 'replace' mode".format(model_title))
        config.add_tailbone_permission(permission_prefix, '{}.create.zero'.format(permission_prefix),
                                       "Create new {} with 'zero' mode".format(model_title))


class ValidBatchRow(forms.validators.ModelValidator):
    model_class = model.InventoryBatchRow

    def _to_python(self, value, state):
        row = super(ValidBatchRow, self)._to_python(value, state)
        if row.batch.executed:
            raise fe.Invalid("Batch has already been executed", value, state)
        return row


class Decimal(fe.validators.Number):

    def _to_python(self, value, state):
        try:
            return decimal.Decimal(value)
        except ValueError:
            raise Invalid(self.message('number', state), value, state)


class InventoryForm(forms.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    row = ValidBatchRow()
    cases = Decimal()
    units = Decimal()


def includeme(config):
    InventoryAdjustmentReasonsView.defaults(config)
    InventoryBatchView.defaults(config)
