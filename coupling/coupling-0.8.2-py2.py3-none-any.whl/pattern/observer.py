# -*- coding: utf-8 -*-

import threading
import six
from abc import ABCMeta, abstractmethod

import logging
logger = logging.getLogger(__name__)


@six.add_metaclass(ABCMeta)
class BaseObserver(object):
    @abstractmethod
    def update(self, subject):
        pass


@six.add_metaclass(ABCMeta)
class BaseSubject(object):
    @abstractmethod
    def __init__(self):
        self._observers = []
        self._lock = threading.Lock()

    def notify(self):
        with self._lock:
            for observer in self._observers:
                observer.update(self)

    def attach(self, observer):
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def detach(self, observer):
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
