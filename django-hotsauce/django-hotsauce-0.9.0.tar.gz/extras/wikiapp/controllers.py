#!/usr/bin/env python
# -*- coding: utf-8 -*-

from MoinMoin.request import request_wsgi
from MoinMoin.server.server_wsgi import moinmoinApp
#from MoinMoin.server.server_wsgi import WsgiConfig as ConfigBase
from notmm.controllers.base import BaseController
#from notmm.utils.wsgilib import HTTPResponse
import logging
log = logging.getLogger(__name__)

__all__ = ['MoinMoinController']

#debug_moinmoin_version = '1.8.9'

class MoinMoinController(BaseController):
    """
    A BaseController extension serving a MoinMoin wiki app.
    """

    #debug = False
    logger = log

    def application(self, environ, start_response):
        """Creates a mini MoinMoin wiki handler with generic file 
        upload support.

        """
        return moinmoinApp(environ, start_response)
