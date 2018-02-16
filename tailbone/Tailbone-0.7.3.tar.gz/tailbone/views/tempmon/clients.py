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
Views for tempmon clients
"""

from __future__ import unicode_literals, absolute_import

import subprocess

import six

from rattail_tempmon.db import model as tempmon

import colander
from webhelpers2.html import HTML, tags

from tailbone.views.tempmon import MasterView


class TempmonClientView(MasterView):
    """
    Master view for tempmon clients.
    """
    model_class = tempmon.Client
    model_title = "TempMon Client"
    model_title_plural = "TempMon Clients"
    route_prefix = 'tempmon.clients'
    url_prefix = '/tempmon/clients'

    grid_columns = [
        'config_key',
        'hostname',
        'location',
        'delay',
        'enabled',
        'online',
    ]

    form_fields = [
        'config_key',
        'hostname',
        'location',
        'delay',
        'probes',
        'enabled',
        'online',
    ]

    def configure_grid(self, g):
        super(TempmonClientView, self).configure_grid(g)
        g.filters['hostname'].default_active = True
        g.filters['hostname'].default_verb = 'contains'
        g.filters['location'].default_active = True
        g.filters['location'].default_verb = 'contains'
        g.set_sort_defaults('config_key')

        g.set_type('enabled', 'boolean')
        g.set_type('online', 'boolean')

        g.set_label('config_key', "Key")

        g.set_link('config_key')
        g.set_link('hostname')
        g.set_link('location')

    def configure_form(self, f):
        super(TempmonClientView, self).configure_form(f)

        # config_key
        f.set_validator('config_key', self.unique_config_key)

        # probes
        f.set_renderer('probes', self.render_probes)

        if self.creating or self.editing:
            f.remove_fields('probes',
                            'online')

    def unique_config_key(self, node, value):
        query = self.Session.query(tempmon.Client)\
                            .filter(tempmon.Client.config_key == value)
        if self.editing:
            client = self.get_instance()
            query = query.filter(tempmon.Client.uuid != client.uuid)
        if query.count():
            raise colander.Invalid(node, "Config key must be unique")

    def render_probes(self, client, field):
        probes = client.probes
        if not probes:
            return ""
        items = []
        for probe in probes:
            text = six.text_type(probe)
            url = self.request.route_url('tempmon.probes.view', uuid=probe.uuid)
            items.append(HTML.tag('li', c=[tags.link_to(text, url)]))
        return HTML.tag('ul', c=items)

    def delete_instance(self, client):
        # bulk-delete all readings first
        readings = self.Session.query(tempmon.Reading)\
                               .filter(tempmon.Reading.client == client)
        readings.delete(synchronize_session=False)
        self.Session.flush()
        self.Session.refresh(client)

        # Flush immediately to force any pending integrity errors etc.; that
        # way we don't set flash message until we know we have success.
        self.Session.delete(client)
        self.Session.flush()

    def restartable_client(self, client):
        return True

    def restart(self):
        client = self.get_instance()
        if self.restartable_client(client):
            try:
                subprocess.check_output(self.get_restart_cmd(client),
                                        stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as error:
                self.request.session.flash("Failed to restart client: {}".format(error.output), 'error')
            else:
                self.request.session.flash("Client has been restarted: {}".format(
                    self.get_instance_title(client)))
        else:
            self.request.session.flash("Restart not supported for client: {}".format(client), 'error')
        return self.redirect(self.get_action_url('view', client))

    def get_restart_cmd(self, client):
        return ['ssh', client.hostname, 'sudo service tempmon-client restart']

    @classmethod
    def defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()
        permission_prefix = cls.get_permission_prefix()
        model_key = cls.get_model_key()
        model_title = cls.get_model_title()

        cls._defaults(config)

        # restart tempmon client
        config.add_tailbone_permission(permission_prefix, '{}.restart'.format(permission_prefix),
                                       "Restart a {}".format(model_title))
        config.add_route('{}.restart'.format(route_prefix), '{}/{{{}}}/restart'.format(url_prefix, model_key))
        config.add_view(cls, attr='restart', route_name='{}.restart'.format(route_prefix),
                        permission='{}.restart'.format(permission_prefix))


def includeme(config):
    TempmonClientView.defaults(config)
