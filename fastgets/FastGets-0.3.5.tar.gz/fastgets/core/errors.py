
from werkzeug.exceptions import HTTPException
from flask import jsonify


class ApiError(HTTPException):

    def __init__(self, msg='', code=1):
        HTTPException.__init__(self)
        self.response = jsonify(dict(error_code=code, error_msg=msg))


class CrawlError(Exception):

    def __init__(self, traceback):
        self.traceback = traceback


class ProcessError(Exception):

    def __init__(self, traceback):
        self.traceback = traceback


class WriteError(Exception):
    pass


class NotSupported(Exception):
    pass


class ParseError(Exception):
    pass


class FrameError(Exception):
    pass


class NoCookiesError(Exception):
    pass


class NoProxyError(Exception):
    pass
