import atexit

import signal

from python_agent.test_listener.executors.anonymous_execution import AnonymousExecution
from python_agent.test_listener.managers.footprints_manager import FootprintsManager
from python_agent.test_listener.state_tracker import StateTracker


class SendFootprintsAnonymousExecution(AnonymousExecution):

    def __init__(self, config_data, labid):
        super(SendFootprintsAnonymousExecution, self).__init__(config_data, labid)
        self.state_tracker = StateTracker(config_data)
        self.footprints_manager = FootprintsManager(config_data, self.backend_proxy)
        atexit.register(self.footprints_manager.send_all)
        signal.signal(signal.SIGQUIT, self.footprints_manager.send_all)
        signal.signal(signal.SIGTERM, self.footprints_manager.send_all)

    def execute(self):
        self.footprints_manager.get_active_execution()
        self.footprints_manager.send_current_partial_footprints()

