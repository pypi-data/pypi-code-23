# -*- coding: utf-8 -*-

import unittest
import logging_helper
from classutils.observer import (Observable,
                                 Observer,
                                 ObserverError)

logging = logging_helper.setup_logging()


class CheckObservable(Observable):
    pass


class CheckObserver(Observer):

    def __init__(self):
        self.dummy = None

    def notification(self,
                     **kwargs):
        if u'dummy' in kwargs:
            self.dummy = kwargs[u'dummy']


class CheckBadObserver(object):

    def notification(self,
                     **kwargs):
        pass


class CheckDeprecatedObserver(Observer):

    def notify(self,
               **kwargs):
        pass


class CheckBadDeprecatedObserver(object):

    def notify(self,
               **kwargs):
        pass


class UnObservable(object):
    pass


class TestObservable(unittest.TestCase):

    def setUp(self):
        self.observable = CheckObservable()

    def tearDown(self):
        for observer in self.observable.observers:
            self.observable.unregister_observer(observer)

    # Test Observer sub-classes
    def test_register_observer(self):
        self.observable.register_observer(CheckObserver())
        self.observable.register_observer(CheckDeprecatedObserver())

    def test_unregister_observer(self):
        obs = CheckObserver()
        obs_depr = CheckDeprecatedObserver()
        self.observable.register_observer(obs)
        self.observable.register_observer(obs_depr)

        self.assertIn(obs, self.observable.observers, u'')
        self.assertIn(obs_depr, self.observable.observers, u'')

        self.observable.unregister_observer(obs)
        self.observable.unregister_observer(obs_depr)

    # Test bad observers
    def test_bad_register_observer(self):
        self.observable.register_observer(CheckBadObserver())
        self.observable.register_observer(CheckBadDeprecatedObserver())

    def test_bad_unregister_observer(self):
        obs = CheckBadObserver()
        obs_depr = CheckBadDeprecatedObserver()
        self.observable.register_observer(obs)
        self.observable.register_observer(obs_depr)

        self.assertIn(obs, self.observable.observers, u'')
        self.assertIn(obs_depr, self.observable.observers, u'')

        self.observable.unregister_observer(obs)
        self.observable.unregister_observer(obs_depr)

    # Test registration observer missing required methods
    def test_register_non_observable(self):

        try:
            self.observable.register_observer(UnObservable())
            raise AssertionError(u'ObserverError not thrown')
        except ObserverError:
            pass

    # Test notifications
    def test_notify_observers(self):
        message = u'dummy_message'
        obs = CheckObserver()

        self.observable.register_observer(obs)
        self.observable.notify_observers(dummy=message)

        self.assertEquals(obs.dummy, message)


if __name__ == u'__main__':
    unittest.main()
