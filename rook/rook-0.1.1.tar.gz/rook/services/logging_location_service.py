import logging
import six
import sys
import inspect
import os
import threading

from rook.interfaces.config import LoggingServiceConfig

from rook.lib.logger import logger

from rook.lib.processor.namespaces.container_namespace import ContainerNamespace
from rook.augs.processor_extensions.namespaces.log_record_namespace import LogRecordNamespace


class LoggingLocationService(object):

    NAME = "logging"

    class Handler(logging.Handler):

        def __init__(self, name):
            super(LoggingLocationService.Handler, self).__init__()

            self._name = name

            self._logger = logging.getLogger(name)
            self._old_remove_handler = self._logger.removeHandler

            # Do not allow us to be removed
            def removeHandler(handler):
                if handler != self:
                    self._old_remove_handler(handler)
            self._logger.removeHandler = removeHandler

            self._logger.addHandler(self)

            self._augs = {}
            self._lock = threading.RLock()

        def close(self):
            self._logger.removeHandler = self._old_remove_handler
            self._logger.removeHandler(self)

        def emit(self, record):
            try:
                frame = self._get_frame(record)
                extracted = ContainerNamespace({'log_record': LogRecordNamespace(record)})

                with self._lock:
                    for aug in six.itervalues(self._augs):
                        aug.execute(frame, extracted)
            except:
                logger.exception("Error while processing log record")

        def add_aug(self, aug):
            with self._lock:
                self._augs[aug.aug_id] = aug

                aug.set_active()

        def remove_aug(self, aug_id):
            with self._lock:
                try:
                    aug = self._augs[aug_id]
                except KeyError:
                    return

                del self._augs[aug_id]
                aug.set_removed()

        def clear_augs(self):
            with self._lock:
                aug_ids = list(self._augs.keys())

                for aug_id in aug_ids:
                    self.remove_aug(aug_id)

        def empty(self):
            return len(self._augs) == 0

        def _get_frame(self, record):
            # Skip the top two frames (ours)
            frame = inspect.currentframe().f_back.f_back

            while hasattr(frame, "f_code"):
                filename = os.path.normcase(frame.f_code.co_filename)
                if filename == logging._srcfile:
                    frame = frame.f_back
                else:
                    return frame

            return None

    def __init__(self):
        if LoggingServiceConfig.BASIC_CONFIG_ROOT and len(logging.root.handlers) == 0:
            logging.basicConfig()

        self._handlers = dict()
        self._lock = threading.RLock()

    def add_logging_aug(self, logger, aug):
        with self._lock:
            try:
                handler = self._handlers[logger]
            except KeyError:
                handler = self.Handler(logger)
                self._handlers[logger] = handler

        handler.add_aug(aug)

    def remove_aug(self, aug_id):
        with self._lock:
            for handler in six.itervalues(self._handlers):
                handler.remove_aug(aug_id)

        self.prune_handlers()

    def clear_augs(self):
        with self._lock:
            for handler in six.itervalues(self._handlers):
                handler.clear_augs()

        self.prune_handlers()

    def prune_handlers(self):
        with self._lock:
            loggers_to_prune = [logger for logger, handler in six.iteritems(self._handlers) if handler.empty()]

            for logger in loggers_to_prune:
                self._handlers[logger].close()
                del self._handlers[logger]

    def close(self):
        self.clear_augs()
