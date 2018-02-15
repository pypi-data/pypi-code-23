from __future__ import unicode_literals

import json
import logging
import datetime

# from logging import config


class GrayLogJSONFormatter(logging.Formatter):
    """
    Default keys:
    name            Name of the logger (logging channel)
    levelno         Numeric logging level for the message (DEBUG, INFO,
                        WARNING, ERROR, CRITICAL)
    levelname       Text logging level for the message ("DEBUG", "INFO",
                        "WARNING", "ERROR", "CRITICAL")
    pathname        Full pathname of the source file where the logging
                        call was issued (if available)
    filename        Filename portion of pathname
    module          Module (name portion of filename)
    lineno          Source line number where the logging call was issued
                        (if available)
    funcName        Function name
    created         Time when the LogRecord was created (time.time()
                        return value)
    asctime         Textual time when the LogRecord was created
    msecs           Millisecond portion of the creation time
    relativeCreated Time in milliseconds when the LogRecord was created,
                        relative to the time the logging module was loaded
                        (typically at application startup time)
    thread          Thread ID (if available)
    threadName      Thread name (if available)
    process         Process ID (if available)
    message         The result of record.getMessage(), computed just as
                        the record is emitted
    args            Passed arguments
    exc_text        Formatted traceback exception
    stack_info
    """
    default_keys = {
        'name', 'levelno', 'levelname',
        'pathname', 'filename', 'module', 'lineno', 'funcName',
        'created', 'asctime', 'msecs', 'relativeCreated',
        'thread', 'threadName', 'process',
        'message',
        'exc_text', 'stack_info',
    }

    def __init__(self, fmt=None, datefmt=None, style='%',
                 source=None, keys=None, encoder=None):
        assert source, 'Empty source. You must specify the source.'

        super(GrayLogJSONFormatter, self).__init__(
            fmt=fmt, datefmt=datefmt, style=style)

        self.source = source
        self.keys = keys
        if encoder:
            self.encoder = logging.config._resolve(encoder)
        else:
            self.encoder = json.JSONEncoder

    def get_keys(self):
        return self.keys or self.default_keys

    def format(self, record):
        graylog_data = None
        if 'data' in record.__dict__:
            graylog_data = record.__dict__['data']

        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        message = self.formatMessage(record)

        data = {key: value for key, value in record.__dict__.items()
                if key in self.get_keys()}
        asctime = datetime.datetime.fromtimestamp(record.created).isoformat()
        data.update({
            'source': self.source,
            'asctime': asctime,
            'message': message,
            'data': graylog_data,
        })

        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

            data['exc_text'] = record.exc_text

        return json.dumps(data, cls=self.encoder)
