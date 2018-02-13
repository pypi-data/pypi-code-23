# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016: Alignak contrib team, see AUTHORS.txt file for contributors
#
# This file is part of Alignak contrib projet.
#
# Alignak is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Alignak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Alignak.  If not, see <http://www.gnu.org/licenses/>.

"""
This module is used to send logs and livestate to alignak-backend with broker
"""

import time
import json
import Queue
import logging

from multiprocessing import Process, Manager

from alignak.brok import Brok
from alignak.stats import Stats
from alignak.basemodule import BaseModule
from alignak_backend_client.client import Backend, BackendException

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name
for handler in logger.parent.handlers:
    if isinstance(handler, logging.StreamHandler):
        logger.parent.removeHandler(handler)

# pylint: disable=invalid-name
properties = {
    'daemons': ['broker'],
    'type': 'backend_broker',
    'external': True,
}


# mapping = {
#             'host': {},
#             'service': {},
#             'user': {}
#         }
#
# ref_live = {
#     'host': {},
#     'service': {},
#     'user': {}
# }


def get_instance(mod_conf):
    """
    Return a module instance for the modules manager

    :param mod_conf: the module properties as defined globally in this file
    :return:
    """
    logger.info("Give an instance of %s for alias: %s", mod_conf.python_name, mod_conf.module_alias)

    return AlignakBackendBroker(mod_conf)


class AlignakBackendBroker(BaseModule):
    """ This class is used to send logs and livestate to alignak-backend
    """

    def __init__(self, mod_conf):
        """Module initialization

        mod_conf is a dictionary that contains:
        - all the variables declared in the module configuration file
        - a 'properties' value that is the module properties as defined globally in this file

        :param mod_conf: module configuration file as a dictionary
        """
        BaseModule.__init__(self, mod_conf)

        # pylint: disable=global-statement
        global logger
        logger = logging.getLogger('alignak.module.%s' % self.alias)
        logger.setLevel(getattr(mod_conf, 'log_level', logging.INFO))

        logger.debug("inner properties: %s", self.__dict__)
        logger.debug("received configuration: %s", mod_conf.__dict__)

        logger.info("StatsD configuration: %s:%s, prefix: %s, enabled: %s",
                    getattr(mod_conf, 'statsd_host', 'localhost'),
                    int(getattr(mod_conf, 'statsd_port', '8125')),
                    getattr(mod_conf, 'statsd_prefix', 'alignak'),
                    (getattr(mod_conf, 'statsd_enabled', '0') != '0'))

        self.stats = Stats()
        self.stats.register(self.alias, 'broker',
                            statsd_host=getattr(mod_conf, 'statsd_host', 'localhost'),
                            statsd_port=int(getattr(mod_conf, 'statsd_port', '8125')),
                            statsd_prefix=getattr(mod_conf, 'statsd_prefix', 'alignak'),
                            statsd_enabled=(getattr(mod_conf, 'statsd_enabled', '0') != '0'))

        self.mod_conf = mod_conf

        self.message_pool = list()
        self.message_pool_size = 1

        # Initialize shared dicts
        manager = Manager()
        self.mapping = manager.dict(host=manager.dict(),
                                    service=manager.dict(),
                                    user=manager.dict())
        self.ref_live = manager.dict(host=manager.dict(),
                                     service=manager.dict(),
                                     user=manager.dict())

    def do_loop_turn(self):
        """This function is called/used when you need a module with
        a loop function (and use the parameter 'external': True)

        Note: We are obliged to define this method (even if not called!) because
        it is an abstract function in the base class
        """
        logger.info("In loop")
        time.sleep(0.1)

    # def manage_workers(self, message):
    #     if len(message) > 0:
    #         start = time.time()
    #         workers = [Worker(mod_conf=self.mod_conf,
    #                           alias=self.alias,
    #                           stats=self.stats,
    #                           brok=brok) for brok in message]
    #         managed = [worker.managed for worker in workers]
    #         end = time.time()
    #         types = [brok.type for brok in message]
    #         goods = managed.count(True)
    #         bads = managed.count(False)
    #         logger.info("managing {0} broks in {1} secs [{2} goods | {3} bads] [{4}]".format(len(message),
    #                                                                                          end-start,
    #                                                                                          goods,
    #                                                                                          bads,
    #                                                                                          types))

    def manage_message(self, message, priority=False):
        if len(message) > 0:
            message_process = MessageProcess(mod_conf=self.mod_conf,
                                             alias=self.alias,
                                             stats=self.stats,
                                             mapping=self.mapping,
                                             ref_live=self.ref_live,
                                             message=message)
            if not priority:
                if len(self.message_pool) < self.message_pool_size:
                    # The pool is not full
                    self.message_pool.append(message_process)
                else:
                    # The pool is full, we run the processes
                    logger.debug("Running pool of size {0}".format(len(self.message_pool)))
                    [mp.start() for mp in self.message_pool]
                    # [mp.join() for mp in self.message_pool]
                    self.message_pool = []
            else:
                # Message needs to be runs immediately
                message_process.start()
                message_process.join()

    def main(self):
        """
        Main loop of the process

        This module is an "external" module
        :return:
        """
        # Set the OS process title
        self.set_proctitle(self.alias)
        self.set_exit_handler()

        logger.info("starting...")

        # Update shared dicts by using a 'new_conf' brok
        params = {'type': 'new_conf', 'data': {}}
        brok = Brok(params)
        self.manage_message(message=[brok], priority=True)

        while not self.interrupted:
            try:
                queue_size = self.to_q.qsize()
                logger.debug("queue length: %s", queue_size)
                self.stats.gauge('queue-size', queue_size)
                start = time.time()

                message = self.to_q.get_nowait()
                brok_count = 0

                self.manage_message(message=message, priority=False)

                brok_count += len(message)
                self.stats.gauge('managed-broks-count', len(message))

                logger.debug("time to manage %s broks (%d secs)", brok_count, time.time() - start)
                self.stats.timer('managed-broks-time', time.time() - start)
            except Queue.Empty:
                # logger.debug("No message in the module queue")
                time.sleep(0.01)

        logger.info("stopping...")
        logger.info("stopped")


