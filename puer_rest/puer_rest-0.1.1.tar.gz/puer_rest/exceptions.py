from json import dumps
from aiohttp.web_exceptions import HTTPException


class APIError(HTTPException):
    status_code = None
    empty_body = False

    def __init__(self, errors=None):
        kwargs = dict()
        kwargs["content_type"] = "application/json"
        kwargs["body"] = dumps({
            "errors": errors or []
        })
        super().__init__(**kwargs)


class InvalidAuthorizationError(APIError):
    status_code = 401


class APIInvalidJSONError(APIError):
    status_code = 400

    def __init__(self):
        super().__init__({"request": "Not valid JSON"})


class APIBadRequest(APIError):
    status_code = 400


class APINeedPermissions(APIError):
    status_code = 403


class APINotFound(APIError):
    status_code = 404

    def __init__(self):
        super().__init__({"request": "Document with requested ID doesn't exist"})


class APIContentTypeError(APIError):
    status_code = 400

    def __init__(self):
        super().__init__({"request": "Content-Type must be 'application/json'"})
