# Copyright (c) 2014 OpenStack Foundation.
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

import os

import eventlet
from oslo_log import log as logging
from oslo_utils import fileutils
import webob

from neutron.agent.linux import utils as agent_utils
from neutron.common import constants
from neutron.notifiers import batch_notifier

LOG = logging.getLogger(__name__)

KEEPALIVED_STATE_CHANGE_SERVER_BACKLOG = 4096

TRANSLATION_MAP = {'master': constants.HA_ROUTER_STATE_ACTIVE,
                   'backup': constants.HA_ROUTER_STATE_STANDBY,
                   'fault': constants.HA_ROUTER_STATE_STANDBY}


class KeepalivedStateChangeHandler(object):
    def __init__(self, agent):
        self.agent = agent

    @webob.dec.wsgify(RequestClass=webob.Request)
    def __call__(self, req):
        router_id = req.headers['X-Neutron-Router-Id']
        state = req.headers['X-Neutron-State']
        self.enqueue(router_id, state)

    def enqueue(self, router_id, state):
        LOG.debug('Handling notification for router '
                  '%(router_id)s, state %(state)s', {'router_id': router_id,
                                                     'state': state})
        self.agent.enqueue_state_change(router_id, state)


class L3AgentKeepalivedStateChangeServer(object):
    def __init__(self, agent, conf):
        self.agent = agent
        self.conf = conf

        agent_utils.ensure_directory_exists_without_file(
            self.get_keepalived_state_change_socket_path(self.conf))

    @classmethod
    def get_keepalived_state_change_socket_path(cls, conf):
        return os.path.join(conf.state_path, 'keepalived-state-change')

    def run(self):
        server = agent_utils.UnixDomainWSGIServer(
            'neutron-keepalived-state-change',
            num_threads=self.conf.ha_keepalived_state_change_server_threads)
        server.start(KeepalivedStateChangeHandler(self.agent),
                     self.get_keepalived_state_change_socket_path(self.conf),
                     workers=0,
                     backlog=KEEPALIVED_STATE_CHANGE_SERVER_BACKLOG)
        server.wait()


class AgentMixin(object):
    def __init__(self, host):
        self._init_ha_conf_path()
        super(AgentMixin, self).__init__(host)
        # BatchNotifier queue is needed to ensure that the HA router
        # state change sequence is under the proper order.
        self.state_change_notifier = batch_notifier.BatchNotifier(
            self._calculate_batch_duration(), self.notify_server)
        eventlet.spawn(self._start_keepalived_notifications_server)

    def _get_router_info(self, router_id):
        try:
            return self.router_info[router_id]
        except KeyError:
            LOG.info('Router %s is not managed by this agent. It was '
                     'possibly deleted concurrently.', router_id)

    def check_ha_state_for_router(self, router_id, current_state):
        ri = self._get_router_info(router_id)
        if ri and current_state != TRANSLATION_MAP[ri.ha_state]:
            LOG.debug("Updating server with state %(state)s for router "
                      "%(router_id)s", {'router_id': router_id,
                                        'state': ri.ha_state})
            self.state_change_notifier.queue_event((router_id, ri.ha_state))

    def _start_keepalived_notifications_server(self):
        state_change_server = (
            L3AgentKeepalivedStateChangeServer(self, self.conf))
        state_change_server.run()

    def _calculate_batch_duration(self):
        # Set the BatchNotifier interval to ha_vrrp_advert_int,
        # default 2 seconds.
        return self.conf.ha_vrrp_advert_int

    def enqueue_state_change(self, router_id, state):
        state_change_data = {"router_id": router_id, "state": state}
        LOG.info('Router %(router_id)s transitioned to %(state)s',
                 state_change_data)

        ri = self._get_router_info(router_id)
        if ri is None:
            return

        # TODO(dalvarez): Fix bug 1677279 by moving the IPv6 parameters
        # configuration to keepalived-state-change in order to remove the
        # dependency that currently exists on l3-agent running for the IPv6
        # failover.
        self._configure_ipv6_params_on_ext_gw_port_if_necessary(ri, state)
        if self.conf.enable_metadata_proxy:
            self._update_metadata_proxy(ri, router_id, state)
        self._update_radvd_daemon(ri, state)
        self.pd.process_ha_state(router_id, state == 'master')
        self.state_change_notifier.queue_event((router_id, state))
        self.l3_ext_manager.ha_state_change(self.context, state_change_data)

    def _configure_ipv6_params_on_ext_gw_port_if_necessary(self, ri, state):
        # If ipv6 is enabled on the platform, ipv6_gateway config flag is
        # not set and external_network associated to the router does not
        # include any IPv6 subnet, enable the gateway interface to accept
        # Router Advts from upstream router for default route on master
        # instances as well as ipv6 forwarding. Otherwise, disable them.
        ex_gw_port_id = ri.ex_gw_port and ri.ex_gw_port['id']
        if not ex_gw_port_id:
            return

        interface_name = ri.get_external_device_name(ex_gw_port_id)
        if ri.router.get('distributed', False):
            namespace = ri.ha_namespace
        else:
            namespace = ri.ns_name

        enable = state == 'master'
        ri._configure_ipv6_params_on_gw(ri.ex_gw_port, namespace,
                                        interface_name, enable)

    def _update_metadata_proxy(self, ri, router_id, state):
        if state == 'master':
            LOG.debug('Spawning metadata proxy for router %s', router_id)
            self.metadata_driver.spawn_monitored_metadata_proxy(
                self.process_monitor, ri.ns_name, self.conf.metadata_port,
                self.conf, router_id=ri.router_id)
        else:
            LOG.debug('Closing metadata proxy for router %s', router_id)
            self.metadata_driver.destroy_monitored_metadata_proxy(
                self.process_monitor, ri.router_id, self.conf, ri.ns_name)

    def _update_radvd_daemon(self, ri, state):
        # Radvd has to be spawned only on the Master HA Router. If there are
        # any state transitions, we enable/disable radvd accordingly.
        if state == 'master':
            ri.enable_radvd()
        else:
            ri.disable_radvd()

    def notify_server(self, batched_events):
        translated_states = dict((router_id, TRANSLATION_MAP[state]) for
                                 router_id, state in batched_events)
        LOG.debug('Updating server with HA routers states %s',
                  translated_states)
        self.plugin_rpc.update_ha_routers_states(
            self.context, translated_states)

    def _init_ha_conf_path(self):
        ha_full_path = os.path.dirname("/%s/" % self.conf.ha_confs_path)
        fileutils.ensure_tree(ha_full_path, mode=0o755)