class Worker(object):
    """ This class is used to send logs and livestate to alignak-backend
    """

    def __init__(self, mod_conf, alias, stats, mapping, ref_live):
        """Module initialization

        mod_conf is a dictionary that contains:
        - all the variables declared in the module configuration file
        - a 'properties' value that is the module properties as defined globally in this file

        :param mod_conf: module configuration file as a dictionary
        """

        self.alias = alias
        self.stats = stats
        self.mapping = mapping
        self.ref_live = ref_live

        self.url = getattr(mod_conf, 'api_url', 'http://localhost:5000')

        self.client_processes = int(getattr(mod_conf, 'client_processes', 1))

        self.backend_connection_retry_planned = 0
        self.backend_errors_count = 0
        self.backend_username = getattr(mod_conf, 'username', '')
        self.backend_password = getattr(mod_conf, 'password', '')
        self.backend_generate = getattr(mod_conf, 'allowgeneratetoken', False)
        self.backend_token = getattr(mod_conf, 'token', '')
        self.backend = Backend(self.url, self.client_processes)

        # Log in to the backend
        self.backend_connected = self.backend_login()

        # Get the default realm
        self.default_realm = self.get_default_realm()

        # Objects reference
        self.load_protect_delay = int(getattr(mod_conf, 'load_protect_delay', '300'))
        self.last_load = 0

    def backend_login(self):
        """Log in to the backend

        :return: bool
        """
        generate = 'enabled'
        if not self.backend_generate:
            generate = 'disabled'

        self.stats.counter('backend-login', 1)

        if self.backend_token:
            # We have a token, don't ask for a new one
            self.backend.token = self.backend_token
            connected = True  # Not really yet, but assume yes
        else:
            if not self.backend_username or not self.backend_password:
                logger.error("No user or password supplied, and no default token defined. Can't connect to backend")
                connected = False
            else:
                try:
                    connected = self.backend.login(self.backend_username, self.backend_password, generate)
                except BackendException as exp:
                    logger.error("Error on backend login: {0}".format(exp))
                    connected = False

        return connected

    def get_default_realm(self):
        """
        Retrieves the default top level realm for the connected user
        :return: str or None
        """
        default_realm = None

        self.stats.counter('backend-get.realm', 1)

        if self.backend_connected:
            try:
                result = self.backend.get('/realm', {'max_results': 1, 'sort': '_level'})
            except BackendException as exp:
                logger.warning("Error on backend when retrieving default realm: {0}".format(exp))
            else:
                try:
                    default_realm = result['_items'][0]['_id']
                except Exception as exp:
                    logger.error("Can't get the default realm in the backend response: {0}".format(exp))

        return default_realm

    def get_refs(self):
        """
        Get the _id in the backend for hosts, services and users

        :return: None
        """
        start = time.time()
        now = int(time.time())

        # Get managed inter-process dicts
        host_mapping = self.mapping['host']
        serv_mapping = self.mapping['service']
        user_mapping = self.mapping['user']
        host_ref_live = self.ref_live['host']
        serv_ref_live = self.ref_live['service']
        user_ref_live = self.ref_live['user']

        if now - self.last_load > self.load_protect_delay:
            logger.info("Got a new configuration, reloading objects...")
            # Updating hosts
            hosts = {}
            params = {
                'projection': '{"name":1,"ls_state":1,"ls_state_type":1,"_realm":1}',
                'where': '{"_is_template":false}'
            }
            content = self.backend.get_all('host', params)
            self.stats.counter('backend-getall.host', 1)
            for item in content['_items']:
                host_mapping[item['name']] = item['_id']

                host_ref_live[item['_id']] = {
                    '_id': item['_id'],
                    '_etag': item['_etag'],
                    '_realm': item['_realm'],
                    'initial_state': item['ls_state'],
                    'initial_state_type': item['ls_state_type']
                }
                hosts[item['_id']] = item['name']
            logger.info("- hosts references reloaded")

            # Updating services
            params = {
                'projection': '{"host":1,"name":1,"ls_state":1,"ls_state_type":1,"_realm":1}',
                'where': '{"_is_template":false}'
            }
            content = self.backend.get_all('service', params)
            self.stats.counter('backend-getall.service', 1)
            for item in content['_items']:
                serv_mapping['__'.join([hosts[item['host']], item['name']])] = item['_id']

                serv_ref_live[item['_id']] = {
                    '_id': item['_id'],
                    '_etag': item['_etag'],
                    '_realm': item['_realm'],
                    'initial_state': item['ls_state'],
                    'initial_state_type': item['ls_state_type']
                }
            logger.info("- services references reloaded")

            # Updating users
            params = {
                'projection': '{"name":1,"_realm":1}',
                'where': '{"_is_template":false}'
            }
            content = self.backend.get_all('user', params)
            self.stats.counter('backend-getall.user', 1)
            for item in content['_items']:
                user_mapping[item['name']] = item['_id']

                user_ref_live[item['_id']] = {
                    '_id': item['_id'],
                    '_etag': item['_etag'],
                    '_realm': item['_realm']
                }
            logger.info("- users references reloaded")

            self.last_load = now
        else:
            logger.warning("- references not reloaded. "
                           "Last reload is too recent; set the 'load_protect_delay' parameter accordingly.")

        # Propagate changes in the inter-process dicts
        self.mapping['host'] = host_mapping
        self.mapping['service'] = serv_mapping
        self.mapping['user'] = user_mapping
        self.ref_live['host'] = host_ref_live
        self.ref_live['service'] = serv_ref_live
        self.ref_live['user'] = user_ref_live

        end = time.time()
        self.stats.timer('backend-getall.time', end - start)

    def update_next_check(self, data, obj_type):
        """Update livestate host and service next check timestamp

        {'instance_id': u'475dc864674943b4aa4cbc966f7cc737', u'service_description': u'nsca_disk',
        u'next_chk': 0, u'in_checking': True, u'host_name': u'ek3022fdj-00011'}

        :param data: dictionary of data from scheduler
        :type data: dict
        :param obj_type: type of data (host | service)
        :type obj_type: str
        :return: Counters of updated or add data to alignak backend
        :rtype: dict
        """
        start_time = time.time()
        counters = {
            'livestate_host': 0,
            'livestate_service': 0,
            'log_host': 0,
            'log_service': 0
        }
        logger.debug("Update next check: %s, %s", obj_type, data)

        if obj_type == 'host':
            if data['host_name'] in self.mapping['host']:
                # Received data for an host:
                data_to_update = {
                    'ls_next_check': data['next_chk']
                }

                # Update live state
                ret = self.send_to_backend('livestate_host', data['host_name'], data_to_update)
                if ret:
                    counters['livestate_host'] += 1
                logger.debug("Updated host live state data: %s", data_to_update)
        elif obj_type == 'service':
            service_name = '__'.join([data['host_name'], data['service_description']])
            if service_name in self.mapping['service']:
                # Received data for a service:
                data_to_update = {
                    'ls_next_check': data['next_chk']
                }

                # Update live state
                ret = self.send_to_backend('livestate_service', service_name, data_to_update)
                if ret:
                    counters['livestate_service'] += 1
                logger.debug("Updated service live state data: %s", data_to_update)
        if (counters['livestate_host'] + counters['livestate_service']) > 0:
            logger.debug("--- %s seconds ---", (time.time() - start_time))
        return counters

    def update_livestate(self, data, obj_type):
        """
        Update livestate_host and livestate_service

        :param data: dictionary of data from scheduler
        :type data: dict
        :param obj_type: type of data (host | service)
        :type obj_type: str
        :return: Counters of updated or add data to alignak backend
        :rtype: dict
        """
        start_time = time.time()
        counters = {
            'livestate_host': 0,
            'livestate_service': 0,
            'log_host': 0,
            'log_service': 0
        }
        logger.debug("Update livestate: %s - %s", obj_type, data)

        if obj_type == 'host':
            if data['host_name'] in self.mapping['host']:
                # Received data for an host:
                data_to_update = {
                    'ls_state': data['state'],
                    'ls_state_id': data['state_id'],
                    'ls_state_type': data['state_type'],
                    'ls_last_check': data['last_chk'],
                    'ls_last_state': data['last_state'],
                    'ls_last_state_type': data['last_state_type'],
                    'ls_last_state_changed': data['last_state_change'],
                    'ls_output': data['output'],
                    'ls_long_output': data['long_output'],
                    'ls_perf_data': data['perf_data'],
                    'ls_acknowledged': data['problem_has_been_acknowledged'],
                    'ls_acknowledgement_type': data['acknowledgement_type'],
                    'ls_downtimed': data['in_scheduled_downtime'],
                    'ls_execution_time': data['execution_time'],
                    'ls_latency': data['latency'],

                    # 'ls_passive_check': data['passive_check'],
                    'ls_attempt': data['attempt'],
                    'ls_last_hard_state_changed': data['last_hard_state_change'],
                    # Last time in the corresponding state
                    'ls_last_time_up': data['last_time_up'],
                    'ls_last_time_down': data['last_time_down'],
                    'ls_last_time_unknown': 0,
                    'ls_last_time_unreachable': data['last_time_unreachable']
                }

                h_id = self.mapping['host'][data['host_name']]
                if 'initial_state' in self.ref_live['host'][h_id]:
                    data_to_update['ls_last_state'] = self.ref_live['host'][h_id]['initial_state']
                    data_to_update['ls_last_state_type'] = self.ref_live['host'][h_id]['initial_state_type']
                    del self.ref_live['host'][h_id]['initial_state']
                    del self.ref_live['host'][h_id]['initial_state_type']

                data_to_update['_realm'] = self.ref_live['host'][h_id]['_realm']

                # Update live state
                ret = self.send_to_backend('livestate_host', data['host_name'], data_to_update)
                if ret:
                    counters['livestate_host'] += 1
                logger.debug("Updated host live state data: %s", data_to_update)

                # Add an host log
                data_to_update['ls_state_changed'] = (
                    data_to_update['ls_state'] != data_to_update['ls_last_state']
                )
                data_to_update['host'] = self.mapping['host'][data['host_name']]
                data_to_update['service'] = None

                # Rename ls_ keys and delete non used keys...
                for field in ['ls_attempt', 'ls_last_state_changed', 'ls_last_hard_state_changed',
                              'ls_last_time_up', 'ls_last_time_down', 'ls_last_time_unknown',
                              'ls_last_time_unreachable']:
                    del data_to_update[field]
                for key in data_to_update:
                    if key.startswith('ls_'):
                        data_to_update[key[3:]] = data_to_update[key]
                        del data_to_update[key]

                ret = self.send_to_backend('log_host', data['host_name'], data_to_update)
                if ret:
                    counters['log_host'] += 1
        elif obj_type == 'service':
            service_name = '__'.join([data['host_name'], data['service_description']])
            if service_name in self.mapping['service']:
                # Received data for a service:
                data_to_update = {
                    'ls_state': data['state'],
                    'ls_state_id': data['state_id'],
                    'ls_state_type': data['state_type'],
                    'ls_last_check': data['last_chk'],
                    'ls_last_state': data['last_state'],
                    'ls_last_state_type': data['last_state_type'],
                    'ls_last_state_changed': data['last_state_change'],
                    'ls_output': data['output'],
                    'ls_long_output': data['long_output'],
                    'ls_perf_data': data['perf_data'],
                    'ls_acknowledged': data['problem_has_been_acknowledged'],
                    'ls_acknowledgement_type': data['acknowledgement_type'],
                    'ls_downtimed': data['in_scheduled_downtime'],
                    'ls_execution_time': data['execution_time'],
                    'ls_latency': data['latency'],

                    # 'ls_passive_check': data['passive_check'],
                    'ls_attempt': data['attempt'],
                    'ls_last_hard_state_changed': data['last_hard_state_change'],
                    # Last time in the corresponding state
                    'ls_last_time_ok': data['last_time_ok'],
                    'ls_last_time_warning': data['last_time_warning'],
                    'ls_last_time_critical': data['last_time_critical'],
                    'ls_last_time_unknown': data['last_time_unknown'],
                    'ls_last_time_unreachable': data['last_time_unreachable']
                }
                s_id = self.mapping['service'][service_name]
                if 'initial_state' in self.ref_live['service'][s_id]:
                    data_to_update['ls_last_state'] = self.ref_live['service'][s_id]['initial_state']
                    data_to_update['ls_last_state_type'] = self.ref_live['service'][s_id]['initial_state_type']
                    del self.ref_live['service'][s_id]['initial_state']
                    del self.ref_live['service'][s_id]['initial_state_type']

                data_to_update['_realm'] = self.ref_live['service'][s_id]['_realm']

                # Update live state
                ret = self.send_to_backend('livestate_service', service_name, data_to_update)
                if ret:
                    counters['livestate_service'] += 1
                logger.debug("Updated service live state data: %s", data_to_update)

                # Add a service log
                data_to_update['ls_state_changed'] = (
                    data_to_update['ls_state'] != data_to_update['ls_last_state']
                )
                data_to_update['host'] = self.mapping['host'][data['host_name']]
                data_to_update['service'] = self.mapping['service'][service_name]

                # Rename ls_ keys and delete non used keys...
                for field in ['ls_attempt', 'ls_last_state_changed', 'ls_last_hard_state_changed',
                              'ls_last_time_ok', 'ls_last_time_warning', 'ls_last_time_critical',
                              'ls_last_time_unknown', 'ls_last_time_unreachable']:
                    del data_to_update[field]
                for key in data_to_update:
                    if key.startswith('ls_'):
                        data_to_update[key[3:]] = data_to_update[key]
                        del data_to_update[key]

                self.send_to_backend('log_service', service_name, data_to_update)
                if ret:
                    counters['log_service'] += 1

        if (counters['livestate_host'] + counters['livestate_service']) > 0:
            logger.debug("--- %s seconds ---", (time.time() - start_time))
        return counters

    def send_to_backend(self, type_data, name, data):
        """
        Send data to alignak backend

        :param type_data: one of ['livestate_host', 'livestate_service', 'log_host', 'log_service']
        :type type_data: str
        :param name: name of host or service
        :type name: str
        :param data: dictionary with data to add / update
        :type data: dict
        :return: True if send is ok, False otherwise
        :rtype: bool
        """
        if not self.backend_connected:
            logger.error("Not connected to the backend, ignoring brok...")
            return False

        logger.debug("Send to backend: %s, %s", type_data, data)

        headers = {'Content-Type': 'application/json'}

        ret = True

        if type_data in ['livestate_host', 'log_host']:
            obj_type = 'host'
            stats_counter = 'backend-patch.{0}'.format(obj_type)
            stats_time = 'backend-patch-time.{0}'.format(obj_type)

        elif type_data in ['livestate_service', 'log_service']:
            obj_type = 'service'
            stats_counter = 'backend-post.logcheckresult'
            stats_time = 'backend-post-time.{0}-logcheckresult'.format(obj_type)

        else:
            logger.error("Can't sent {0} to backend. "
                         "Must be a livestate or a log for a host or a service".format(type_data))
            return False

        # Object parameters definition
        obj_mapping = self.mapping[obj_type]
        obj_ref_live = self.ref_live[obj_type]
        obj_id = obj_mapping[name]
        obj_etag = obj_ref_live[obj_id]['_etag']
        obj_endpoint = '{0}/{1}'.format(obj_type, obj_id)

        self.stats.counter(stats_counter, 1)
        start = time.time()

        try:
            if type_data in ['livestate_host', 'livestate_service']:
                headers['If-Match'] = obj_etag
                response = self.backend.patch(endpoint=obj_endpoint, data=data, headers=headers, inception=True)
            else:  # type_data in ['log_host', 'log_service']
                response = self.backend.post(endpoint='logcheckresult', data=data)
        except BackendException as exp:  # pragma: no cover - should not happen
            logger.error('Error on sending a {0} for {1} (_id {2}) to the backend'.format(type_data, name, obj_id))
            logger.error('Data: {0}'.format(data))
            logger.error("Exception: {0}".format(exp))
            ret = False
        else:
            if response['_status'] == 'ERR':  # pragma: no cover - should not happen
                logger.error('{0}'.format(response['_issues']))
                ret = False
            else:
                if type_data in ['livestate_host', 'livestate_service']:
                    # update the ref_live dict
                    new_etag = response['_etag']
                    obj_ref_live[obj_id]['_etag'] = new_etag
                    # Propagate changes in the inter-process dict
                    self.ref_live[obj_type] = obj_ref_live

        end = time.time()
        self.stats.timer(stats_time, end - start)

        return ret

    # def send_to_backend(self, type_data, name, data):
    #     """
    #     Send data to alignak backend
    #
    #     :param type_data: one of ['livestate_host', 'livestate_service', 'log_host', 'log_service']
    #     :type type_data: str
    #     :param name: name of host or service
    #     :type name: str
    #     :param data: dictionary with data to add / update
    #     :type data: dict
    #     :return: True if send is ok, False otherwise
    #     :rtype: bool
    #     """
    #     if not self.backend_connected:
    #         logger.error("Not connected to the backend, ignoring brok...")
    #         return
    #
    #     logger.debug("Send to backend: %s, %s", type_data, data)
    #
    #     headers = {
    #         'Content-Type': 'application/json',
    #     }
    #     ret = True
    #     if type_data == 'livestate_host':
    #         headers['If-Match'] = self.ref_live['host'][self.mapping['host'][name]]['_etag']
    #         try:
    #             self.stats.counter('backend-patch.host', 1)
    #             start = time.time()
    #             response = self.backend.patch(
    #                 'host/%s' % self.ref_live['host'][self.mapping['host'][name]]['_id'],
    #                 data, headers, True)
    #             end = time.time()
    #             self.stats.timer('backend-patch-time.host', end - start)
    #             if response['_status'] == 'ERR':  # pragma: no cover - should not happen
    #                 logger.error('%s', response['_issues'])
    #                 ret = False
    #             else:
    #                 self.ref_live['host'][self.mapping['host'][name]]['_etag'] = response['_etag']
    #         except BackendException as exp:  # pragma: no cover - should not happen
    #             logger.error('Patch livestate for host %s error', self.mapping['host'][name])
    #             logger.error('Data: %s', data)
    #             logger.exception("Exception: %s", exp)
    #             if exp.code == 404:
    #                 logger.error('Seems the host %s deleted in the Backend',
    #                              self.mapping['host'][name])
    #     elif type_data == 'livestate_service':
    #         headers['If-Match'] = self.ref_live['service'][self.mapping['service'][name]]['_etag']
    #         try:
    #             self.stats.counter('backend-patch.service', 1)
    #             start = time.time()
    #             response = self.backend.patch(
    #                 'service/%s' % self.ref_live['service'][self.mapping['service'][name]]['_id'],
    #                 data, headers, True)
    #             end = time.time()
    #             self.stats.timer('backend-patch-time.service', end - start)
    #             if response['_status'] == 'ERR':  # pragma: no cover - should not happen
    #                 logger.error('%s', response['_issues'])
    #                 ret = False
    #             else:
    #                 self.ref_live['service'][self.mapping['service'][name]]['_etag'] = response[
    #                     '_etag']
    #         except BackendException as exp:  # pragma: no cover - should not happen
    #             logger.error('Patch livestate for service %s error', self.mapping['service'][name])
    #             logger.error('Data: %s', data)
    #             logger.exception("Exception: %s", exp)
    #             if exp.code == 404:
    #                 logger.error('Seems the service %s deleted in the Backend',
    #                              self.mapping['service'][name])
    #     elif type_data == 'log_host':
    #         try:
    #             self.stats.counter('backend-post.logcheckresult', 1)
    #             start = time.time()
    #             response = self.backend.post('logcheckresult', data)
    #             end = time.time()
    #             self.stats.timer('backend-post-time.host-logcheckresult', end - start)
    #         except BackendException as exp:  # pragma: no cover - should not happen
    #             logger.error('Post logcheckresult for host %s error', self.mapping['host'][name])
    #             logger.error('Data: %s', data)
    #             logger.exception("Exception: %s", exp)
    #             if exp.code == 422:
    #                 logger.error('Seems the host %s deleted in the Backend',
    #                              self.mapping['host'][name])
    #             ret = False
    #     elif type_data == 'log_service':
    #         try:
    #             self.stats.counter('backend-post.logcheckresult', 1)
    #             start = time.time()
    #             response = self.backend.post('logcheckresult', data)
    #             end = time.time()
    #             self.stats.timer('backend-post-time.service-logcheckresult', end - start)
    #         except BackendException as exp:  # pragma: no cover - should not happen
    #             logger.error('Post logcheckresult for service %s error',
    #                          self.mapping['service'][name])
    #             logger.error('Data: %s', data)
    #             logger.exception("Exception: %s", exp)
    #             logger.error('Error detail: %s, %s, %s', exp.code, exp.message, exp.response)
    #             if exp.code == 422:
    #                 logger.error('Seems the service %s deleted in the Backend',
    #                              self.mapping['service'][name])
    #             ret = False
    #     return ret

    def update_status(self, brok):
        # pylint: disable=too-many-locals
        """We manage the status change for a backend host/service/contact

        :param brok: the brok
        :type brok:
        :return: None
        """
        if 'contact_name' in brok.data:
            contact_name = brok.data['contact_name']
            if brok.data['contact_name'] not in self.mapping['user']:
                logger.warning("Updating status for a brok for an unknown user: '%s'", contact_name)
                return
            endpoint = 'user'
            name = contact_name
            item_id = self.mapping['user'][name]
        else:
            host_name = brok.data['host_name']
            if brok.data['host_name'] not in self.mapping['host']:
                logger.warning("Updating status for a brok for an unknown host: '%s'", host_name)
                return
            endpoint = 'host'
            name = host_name
            item_id = self.mapping['host'][name]
            if 'service_description' in brok.data:
                service_name = '__'.join([host_name, brok.data['service_description']])
                endpoint = 'service'
                name = service_name
                item_id = self.mapping['service'][name]
                if service_name not in self.mapping['service']:
                    logger.warning("Updating status for a brok for an unknown service: '%s'", service_name)
                    return

        # Sort brok properties
        sorted_brok_properties = sorted(brok.data)
        logger.debug("Update status %s: %s", endpoint, sorted(brok.data))

        # Search the concerned element
        self.stats.counter('backend-get.%s' % endpoint, 1)
        item = self.backend.get(endpoint + '/' + item_id)
        logger.debug("Found %s: %s", endpoint, sorted(item))

        differences = {}
        for key in sorted_brok_properties:
            value = brok.data[key]
            # Filter livestate keys...
            if "ls_%s" % key in item:
                logger.debug("Filtered live state: %s", key)
                continue

            # Filter noisy keys...
            if key in ["display_name", "tags", "notificationways"]:
                logger.debug("Filtered noisy key: %s", key)
                continue

            # Filter linked objects...
            if key in ['parents', 'parent_dependencies',
                       'check_command', 'event_handler', 'snapshot_command', 'check_period',
                       'maintenance_period', 'snapshot_period', 'notification_period',
                       'host_notification_period', 'service_notification_period',
                       'host_notification_commands', 'service_notification_commands',
                       'contacts', 'contact_groups', 'hostgroups',
                       'checkmodulations']:
                logger.debug("Filtered linked object: %s", key)
                continue

            if key not in item:
                logger.debug("Not existing: %s", key)
                continue

            if item[key] != value:
                if isinstance(value, bool):
                    logger.debug("Different (%s): '%s' != '%s'!", key, item[key], value)
                    differences.update({key: value})
                elif not item[key] and not value:
                    logger.debug("Different but empty fields (%s): '%s' != "
                                 "'%s' (brok), types: %s / %s",
                                 key, item[key], value, type(item[key]), type(value))
                else:
                    logger.debug("Different (%s): '%s' != '%s'!", key, item[key], value)
                    differences.update({key: value})
            else:
                logger.debug("Identical (%s): '%s'.", key, value)

        update = False
        if differences:
            logger.debug("%s / %s, some modifications exist: %s.",
                         endpoint, item['name'], differences)

            headers = {
                'Content-Type': 'application/json',
                'If-Match': item['_etag']
            }
            try:
                self.stats.counter('backend-patch.%s' % endpoint, 1)
                response = self.backend.patch('%s/%s' % (endpoint, item['_id']),
                                              differences, headers, True)
                if response['_status'] == 'ERR':  # pragma: no cover - should not happen
                    logger.warning("Update %s: %s failed, errors: %s.",
                                   endpoint, name, response['_issues'])
                else:
                    update = True
                    logger.debug("Updated %s: %s.", endpoint, name)
            except BackendException as exp:  # pragma: no cover - should not happen
                logger.error("Update %s '%s' failed", endpoint, name)
                logger.error("Data: %s", differences)
                logger.exception("Exception: %s", exp)
                if exp.code == 404:
                    logger.error('Seems the %s %s deleted in the Backend',
                                 endpoint, name)

        return update

    def update_program_status(self, brok):
        """Manage the whole program status change

        `program_status` brok is raised on program start whereas `update_program_status` brok
        is raised on every scheduler loop.

        `program_status` and `update_program_status` broks may contain:
        {
            # Some general information
            u'alignak_name': u'arbiter-master',
            u'instance_id': u'176064a1b30741d39452415097807ab0',
            u'instance_name': u'scheduler-master',

            # Some running information
            u'program_start': 1493969754,
            u'daemon_mode': 1,
            u'pid': 68989,
            u'last_alive': 1493970641,
            u'last_command_check': 1493970641,
            u'last_log_rotation': 1493970641,
            u'is_running': 1,

            # Some configuration parameters
            u'process_performance_data': True,
            u'passive_service_checks_enabled': True,
            u'event_handlers_enabled': True,
            u'command_file': u'',
            u'global_host_event_handler': None,
            u'interval_length': 60,
            u'modified_host_attributes': 0,
            u'check_external_commands': True,
            u'modified_service_attributes': 0,
            u'passive_host_checks_enabled': True,
            u'global_service_event_handler': None,
            u'notifications_enabled': True,
            u'check_service_freshness': True,
            u'check_host_freshness': True,
            u'flap_detection_enabled': True,
            u'active_service_checks_enabled': True,
            u'active_host_checks_enabled': True
        }

        :param brok: the brok
        :type brok:
        :return: None
        """
        if 'alignak_name' not in brok.data:
            logger.warning("Missing alignak_name in the brok data, "
                           "the program status cannot be updated. "
                           "Your Alignak framework version is too old to support this feature.")
            return
        if not self.default_realm:
            logger.warning("Missing Alignak backend default realm, "
                           "the program status cannot be updated. "
                           "Your Alignak backend is in a very bad state!")
            return

        # Set event handlers as strings - simple protectection
        if 'global_host_event_handler' in brok.data and \
                not isinstance(brok.data['global_host_event_handler'], basestring):
            brok.data['global_host_event_handler'] = str(brok.data['global_host_event_handler'])

        if 'global_service_event_handler' in brok.data and \
                not isinstance(brok.data['global_service_event_handler'], basestring):
            brok.data['global_service_event_handler'] = \
                str(brok.data['global_service_event_handler'])

        name = brok.data.pop('alignak_name')
        brok.data['name'] = name
        brok.data['_realm'] = self.default_realm

        params = {'sort': '_id', 'where': '{"name": "%s"}' % name}
        self.stats.counter('backend-getall.alignak', 1)
        all_alignak = self.backend.get_all('alignak', params)
        logger.debug("Got %d Alignak configurations for %s", len(all_alignak['_items']), name)

        headers = {'Content-Type': 'application/json'}
        if not all_alignak['_items']:
            try:
                self.stats.counter('backend-post.alignak', 1)
                response = self.backend.post('alignak', brok.data)
                if response['_status'] == 'ERR':  # pragma: no cover - should not happen
                    logger.warning("Create alignak: %s failed, errors: %s.",
                                   name, response['_issues'])
                else:
                    logger.info("Created alignak: %s.", name)
            except BackendException as exp:  # pragma: no cover - should not happen
                logger.error("Create alignak '%s' failed", name)
                logger.error("Data: %s", brok.data)
                logger.exception("Exception: %s", exp)
        else:
            item = all_alignak['_items'][0]
            for key in item:
                if key not in brok.data:
                    continue
                if item[key] == brok.data[key]:
                    brok.data.pop(key)
                    continue
                logger.debug("- updating: %s = %s", key, brok.data[key])

            if not brok.data:
                logger.debug("Nothing to update")
                return

            headers['If-Match'] = item['_etag']
            try:
                self.stats.counter('backend-patch.alignak', 1)
                response = self.backend.patch('alignak/%s' % (item['_id']),
                                              brok.data, headers, True)
                if response['_status'] == 'ERR':  # pragma: no cover - should not happen
                    logger.warning("Update alignak: %s failed, errors: %s.",
                                   name, response['_issues'])
                else:
                    logger.debug("Updated alignak: %s. %s", name, response)
            except BackendException as exp:  # pragma: no cover - should not happen
                logger.error("Update alignak '%s' failed", name)
                logger.error("Data: %s", brok.data)
                logger.exception("Exception: %s / %s", exp, exp.response)

    def manage_brok(self, brok=None):
        """
        We get the data to manage

        :return: False if broks were not managed by the module
        """
        if not self.backend_connected:
            logger.error("Not connected to the backend, ignoring brok...")
            return False

        if brok is None:
            logger.error("No brok to manage")
            return False

        brok.prepare()

        logger.debug("manage_brok receives a Brok:")
        logger.debug("\t-Brok type: {0}".format(brok.type))
        logger.debug("\t-Brok data: {0}".format(brok.data))

        try:
            if brok.type in ['new_conf']:
                self.get_refs()

            # Temporary: get concerned item for tracking received broks
            if 'contact_name' in brok.data:
                contact_name = brok.data['contact_name']
                if brok.data['contact_name'] not in self.mapping['user']:
                    logger.warning("Managing a brok %s for an unknown user: '%s'", brok.type, contact_name)
                    return False
            else:
                if 'host_name' in brok.data:
                    host_name = brok.data['host_name']
                    if brok.data['host_name'] not in self.mapping['host']:
                        logger.warning("Managing a brok %s for an unknown host: '%s'", brok.type, host_name)
                        return False
                    if 'service_description' in brok.data:
                        service_name = '__'.join([host_name, brok.data['service_description']])
                        if service_name not in self.mapping['service']:
                            logger.warning("Managing a brok %s for an unknown service: '%s'", brok.type, service_name)
                            return False

            start = time.time()
            self.stats.counter('managed-broks-type-count.%s' % brok.type, 1)

            if brok.type in ['program_status', 'update_program_status']:
                self.update_program_status(brok)

            # if brok.type == 'host_next_schedule':
            #     self.update_next_check(brok.data, 'host')
            #
            # if brok.type == 'service_next_schedule':
            #     self.update_next_check(brok.data, 'service')

            if brok.type in ['update_host_status', 'update_service_status', 'update_contact_status']:
                self.update_status(brok)

            if brok.type == 'host_check_result':
                self.update_livestate(brok.data, 'host')

            if brok.type == 'service_check_result':
                self.update_livestate(brok.data, 'service')

            if brok.type in ['acknowledge_raise', 'acknowledge_expire',
                             'downtime_raise', 'downtime_expire']:
                self.update_actions(brok)

            end = time.time()
            self.stats.timer('managed-broks-type-time.%s' % brok.type, end - start)
            logger.debug("brok type {0}, time: {1} s".format(brok.type, end - start))

            return True
        except Exception as exp:  # pragma: no cover - should not happen
            logger.exception("Manage brok exception: %s", exp)

        return False

    def update_actions(self, brok):
        """We manage the acknowledge and downtime broks

        :param brok: the brok
        :type brok:
        :return: None
        """
        host_name = brok.data['host']
        if host_name not in self.mapping['host']:
            logger.warning("Updating action for a brok for an unknown host: '%s'", host_name)
            return
        service_name = ''
        if 'service' in brok.data:
            service_name = '__'.join([host_name, brok.data['service']])
            if service_name not in self.mapping['service']:
                logger.warning("Updating action for a brok for an unknown service: '%s'", service_name)
                return

        data_to_update = {}
        endpoint = 'actionacknowledge'
        if brok.type == 'acknowledge_raise':
            data_to_update['ls_acknowledged'] = True
        elif brok.type == 'acknowledge_expire':
            data_to_update['ls_acknowledged'] = False
        elif brok.type == 'downtime_raise':
            data_to_update['ls_downtimed'] = True
            endpoint = 'actiondowntime'
        elif brok.type == 'downtime_expire':
            data_to_update['ls_downtimed'] = False
            endpoint = 'actiondowntime'

        where = {
            'processed': True,
            'notified': False,
            'host': self.mapping['host'][host_name],
            'comment': brok.data['comment'],
            'service': None
        }

        if 'service' in brok.data:
            # it's a service
            self.send_to_backend('livestate_service', service_name, data_to_update)
            where['service'] = self.mapping['service'][service_name]
        else:
            # it's a host
            self.send_to_backend('livestate_host', host_name, data_to_update)

        params = {
            'where': json.dumps(where)
        }
        self.stats.counter('backend-getall.%s' % endpoint, 1)
        actions = self.backend.get_all(endpoint, params)
        if actions['_items']:
            # case 1: the acknowledge / downtime come from backend, we update the 'notified' field
            # to True
            headers = {
                'Content-Type': 'application/json',
                'If-Match': actions['_items'][0]['_etag']
            }
            self.stats.counter('backend-patch.%s' % endpoint, 1)
            self.backend.patch(
                endpoint + '/' + actions['_items'][0]['_id'], {"notified": True}, headers, True)
        else:
            # case 2: the acknowledge / downtime do not come from the backend, it's an external
            # command so we create a new entry
            where['notified'] = True
            # try find the user
            self.stats.counter('backend-getall.user', 1)
            users = self.backend.get_all('user',
                                         {'where': '{"name":"' + brok.data['author'] + '"}'})
            if users['_items']:
                where['user'] = users['_items'][0]['_id']
            else:
                return

            if brok.type in ['acknowledge_raise', 'downtime_raise']:
                where['action'] = 'add'
            else:
                where['action'] = 'delete'
            where['_realm'] = self.ref_live['host'][where['host']]['_realm']

            if endpoint == 'actionacknowledge':
                if brok.data['sticky'] == 2:
                    where['sticky'] = False
                else:
                    where['sticky'] = True
                where['notify'] = bool(brok.data['notify'])
            elif endpoint == 'actiondowntime':
                where['start_time'] = int(brok.data['start_time'])
                where['end_time'] = int(brok.data['end_time'])
                where['fixed'] = bool(brok.data['fixed'])
                where['duration'] = int(brok.data['duration'])
            self.stats.counter('backend-post.%s' % endpoint, 1)
            self.backend.post(endpoint, where)


class MessageProcess(Process):
    def __init__(self, mod_conf, alias, stats, mapping, ref_live, message):
        """
        """
        super(MessageProcess, self).__init__()
        self.daemon = True

        self.message = message

        self.worker = Worker(mod_conf=mod_conf,
                             alias=alias,
                             stats=stats,
                             mapping=mapping,
                             ref_live=ref_live)

    def _unit_of_work(self, brok):
        """
        Run a single unit of work
        :return: bool
        """

        return self.worker.manage_brok(brok)

    def run(self):
        """
        Run the process
        :return: Nothing
        """
        start = time.time()
        managed = [self._unit_of_work(brok) for brok in self.message]
        end = time.time()
        # types = [brok.type for brok in self.message]
        goods = managed.count(True)
        bads = managed.count(False)
        logger.info("managing {0} broks in {1} secs [{2} goods | {3} bads]".format(len(self.message),
                                                                                   end - start,
                                                                                   goods,
                                                                                   bads))
