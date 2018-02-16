from typing import Callable

from tornado.web import RequestHandler
import json

def error_decorator(func:Callable) -> Callable:
    def resp_error(handler:RequestHandler, code=500, message=None, *args, **kwargs):
        handler.clear()
        handler.logger.info(f"resp({handler.requ_id}): {code}")
        handler.set_status(code, reason=message)
        if not (message is None):
            handler.logger.warning(f"resp({handler.requ_id}): {message}")
        func(handler, code, message, *args, **kwargs)
        handler.finish()
    return resp_error

def success_decorator(func):
    def resp_success(handler:RequestHandler, code=200, message=None, result=None, *args, **kwargs):
        handler.logger.info(f"resp({handler.requ_id}): {code}")
        handler.set_status(code, reason=message)
        if not (message is None):
            handler.logger.debug(f"resp({handler.requ_id}): {message}")
        if not (result is None):
            handler.logger.debug(f"resp({handler.requ_id}): {result}")
        func(handler, code, message, result, *args, **kwargs)
    return resp_success

class BasicResponder:
    """
    Works ONLY for the Logged_RequestHandler's
    """
    @staticmethod
    @error_decorator
    def resp_error(handler:RequestHandler, code, message):
        pass
    @staticmethod
    @success_decorator
    def resp_success(handler:RequestHandler, code, message, result):
        pass
    
class TextBasicResponder(BasicResponder):
    @staticmethod
    @error_decorator
    def resp_error(handler:RequestHandler, code=500, message=None):
        handler.send_error(code, reason=message)

    @staticmethod
    @success_decorator
    def resp_success(handler:RequestHandler, code=200, message=None, result=None):
        if (result):
            handler.set_header('Content-Type', 'text/plain')
            handler.write(bytes(str(result), 'utf8'))


class HtmlBasicResponder(BasicResponder):
    @staticmethod
    @error_decorator
    def resp_error(handler: RequestHandler, code=500, message=None):
        handler.send_error(code, reason=message)
    
    @staticmethod
    @success_decorator
    def resp_success(handler: RequestHandler, code=200, message=None, result=None):
        if (not result is None):
            handler.set_header('Content-Type', 'text/html')
            _html = f'<html><title>{code}: {message}</title><body>{str(result)}</body></html>'
            handler.write(bytes(_html, 'utf8'))

class JsonBasicResponder(BasicResponder):
    @staticmethod
    @error_decorator
    def resp_error(handler:RequestHandler, code=500, message=None):
        handler.set_status(code)
        handler.set_header('Content-Type', 'application/json')
        _json = { 'success': False, 'reason': message, 'code': code }
        handler.write(bytes(json.dumps(_json), 'utf8'))

    @staticmethod
    @success_decorator
    def resp_success(handler:RequestHandler, code=200, message=None, result=None):
        handler.set_header('Content-Type', 'application/json')
        _json = { 'success': True, 'code': code, 'result': result }
        if (not message is None):
            _json['message'] = message
        handler.write(bytes(json.dumps(_json), 'utf8'))
