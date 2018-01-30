# -*- coding: utf-8 -*-

import socket
import pprint
from six.moves.socketserver import ThreadingMixIn
from six.moves.xmlrpc_client import ServerProxy, Transport
from six.moves.xmlrpc_server import SimpleXMLRPCServer, SimpleXMLRPCDispatcher, resolve_dotted_attribute
from six.moves.xmlrpc_server import MultiPathXMLRPCServer as BaseMultiPathXMLRPCServer


import logging
logger = logging.getLogger(__name__)


class TimeoutTransport(Transport):
    def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, *args, **kwargs):
        Transport.__init__(self, *args, **kwargs)
        self._timeout = timeout

    def make_connection(self, host):
        conn = Transport.make_connection(self, host)
        conn.timeout = self._timeout
        return conn


class XMLRPCClient(ServerProxy):
    """
    An XMLRPC client which support keyword arguments call
    Note: When using keyword argument call, it always pass a list as first argument, and a dictionary as a second,
          So it require the server support the this kind of argument structure
    """
    class MethodDispatcher:
        def __init__(self, send, name):
            self.__send = send
            self.__name = name

        def __getattr__(self, name):
            return XMLRPCClient.MethodDispatcher(self.__send, "%s.%s" % (self.__name, name))

        def __call__(self, *args, **kwargs):
            if kwargs:
                logger.debug("Send XMLRPC call: method=%s, params=(%s, %s)", self.__name, args, kwargs)
                return self.__send(self.__name, (args, kwargs))
            else:
                logger.debug("Send XMLRPC call: method=%s, params=%s", self.__name, args)
                return self.__send(self.__name, args)
   
    def __getattr__(self, name):
        return XMLRPCClient.MethodDispatcher(self._ServerProxy__request, name)
    
    def execute(self, name, args=(), kwargs=None):
        if kwargs is None:
            self.__getattr__(name)(*args)
        else:
            self.__getattr__(name)(*args, **kwargs)


class XMLRPCDispatcher(SimpleXMLRPCDispatcher):
    """
    add some log for debug
    """
    def _marshaled_dispatch(self, data, dispatch_method=None, path=None):
        setattr(self, "_path", path)
        return SimpleXMLRPCDispatcher._marshaled_dispatch(self, data, dispatch_method, path)
        
    def _dispatch(self, method, params):
        logger.info("Recv XMLRPC call: path=%s, method=%s, params=%s", getattr(self, "_path", None), method, params)
        try:
            return SimpleXMLRPCDispatcher._dispatch(self, method, params)
        except:
            logger.exception("")
            raise


class KeywordArgsXMLRPCDispatcher(SimpleXMLRPCDispatcher):
    """
    A dispatcher which support keyword arguments call
    It is not recommand to use if integrating with other languages because this is not a standard of the xmlrpc protocl.
    """
    def _dispatch(self, method, params):
        logger.info("Recv XMLRPC call: path=%s, method=%s, params=%s", getattr(self, "_path", None), method, params)
        func = None
        try:
            func = self.funcs[method]
        except KeyError:
            if self.instance is not None:
                if hasattr(self.instance, '_dispatch'):
                    return self.instance._dispatch(method, params)
                else:
                    try:
                        func = resolve_dotted_attribute(self.instance, method, self.allow_dotted_names)
                    except AttributeError:
                        pass

        if func is not None:
            try:
                params = params or ([], {})
                return func(*params[0], **params[1])
            except:
                logger.exception("")
                raise
        else:
            raise Exception('method "%s" is not supported' % method)


class XMLRPCServer(ThreadingMixIn, XMLRPCDispatcher, SimpleXMLRPCServer):
    def __init__(self, *args, **kwargs):
        SimpleXMLRPCServer.__init__(self, *args, **kwargs)


class KeywordArgsXMLRPCServer(ThreadingMixIn, KeywordArgsXMLRPCDispatcher, SimpleXMLRPCServer):
    def __init__(self, *args, **kwargs):
        SimpleXMLRPCServer.__init__(self, *args, **kwargs)


class MultiPathXMLRPCServer(BaseMultiPathXMLRPCServer):
    def __init__(self, *args, **kwargs):
        BaseMultiPathXMLRPCServer.__init__(self, *args, **kwargs)
        self.RequestHandlerClass.rpc_paths = ['/', '/RPC2']

    def add_dispatcher(self, path, dispatcher):
        logger.info("add dispatcher: path=%s", path)
        self.RequestHandlerClass.rpc_paths.append(path)
        self.dispatchers[path] = dispatcher
        logger.debug("current dispatchers: \n%s", pprint.pformat(self.dispatchers))
        return dispatcher

    def get_dispatcher(self, path):
        return self.dispatchers[path]

    def del_dispatcher(self, path):
        logger.info("remove dispatcher: path=%s", path)
        if path in self.RequestHandlerClass.rpc_paths:
            self.RequestHandlerClass.rpc_paths.remove(path)
            
        if path in self.dispatchers:
            del self.dispatchers[path]
        logger.debug("current dispatchers: \n%s", pprint.pformat(self.dispatchers))
