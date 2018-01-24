# Copyright 2015 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

import multiprocessing
import os
import signal
import sys

from futurist import periodics

from oslo_config import cfg
from oslo_log import log as logging
from oslo_reports import guru_meditation_report as gmr

from octavia.amphorae.drivers.health import heartbeat_udp
from octavia.common import service
from octavia.controller.healthmanager import health_manager
from octavia.controller.healthmanager import update_db
from octavia import version


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def hm_listener(exit_event):
    # TODO(german): stevedore load those drivers
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    udp_getter = heartbeat_udp.UDPStatusGetter(
        update_db.UpdateHealthDb(),
        update_db.UpdateStatsDb())
    while not exit_event.is_set():
        udp_getter.check()


def hm_health_check(exit_event):
    hm = health_manager.HealthManager(exit_event)

    @periodics.periodic(CONF.health_manager.health_check_interval,
                        run_immediately=True)
    def periodic_health_check():
        hm.health_check()

    health_check = periodics.PeriodicWorker(
        [(periodic_health_check, None, None)],
        schedule_strategy='aligned_last_finished')

    def hm_exit(*args, **kwargs):
        health_check.stop()
        hm.executor.shutdown()
    signal.signal(signal.SIGINT, hm_exit)
    LOG.debug("Pausing before starting health check")
    exit_event.wait(CONF.health_manager.heartbeat_timeout)
    health_check.start()


def main():
    service.prepare_service(sys.argv)

    gmr.TextGuruMeditation.setup_autorun(version)

    processes = []
    exit_event = multiprocessing.Event()

    hm_listener_proc = multiprocessing.Process(name='HM_listener',
                                               target=hm_listener,
                                               args=(exit_event,))
    processes.append(hm_listener_proc)
    hm_health_check_proc = multiprocessing.Process(name='HM_health_check',
                                                   target=hm_health_check,
                                                   args=(exit_event,))
    processes.append(hm_health_check_proc)

    LOG.info("Health Manager listener process starts:")
    hm_listener_proc.start()
    LOG.info("Health manager check process starts:")
    hm_health_check_proc.start()

    def process_cleanup(*args, **kwargs):
        LOG.info("Health Manager exiting due to signal")
        exit_event.set()
        os.kill(hm_health_check_proc.pid, signal.SIGINT)
        hm_health_check_proc.join()
        hm_listener_proc.terminate()

    signal.signal(signal.SIGTERM, process_cleanup)

    try:
        for process in processes:
            process.join()
    except KeyboardInterrupt:
        process_cleanup()
