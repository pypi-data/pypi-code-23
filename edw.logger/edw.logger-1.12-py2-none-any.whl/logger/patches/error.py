import os
import logging
import json
from datetime import datetime

from zExceptions.ExceptionFormatter import format_exception
from AccessControl.SecurityManagement import getSecurityManager

from edw.logger.util import get_ip

EDW_LOGGER_ERRORS = os.environ.get(
    'EDW_LOGGER_ERRORS', 'true').lower() in ('true', 'yes', 'on')


logger = logging.getLogger("edw.logger")


def error_logger(self, info):
    strtype = str(getattr(info[0], '__name__', info[0]))
    if strtype in self._ignored_exceptions:
        return

    if not isinstance(info[2], basestring):
        tb_text = ''.join(
            format_exception(*info, **{'as_html': 0}))
    else:
        tb_text = info[2]

    url = None
    username = None
    request = getattr(self, 'REQUEST', None)
    if request:
        user = getSecurityManager().getUser()
        url = request.get("URL", None)
        username = user.getUserName()

    action = getattr(url, 'split', lambda sep: [''])('/')[-1]
    data = {
        "IP": get_ip(request),
        "User": username,
        "Date": datetime.now().isoformat(),
        "Type": "Error",
        "URL": url,
        "Action": action,
        "ErrorType": strtype,
        "Traceback": tb_text.decode('utf-8', 'ignore').encode('utf-8'),
        "LoggerName": logger.name
    }

    logger.error(json.dumps(data))


def error_wrapper(meth):
    """Log errors"""

    def extract(self, *args, **kwargs):
        error_logger(self, *args, **kwargs)
        return meth(self, *args, **kwargs)

    return extract

if EDW_LOGGER_ERRORS:
    from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
    SiteErrorLog.orig_raising = SiteErrorLog.raising
    SiteErrorLog.raising = error_wrapper(SiteErrorLog.raising)
