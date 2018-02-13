import logging

class ClientMock():
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def __getattr__(self, name):
        self.logger.info("Not executing %s" % name)
        return self.noop

    def noop(self, *args, **kwargs):
        return