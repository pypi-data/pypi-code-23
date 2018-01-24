# Copyright (c) 2016 Mirantis, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from neutron_lib import exceptions as n_exc
from neutron_lib.objects import exceptions as o_exc
from oslo_db import exception as o_db_exc
from oslo_utils import versionutils
from oslo_versionedobjects import fields as obj_fields

from neutron.db import api as db_api
from neutron.objects import base
from neutron.objects import common_types
from neutron.services.trunk import exceptions as t_exc
from neutron.services.trunk import models


@base.NeutronObjectRegistry.register
class SubPort(base.NeutronDbObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    db_model = models.SubPort

    primary_keys = ['port_id']
    foreign_keys = {'Trunk': {'trunk_id': 'id'}}

    fields = {
        'port_id': common_types.UUIDField(),
        'trunk_id': common_types.UUIDField(),
        'segmentation_type': obj_fields.StringField(),
        'segmentation_id': obj_fields.IntegerField(),
    }

    fields_no_update = ['segmentation_type', 'segmentation_id', 'trunk_id']

    def to_dict(self):
        _dict = super(SubPort, self).to_dict()
        # trunk_id is redundant in the subport dict.
        _dict.pop('trunk_id')
        return _dict

    def create(self):
        with db_api.autonested_transaction(self.obj_context.session):
            try:
                super(SubPort, self).create()
            except o_db_exc.DBReferenceError as ex:
                if ex.key_table is None:
                    # NOTE(ivc): 'key_table' is provided by 'oslo.db' [1]
                    # only for a limited set of database backends (i.e.
                    # MySQL and PostgreSQL). Other database backends
                    # (including SQLite) would have 'key_table' set to None.
                    # We emulate the 'key_table' support for such database
                    # backends.
                    #
                    # [1] https://github.com/openstack/oslo.db/blob/3fadd5a
                    #     /oslo_db/sqlalchemy/exc_filters.py#L190-L203
                    if not Trunk.get_object(self.obj_context,
                                            id=self.trunk_id):
                        ex.key_table = Trunk.db_model.__tablename__

                if ex.key_table == Trunk.db_model.__tablename__:
                    raise t_exc.TrunkNotFound(trunk_id=self.trunk_id)

                raise n_exc.PortNotFound(port_id=self.port_id)
            except o_exc.NeutronDbObjectDuplicateEntry:
                raise t_exc.DuplicateSubPort(
                    segmentation_type=self.segmentation_type,
                    segmentation_id=self.segmentation_id,
                    trunk_id=self.trunk_id)


@base.NeutronObjectRegistry.register
class Trunk(base.NeutronDbObject):
    # Version 1.0: Initial version
    # Version 1.1: Changed tenant_id to project_id
    VERSION = '1.1'

    db_model = models.Trunk

    fields = {
        'admin_state_up': obj_fields.BooleanField(),
        'id': common_types.UUIDField(),
        'project_id': obj_fields.StringField(),
        'name': obj_fields.StringField(),
        'port_id': common_types.UUIDField(),
        'status': obj_fields.StringField(),
        'sub_ports': obj_fields.ListOfObjectsField(SubPort.__name__),
    }

    fields_no_update = ['project_id', 'port_id']

    synthetic_fields = ['sub_ports']

    def create(self):
        with db_api.autonested_transaction(self.obj_context.session):
            sub_ports = []
            if self.obj_attr_is_set('sub_ports'):
                sub_ports = self.sub_ports

            try:
                super(Trunk, self).create()
            except o_db_exc.DBReferenceError:
                raise n_exc.PortNotFound(port_id=self.port_id)

            if sub_ports:
                for sub_port in sub_ports:
                    sub_port.trunk_id = self.id
                    sub_port.create()
                    self.sub_ports.append(sub_port)
                self.obj_reset_changes(['sub_ports'])

    def update(self, **kwargs):
        self.update_fields(kwargs)
        super(Trunk, self).update()

    # TODO(hichihara): For tag mechanism. This will be removed in bug/1704137
    def to_dict(self):
        _dict = super(Trunk, self).to_dict()
        try:
            _dict['tags'] = [t.tag for t in self.db_obj.standard_attr.tags]
        except AttributeError:
            # AttrtibuteError can be raised when accessing self.db_obj
            # or self.db_obj.standard_attr
            pass
        return _dict

    def obj_make_compatible(self, primitive, target_version):
        _target_version = versionutils.convert_version_to_tuple(target_version)

        if _target_version < (1, 1):
            primitive['tenant_id'] = primitive.pop('project_id')
