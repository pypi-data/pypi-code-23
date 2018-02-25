import logging
import threading
import time

from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from python_agent.common import constants
from python_agent.packages import interval
from python_agent.packages.blinker import signal
from python_agent.test_listener.managers.code_coverage_manager import CodeCoverageManager
from python_agent.test_listener.queues.footprints_queue import FootprintsQueue
from python_agent.test_listener.services.footprints_service import FootprintsService
from python_agent.test_listener.state_tracker import StateTracker
from python_agent.test_listener.utils import get_execution_id_from_identifier
from python_agent.test_listener.utils import get_test_name_from_identifier

try:
    from apscheduler.schedulers.gevent import GeventScheduler
    scheduler_class = GeventScheduler
    kwargs = {}
except:
    scheduler_class = BackgroundScheduler
    kwargs = {
        "executors": {'processpool': ProcessPoolExecutor(3)}
    }

log = logging.getLogger(__name__)


class FootprintsManager(object):
    def __init__(self, config_data, backend_proxy):
        self.config_data = config_data
        self.backend_proxy = backend_proxy
        self.footprints_service = FootprintsService(self.config_data, backend_proxy)
        self.footprints_queue = FootprintsQueue(maxsize=constants.MAX_ITEMS_IN_QUEUE)
        self.code_coverage_manager = CodeCoverageManager(config_data)
        self.watchdog = scheduler_class(**kwargs)
        self.watchdog.add_job(self.send_all, interval.IntervalTrigger(milliseconds=constants.INTERVAL_IN_MILLISECONDS))
        self.watchdog.add_job(self.send_current_partial_footprints, interval.IntervalTrigger(milliseconds=constants.INTERVAL_IN_MILLISECONDS))
        self.watchdog.add_job(self.get_active_execution, interval.IntervalTrigger(milliseconds=constants.ACTIVE_EXECUTION_INTERVAL_IN_MILLISECONDS))
        self._is_sending_lock = threading.Lock()
        self.has_active_execution = False

    def test_identifier_changing(self, sender, **kwargs):
        old_test_identifier = kwargs.get("old_test_identifier")
        new_test_identifier = kwargs.get("new_test_identifier")
        log.info("Test Identifier Changed. Old: %s. New: %s" % (old_test_identifier, new_test_identifier))
        self.get_and_enqueue_coverage(old_test_identifier)

    def send_current_partial_footprints(self):
        current_test_identifier = StateTracker().current_test_identifier
        if current_test_identifier:
            log.info("Enqueuing Current Partial Footprints. Test Identifier: %s" % current_test_identifier)
            self.get_and_enqueue_coverage(current_test_identifier)

    def get_and_enqueue_coverage(self, test_identifier):
        if not test_identifier:
            log.warning("Test Identifier is Null or Empty. Not Enqueuing Footprints")
            return
        try:
            log.info("Getting Footprints From Code Coverage Manager For Test: %s" % test_identifier)

            test_name = get_test_name_from_identifier(test_identifier)
            execution_id = get_execution_id_from_identifier(test_identifier)
            footprints = self.code_coverage_manager.get_footprints_and_clear()
            if footprints.get("methods") or footprints.get("lines"):
                self.footprints_queue.put({
                    "test_identifier": test_identifier,
                    "footprints": footprints,
                    "test_name": test_name,
                    "execution_id": execution_id,
                    "local_time": self.get_current_time_milliseconds()
                })
                log.info("Enqueued Test Coverage Item For Test: %s" % test_identifier)
        except Exception as e:
            log.exception("Failed Enqueuing Coverage. Test: %s. Error: %s" % (test_identifier, str(e)))

    def send_all(self, *args, **kwargs):
        self._is_sending_lock.acquire()
        try:
            if not self.should_send_footprints():
                return
            footprint_items = self.footprints_queue.get_all()
            if footprint_items:
                self.footprints_service.send_footprints(footprint_items)
            else:
                log.info("No Footprint Items. Nothing To Send")
        except Exception as e:
            log.exception("Failed Sending All Footprints. Error: %s" % str(e))
        finally:
            self._is_sending_lock.release()

    def start(self):
        log.info("Starting Footprints Manager")
        try:
            self.watchdog.start()
            self.get_active_execution()
            log.info("Started Footprints Watchdog")
            test_identifier_signal = signal('test_identifier_changing')
            test_identifier_signal.connect(self.test_identifier_changing)
            footprints_queue_full = signal('footprints_queue_full')
            footprints_queue_full.connect(self.send_all)
            log.info("Started Footprints Manager")
        except Exception as e:
            log.exception("Failed Starting Footprints Manager. Error: %s" % str(e))

    def shutdown(self):
        log.info("Shutting Down Footprints Manager")
        try:
            current_test_identifier = StateTracker().current_test_identifier
            self.get_and_enqueue_coverage(current_test_identifier)
            self.send_all()
            self.code_coverage_manager.shutdown()
            self.watchdog.shutdown()
            log.info("Finished Shutting Down Footprints Manager")
        except Exception as e:
            log.exception("Failed Shutting Down Footprints Manager. Error: %s" % str(e))

    def get_active_execution(self):
        self.has_active_execution = self.backend_proxy.has_active_execution(self.config_data.customerId, self.config_data.labId)

    def get_current_time_milliseconds(self):
        return int(round(time.time() * 1000))

    def should_send_footprints(self):
        if self.has_active_execution:
            log.info("Has active execution - send all footprints (include init)")
            return True

        current_test_identifier = StateTracker().current_test_identifier
        if current_test_identifier != constants.INITIAL_COLOR:
            log.info("No active execution, but found colored footprints - send footprints")
            return True

        log.info("No active execution and no colored footprints - not sending footprints")
        return False

    def get_trace_function(self):
        return self.code_coverage_manager.get_trace_function()

