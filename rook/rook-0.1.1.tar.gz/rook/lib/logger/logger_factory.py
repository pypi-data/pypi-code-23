import logging
import os
import sys
import six

from .handlers import RookoutStreamHandler, RookoutFileHandler
from .namespace_serializer_handler import NamespaceSerializerHandler


class LoggerFactory(object):
    def __init__(self, name, log_level, file_name, stderr, log_to_remote, propagate_logs):

        # Get the logger we'll use
        self.main_logger = logging.getLogger(name)
        self.main_logger.propagate = propagate_logs
        self.main_logger.setLevel(log_level)

        # Add flush functionality to logger
        self.main_logger.flush = self.flush

        # Remove old handlers if they exist, to prevent duplicates which cause multiple log entries
        handlers_dupe_list = list(self.main_logger.handlers)
        for log_handler in handlers_dupe_list:
            self.main_logger.removeHandler(log_handler)

        # Configure formatting
        self.formatting = r'%(asctime)s - %(module)s:%(funcName)s@%(lineno)d - %(levelname)s - %(message)s'
        formatter = logging.Formatter(self.formatting)

        # Configure STD-ERR logging
        if stderr:
            console_stream = RookoutStreamHandler(sys.stderr)
            console_stream.setFormatter(formatter)
            self.main_logger.addHandler(console_stream)

        # GRPC logging
        self.main_logger.addHandler(NamespaceSerializerHandler())

        # Direct (HTTP) Remote logs
        if log_to_remote:
            from .remote_handler import RemoteHandler
            self.main_logger.addHandler(RemoteHandler())

        # Configure File logging
        if file_name:
            if os.path.isabs(file_name):
                abs_log_path = file_name
            else:
                if "darwin" in sys.platform:
                    abs_log_path = os.path.join(os.getenv("HOME"), file_name)
                elif sys.platform == "win32":
                    abs_log_path = os.path.join(os.environ['USERPROFILE'], file_name)
                else:
                    abs_log_path = os.path.join("/var/log", file_name)

            try:
                # Create directory if does not exist
                dirname = os.path.dirname(abs_log_path)
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)

                # file handler
                file_handler = RookoutFileHandler(abs_log_path, maxBytes=10 * 1024 * 1024, backupCount=4)
                file_handler.setFormatter(formatter)
                self.main_logger.addHandler(file_handler)
            except Exception:
                self.main_logger.exception("Failed to open log file: %s", abs_log_path)

    def flush(self):
        for handler in self.main_logger.handlers:
            handler.flush()

    def get_logger(self):
        """

        :rtype: logging.Logger
        """
        return self.main_logger
