import logging
import threading

from python_agent.common import constants
from python_agent.packages.blinker import signal
from python_agent.test_listener.utils import Singleton

log = logging.getLogger(__name__)


class StateTracker(object):
    __metaclass__ = Singleton

    def __init__(self, config_data=None):
        self._lock = threading.Lock()
        if config_data and config_data.isInitialColor:
            self.__current_test_identifier = constants.INITIAL_COLOR
        else:
            self.__current_test_identifier = None
        log.info("Initialized State Tracker. Current Test Identifier: %s" % self.__current_test_identifier)

    @property
    def current_test_identifier(self):
        return self.__current_test_identifier

    def set_current_test_identifier(self, test_id):
        self._lock.acquire()
        if self.__current_test_identifier != test_id:
            old_test_identifier = self.__current_test_identifier
            self.__current_test_identifier = test_id

            test_identifier_signal = signal('test_identifier_changing')
            test_identifier_signal.send(
                old_test_identifier=old_test_identifier,
                new_test_identifier=test_id
            )
        self._lock.release()
