import os
import logging
import traceback
import json

logging.basicConfig(
    format='%(message)s',
    level=logging.ERROR
)


class StackdriverReporter(object):
    def __init__(self, service_name=None, service_version=None):
        self.service_name = service_name or os.environ.get('SERVICE_NAME', '')
        self.service_version = service_version or os.environ.get(
            'SERVICE_VERSION', '')

    def log_error(self, additional_fields=False, severity='error'):
        log_entry = {
            'serviceContext': {'service': self.service_name,
                               'version': self.service_version},
            'message': traceback.format_exc(),
            'severity': severity
        }

        if additional_fields and isinstance(additional_fields, dict):
            log_entry.update(additional_fields)

        payload = json.dumps(log_entry)

        logging.error(payload)
        return
