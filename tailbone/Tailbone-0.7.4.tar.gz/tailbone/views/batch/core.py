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
Base views for maintaining "new-style" batches.
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime
import logging
import tempfile
from six import StringIO

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail.db import model, Session as RattailSession
from rattail.threads import Thread
from rattail.util import load_object, prettify

import colander
import deform
from deform import widget as dfwidget
from pyramid import httpexceptions
from pyramid.renderers import render_to_response
from pyramid.response import FileResponse
from pyramid_deform import SessionFileUploadTempStore
from webhelpers2.html import HTML, tags

from tailbone import forms, grids
from tailbone.db import Session
from tailbone.views import MasterView
from tailbone.progress import SessionProgress


log = logging.getLogger(__name__)


class BatchMasterView(MasterView):
    """
    Base class for all "batch master" views.
    """
    default_handler_spec = None
    has_rows = True
    rows_deletable = True
    rows_downloadable_csv = True
    refreshable = True
    refresh_after_create = False
    cloneable = False
    executable = True
    results_executable = False
    supports_mobile = True
    mobile_filterable = True
    mobile_rows_viewable = True
    has_worksheet = False

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
        'created',
        'created_by',
        'rowcount',
        'status_code',
        'executed',
        'executed_by',
        'purge',
    ]

    row_labels = {
        'status_code': "Status",
    }

    def __init__(self, request):
        super(BatchMasterView, self).__init__(request)
        self.handler = self.get_handler()

    def get_handler(self):
        """
        Returns a `BatchHandler` instance for the view.  All (?) custom batch
        views should define a default handler class; however this may in all
        (?)  cases be overridden by config also.  The specific setting required
        to do so will depend on the 'key' for the type of batch involved, e.g.
        assuming the 'vendor_catalog' batch:

        .. code-block:: ini

           [rattail.batch]
           vendor_catalog.handler = myapp.batch.vendorcatalog:CustomCatalogHandler

        Note that the 'key' for a batch is generally the same as its primary
        table name, although technically it is whatever value returns from the
        ``batch_key`` attribute of the main batch model class.
        """
        key = self.model_class.batch_key
        spec = self.rattail_config.get('rattail.batch', '{}.handler'.format(key),
                                       default=self.default_handler_spec)
        if spec:
            return load_object(spec)(self.rattail_config)
        return self.batch_handler_class(self.rattail_config)

    def template_kwargs_view(self, **kwargs):
        batch = kwargs['instance']
        kwargs['batch'] = batch
        kwargs['handler'] = self.handler
        kwargs['execute_title'] = self.get_execute_title(batch)
        kwargs['execute_enabled'] = self.instance_executable(batch)
        if kwargs['execute_enabled']:
            url = self.get_action_url('execute', batch)
            kwargs['execute_form'] = self.make_execute_form(batch, action_url=url)
        return kwargs

    def allow_worksheet(self, batch):
        return not batch.executed and not batch.complete

    def configure_grid(self, g):
        super(BatchMasterView, self).configure_grid(g)

        g.joiners['created_by'] = lambda q: q.join(model.User, model.User.uuid == self.model_class.created_by_uuid)
        g.joiners['executed_by'] = lambda q: q.outerjoin(model.User, model.User.uuid == self.model_class.executed_by_uuid)

        g.filters['executed'].default_active = True
        g.filters['executed'].default_verb = 'is_null'

        # TODO: not sure this todo is still relevant?
        # TODO: in some cases grid has no sorters yet..e.g. when building query for bulk-delete
        # if hasattr(g, 'sorters'):
        g.sorters['created_by'] = g.make_sorter(model.User.username)
        g.sorters['executed_by'] = g.make_sorter(model.User.username)

        g.set_sort_defaults('id', 'desc')

        g.set_enum('status_code', self.model_class.STATUS)

        g.set_type('created', 'datetime')
        g.set_type('executed', 'datetime')

        g.set_renderer('id', self.render_batch_id)

        g.set_link('id')
        g.set_link('description')
        g.set_link('created')
        g.set_link('executed')

        g.set_label('id', "Batch ID")
        g.set_label('created_by', "Created by")
        g.set_label('rowcount', "Rows")
        g.set_label('status_code', "Status")
        g.set_label('executed_by', "Executed by")

    def render_batch_id(self, batch, column):
        return batch.id_str

    def template_kwargs_index(self, **kwargs):
        route_prefix = self.get_route_prefix()
        if self.results_executable:
            url = self.request.route_url('{}.execute_results'.format(route_prefix))
            kwargs['execute_form'] = self.make_execute_form(action_url=url)
        return kwargs

    def get_exec_options_kwargs(self, **kwargs):
        return kwargs

    def get_instance_title(self, batch):
        if batch.description:
            return "{} {}".format(batch.id_str, batch.description)
        return batch.id_str

    def get_mobile_data(self, session=None):
        return super(BatchMasterView, self).get_mobile_data(session=session)\
                                           .order_by(self.model_class.id.desc())

    def make_mobile_filters(self):
        """
        Returns a set of filters for the mobile grid.
        """
        filters = grids.filters.GridFilterSet()
        filters['status'] = MobileBatchStatusFilter(self.model_class, 'status', default_value='pending')
        return filters

    def configure_form(self, f):
        super(BatchMasterView, self).configure_form(f)

        # id
        f.set_readonly('id')
        f.set_renderer('id', self.render_batch_id)
        f.set_label('id', "Batch ID")

        # created
        f.set_readonly('created')
        f.set_readonly('created_by')
        f.set_renderer('created_by', self.render_user)
        f.set_label('created_by', "Created by")

        # cognized
        f.set_renderer('cognized_by', self.render_user)
        f.set_label('cognized_by', "Cognized by")

        # row count
        f.set_readonly('rowcount')
        f.set_label('rowcount', "Row Count")

        # status_code
        f.set_readonly('status_code')
        f.set_renderer('status_code', self.make_status_renderer(self.model_class.STATUS))
        f.set_label('status_code', "Status")

        # executed
        f.set_readonly('executed')
        f.set_readonly('executed_by')
        f.set_renderer('executed_by', self.render_user)
        f.set_label('executed_by', "Executed by")

        # notes
        f.set_type('notes', 'text')

        # if self.creating and self.request.user:
        #     batch = fs.model
        #     batch.created_by_uuid = self.request.user.uuid

        if self.creating:
            f.remove_fields('id',
                            'rowcount',
                            'created',
                            'created_by',
                            'cognized',
                            'cognized_by',
                            'executed',
                            'executed_by',
                            'purge')

        else: # not creating
            batch = self.get_instance()
            if not batch.executed:
                f.remove_fields('executed',
                                'executed_by')

    def make_status_renderer(self, enum):
        def render_status(batch, field):
            value = batch.status_code
            if value is None:
                return ""
            status_code_text = enum.get(value, six.text_type(value))
            if batch.status_text:
                return HTML.tag('span', title=batch.status_text, c=status_code_text)
            return status_code_text
        return render_status

    def download_path(self, batch, filename):
        return self.rattail_config.batch_filepath(batch.batch_key, batch.uuid, filename)

    def render_user(self, batch, field):
        user = getattr(batch, field)
        if not user:
            return ""
        title = six.text_type(user)
        url = self.request.route_url('users.view', uuid=user.uuid)
        return tags.link_to(title, url)

    def configure_mobile_form(self, f):
        super(BatchMasterView, self).configure_mobile_form(f)
        batch = f.model_instance

        if self.creating:
            f.remove_fields('id',
                            'rowcount',
                            'created',
                            'created_by',
                            'cognized',
                            'cognized_by',
                            'executed',
                            'executed_by',
                            'purge')

        else: # not creating
            if not batch.executed:
                f.remove_fields('executed',
                                'executed_by')
                if not batch.complete:
                    f.remove_field('complete')

    def save_create_form(self, form):
        self.before_create(form)

        session = self.Session()
        with session.no_autoflush:

            # transfer form data to batch instance
            batch = self.objectify(form, self.form_deserialized)

            # current user is batch creator
            batch.created_by = self.request.user or self.late_login_user()

            # obtain kwargs for making batch via handler, below
            kwargs = self.get_batch_kwargs(batch)

            # TODO: this needs work yet surely...
            if 'filename' in form.schema:
                filedict = kwargs.pop('filename', None)
                filepath = None
                if filedict:
                    kwargs['filename'] = '' # null not allowed
                    tempdir = tempfile.mkdtemp()
                    filepath = os.path.join(tempdir, filedict['filename'])
                    tmpinfo = form.deform_form['filename'].widget.tmpstore.get(filedict['uid'])
                    tmpdata = tmpinfo['fp'].read()
                    with open(filepath, 'wb') as f:
                        f.write(tmpdata)

            # TODO: is this still necessary with colander?
            # destroy initial batch and re-make using handler
            # if batch in self.Session:
            #     self.Session.expunge(batch)
            batch = self.handler.make_batch(session, **kwargs)

        self.Session.flush()

        # TODO: this needs work yet surely...
        # if batch has input data file, let handler properly establish that
        if 'filename' in form.schema:
            if filedict:
                self.handler.set_input_file(batch, filepath)
                os.remove(filepath)
                os.rmdir(tempdir)

        return batch

    def save_mobile_create_form(self, form):
        self.before_create(form)
        session = self.Session()
        with session.no_autoflush:

            # transfer form data to batch instance
            batch = self.objectify(form, self.form_deserialized)

            # current user is batch creator
            batch.created_by = self.request.user

            # TODO: is this still necessary with colander?
            # destroy initial batch and re-make using handler
            kwargs = self.get_batch_kwargs(batch)
            if batch in session:
                session.expunge(batch)
            batch = self.handler.make_batch(session, **kwargs)

        session.flush()
        return batch

    def get_batch_kwargs(self, batch, mobile=False):
        """
        Return a kwargs dict for use with ``self.handler.make_batch()``, using
        the given batch as a template.
        """
        kwargs = {}
        if batch.created_by:
            kwargs['created_by'] = batch.created_by
        elif batch.created_by_uuid:
            kwargs['created_by_uuid'] = batch.created_by_uuid
        kwargs['description'] = batch.description
        kwargs['notes'] = batch.notes
        if hasattr(batch, 'filename'):
            kwargs['filename'] = batch.filename
        kwargs['complete'] = batch.complete
        return kwargs

    # TODO: deprecate / remove this (is it used at all now?)
    def init_batch(self, batch):
        """
        Initialize a new batch.  Derived classes can override this to
        effectively provide default values for a batch, etc.  This method is
        invoked after a batch has been fully prepared for insertion to the
        database, but before the push to the database occurs.

        Note that the return value of this function matters; if it is boolean
        false then the batch will not be persisted at all, and the user will be
        redirected to the "create batch" page.
        """
        return True

    def redirect_after_create(self, batch, mobile=False):
        if self.handler.should_populate(batch):
            return self.redirect(self.get_action_url('prefill', batch, mobile=mobile))
        elif self.refresh_after_create:
            return self.redirect(self.get_action_url('refresh', batch, mobile=mobile))
        else:
            return self.redirect(self.get_action_url('view', batch, mobile=mobile))

    def template_kwargs_edit(self, **kwargs):
        batch = kwargs['instance']
        kwargs['batch'] = batch
        return kwargs

    def mobile_mark_complete(self):
        batch = self.get_instance()
        batch.complete = True
        return self.redirect(self.get_index_url(mobile=True))

    def mobile_mark_pending(self):
        batch = self.get_instance()
        batch.complete = False
        return self.redirect(self.get_action_url('view', batch, mobile=True))

    def rows_creatable_for(self, batch):
        """
        Only allow creating new rows on a batch if it hasn't yet been executed.
        """
        return not batch.executed

    def configure_row_grid(self, g):
        super(BatchMasterView, self).configure_row_grid(g)

        if 'status_code' in g.filters:
            g.filters['status_code'].set_value_renderer(grids.filters.EnumValueRenderer(self.model_row_class.STATUS))

        g.set_sort_defaults('sequence')

        if self.model_row_class:
            g.set_enum('status_code', self.model_row_class.STATUS)

        g.set_renderer('status_code', self.render_row_status)

        g.set_label('sequence', "Seq.")
        g.set_label('status_code', "Status")
        g.set_label('item_id', "Item ID")

    def get_row_status_enum(self):
        return self.model_row_class.STATUS

    def render_row_status(self, row, column):
        code = row.status_code
        if code is None:
            return ""
        text = self.get_row_status_enum().get(code, six.text_type(code))
        if row.status_text:
            return HTML.tag('span', title=row.status_text, c=text)
        return text

    def create_row(self):
        """
        Only allow creating a new row if the batch hasn't yet been executed.
        """
        batch = self.get_instance()
        if batch.executed:
            self.request.session.flash("You cannot add new rows to a batch which has been executed")
            return self.redirect(self.get_action_url('view', batch))
        return super(BatchMasterView, self).create_row()

    def mobile_create_row(self):
        """
        Only allow creating a new row if the batch hasn't yet been executed.
        """
        batch = self.get_instance()
        if batch.executed:
            self.request.session.flash("You cannot add new rows to a batch which has been executed")
            return self.redirect(self.get_action_url('view', batch, mobile=True))
        return super(BatchMasterView, self).mobile_create_row()

    def save_create_row_form(self, form):
        batch = self.get_instance()
        row = self.objectify(form, self.form_deserialized)
        self.handler.add_row(batch, row)
        self.Session.flush()
        return row

    def after_create_row(self, row):
        self.handler.refresh_row(row)

    def configure_row_form(self, f):
        super(BatchMasterView, self).configure_row_form(f)

        # sequence
        f.set_readonly('sequence')

        # status_code
        if self.model_row_class:
            f.set_enum('status_code', self.model_row_class.STATUS)
        f.set_renderer('status_code', self.render_row_status)
        f.set_readonly('status_code')
        f.set_label('status_code', "Status")

    def configure_mobile_row_form(self, f):
        super(BatchMasterView, self).configure_mobile_row_form(f)

        # sequence
        f.set_readonly('sequence')

        # status_code
        if self.model_row_class:
            f.set_enum('status_code', self.model_row_class.STATUS)
        f.set_renderer('status_code', self.render_row_status)
        f.set_readonly('status_code')
        f.set_label('status_code', "Status")

    def make_default_row_grid_tools(self, batch):
        if self.rows_creatable and not batch.executed:
            permission_prefix = self.get_permission_prefix()
            if self.request.has_perm('{}.create_row'.format(permission_prefix)):
                link = tags.link_to("Create a new {}".format(self.get_row_model_title()),
                                    self.get_action_url('create_row', batch))
                return HTML.tag('p', c=link)

    def make_batch_row_grid_tools(self, batch):
        if self.rows_bulk_deletable and not batch.executed and self.request.has_perm('{}.delete_rows'.format(self.get_permission_prefix())):
            url = self.request.route_url('{}.delete_rows'.format(self.get_route_prefix()), uuid=batch.uuid)
            return HTML.tag('p', c=[tags.link_to("Delete all rows matching current search", url)])

    def make_row_grid_tools(self, batch):
        return (self.make_default_row_grid_tools(batch) or '') + (self.make_batch_row_grid_tools(batch) or '')

    def get_mobile_row_data(self, batch):
        return super(BatchMasterView, self).get_mobile_row_data(batch)\
                                           .order_by(self.model_row_class.sequence)

    def redirect_after_edit(self, batch):
        """
        If refresh flag is set, do that; otherwise go (back) to view/edit page.
        """
        if self.request.params.get('refresh') == 'true':
            return self.redirect(self.get_action_url('refresh', batch))
        return self.redirect(self.get_action_url('view', batch))

    def delete_instance(self, batch):
        """
        Delete all data (files etc.) for the batch.
        """
        if hasattr(batch, 'delete_data'):
            batch.delete_data(self.rattail_config)
        if hasattr(batch, 'data_rows'):
            del batch.data_rows[:]
        super(BatchMasterView, self).delete_instance(batch)

    def get_fallback_templates(self, template, mobile=False):
        if mobile:
            return [
                '/mobile/batch/{}.mako'.format(template),
                '/mobile/master/{}.mako'.format(template),
            ]
        return [
            '/batch/{}.mako'.format(template),
            '/master/{}.mako'.format(template),
        ]

    def editable_instance(self, batch):
        return not bool(batch.executed)

    def after_edit_row(self, row):
        self.handler.refresh_row(row)

    def instance_executable(self, batch=None):
        return self.handler.executable(batch)

    def batch_refreshable(self, batch):
        """
        Return a boolean indicating whether the given batch should allow a
        refresh operation.
        """
        # TODO: deprecate/remove this?
        if not self.refreshable:
            return False

        # (this is how it should be done i think..)
        if callable(self.handler.refreshable):
            return self.handler.refreshable(batch)

        # TODO: deprecate/remove this
        return self.handler.refreshable and not batch.executed

    def has_execution_options(self, batch=None):
        return bool(self.execution_options_schema)

    # TODO
    execution_options_schema = None

    def make_execute_schema(self, batch):
        return self.execution_options_schema().bind(batch=batch)

    def make_execute_form(self, batch=None, **kwargs):
        """
        Return a proper Form for execution options.
        """
        defaults = {}
        route_prefix = self.get_route_prefix()

        if self.has_execution_options(batch):
            if batch is None:
                batch = self.model_class
            schema = self.make_execute_schema(batch)
            for field in schema:

                # if field does not yet have a default, maybe provide one from session storage
                if field.default is colander.null:
                    key = 'batch.{}.execute_option.{}'.format(batch.batch_key, field.name)
                    if key in self.request.session:
                        defaults[field.name] = self.request.session[key]

        else:
            schema = colander.Schema()

        return forms.Form(schema=schema, request=self.request, defaults=defaults, **kwargs)

    def get_execute_title(self, batch):
        if hasattr(self.handler, 'get_execute_title'):
            return self.handler.get_execute_title(batch)
        return "Execute Batch"

    def prefill(self):
        """
        View which will attempt to prefill all data for the batch.  What
        exactly this means will depend on the type of batch etc.
        """
        batch = self.get_instance()
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        # showing progress requires a separate thread; start that first
        key = '{}.prefill'.format(route_prefix)
        progress = SessionProgress(self.request, key)
        thread = Thread(target=self.prefill_thread, args=(batch.uuid, progress))
        thread.start()

        # Send user to progress page.
        kwargs = {
            'cancel_url': self.get_action_url('view', batch),
            'cancel_msg': "Batch prefill was canceled.",
        }

        # TODO: This seems hacky...it exists for (only) one specific scenario.
        if not self.request.has_perm('{}.view'.format(permission_prefix)):
            kwargs['cancel_url'] = self.request.route_url('{}.create'.format(route_prefix))

        return self.render_progress(progress, kwargs)

    def prefill_thread(self, batch_uuid, progress):
        """
        Thread target for prefilling batch data with progress indicator.
        """
        # mustn't use tailbone web session here
        session = RattailSession()
        batch = session.query(self.model_class).get(batch_uuid)
        try:
            self.handler.populate(batch, progress=progress)
            self.handler.refresh_batch_status(batch)
        except Exception as error:
            session.rollback()
            log.warning("batch population failed: %s", batch, exc_info=True)
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "Batch population failed: {} - {}".format(error.__class__.__name__, error)
                progress.session.save()
            return

        session.commit()
        session.refresh(batch)
        session.close()

        # finalize progress
        if progress:
            progress.session.load()
            progress.session['complete'] = True
            progress.session['success_url'] = self.get_action_url('view', batch)
            progress.session.save()

    def refresh(self):
        """
        View which will attempt to refresh all data for the batch.  What
        exactly this means will depend on the type of batch etc.
        """
        batch = self.get_instance()
        route_prefix = self.get_route_prefix()
        permission_prefix = self.get_permission_prefix()

        # TODO: deprecate / remove this
        cognizer = self.request.user
        if not cognizer:
            uuid = self.request.session.pop('late_login_user', None)
            cognizer = Session.query(model.User).get(uuid) if uuid else None

        # TODO: refresh should probably always imply/use progress
        # If handler doesn't declare the need for progress indicator, things
        # are nice and simple.
        if not getattr(self.handler, 'show_progress', True):
            self.refresh_data(Session, batch, cognizer=cognizer)
            self.request.session.flash("Batch data has been refreshed.")

            # TODO: This seems hacky...it exists for (only) one specific scenario.
            if not self.request.has_perm('{}.view'.format(permission_prefix)):
                return self.redirect(self.request.route_url('{}.create'.format(route_prefix)))

            return self.redirect(self.get_action_url('view', batch))

        # Showing progress requires a separate thread; start that first.
        key = '{}.refresh'.format(self.model_class.__tablename__)
        progress = SessionProgress(self.request, key)
        # success_url = self.request.route_url('vendors.scangenius.create') if not self.request.user else None
        
        # TODO: This seems hacky...it exists for (only) one specific scenario.
        success_url = None
        if not self.request.user:
            success_url = self.request.route_url('{}.create'.format(route_prefix))
            
        thread = Thread(target=self.refresh_thread, args=(batch.uuid, progress,
                                                          cognizer.uuid if cognizer else None,
                                                          success_url))
        thread.start()

        # Send user to progress page.
        kwargs = {
            'cancel_url': self.get_action_url('view', batch),
            'cancel_msg': "Batch refresh was canceled.",
        }

        # TODO: This seems hacky...it exists for (only) one specific scenario.
        if not self.request.has_perm('{}.view'.format(permission_prefix)):
            kwargs['cancel_url'] = self.request.route_url('{}.create'.format(route_prefix))

        return self.render_progress(progress, kwargs)

    def refresh_data(self, session, batch, cognizer=None, progress=None):
        """
        Instruct the batch handler to refresh all data for the batch.
        """
        # TODO: deprecate/remove this
        if hasattr(self.handler, 'refresh_data'):
            self.handler.refresh_data(session, batch, progress=progress)
            batch.cognized = datetime.datetime.utcnow()
            batch.cognized_by = cognizer or session.merge(self.request.user)

        else: # the future
            self.handler.refresh(batch, progress=progress)

    def refresh_thread(self, batch_uuid, progress=None, cognizer_uuid=None, success_url=None):
        """
        Thread target for refreshing batch data with progress indicator.
        """
        # Refresh data for the batch, with progress.  Note that we must use the
        # rattail session here; can't use tailbone because it has web request
        # transaction binding etc.
        session = RattailSession()
        batch = session.query(self.model_class).get(batch_uuid)
        cognizer = session.query(model.User).get(cognizer_uuid) if cognizer_uuid else None
        try:
            self.refresh_data(session, batch, cognizer=cognizer, progress=progress)
        except Exception as error:
            session.rollback()
            log.warning("refreshing data for batch failed: {}".format(batch), exc_info=True)
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = "Data refresh failed: {} {}".format(error.__class__.__name__, error)
                progress.session.save()
            return

        session.commit()
        session.refresh(batch)
        session.close()

        # Finalize progress indicator.
        if progress:
            progress.session.load()
            progress.session['complete'] = True
            progress.session['success_url'] = success_url or self.get_action_url('view', batch)
            progress.session.save()

    ########################################
    # batch rows
    ########################################

    def get_row_instance_title(self, row):
        return "Row {}".format(row.sequence)

    hide_row_status_codes = []

    def get_row_data(self, batch):
        """
        Generate the base data set for a rows grid.
        """
        query = self.Session.query(self.model_row_class)\
                            .filter(self.model_row_class.batch == batch)\
                            .filter(self.model_row_class.removed == False)
        if self.hide_row_status_codes:
            query = query.filter(~self.model_row_class.status_code.in_(self.hide_row_status_codes))
        return query

    def row_editable(self, row):
        """
        Batch rows are editable only until batch is complete or executed.
        """
        batch = self.get_parent(row)
        return self.rows_editable and not batch.executed and not batch.complete

    def row_deletable(self, row):
        """
        Batch rows are deletable only until batch is complete or executed.
        """
        if self.rows_deletable:
            batch = self.get_parent(row)
            if not batch.executed and not batch.complete:
                return True
        return False

    def template_kwargs_view_row(self, **kwargs):
        kwargs['batch_model_title'] = kwargs['parent_model_title']
        return kwargs

    def get_parent(self, row):
        return row.batch

    def delete_row(self):
        """
        "Delete" a row from the batch.  This sets the ``removed`` flag on the
        row but does not truly delete it.
        """
        row = self.Session.query(self.model_row_class).get(self.request.matchdict['row_uuid'])
        if not row:
            raise httpexceptions.HTTPNotFound()
        row.removed = True
        batch = self.get_parent(row)
        self.handler.refresh_batch_status(batch)
        if batch.rowcount is not None:
            batch.rowcount -= 1
        return self.redirect(self.get_action_url('view', batch))

    def bulk_delete_rows(self):
        """
        "Delete" all rows matching the current row grid view query.  This sets
        the ``removed`` flag on the rows but does not truly delete them.
        """
        batch = self.get_instance()
        query = self.get_effective_row_data(sort=False)
        if batch.rowcount is not None:
            batch.rowcount -= query.count()
        query.update({'removed': True}, synchronize_session=False)
        return self.redirect(self.get_action_url('view', batch))

    def execute(self):
        """
        Execute a batch.  Starts a separate thread for the execution, and
        displays a progress indicator page.
        """
        batch = self.get_instance()
        self.executing = True
        form = self.make_execute_form(batch)
        if form.validate(newstyle=True):
            kwargs = dict(form.validated)

            # cache options to use as defaults next time
            for key, value in form.validated.items():
                self.request.session['batch.{}.execute_option.{}'.format(batch.batch_key, key)] = value

            key = '{}.execute'.format(self.model_class.__tablename__)
            progress = SessionProgress(self.request, key)
            kwargs['progress'] = progress
            thread = Thread(target=self.execute_thread, args=(batch.uuid, self.request.user.uuid), kwargs=kwargs)
            thread.start()

            return self.render_progress(progress, {
                'cancel_url': self.get_action_url('view', batch),
                'cancel_msg': "Batch execution was canceled.",
            })

        self.request.session.flash("Invalid request: {}".format(form.make_deform_form().error), 'error')
        return self.redirect(self.get_action_url('view', batch))

    def mobile_execute(self):
        """
        Mobile view which can prompt user for execution options if applicable,
        and/or execute a batch.  For now this is done in a "blocking" fashion,
        i.e. no progress bar.
        """
        batch = self.get_instance()
        model_title = self.get_model_title()
        instance_title = self.get_instance_title(batch)
        view_url = self.get_action_url('view', batch, mobile=True)
        self.executing = True
        form = self.make_execute_form(batch)
        if form.validate(newstyle=True):
            kwargs = dict(form.validated)

            # cache options to use as defaults next time
            for key, value in form.validated.items():
                self.request.session['batch.{}.execute_option.{}'.format(batch.batch_key, key)] = value

            try:
                result = self.handler.execute(batch, user=self.request.user, **kwargs)
            except Exception as err:
                log.exception("failed to execute %s %s", model_title, batch.id_str)
                self.request.session.flash(self.execute_error_message(err), 'error')
            else:
                if result:
                    batch.executed = datetime.datetime.utcnow()
                    batch.executed_by = self.request.user
                    self.request.session.flash("{} was executed: {}".format(model_title, instance_title))
                else:
                    log.error("not sure why, but failed to execute %s %s: %s", model_title, batch.id_str, batch)
                    self.request.session.flash("Failed to execute {}: {}".format(model_title, err), 'error')
            return self.redirect(view_url)

        form.mobile = True
        form.submit_label = "Execute"
        form.cancel_url = view_url
        return self.render_to_response('execute', {
            'form': form,
            'instance_title': instance_title,
            'instance_url': view_url,
        }, mobile=True)

    def execute_error_message(self, error):
        return "Batch execution failed: {}: {}".format(type(error).__name__, error)

    def execute_thread(self, batch_uuid, user_uuid, progress=None, **kwargs):
        """
        Thread target for executing a batch with progress indicator.
        """
        # Execute the batch, with progress.  Note that we must use the rattail
        # session here; can't use tailbone because it has web request
        # transaction binding etc.
        session = RattailSession()
        batch = session.query(self.model_class).get(batch_uuid)
        user = session.query(model.User).get(user_uuid)
        try:
            result = self.handler.execute(batch, user=user, progress=progress, **kwargs)

        # If anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("execution failed for batch: {}".format(batch))
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = self.execute_error_message(error)
                progress.session.save()

        # If no error, check result flag (false means user canceled).
        else:
            if result:
                batch.executed = datetime.datetime.utcnow()
                batch.executed_by = user
                session.commit()
                # TODO: this doesn't always work...?
                self.request.session.flash("{} has been executed: {}".format(
                    self.get_model_title(), batch.id_str))
            else:
                session.rollback()

            session.refresh(batch)
            success_url = self.get_execute_success_url(batch, result, **kwargs)
            session.close()

            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = success_url
                progress.session.save()

    def get_execute_success_url(self, batch, result, **kwargs):
        return self.get_action_url('view', batch)

    def execute_results(self):
        """
        Execute all batches which are returned from the current index query.
        Starts a separate thread for the execution, and displays a progress
        indicator page.
        """
        form = self.make_execute_form()
        if form.validate(newstyle=True):
            kwargs = dict(form.validated)

            # cache options to use as defaults next time
            for key, value in form.validated.items():
                self.request.session['batch.{}.execute_option.{}'.format(self.model_class.batch_key, key)] = value

            key = '{}.execute_results'.format(self.model_class.__tablename__)
            batches = self.get_effective_data()
            progress = SessionProgress(self.request, key)
            kwargs['progress'] = progress
            thread = Thread(target=self.execute_results_thread, args=(batches, self.request.user.uuid), kwargs=kwargs)
            thread.start()

            return self.render_progress(progress, {
                'cancel_url': self.get_index_url(),
                'cancel_msg': "Batch execution was canceled",
            })

        self.request.session.flash("Invalid request: {}".format(form.make_deform_form().error), 'error')
        return self.redirect(self.get_index_url())

    def execute_results_thread(self, batches, user_uuid, progress=None, **kwargs):
        """
        Thread target for executing multiple batches with progress indicator.
        """
        session = RattailSession()
        batches = batches.with_session(session).all()
        user = session.query(model.User).get(user_uuid)
        try:
            result = self.handler.execute_many(batches, user=user, progress=progress, **kwargs)

        # If anything goes wrong, rollback and log the error etc.
        except Exception as error:
            session.rollback()
            log.exception("execution failed for batch results")
            session.close()
            if progress:
                progress.session.load()
                progress.session['error'] = True
                progress.session['error_msg'] = self.execute_error_message(error)
                progress.session.save()

        # If no error, check result flag (false means user canceled).
        else:
            if result:
                session.commit()
                # TODO: this doesn't always work...?
                self.request.session.flash("{} {} were executed".format(
                    len(batches), self.get_model_title_plural()))
                success_url = self.get_execute_results_success_url(result, **kwargs)
            else:
                session.rollback()
                success_url = self.get_index_url()
            session.close()

            if progress:
                progress.session.load()
                progress.session['complete'] = True
                progress.session['success_url'] = success_url
                progress.session.save()

    def get_execute_results_success_url(self, result, **kwargs):
        return self.get_index_url()

    def get_row_csv_fields(self):
        fields = super(BatchMasterView, self).get_row_csv_fields()
        fields = [field for field in fields
                  if field != 'removed' and not field.endswith('uuid')]
        return fields

    def get_row_results_csv_filename(self, batch):
        return '{}.{}.csv'.format(self.get_route_prefix(), batch.id_str)

    def clone(self):
        """
        Clone current batch as new batch
        """
        batch = self.get_instance()
        batch = self.handler.clone(batch, created_by=self.request.user)
        return self.redirect(self.get_action_url('view', batch))

    @classmethod
    def defaults(cls, config):
        cls._batch_defaults(config)
        cls._defaults(config)

    @classmethod
    def _batch_defaults(cls, config):
        model_key = cls.get_model_key()
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # TODO: currently must do this here (in addition to `_defaults()` or
        # else the perm group label will not display correctly...
        config.add_tailbone_permission_group(permission_prefix, model_title_plural, overwrite=False)

        # prefill row data
        config.add_route('{}.prefill'.format(route_prefix), '{}/{{uuid}}/prefill'.format(url_prefix))
        config.add_view(cls, attr='prefill', route_name='{}.prefill'.format(route_prefix),
                        permission='{}.create'.format(permission_prefix))

        # worksheet
        if cls.has_worksheet:
            config.add_tailbone_permission(permission_prefix, '{}.worksheet'.format(permission_prefix),
                                           "Edit {} data as worksheet".format(model_title))
            config.add_route('{}.worksheet'.format(route_prefix), '{}/{{{}}}/worksheet'.format(url_prefix, model_key))
            config.add_view(cls, attr='worksheet', route_name='{}.worksheet'.format(route_prefix),
                            permission='{}.worksheet'.format(permission_prefix))
            config.add_route('{}.worksheet_update'.format(route_prefix), '{}/{{{}}}/worksheet/update'.format(url_prefix, model_key))
            config.add_view(cls, attr='worksheet_update', route_name='{}.worksheet_update'.format(route_prefix),
                            renderer='json', permission='{}.worksheet'.format(permission_prefix))

        # refresh batch data
        if cls.refreshable:
            config.add_route('{}.refresh'.format(route_prefix), '{}/{{uuid}}/refresh'.format(url_prefix))
            config.add_view(cls, attr='refresh', route_name='{}.refresh'.format(route_prefix),
                            permission='{}.refresh'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.refresh'.format(permission_prefix),
                                           "Refresh data for {}".format(model_title))

        # bulk delete rows
        if cls.rows_bulk_deletable:
            config.add_route('{}.delete_rows'.format(route_prefix), '{}/{{uuid}}/rows/delete'.format(url_prefix))
            config.add_view(cls, attr='bulk_delete_rows', route_name='{}.delete_rows'.format(route_prefix),
                            permission='{}.delete_rows'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.delete_rows'.format(permission_prefix),
                                           "Bulk-delete data rows from {}".format(model_title))

        # mobile mark complete
        config.add_route('mobile.{}.mark_complete'.format(route_prefix), '/mobile{}/{{{}}}/mark-complete'.format(url_prefix, model_key))
        config.add_view(cls, attr='mobile_mark_complete', route_name='mobile.{}.mark_complete'.format(route_prefix),
                        permission='{}.edit'.format(permission_prefix))

        # mobile mark pending
        config.add_route('mobile.{}.mark_pending'.format(route_prefix), '/mobile{}/{{{}}}/mark-pending'.format(url_prefix, model_key))
        config.add_view(cls, attr='mobile_mark_pending', route_name='mobile.{}.mark_pending'.format(route_prefix),
                        permission='{}.edit'.format(permission_prefix))

        # execute (multiple) batch results
        if cls.results_executable:
            config.add_route('{}.execute_results'.format(route_prefix), '{}/execute-results'.format(url_prefix))
            config.add_view(cls, attr='execute_results', route_name='{}.execute_results'.format(route_prefix),
                            permission='{}.execute_multiple'.format(permission_prefix))
            config.add_tailbone_permission(permission_prefix, '{}.execute_multiple'.format(permission_prefix),
                                           "Execute multiple {}".format(model_title_plural))


