import logging, json
from datetime import datetime

TRANSLATION_TABLE = {
    'threadName': 'thread',
    'levelname': 'severity',
    'process': 'pid',
    'module': 'module',
    'pathname': 'source_file',
}


class JSONFormatter(logging.Formatter):
    def format(self, record):
        return self.to_json(record)

    def to_json(self, record):
        log_message = {'description': record.getMessage(),
                       'log_type': 'application_log'}
        for key, item in record.__dict__.items():
            if key in TRANSLATION_TABLE:
                log_message[TRANSLATION_TABLE[key]] = item
        if record.exc_info:
            log_message['stacktrace'] = self.formatException(record.exc_info)
        log_message['@timestamp'] = datetime.fromtimestamp(record.created).isoformat()
        return json.dumps(log_message)
