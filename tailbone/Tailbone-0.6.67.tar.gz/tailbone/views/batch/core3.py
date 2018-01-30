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
Base views for maintaining batches
"""

from __future__ import unicode_literals, absolute_import

import os
import tempfile

import six
import colander
import deform
from deform import widget as dfwidget
from pyramid_deform import SessionFileUploadTempStore
from webhelpers2.html import tags

from tailbone.views import MasterView3
from tailbone.views.batch import BatchMasterView2, FileBatchMasterView2


class BatchMasterView3(MasterView3, BatchMasterView2):
    """
    Base class for all "batch master" views
    """

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

    def configure_form(self, f):
        super(BatchMasterView3, self).configure_form(f)

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
        if filedict:
            self.handler.set_input_file(batch, filepath)
            os.remove(filepath)
            os.rmdir(tempdir)

        return batch

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

    def render_user(self, batch, field):
        user = getattr(batch, field)
        if not user:
            return ""
        title = six.text_type(user)
        url = self.request.route_url('users.view', uuid=user.uuid)
        return tags.link_to(title, url)


class FileBatchMasterView3(BatchMasterView3, FileBatchMasterView2):
    """
    Base class for all file-based "batch master" views
    """

    def configure_form(self, f):
        super(FileBatchMasterView3, self).configure_form(f)

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
