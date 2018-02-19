#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import logging
import json
import traceback
from marshmallow import Schema, fields, post_dump

logger = logging.getLogger(__name__)


class HTTPException(Exception):
    """HTTPException"""

    def __init__(self, code, message, extra=None):
        Exception.__init__(self, code, message)
        self.code = code
        self.message = message
        self.extra = extra if extra else dict()
        self.msgid = self.extra.pop('msgid', None)
        try:
            self.extra['stack'] = self.extra.get(
                'stack', traceback.format_exc()
            )
        except:
            pass

    @classmethod
    def from_json(cls, content):
        data = HTTPExceptionValidator().load(content).data
        result = cls(
            message=data.get('message', "Internal Server Error"),
            extra=data.get('extra', None)
        )
        result.msgid = data.get('msgid', result.msgid)
        return result

    def __repr__(self):
        return "%s<code=%s, message=%s>" % (
            self.__class__.__name__,
            self.code,
            self.message
        )

    def __str__(self):
        return "Error %s: %s (extra=%s)" % (self.code, self.message, self.extra)


class HTTPExceptionValidator(Schema):
    """"""
    code = fields.Integer(required=True)
    message = fields.String(required=True)
    msgid = fields.String(dump_to="msg-id", load_from="msg-id")
    extra = fields.Dict()

    @post_dump
    def json_check(self, data):
        try:
            json.dumps(data)
            return data
        except Exception as exc:
            logger.error("Cannot serialize extra: {}".format(exc))


class Created(HTTPException):
    """201: Created"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            201,
            message if message else "Created",
            extra
        )


class Accepted(HTTPException):
    """202: Accepted"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            202,
            message if message else "Accepted",
            extra
        )


class NoContent(HTTPException):
    """204: No Content"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            204,
            message if message else "No Content",
            extra
        )


class NotModified(HTTPException):
    """304: Not Modified"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            304,
            message if message else "Not Modified",
            extra
        )


class ValidationError(HTTPException):
    """400: Validation error"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            400,
            message if message else "Validation error",
            extra
        )


class Unauthorized(HTTPException):
    """401: Unauthorized"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            401,
            message if message else "Unauthorized",
            extra
        )


class PaymentRequired(HTTPException):
    """402: Payment Required"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            402,
            message if message else "Payment Required",
            extra
        )


class Forbidden(HTTPException):
    """403: Forbidden"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            403,
            message if message else "Forbidden",
            extra
        )


class ServiceDisabled(HTTPException):
    """httpcode: Service Disabled"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            403,
            message if message else "Service Disabled",
            extra
        )


class NotFound(HTTPException):
    """404: Not Found"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            404,
            message if message else "Not Found",
            extra
        )


class MethodNotAllowed(HTTPException):
    """405: Method Not Allowed"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            405,
            message if message else "Method Not Allowed",
            extra
        )


class NotAcceptable(HTTPException):
    """406: Not Acceptable"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            406,
            message if message else "Not Acceptable", extra
        )


class ProxyAuthenticationRequired(HTTPException):
    """407: Proxy Authentication Required"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            407,
            message if message else "Proxy Authentication Required",
            extra
        )


class RequestTimeout(HTTPException):
    """408: Request Time-out"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            408,
            message if message else "Request Time-out",
            extra
        )


class Conflict(HTTPException):
    """409: Conflict"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            409,
            message if message else "Conflict",
            extra
        )


class Gone(HTTPException):
    """410: Gone"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            410,
            message if message else "Gone",
            extra
        )


class MisdirectedRequest(HTTPException):
    """421: Misdirected Request"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            421,
            message if message else "Misdirected Request",
            extra
        )


class InternalServerError(HTTPException):
    """500: Internal Server Error"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            500,
            message if message else "Internal Server Error",
            extra
        )


class ConfigurationError(HTTPException):
    """500: Configuration error"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            500,
            message if message else "Configuration error",
            extra
        )


class RemoteTaskFailed(HTTPException):
    """500: Remote Task Failed"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            500,
            message if message else "Remote Task Failed",
            extra
        )


class RemoteTaskNotFinished(HTTPException):
    """500: Remote task is not finished"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            500,
            message if message else "Remote task is not finished",
            extra
        )


class RemoteTaskTimeout(HTTPException):
    """500: Remote task is not finished"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            500,
            message if message else "Remote task timeout",
            extra
        )


class NotImplemented(HTTPException):
    """501: Not Implemented"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            501,
            message if message else "Not Implemented",
            extra
        )


class ProxyError(HTTPException):
    """502: Proxy Error"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            502,
            message if message else "Proxy Error",
            extra
        )


class ServiceUnavailable(HTTPException):
    """503: Service Unavailable"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            503,
            message if message else "Service Unavailable",
            extra
        )


class ServiceLocked(HTTPException):
    """503: Service locked"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            503,
            message if message else "Service locked",
            extra
        )


class GatewayTimeout(HTTPException):
    """504: Gateway Time-out"""

    def __init__(self, message=None, extra=None):
        HTTPException.__init__(
            self,
            504,
            message if message else "Gateway Time-out",
            extra
        )


HTTP_STATUS_CODES = {
    201: Created,
    202: Accepted,
    304: NotModified,
    400: ValidationError,
    401: Unauthorized,
    402: PaymentRequired,
    403: Forbidden,
    404: NotFound,
    405: MethodNotAllowed,
    406: NotAcceptable,
    407: ProxyAuthenticationRequired,
    408: RequestTimeout,
    409: Conflict,
    410: Gone,
    421: MisdirectedRequest,
    500: InternalServerError,
    501: NotImplemented,
    502: ProxyError,
    503: ServiceUnavailable,
    504: GatewayTimeout
}


def from_status(status, message=None, extra=None):
    """docstring for from_status"""
    if status in HTTP_STATUS_CODES:
        return HTTP_STATUS_CODES[status](message, extra)
    else:
        return HTTPException(
            status,
            message if message else "Unknown Error",
            extra
        )


# noinspection PyBroadException
def from_response(response, url):
    try:
        data = response.json()
        code = data.get('code', response.status_code)
        if code in HTTP_STATUS_CODES:
            return HTTP_STATUS_CODES[code].from_json(data)
        else:
            return HTTPException(**data)
    except:
        return from_status(
            response.status_code, response.text,
            extra=dict(url=url, response=response.text)
        )
