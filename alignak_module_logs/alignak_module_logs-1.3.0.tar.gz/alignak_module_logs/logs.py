# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2048: Alignak contrib team, see AUTHORS.txt file for contributors
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
This module is an Alignak Broker module that collects the `monitoring_log` broks to send
them to a Python logger configured in the module configuration file
"""

import os
import json
import time
import Queue
import logging
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler
from logging.config import dictConfig as logger_dictConfig

from alignak.stats import Stats
from alignak.basemodule import BaseModule

from alignak_backend_client.client import Backend, BackendException

from alignak_module_logs.logevent import LogEvent

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name
for handler in logger.parent.handlers:
    if isinstance(handler, logging.StreamHandler):
        logger.parent.removeHandler(handler)

# pylint: disable=invalid-name
properties = {
    'daemons': ['broker'],
    'type': 'logs',
    'external': True,
    'phases': ['running'],
}


class UTCFormatter(logging.Formatter):
    """This logging formatter converts the log date/time to UTC"""
    converter = time.gmtime


def get_instance(mod_conf):
    """Return a module instance for the modules manager

    :param mod_conf: the module properties as defined globally in this file
    :return:
    """
    # logger.info("Give an instance of %s for alias: %s",
    # mod_conf.python_name, mod_conf.module_alias)

    return MonitoringLogsCollector(mod_conf)


class MonitoringLogsCollector(BaseModule):
    """Monitoring logs module main class"""
    def __init__(self, mod_conf):
        # pylint: disable=global-statement
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
        # Do not change log level for this module ...
        # logger.setLevel(getattr(mod_conf, 'log_level', logging.INFO))

        logger.debug("inner properties: %s", self.__dict__)
        logger.debug("received configuration: %s", mod_conf.__dict__)

        # Internal logger for the monitoring logs
        self.logger = None

        # Logger configuration file
        self.logger_configuration = os.getenv('ALIGNAK_MONITORING_LOGS_CFG', None)
        if not self.logger_configuration:
            self.logger_configuration = getattr(mod_conf, 'logger_configuration', None)
        if self.logger_configuration and self.logger_configuration != \
                os.path.abspath(self.logger_configuration):
            self.logger_configuration = os.path.abspath(self.logger_configuration)

        # Logger default parameters (used if logger_configuration is not defined)
        self.default_configuration = True
        self.log_logger_name = getattr(mod_conf, 'log_logger_name', 'monitoring-logs')
        self.log_dir = getattr(mod_conf, 'log_dir', '/tmp')
        self.log_file = getattr(mod_conf, 'log_file', 'monitoring-logs.log')
        self.log_filename = os.path.join(self.log_dir, self.log_file)
        self.log_rotation_when = getattr(mod_conf, 'log_rotation_when', 'midnight')
        self.log_rotation_interval = int(getattr(mod_conf, 'log_rotation_interval', '1'))
        self.log_rotation_count = int(getattr(mod_conf, 'log_rotation_count', '365'))
        self.log_level = getattr(mod_conf, 'log_level', 'INFO')
        self.log_level = getattr(logging, self.log_level, None)
        self.log_format = getattr(mod_conf, 'log_format ',
                                  '[%(created)i] %(levelname)s: %(message)s')
        self.log_date = getattr(mod_conf, 'log_date', '%Y-%m-%d %H:%M:%S %Z')

        if not self.logger_configuration and not self.log_dir and not self.log_file:
            logger.info("The logging feature is disabled")
        else:
            if self.logger_configuration:
                logger.info("logger configuration defined in %s",
                            self.logger_configuration)
                self.default_configuration = False
                if not os.path.exists(self.logger_configuration):
                    self.default_configuration = True
                    logger.warning("defined logger configuration file (%s) does not exist! "
                                   "Using default configuration.", self.logger_configuration)

            if self.default_configuration:
                logger.info("logger default configuration:")
                logger.info(" - rotating logs in %s", self.log_filename)
                logger.info(" - log level: %s", self.log_level)
                logger.info(" - rotation every %d %s, keeping %s files",
                            self.log_rotation_interval, self.log_rotation_when,
                            self.log_rotation_count)

            self.setup_logging()

        logger.info("StatsD configuration: %s:%s, prefix: %s, enabled: %s",
                    getattr(mod_conf, 'statsd_host', 'localhost'),
                    int(getattr(mod_conf, 'statsd_port', '8125')),
                    getattr(mod_conf, 'statsd_prefix', 'alignak'),
                    (getattr(mod_conf, 'statsd_enabled', '0') != '0'))
        self.statsmgr = Stats()
        self.statsmgr.register(self.alias, 'module',
                               statsd_host=getattr(mod_conf, 'statsd_host', 'localhost'),
                               statsd_port=int(getattr(mod_conf, 'statsd_port', '8125')),
                               statsd_prefix=getattr(mod_conf, 'statsd_prefix', 'alignak'),
                               statsd_enabled=(getattr(mod_conf, 'statsd_enabled', '0') != '0'))

        # Alignak Backend part
        # ---
        self.backend_available = False
        self.backend_connected = False
        self.backend_url = getattr(mod_conf, 'alignak_backend', '')
        if self.backend_url:
            logger.info("Alignak backend endpoint: %s", self.backend_url)

            self.client_processes = int(getattr(mod_conf, 'client_processes', '1'))
            logger.info("Number of processes used by backend client: %s", self.client_processes)

            self.backend_connected = False
            self.backend_connection_retry_planned = 0
            try:
                self.backend_connection_retry_delay = int(getattr(mod_conf,
                                                                  'backend_connection_retry_delay',
                                                                  '10'))
            except ValueError:
                self.backend_connection_retry_delay = 10
            self.backend_errors_count = 0
            self.backend_username = getattr(mod_conf, 'username', '')
            self.backend_password = getattr(mod_conf, 'password', '')
            self.backend_generate = getattr(mod_conf, 'allowgeneratetoken', False)
            self.backend_token = getattr(mod_conf, 'token', '')
            self.backend = Backend(self.backend_url, self.client_processes)

            if not self.backend.token and not self.backend_username:
                logger.warning("No Alignak backend credentials configured (empty token and "
                               "empty username. "
                               "The requested backend connection will not be available")
                self.backend_url = ''
            else:
                # Log in to the backend
                self.logged_in = False
                self.backend_connected = self.backend_connection()
                self.backend_available = self.backend_connected

                # Get the default realm
                self.default_realm = self.get_default_realm()

        else:
            logger.warning('Alignak Backend is not configured. '
                           'Some module features will not be available.')

    def init(self):
        """Handle this module "post" init ; just before it'll be started.

        Like just open necessaries file(s), database(s),
        or whatever the module will need.

        :return: None
        """
        return True

    def setup_logging(self):
        """Setup logging configuration

        :return: none
        """
        self.logger = logging.getLogger(self.log_logger_name)

        if self.default_configuration:
            # Set logger level
            self.logger.setLevel(self.log_level)

            logger.debug("Logger (default) handlers: %s", self.logger.handlers)
            if not self.logger.handlers:
                file_handler = TimedRotatingFileHandler(self.log_filename,
                                                        when=self.log_rotation_when,
                                                        interval=self.log_rotation_interval,
                                                        backupCount=self.log_rotation_count)
                file_handler.setFormatter(Formatter(self.log_format, self.log_date))
                self.logger.addHandler(file_handler)
                logger.debug("Logger (default), added a TimedRotatingFileHandler")
        else:
            with open(self.logger_configuration, 'rt') as my_logger_configuration_file:
                config = json.load(my_logger_configuration_file)
                # Update the declared log file names with the log directory
                for hdlr in config['handlers']:
                    if 'filename' in config['handlers'][hdlr]:
                        config['handlers'][hdlr]['filename'] = \
                            config['handlers'][hdlr]['filename'].replace("%(logdir)s", self.log_dir)
            try:
                logger_dictConfig(config)
            except ValueError as exp:
                logger.error("Logger configuration file is not parsable correctly!")
                logger.exception(exp)

    def backend_connection(self):
        """Backend connection to check live state update is allowed

        :return: True/False
        """
        if self.backend_login():
            self.get_default_realm()

            try:
                start = time.time()
                params = {'where': '{"token":"%s"}' % self.backend.token}
                users = self.backend.get('user', params)
                self.statsmgr.counter('backend-get.user', 1)
                self.statsmgr.timer('backend-get-time.user', time.time() - start)
            except BackendException as exp:
                logger.warning("Error on backend when retrieving user information: %s", exp)
            else:
                try:
                    for item in users['_items']:
                        self.logged_in = item['can_update_livestate']
                    return self.logged_in
                except Exception as exp:
                    logger.error("Can't get the user information in the backend response: %s", exp)

        logger.error("Configured user account is not allowed for this module")
        return False

    def backend_login(self):
        """Log in to the backend

        :return: bool
        """
        generate = 'enabled'
        if not self.backend_generate:
            generate = 'disabled'

        if self.backend_token:
            # We have a token, don't ask for a new one
            self.backend.token = self.backend_token
            connected = True  # Not really yet, but assume yes
        else:
            if not self.backend_username or not self.backend_password:
                logger.error("No user or password supplied, and no default token defined. "
                             "Can't connect to backend")
                connected = False
            else:
                try:
                    start = time.time()
                    connected = self.backend.login(self.backend_username, self.backend_password,
                                                   generate)
                    self.statsmgr.counter('backend-login', 1)
                    self.statsmgr.timer('backend-login-time', time.time() - start)
                except BackendException as exp:
                    logger.error("Error on backend login: %s", exp)
                    connected = False

        return connected

    def get_default_realm(self):
        """
        Retrieves the default top level realm for the connected user
        :return: str or None
        """
        default_realm = None

        if self.backend_connected:
            try:
                start = time.time()
                result = self.backend.get('/realm', {'max_results': 1, 'sort': '_level'})
                self.statsmgr.counter('backend-get.realm', 1)
                self.statsmgr.timer('backend-get-time.realm', time.time() - start)
            except BackendException as exp:
                logger.warning("Error on backend when retrieving default realm: %s", exp)
            else:
                try:
                    default_realm = result['_items'][0]['_id']
                except Exception as exp:
                    logger.error("Can't get the default realm in the backend response: %s", exp)

        return default_realm

    def do_loop_turn(self):  # pragma: no cover
        """This function is present because of an abstract function in the BaseModule class"""
        logger.info("In loop")
        time.sleep(1)

    def manage_brok(self, brok):
        """We got the data to manage

        :param brok: Brok object
        :type brok: object
        :return: False if a backend post error happens
        """
        # Ignore all except 'monitoring_log' broks...
        if brok.type not in ['monitoring_log']:
            return False

        level = brok.data['level'].lower()
        if level not in ['debug', 'info', 'warning', 'error', 'critical']:
            return False

        logger.debug("Got monitoring log brok: %s", brok)

        # Send to configured logger
        if self.logger:
            message = brok.data['message']
            message = message.replace('\r', '\\r')
            message = message.replace('\n', '\\n')
            func = getattr(self.logger, level)
            func(message)

        if not self.backend_url:
            return False

        if not self.backend_connected and int(time.time() > self.backend_connection_retry_planned):
            self.backend_connected = self.backend_connection()

        if not self.backend_connected:
            logger.error("Alignak backend connection is not available. Ignoring event.")
            return False

        # Try to get a monitoring event
        try:
            event = LogEvent(('[%s] ' % int(time.time())) + brok.data['message'])
            if event.valid:
                # -------------------------------------------
                # Add an history event
                self.statsmgr.counter('monitoring-event-get.%s' % event.event_type, 1)

                data = {}
                if event.event_type == 'TIMEPERIOD':
                    data = {
                        "host_name": 'n/a',
                        "service_name": 'n/a',
                        "user_name": "Alignak",
                        "type": "monitoring.timeperiod_transition",
                        "message": brok.data['message'],
                    }

                if event.event_type == 'NOTIFICATION':
                    data = {
                        "host_name": event.data['hostname'],
                        "service_name": event.data['service_desc'] or 'n/a',
                        "user_name": "Alignak",
                        "type": "monitoring.notification",
                        "message": brok.data['message'],
                    }

                if event.event_type == 'ALERT':
                    data = {
                        "host_name": event.data['hostname'],
                        "service_name": event.data['service_desc'] or 'n/a',
                        "user_name": "Alignak",
                        "type": "monitoring.alert",
                        "message": brok.data['message'],
                    }

                if event.event_type == 'DOWNTIME':
                    downtime_type = "monitoring.downtime_start"
                    if event.data['state'] == 'STOPPED':
                        downtime_type = "monitoring.downtime_end"
                    if event.data['state'] == 'CANCELLED':
                        downtime_type = "monitoring.downtime_cancelled"

                    data = {
                        "host_name": event.data['hostname'],
                        "service_name": event.data['service_desc'] or 'n/a',
                        "user_name": "Alignak",
                        "type": downtime_type,
                        "message": brok.data['message'],
                    }

                if event.event_type == 'FLAPPING':
                    flapping_type = "monitoring.flapping_start"
                    if event.data['state'] == 'STOPPED':
                        flapping_type = "monitoring.flapping_stop"

                    data = {
                        "host_name": event.data['hostname'],
                        "service_name": event.data['service_desc'] or 'n/a',
                        "user_name": "Alignak",
                        "type": flapping_type,
                        "message": brok.data['message'],
                    }

                if event.event_type == 'COMMENT':
                    data = {
                        "host_name": event.data['hostname'],
                        "service_name": event.data['service_desc'] or 'n/a',
                        "user_name": event.data['author'] or 'Alignak',
                        "type": "webui.comment",
                        "message": event.data['comment'],
                    }

                if data:
                    try:
                        logger.debug("Posting history data: %s", data)
                        start = time.time()
                        self.backend.post('history', data)
                        self.statsmgr.counter('monitoring-event-stored.%s' % event.event_type, 1)
                        self.statsmgr.timer('backend-post-time.history', time.time() - start)
                    except BackendException as exp:
                        logger.exception("Exception: %s", exp)
                        logger.error("Exception response: %s", exp.response)
                        return False
                else:
                    self.statsmgr.counter('monitoring-event-ignored.%s' % event.event_type, 1)
                    logger.debug("Monitoring event not stored in the backend: %s",
                                 brok.data['message'])
            else:
                logger.warning("No monitoring event detected from: %s", brok.data['message'])
        except ValueError:
            logger.warning("Unable to decode a monitoring event from: %s", brok.data['message'])

        return True

    def main(self):
        """Main loop of the process

        This module is an "external" module
        :return:
        """
        # Set the OS process title
        self.set_proctitle(self.alias)
        self.set_exit_handler()

        logger.info("starting...")

        while not self.interrupted:
            try:
                queue_size = self.to_q.qsize()
                if queue_size:
                    logger.debug("queue length: %s", queue_size)
                    self.statsmgr.gauge('queue-size', queue_size)

                message = self.to_q.get_nowait()
                start = time.time()
                for brok in message:
                    # Prepare and manage each brok in the queue message
                    brok.prepare()
                    self.manage_brok(brok)

                logger.debug("time to manage %s broks (%d secs)", len(message), time.time() - start)
                self.statsmgr.timer('managed-broks-time', time.time() - start)
            except Queue.Empty:
                # logger.debug("No message in the module queue")
                time.sleep(0.1)

        logger.info("stopping...")

        # Properly close all the Python logging stuff
        # fixme: this seems to make the alignak daemon hung when shutting down...
        # probably because it is running as a daemon.
        # See: http://stackoverflow.com/questions/24816456/python-logging-wont-shutdown
        logging.shutdown()

        logger.info("stopped")
