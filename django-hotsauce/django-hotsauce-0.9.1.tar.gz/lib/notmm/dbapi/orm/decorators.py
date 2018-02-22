#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008-2017 Etienne Robillard <tkadm30@yandex.com>
# All rights reserved.
"""Decorator functions to interact with Schevo databases"""

from functools import wraps
from notmm.controllers.schevo import SchevoController

__all__ = ('with_schevo_database',)


def with_schevo_database(dbname, controller_class=SchevoController):
    """
    Decorator that adds a schevo database object reference
    in the ``request.environ`` dictionary.

    """


    def decorator(view_func):
        @wraps(view_func)
        def _wrapper(*args, **kwargs):
            req = args[0]
            #assert isinstance(dbname, str), 'dbname should be a string, bummer!'
            wsgi_app = controller_class(req, dbname)
            #if isinstance(controller_class, ZODBController):
            #    prefix, dbname_ = dbname.rsplit('/', 1)
            #else:
            #    dbname_ = dbname
            #wsgi_app.init_request(args[0])
            #key = 'schevo.db.%s' % dbname_
            req.environ[wsgi_app.environ_key] = wsgi_app.db
            return view_func(req, **kwargs)
        #locals()['dbname'] = dbname    
        #print "dbname: %s" % dbname
        #return wraps(view_func)(_wrapper, **kwargs)
        return _wrapper
    return decorator

