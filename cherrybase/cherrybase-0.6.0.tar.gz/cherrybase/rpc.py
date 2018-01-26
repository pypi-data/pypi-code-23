# -*- coding: utf-8 -*-

import cherrypy
from cherrypy._cptools import ErrorTool
from cherrypy.lib import xmlrpcutil
import inspect
import sys
from . import utils
import logging
from .compat import PY3, unicode


class JsonRpcUtil(object):

    @staticmethod
    def get_jsonrpclib():
        import jsonrpclib as j
        return j

    @staticmethod
    def _set_response(body):
        """
        Метод для создания response объекта.
        :param body: string тело ответа сервиса
        """
        from cherrypy._cpcompat import ntob

        response = cherrypy.response
        response.status = '200 OK'
        response.body = ntob(body, 'utf-8')
        response.headers['Content-Type'] = 'text/json'
        response.headers['Content-Length'] = len(body)

    def respond(self, body, encoding='utf-8', rpcid=None):
        """
        Метод для создания success тела ответа JSON-RPC.
        :param body: ответ сервиса
        :param encoding: кодировка для преобразования в JSON
        :param rpcid: id обращения (по специфиикации JSON-RPC)
        """
        jsonrpclib = self.get_jsonrpclib()
        if not isinstance(body, jsonrpclib.Fault):
            body = (body,)
        self._set_response(jsonrpclib.dumps(body,
                                            methodresponse=True,
                                            rpcid=rpcid,
                                            encoding=encoding))

    def on_error(self, *args, **kwargs):
        """
        Метод для создания exception тела ответа JSON-RPC.
        """
        e = sys.exc_info()[1]
        if hasattr(e, 'args') and len(e.args) > 1:
            message = unicode(e.args[0])
            code = utils.to(int, e.args[1], 1)
        else:
            message = '{}: {}'.format(type(e).__name__, unicode(e))
            code = 1
        jsonrpclib = self.get_jsonrpclib()
        self._set_response(jsonrpclib.dumps(jsonrpclib.Fault(code, message)))


jsonrpcutil = JsonRpcUtil()


def _on_error(*args, **kwargs):
    e = sys.exc_info()[1]
    if hasattr(e, 'args') and len(e.args) > 1:
        message = unicode(e.args[0])
        code = utils.to(int, e.args[1], 1)
    else:
        message = '{}: {}'.format(type(e).__name__, unicode(e))
        code = 1
    xmlrpclib = xmlrpcutil.get_xmlrpclib()
    xmlrpcutil._set_response(xmlrpclib.dumps(xmlrpclib.Fault(code, message)))


cherrypy.tools.xmlrpc = ErrorTool(_on_error)
cherrypy.tools.jsonrpc = ErrorTool(jsonrpcutil.on_error)


def expose(entity):
    entity.__rpc_exposed = True
    return entity


class Introspection(object):
    '''
    Класс RPC-библиотеки, обспечивающей интроспекцию (system)
    '''

    def __init__(self, controller):
        self._controller = controller
        self.methods = {}

    def scan(self, obj=None, path='', prev=None):
        _obj = obj or self._controller
        if _obj == self._controller:
            self.methods = {}
        for member in inspect.getmembers(_obj):
            if member[0].startswith('_') or inspect.isclass(member[1]) or member[1] == prev or member[1] is None or isinstance(member[1], Controller):
                continue
            _path = '.'.join((path, member[0])) if path else member[0]
            if _path in self.methods or _obj in self.methods.values():
                continue
            if callable(member[1]) and getattr(member[1], '__rpc_exposed', False):
                self.methods[_path] = member[1].__doc__
            elif not inspect.ismethod(member[1]) and not inspect.isfunction(member[1]):
                self.scan(member[1], _path, _obj)

    @expose
    def listMethods(self):
        '''This method returns a list of the methods the server has, by name.'''
        return sorted(self.methods.keys())

    @expose
    def methodSignature(self, method):
        '''This method returns a description of the argument format a particular method expects.'''
        return 'undef'

    @expose
    def methodHelp(self, method):
        '''This method returns a text description of a particular method.'''
        if method not in self.methods:
            raise Exception('Unknown method "{0}"'.format(method))
        return self.methods[method] if self.methods[method] else ''


class Controller(object):
    '''
    Базовый класс контроллеров RPC-библиотек
    '''
    _cp_config = {'tools.xmlrpc.on': True}

    def __init__(self, introspection_factory=Introspection):
        if introspection_factory:
            self.system = introspection_factory(self)
            self.system.scan()

    def _find_method(self, name):
        result = self
        for attr in str(name).split('.'):
            result = getattr(result, attr, None)
            if not result:
                return None
        return result if getattr(result, '__rpc_exposed', False) else None

    def _call_method(self, method, name, args, vpath=None, parameters=None):
        '''Можно перекрыть в наследнике и переопределить поведение, например, проверить права и т.п.'''
        request = cherrypy.request
        request.app.log.error('call {}:{} {}'.format(
            '/'.join(vpath), name, args), 'RPC', logging.DEBUG)
        return method(*args)

    @cherrypy.expose
    def default(self, *vpath, **params):
        '''Обработчик по умолчанию'''
        cherrypy.request.body.fp.bytes_read = 0
        try:
            body = cherrypy.request.body.read()
            if not PY3:
                body = body if isinstance(body, str) else body.encode('utf-8')
            rpc_params, rpc_method = xmlrpcutil.get_xmlrpclib().loads(body)
        except:
            cherrypy.log.error('Parsing request error',
                               'RPC', logging.WARNING, True)
            raise Exception('Invalid request', -32700)

        method = self._find_method(rpc_method)
        if method:
            body = self._call_method(
                method, rpc_method, rpc_params, vpath, params)
        else:
            raise Exception('Method "{}" not found'.format(rpc_method), -32601)

        conf = cherrypy.serving.request.toolmaps['tools'].get('xmlrpc', {})
        xmlrpcutil.respond(
            body,
            conf.get('encoding', 'utf-8'),
            conf.get('allow_none', 0)
        )
        return cherrypy.serving.response.body


class JController(Controller):
    '''
    Класс контроллеров JSON-RPC
    '''

    _cp_config = {'tools.jsonrpc.on': True}

    @cherrypy.expose
    def default(self, *vpath, **params):
        '''Обработчик по умолчанию'''
        cherrypy.request.body.fp.bytes_read = 0
        try:
            body = cherrypy.request.body.read()
            rpc_result = jsonrpcutil.get_jsonrpclib().loads(
                body if isinstance(body, str) else body.encode('utf-8')
            )
            rpc_method = rpc_result['method']
            rpc_params = rpc_result.get('params', [])
            rpc_rpcid = rpc_result.get('id', None)
        except:
            cherrypy.log.error('Parsing request error',
                               'RPC', logging.WARNING, True)
            raise Exception('Invalid request', -32700)

        method = self._find_method(rpc_method)
        if method:
            body = self._call_method(
                method, rpc_method, rpc_params, vpath, params)
        else:
            raise Exception('Method "{}" not found'.format(rpc_method), -32601)

        conf = cherrypy.serving.request.toolmaps['tools'].get('xmlrpc', {})
        jsonrpcutil.respond(
            body,
            rpcid=rpc_rpcid,
            encoding=conf.get('encoding', 'utf-8')
        )
        return cherrypy.serving.response.body
