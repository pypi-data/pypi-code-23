# pylint: disable=W1201,C0103

import logging

class _Motor:
    def __init__(self, name=None):
        self.name = name
        if not name:
            self.name = 'all'
            self.one = _Motor('one')
            self.two = _Motor('two')

    def invert(self):
        logging.debug(self.name + ' invert')

    def forwards(self, speed=100):
        logging.debug(self.name + ' forwards ' + str(speed))

    def backwards(self, speed=100):
        logging.debug(self.name + ' backwards ' + str(speed))

    def speed(self, speed):
        logging.debug(self.name + ' speed ' + str(speed))

    def stop(self):
        logging.debug(self.name + ' stop')

motor = _Motor()
