# Copyright (C) 2018 Bonsai, Inc.

import abc
import logging

from tornado.ioloop import IOLoop

from bonsai_ai.simulator_ws import Simulator_WS

log = logging.getLogger(__name__)

_CONNECT_TIMEOUT_SECS = 60


class Simulator(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, brain, name):
        self.name = name
        self.brain = brain
        self._ioloop = IOLoop.current()
        self._impl = Simulator_WS(brain, self, name)

    def __repr__(self):
        return '{{'\
            'name: {self.name!r}, ' \
            'objective_name: {self._impl.objective_name!r}, ' \
            'predict: {self.predict!r}, ' \
            'brain: {self.brain!r}' \
            '}}'.format(self=self)

    @property
    def predict(self):
        return self.brain.config.predict

    @abc.abstractmethod
    def episode_start(self, episode_parameters):
        ''' callback for episode start messages '''
        return {}  # initial_state

    @abc.abstractmethod
    def simulate(self, action, state):
        ''' callback for simulate messages '''
        return {}  # state, reward, terminal

    def standby(self, reason):
        log.info(reason)

    def run(self):
        # take one pass through the loop
        success = self._ioloop.run_sync(self._impl.run, 1000)
        return success
