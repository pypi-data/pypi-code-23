import logging

from python_agent.build_scanner.entities.environment_data import EnvironmentData
from python_agent.test_listener.entities.events_request import EventsRequest

log = logging.getLogger(__name__)


class EventsService(object):
    def __init__(self, config_data, backend_proxy):
        self.config_data = config_data
        self.backend_proxy = backend_proxy

    def send_events(self, events):
        try:
            log.info("Sending Events. Number Of Events: %s" % len(events))
            environment_data = EnvironmentData(self.config_data.labId, self.config_data.testStage)
            events_request = EventsRequest(self.config_data.customerId, self.config_data.appName,
                                           self.config_data.branchName, self.config_data.buildName, environment_data,
                                           events)
            self.backend_proxy.send_events(events_request)
            log.info("Sent Events to Server. Number Of Events: %s" % len(events))
        except Exception as e:
            log.exception("Failed Sending Events. Number Of Events: %s. error: %s" % (len(events), str(e)))
