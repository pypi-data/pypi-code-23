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
Views for tempmon probes
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail_tempmon.db import model as tempmon

import colander
from deform import widget as dfwidget
from webhelpers2.html import tags

from tailbone.views.tempmon import MasterView


class TempmonProbeView(MasterView):
    """
    Master view for tempmon probes.
    """
    model_class = tempmon.Probe
    model_title = "TempMon Probe"
    model_title_plural = "TempMon Probes"
    route_prefix = 'tempmon.probes'
    url_prefix = '/tempmon/probes'

    grid_columns = [
        'client',
        'config_key',
        'appliance_type',
        'description',
        'device_path',
        'enabled',
        'status',
    ]

    form_fields = [
        'client',
        'config_key',
        'appliance_type',
        'description',
        'device_path',
        'critical_temp_min',
        'good_temp_min',
        'good_temp_max',
        'critical_temp_max',
        'therm_status_timeout',
        'status_alert_timeout',
        'enabled',
        'status',
    ]

    def configure_grid(self, g):
        super(TempmonProbeView, self).configure_grid(g)

        g.joiners['client'] = lambda q: q.join(tempmon.Client)
        g.sorters['client'] = g.make_sorter(tempmon.Client.config_key)
        g.set_sort_defaults('client')

        g.set_enum('appliance_type', self.enum.TEMPMON_APPLIANCE_TYPE)
        g.set_enum('status', self.enum.TEMPMON_PROBE_STATUS)

        g.set_type('enabled', 'boolean')

        g.set_label('config_key', "Key")

        g.set_link('client')
        g.set_link('config_key')
        g.set_link('description')

    def configure_form(self, f):
        super(TempmonProbeView, self).configure_form(f)

        # config_key
        f.set_validator('config_key', self.unique_config_key)

        # client
        f.set_renderer('client', self.render_client)
        f.set_label('client', "Tempmon Client")
        if self.creating or self.editing:
            f.replace('client', 'client_uuid')
            clients = self.Session.query(tempmon.Client)\
                                  .order_by(tempmon.Client.config_key)
            client_values = [(client.uuid, "{} ({})".format(client.config_key, client.hostname))
                             for client in clients]
            f.set_widget('client_uuid', dfwidget.SelectWidget(values=client_values))
            f.set_label('client_uuid', "Tempmon Client")

        # appliance_type
        f.set_enum('appliance_type', self.enum.TEMPMON_APPLIANCE_TYPE)

        # status
        f.set_enum('status', self.enum.TEMPMON_PROBE_STATUS)
        if self.creating or self.editing:
            f.remove_fields('status')

    def unique_config_key(self, node, value):
        query = self.Session.query(tempmon.Probe)\
                            .filter(tempmon.Probe.config_key == value)
        if self.editing:
            probe = self.get_instance()
            query = query.filter(tempmon.Probe.uuid != probe.uuid)
        if query.count():
            raise colander.Invalid(node, "Config key must be unique")

    def render_client(self, probe, field):
        client = probe.client
        if not client:
            return ""
        text = six.text_type(client)
        url = self.request.route_url('tempmon.clients.view', uuid=client.uuid)
        return tags.link_to(text, url)

    def delete_instance(self, probe):
        # bulk-delete all readings first
        readings = self.Session.query(tempmon.Reading)\
                               .filter(tempmon.Reading.probe == probe)
        readings.delete(synchronize_session=False)
        self.Session.flush()
        self.Session.refresh(probe)

        # Flush immediately to force any pending integrity errors etc.; that
        # way we don't set flash message until we know we have success.
        self.Session.delete(probe)
        self.Session.flush()


def includeme(config):
    TempmonProbeView.defaults(config)
