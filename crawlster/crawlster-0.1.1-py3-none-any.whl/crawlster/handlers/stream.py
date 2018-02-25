import sys
import pprint

from .base import BaseItemHandler


class StreamItemHandler(BaseItemHandler):
    def __init__(self, stream=sys.stdout):
        self.stream = stream
        super(StreamItemHandler, self).__init__()

    def handle(self, item):
        self.stream.write(pprint.pformat(item, indent=4) + '\n')
