#!/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    #Py3
    from urllib.parse import unquote_plus
except ImportError:
    from urllib import unquote_plus

import cgi # XXX Not a hack anymore..
from webob.request import BaseRequest

from .multidict import MultiDict


__all__ = ['HTTPRequest']

class HTTPRequest(BaseRequest):
    """A generic HTTP request object."""
    
    def __init__(self, environ, charset=None, **kwargs):
        """provide a generic environment for HTTP requests"""
        super(HTTPRequest, self).__init__(environ, charset=charset, **kwargs)
        #if isinstance(environ, dict):
        #    self.wsgi_environ.update(environ)
        #self._environ['REQUEST_METHOD'] = method
        # parse the query string
        #if 'QUERY_STRING' in environ:
        #    import pdb; pdb.set_trace()
        #    self.query_args =  MultiDict(environ['QUERY_STRING'])
        #else:
        #    self.query_args = MultiDict()

    def get_remote_user(self):
        '''Subclasses should override this method to retrieve a User storage class
        programmatically.'''
        # Adds a copy of the user settings to the
        # session store
        user = self.environ.get('REMOTE_USER', None)
        return user
        #return self.remote_user

    @property
    def user(self):
        """Returns the current user as defined in environ['REMOTE_USER'] or
        None if not set"""
        return self.get_remote_user()

    def get_full_path(self):
        """Return the value of PATH_INFO, a web browser dependent
        HTTP header, or None if the value is not set"""

        try:
            p = unquote_plus(self.environ['PATH_INFO'])
        except KeyError:
            # invalid CGI environment
            return None
        return p    
            
    def get_POST(self):
        """Extracts data from a POST request
        Returns a dict instance with extracted keys/values pairs."""
        if not (self.method == 'POST' or 'wsgi.input' in self.environ):
            return {}
        fs_environ = self.environ.copy()
    
        fs = cgi.FieldStorage(fp=fs_environ['wsgi.input'],
            environ=fs_environ,
            keep_blank_values=True)
    
        return MultiDict.from_fieldstorage(fs)


    # extra public methods borrowed from Django
    def is_ajax(self):
        """check if the http request was transmitted with asyncronous (AJAX) transport"""
        if 'HTTP_X_REQUESTED_WITH' in self.environ:
            if self.environ['HTTP_X_REQUESTED_WITH'] is 'XMLHttpRequest':
                return True
        #print 'not ajax'        
        return False        

    
    def is_secure(self):
        return bool(self.environ.get("HTTPS") == "on")
    
    def get_session(self):
        return getattr(self, '_session')
    
    @property
    def method(self):
        return str(self.environ.get('REQUEST_METHOD'))
    
    @property
    def POST(self):
        return self.get_POST()
    
    @property
    def GET(self):
        return getattr(self, 'query_args', ())

    path_url = property(get_full_path)
