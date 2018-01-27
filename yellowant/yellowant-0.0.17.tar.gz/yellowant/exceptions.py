# -*- coding: utf-8 -*-

"""
yellowant.exceptions
~~~~~~~~~~~~~~~~~~

This module contains YellowAnt specific Exception classes.
"""

from .endpoints import YELLOWANT_HTTP_STATUS_CODE


class YellowAntError(Exception):
    """Generic error class, catch-all for most YellowAnt issues.
    Special cases are handled by YellowAntAuthError & YellowAntRateLimitError.

    from yellowant import YellowAntError, YellowAntRateLimitError, YellowAntAuthError

    """
    def __init__(self, msg, error_code=None, retry_after=None):
        self.error_code = error_code

        if error_code is not None and error_code in YELLOWANT_HTTP_STATUS_CODE:
            msg = 'YellowAnt API returned a %s (%s), %s' % \
                  (error_code,
                   YELLOWANT_HTTP_STATUS_CODE[error_code][0],
                   msg)

        super(YellowAntError, self).__init__(msg)

    @property
    def msg(self):  # pragma: no cover
        return self.args[0]


class YellowAntAuthError(YellowAntError):
    """Raised when you try to access a protected resource and it fails due to
    some issue with your authentication.

    """
    pass


class YellowAntRateLimitError(YellowAntError):  # pragma: no cover
    """Raised when you've hit a rate limit.

    The amount of seconds to retry your request in will be appended
    to the message.

    """
    def __init__(self, msg, error_code, retry_after=None):
        if isinstance(retry_after, int):
            msg = '%s (Retry after %d seconds)' % (msg, retry_after)
        YellowAntError.__init__(self, msg, error_code=error_code)

        self.retry_after = retry_after


class YellowAntStreamError(YellowAntError):
    """Raised when an invalid response from the Stream API is received"""
    pass


class YellowAntCronAuthError(YellowAntError):
    """Raised when you try to access a protected resource and it fails due to
    some issue with your authentication.

    """
    pass


class YellowAntCronRateLimitError(YellowAntError):
    """Raised when you try to access a protected resource and it fails due to
    some issue with your authentication.

    """
    pass