import atexit
import logging
import signal
import sys
import uuid

from python_agent.common.http.backend_proxy import BackendProxy
from python_agent.test_listener.managers.events_manager import EventsManager
from python_agent.test_listener.managers.footprints_manager import FootprintsManager
from python_agent.test_listener.state_tracker import StateTracker
from python_agent.test_listener.utils import Singleton

log = logging.getLogger(__name__)


class AgentManager(object):
    __metaclass__ = Singleton

    def __init__(self, config_data=None):
        log.info("Initializing...")
        if not config_data:
            raise Exception("'config_data' must be provided")
        backend_proxy = BackendProxy(config_data)
        self.state_tracker = StateTracker(config_data)
        self.footprints_manager = FootprintsManager(config_data, backend_proxy)
        self.events_manager = EventsManager(config_data, backend_proxy)
        self.footprints_manager.start()
        self.events_manager.start()
        atexit.register(self.shutdown) 
        self.agent_started()
        # self.register_uwsgi_at_exit()

    def create_execution_id(self):
        return str(uuid.uuid4())

    def push_event(self, event):
        self.events_manager.push_event(event)

    def send_all(self):
        self.events_manager.send_all()
        self.footprints_manager.send_all()

    def shutdown(self):
        self.events_manager.shutdown()
        self.footprints_manager.shutdown()
        log.info("Finished Shutting Down Agent Manager")

    def get_trace_function(self):
        return self.footprints_manager.get_trace_function()

    def agent_started(self):
        self.push_event({
            "type": "agentStarted"
        })

    def register_uwsgi_at_exit(self):
        if 'uwsgi' in sys.modules:
            import uwsgi
            uwsgi_original_atexit_callback = getattr(uwsgi, 'atexit', None)

            def uwsgi_atexit_callback():
                self.shutdown()
                if uwsgi_original_atexit_callback:
                    uwsgi_original_atexit_callback()

            uwsgi.atexit = uwsgi_atexit_callback

