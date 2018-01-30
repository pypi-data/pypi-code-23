import logging
from numbers import Number
from http.client import responses as http_codes
__author__ = 'Benjamin P. Trachtenberg'
__copyright__ = "Copyright (c) 2018, Benjamin P. Trachtenberg"
__credits__ = 'Benjamin P. Trachtenberg'
__license__ = 'MIT'
__status__ = 'prod'
__version_info__ = (1, 0, 0, __status__)
__version__ = '.'.join(map(str, __version_info__))
__maintainer__ = 'Benjamin P. Trachtenberg'
__email__ = 'e_ben_75-python@yahoo.com'
LOGGER = logging.getLogger(__name__)


class OperationFailed(Exception):
    _OPERATIONS = dict(
        HEAD="get header",
        GET="download",
        PUT="upload",
        DELETE="delete",
        MKCOL="create directory",
        PROPFIND="list directory",
        )

    def __init__(self, method, path, expected_code, actual_code):
        self.method = method
        self.path = path
        self.expected_code = expected_code
        self.actual_code = actual_code
        operation_name = self._OPERATIONS[method]
        self.reason = 'Failed to {operation_name} "{path}"'.format(**locals())
        expected_codes = (expected_code,) if isinstance(expected_code, Number) else expected_code
        expected_codes_str = ", ".join('{0} {1}'.format(code, http_codes.get(code, 'UNKNOWN')) for code in expected_codes)
        actual_code_str = http_codes.get(actual_code, 'UNKNOWN')
        msg = '''
        {self.reason}.
             Operation     :  {method} {path}
             Expected code :  {expected_codes_str}
             Actual code   :  {actual_code} {actual_code_str}'''.format(**locals())
        LOGGER.critical(msg)


class BadPortNumber(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        LOGGER.critical(self.value)
        return repr(self.value)


class NotNumber(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        LOGGER.critical(self.value)
        return repr(self.value)


class CouldNotDetermineProtocol(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        LOGGER.critical(self.value)
        return repr(self.value)