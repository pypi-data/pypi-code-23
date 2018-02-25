import json

from .base import BaseItemHandler


class JsonLinesHandler(BaseItemHandler):
    def __init__(self, filename):
        super(JsonLinesHandler, self).__init__()
        self.file_name = filename
        self.fp = None

    def initialize(self):
        self.fp = open(self.file_name, 'w')

    def handle(self, item):
        self.fp.write(json.dumps(item) + '\n')

    def finalize(self):
        self.fp.close()
