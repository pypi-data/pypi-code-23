#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SessionController API

Copyright (c) 2007-2011 Etienne Robillard
All rights reserved.

<LICENSE=ISC>
"""
from notmm.controllers.wsgi import WSGIController

__all__ = ['SessionController']

class SessionController(WSGIController):
    """
    A simple WSGI middleware which adds a ``session`` attribute
    to the current request instance.
    """
    def __init__(self, *args, **kwargs):
        super(SessionController, self).__init__(*args, **kwargs)
        
    #If we define a BeakerController extension the following would
    #make sense:
    def session_active(self, wsgi_app):
        return bool('beaker' in wsgi_app.environ.keys() == True)
