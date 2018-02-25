import logging
import threading
from abc import ABCMeta, abstractmethod

try:
    from coverage import Coverage
except ImportError:
    from coverage import coverage as Coverage

log = logging.getLogger(__name__)


class FootprintsCollector(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_footprints_and_clear(self, test_coverage):
        raise NotImplementedError("Please Implement this method")