class FileBatchMasterView(BatchMasterView):
    """
    Base class for all file-based "batch master" views.
    """

    @property
    def upload_dir(self):
        """
        The path to the root upload folder, to be used as the ``storage_path``
        argument for the file field renderer.
        """
        uploads = os.path.join(
            self.rattail_config.require('rattail', 'batch.files'),
            'uploads')
        uploads = self.rattail_config.get('tailbone', 'batch.uploads',
                                          default=uploads)
        if not os.path.exists(uploads):
            os.makedirs(uploads)
        return uploads

    def configure_form(self, f):
        super(FileBatchMasterView, self).configure_form(f)

        # filename
        f.set_renderer('filename', self.render_filename)
        f.set_label('filename', "Data File")
        if self.editing:
            f.set_readonly('filename')

        if self.creating:
            if 'filename' not in f.fields:
                f.fields.insert(0, 'filename')
            tmpstore = SessionFileUploadTempStore(self.request)
            f.set_node('filename', colander.SchemaNode(deform.FileData(), widget=dfwidget.FileUploadWidget(tmpstore)))

    def render_filename(self, batch, field):
        path = batch.filepath(self.rattail_config, filename=batch.filename)
        url = self.get_action_url('download', batch)
        return self.render_file_field(path, url)

    def download(self):
        """
        View for downloading the data file associated with a batch.
        """
        batch = self.get_instance()
        if not batch:
            raise httpexceptions.HTTPNotFound()
        path = batch.filepath(self.rattail_config)
        response = FileResponse(path, request=self.request)
        response.headers[b'Content-Length'] = six.binary_type(os.path.getsize(path))
        filename = os.path.basename(batch.filename).encode('ascii', 'replace')
        response.headers[b'Content-Disposition'] = b'attachment; filename="{}"'.format(filename)
        return response

    @classmethod
    def defaults(cls, config):
        cls._filebatch_defaults(config)
        cls._batch_defaults(config)
        cls._defaults(config)

    @classmethod
    def _filebatch_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_title = cls.get_model_title()
        model_title_plural = cls.get_model_title_plural()

        # fix permission group title
        config.add_tailbone_permission_group(permission_prefix, model_title_plural)

        # download batch data file
        config.add_route('{}.download'.format(route_prefix), '{}/{{uuid}}/download'.format(url_prefix))
        config.add_view(cls, attr='download', route_name='{}.download'.format(route_prefix),
                        permission='{}.download'.format(permission_prefix))
        config.add_tailbone_permission(permission_prefix, '{}.download'.format(permission_prefix),
                                       "Download existing {} data file".format(model_title))


class MobileBatchStatusFilter(grids.filters.MobileFilter):

    value_choices = ['pending', 'complete', 'executed', 'all']

    def __init__(self, model_class, key, **kwargs):
        self.model_class = model_class
        super(MobileBatchStatusFilter, self).__init__(key, **kwargs)

    def filter_equal(self, query, value):

        if value == 'pending':
            return query.filter(self.model_class.executed == None)\
                        .filter(sa.or_(
                            self.model_class.complete == None,
                            self.model_class.complete == False))

        if value == 'complete':
            return query.filter(self.model_class.executed == None)\
                        .filter(self.model_class.complete == True)

        if value == 'executed':
            return query.filter(self.model_class.executed != None)

        return query

    def iter_choices(self):
        for value in self.value_choices:
            yield value, prettify(value)
