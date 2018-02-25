class BaseItemHandler(object):
    config_options = {}

    def __init__(self):
        self.crawler = None
        self.config = None

    def initialize(self):
        pass

    def handle(self, item):
        raise NotImplementedError()

    def finalize(self):
        pass
