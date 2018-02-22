#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mostly Random WSGI Utilities.

"""
import sys
PY3K = sys.version_info[0] == 3

import socket, hashlib
try:
    #Py3
    from http.client import responses
    from http.cookies import SimpleCookie
except ImportError:
    from httplib import responses
    from Cookie import SimpleCookie

from webob.headers import ResponseHeaders
from datetime import datetime

from .request import HTTPRequest
from .exc import *

try:
    import chardet
except ImportError:
    # charset autodetection disabled
    pass

__all__ = (
        'sniff_content_encoding',
        'format_status_int',
        'IterableWSGIResponse', 
        'HTTPResponse',
        'HTTPFoundResponse',
        'HTTPSeeOtherResponse',
        'HTTPRedirectResponse',
        'HTTPNotModifiedResponse',
        'HTTPUnauthorizedResponse',
        'HTTPUnauthorized',
        'HTTPForbiddenResponse',
        'HTTPForbidden',
        'HTTPNotFound',
        )

def bytearray2str(obj, mode='replace'):
    obj.decode('utf8', errors=mode)
    return obj

def sniff_content_encoding(s, default='utf-8'):
    """
    Attempts to detect the character set of a string value ``s`` or 
    ``default`` if the ``chardet`` module is not found.

    """
    try:
        content_encoding = chardet.detect(s)['encoding']
    except (NameError, UnicodeDecodeError):
        content_encoding = default

    return content_encoding

def format_status_int(status_int):
    """
    Returns a string like "200 OK" if the status_int
    numeric value matches something in our internal
    map.
    
    """
    try:
        status_code = responses[int(status_int)]
    except (TypeError, KeyError):
        status_code = responses[500]    
    
    return "%s %s" % (status_int, status_code)

class IterableWSGIResponse(object):
    """
    A iterable WSGI object using a simple API inspired by Django
    ``HttpResponse``.
    
    >>>response = IterableWSGIResponse(content='hello world', mimetype='text/plain')
    """
    
    # default headers 
    headerClass = ResponseHeaders
    status_int = None
    #environ = HeaderDct([])


    def __init__(
        self, content='', request=None, status=None, headers=[], 
        mimetype='text/plain', charset='UTF-8', force_unicode=False, 
        cookies=None):
        """Create a new WSGI response instance.
        
        If ``force_unicode`` is set to ``False``, disable explicit
        multibyte conversion. (Binary files handlers may need this)
        """
        self.request = request
        self.mimetype = mimetype
        self.charset = charset
        # XXX workaround the broken unicode stuff in python 2.7.3 
        # note: wsgi require a str though

        if PY3K: # Python 3
            self.content = bytes(content, charset)
        elif not force_unicode:
            self.content = str(content)
        else:    
            #self.content = str(bytearray(content, charset).decode())
            self.content = unicode(content)

        #assert isinstance(content, bytes), type(content)
                
        # 14.15 - Content-MD5 (for integrity checking of
        # the entity-body)
        self.content_hash = str(hashlib.md5(content).hexdigest())

        # Get the HTTP status code human representation. 
        if status is not None and status >= 200:
            self.status_code = format_status_int(status)
        else:
            # by default attempt to use status_int
            #assert isinstance(self.status_int, int)
            self.status_code = format_status_int(self.status_int)
        
        #update status_int
        if not self.status_int:
            self.status_int = int(self.status_code[0:4])
        
        self.etag = self.content_hash
        
        #if request is not None and request.if_none_match:
        #    self.conditional = True
        #    self.if_none_match = request.environ['HTTP_IF_NONE_MATCH']
        #    #assert request.environ.has_key('HTTP_IF_NONE_MATCH') == True
        #else:
        #    self.conditional = False
        #    self.if_none_match = None

        # Provides a basic HTTP/1.1 headers set
        self.http_headers = self.headerClass([
            ('Content-Type', self.content_type),
            ('Content-Length', self.content_length),
            #('Content-MD5', self.content_hash),
            #('Cache-Control', 'max-age=%i' % (60 * 10)),
            ('Etag', self.etag)
        ])
    
        #if self.conditional:
        #    self.http_headers['ETag'] = self.etag

        #if len(headers) >= 1:
        #    for hdr in headers:
        #        if not hdr in self.http_headers:
        #            self.http_headers[hdr] = headers[hdr]
        
        # Handle cookies management
        if cookies is not None:
            for name, value in cookies:
                c = SimpleCookie()
                c[name] = value
                for item in c.itervalues():
                    item['domain'] = socket.getfqdn()
                    #item['path'] = '/'
                    self.http_headers.add('Set-Cookie', item.OutputString())

    # This __str__ silently borrowed from webob.Response.__str__...
    def __str__(self, skip_body=False):
        parts = [str(self.status)]
        parts += map('%s: %s'.__mod__, self.headers)
        if not skip_body and self.content != '':
            parts += ['', self.content]
        #outs = bytearray2str(bytearray(parts))
        return '\n'.join(parts)
    
    def __iter__(self):
        """Return a custom iterator type which iterates over the response."""  
        return iter([self.content])

    app_iter = property(__iter__)
    
    __await__ = __iter__

    def __len__(self):
        """Return the Content-length value (type int)."""
         
        return len(self.content)
    
    def __getitem__(self, k):
        """For foo = response['foo'] operations"""
        try:
            v = self.http_headers[k]
        except KeyError:
            return None
        else:
            return v
    
    def __setitem__(self, item, value):
        """For response['foo'] = 'Bar' operations"""
        try:
            self.http_headers[item] = value
        except:
            raise
            
    content_length = property(__len__)
    
    def __call__(self, environ, start_response):
        if_none_match = environ.get('HTTP_IF_NONE_MATCH', None)
        
        if if_none_match == self.etag:
            #print "request not modified!!!"
            start_response('304 Not Modified', [])
            return []
        else:
            #self.http_headers.add('ETag', self.etag)
            status_code = self.status_code
            start_response(status_code, self.headers)
            #assert isinstance(self.content, bytes)
            return self.app_iter

    def get_content_type(self):
        """Returns the current Content-type header"""
        return "%s; charset=%s" % (self.mimetype, self.charset)
    
    content_type = property(get_content_type)

    def write(self, text=''):
        """Writes characters (text) in the input buffer stream (body)"""
        if isinstance(text, basestring): 
            text.encode(self.charset)
        self.content += text
    
    def __next__(self):
        """ required method for being a proper iterator type """
        chunk = next(self.app_iter)

        #if isinstance(chunk, basestring):
        #    chunk.encode(self.charset)
        return chunk
    next = property(__next__)     
    
    def has_header(self, value):
        """ return True when ``value`` is found in self.headers (HTTP headers)
        """
        try:
            valueof = self.headers[value]
        except (KeyError, TypeError):
            return False
        else:
            return True
    
    @property        
    def headers(self):
        return [(hdr, str(val)) for hdr, val in self.http_headers.items()]

    @property    
    def status(self):
        return self.status_int 

HTTPResponse = IterableWSGIResponse
HTTPResponse.status_int = 200
#HTTPResponse.__doc__ = "HTTP 200 (OK)"


class HTTPFoundResponse(HTTPResponse):
    """HTTP 302 (Found)
    
    Requires one param: 
    * location: a URI string.
    """
    
    status_int = 302
    
    def __init__(self, location, **kwargs):
        kwargs['status'] = str(self.status_int)
        # Displays a short message to the user with a link to
        # the given resource URI
        kwargs['content'] = '''\
        <p>Click here to follow this redirect: <a href=\"%s\">Link</a></p>'''%location
        super(HTTPFoundResponse, self).__init__(**kwargs)
        
        #self.location = location     # location to redirect to

        #self.initial_kwargs = kwargs 
        self.http_headers['Location'] = location #.split('?next=')[1]
        self.http_headers['Cache-Control'] = 'no-cache' # Prevent caching redirects

    #def __call__(self, env, start_response):
    #    start_response(self.status_code, self.headers)
    #    return self.app_iter

HTTPRedirectResponse = HTTPFoundResponse # alias

class HTTPSeeOtherResponse(HTTPFoundResponse):
    """HTTP 303 (See Other)"""
    status_int = 303

class HTTPNotModifiedResponse(HTTPResponse):
    """HTTP 304 (Not Modified)"""
    status_int = 304

    def __init__(self, *args, **kwargs):
        super(HTTPNotModifiedResponse, self).__init__(*args, **kwargs)
        
        self.http_headers['Date'] = datetime.now().ctime()
            

        del self.http_headers['Content-Type']
    
        self.content = '';


class HTTPUnauthorizedResponse(HTTPResponse):
    """HTTP 401 (Unauthorized)"""
    status_int = 401

class HTTPForbiddenResponse(HTTPResponse):
    """HTTP 403 (Forbidden)"""
    status_int = 403

HTTPForbidden = HTTPForbiddenResponse

class HTTPNotFound(HTTPResponse):
    """HTTP 404 (Not Found)"""
    status_int = 404
