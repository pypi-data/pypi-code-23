import logging
import threading

from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from python_agent.common import constants
from python_agent.packages import interval
from python_agent.packages.blinker import signal
from python_agent.test_listener.queues.events_queue import EventsQueue
from python_agent.test_listener.services.events_service import EventsService

try:
    from apscheduler.schedulers.gevent import GeventScheduler
    scheduler_class = GeventScheduler
    kwargs = {}
except:
    scheduler_class = BackgroundScheduler
    kwargs = {
        "executors": {'processpool': ProcessPoolExecutor(1)}
    }

log = logging.getLogger(__name__)


class EventsManager(object):
    def __init__(self, config_data, backend_proxy):
        self.config_data = config_data
        self.events_service = EventsService(config_data, backend_proxy)
        self.events_queue = EventsQueue(maxsize=constants.MAX_ITEMS_IN_QUEUE)
        self.watchdog = scheduler_class(**kwargs)
        self.watchdog.add_job(self.send_all, interval.IntervalTrigger(milliseconds=constants.INTERVAL_IN_MILLISECONDS))
        self._is_sending_lock = threading.Lock()

    def push_event(self, event):
        try:
            if not event:
                return
            self.events_queue.put(event)
            log.info("Pushed Event. Event: %s" % event)
        except Exception as e:
            log.exception("Failed Pushing Event: %s. Error: %s" % (event, str(e)))

    def send_all(self, *args, **kwargs):
        self._is_sending_lock.acquire()
        events = []
        try:
            events = self.events_queue.get_all()
            if not events:
                return
            log.info("Dequeued Events From Events Queue. Number Of Events: %s" % len(events))
            self.events_service.send_events(events)
        except Exception as e:
            log.exception("Failed Sending All Events. Number Of Events: %s. Error: %s " % (len(events), str(e)))
            self.events_queue.put_all(events)
        finally:
            self._is_sending_lock.release()

    def start(self):
        log.info("Starting Events Manager")
        try:
            self.watchdog.start()
            log.info("Started Events Watchdog")
            events_queue_full = signal('events_queue_full')
            events_queue_full.connect(self.send_all)
            log.info("Started Events Manager")
        except Exception as e:
            log.exception("Failed Starting Events Manager. error: %s" % str(e))

    def shutdown(self):
        log.info("Shutting Down Events Manager")
        try:
            self.send_all()
            self.watchdog.shutdown()
            log.info("Finished Shutting Down Events Manager")
        except Exception as e:
            log.exception("Failed Shutting Down Events Manager. Error: %s" % str(e))


