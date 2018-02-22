#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <LICENSE=ISC>
#
"""
Authentication and Authorization API 0.5.0

This is a thin wrapper on top of LibAuthKit to allow easy
integration with Django-based apps.
"""

from authkit.authenticate import middleware as auth_middleware
from authkit.authorize import NotAuthenticatedError
from notmm.utils.wsgilib import HTTPRequest, HTTPResponse

from session import SessionController

__all__ = ['AuthCookieController', 'LoginController']

class AuthCookieController(SessionController):
    """
    Authentication controller to delegate authorization to generic
    user-defined backends.
    
    """

    request_class = HTTPRequest
    response_class = HTTPResponse

    def __init__(self, wsgi_app, auth_conf=None, **kwargs):
            
        #super(AuthCookieController, self).__init__(**kwargs)

        #put a pointer on the previous wsgi app in the stack
        #self.wsgi_app = wsgi_app

        self.application = auth_middleware(wsgi_app(),
            app_conf=auth_conf,
            cookie_secret='secret string',
            handle_httpexception=True,
            valid=self.authenticate,
            #enforce=self.auth_conf['enforce']
            )
        
        #try to enforce cookie user setter here
        #self.auth_conf_wrapper = make_cookie_user_setter(wsgi_app, auth_conf)

    def authenticate(self, username, password):
        """
        Authenticate with the provided ``username`` and ``password``. 
        
        Developers are expected to override this method in custom
        authentication subclasses.
        """

        if username == password:
            return username
        else:
            return None

LoginController = AuthCookieController
