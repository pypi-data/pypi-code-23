"""
This is the interface for interacting with
the hrp web service.
"""

import logging
import json
from uw_hrp.dao import HRP_DAO
from restclients_core.exceptions import DataFailureException


logger = logging.getLogger(__name__)


def get_resource(url):
    response = HRP_DAO().getURL(url, {'Accept': 'application/json'})
    logger.info("%s ==status==> %s" % (url, response.status))

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    logger.debug("%s ==data==> %s" % (url, response.data))
    return response.data
