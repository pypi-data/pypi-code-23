import logging
import colorama

from .settings import LOGORAMA_COLORS


class ColoredStreamHandler(logging.StreamHandler):
    def emit(self, record):
        message = self.format(record)
        self.stream.write(LOGORAMA_COLORS[record.levelname] + message +
                          colorama.Style.RESET_ALL)
        self.stream.write(getattr(self, 'terminator', '\n'))
        self.flush()
