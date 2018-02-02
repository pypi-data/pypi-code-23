"""Util exceptions.

To be used with the utils.views classes.
Raising these exceptions within the view will return the appropriate
response.
"""
__all__ = [
    'APIException',
    'APIBadRequestException',
    'APIUnauthorizedException',
    'APIForbiddenException',
    'APINotFoundException',
    'APITooManyRequestsException',
]

from rest_framework.response import Response


class APIException(Exception):
    """Bad request exception.

    Raising this exception will return a bad request response,
    with the relevant status code and description.

    Parameters
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int
        HTTP status code

    Attributes
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int
        HTTP status code

    """
    def __init__(self, status_code, status_description, http_code):
        self.status_code = status_code
        self.status_description = status_description
        self.http_code = http_code

    def as_tuple(self):
        """Exception info as a tuple for easier unpacking handling.

        Returns
        -------
        tuple
            Tuple of status code, status description and HTTP status code.

        """
        return (self.status_code, self.status_description, self.http_code)

    def as_context(self):
        """Exception info as required in response context.

        Returns
        -------
        dict
            Exception info as context dictionary.

        """
        return {
            'status_cd': self.status_code,
            'status_desc': self.status_description,
        }

    def as_response(self):
        """Exception info as response.

        Can be returned directly from a view.

        Returns
        -------
        Response
            DRF Response.

        """
        return Response(self.as_context(), status=self.http_code)


class APIBadRequestException(APIException):
    """API exception for object not found instances.

    Making use of this exception class means you can catch only this
    exception instead of needing to check the exceptions http_code.

    Parameters
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int, optional
        HTTP status code (defaults to 400)

    Attributes
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int
        HTTP status code

    """
    def __init__(self, status_code, status_description):
        super().__init__(status_code, status_description, http_code=400)


class APIUnauthorizedException(APIException):
    """API exception for object not found instances.

    Making use of this exception class means you can catch only this
    exception instead of needing to check the exceptions http_code.

    Parameters
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int, optional
        HTTP status code (defaults to 401)

    Attributes
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int
        HTTP status code

    """
    def __init__(self, status_code, status_description):
        super().__init__(status_code, status_description, http_code=401)


class APIForbiddenException(APIException):
    """API exception for object not found instances.

    Making use of this exception class means you can catch only this
    exception instead of needing to check the exceptions http_code.

    Parameters
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int, optional
        HTTP status code (defaults to 403)

    Attributes
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int
        HTTP status code

    """
    def __init__(self, status_code, status_description):
        super().__init__(status_code, status_description, http_code=403)


class APINotFoundException(APIException):
    """API exception for object not found instances.

    Making use of this exception class means you can catch only this
    exception instead of needing to check the exceptions http_code.

    Parameters
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int, optional
        HTTP status code (defaults to 404)

    Attributes
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int
        HTTP status code

    """
    def __init__(self, status_code, status_description):
        super().__init__(status_code, status_description, http_code=404)


class APITooManyRequestsException(APIException):
    """API exception for object not found instances.

    Making use of this exception class means you can catch only this
    exception instead of needing to check the exceptions http_code.

    Parameters
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int, optional
        HTTP status code (defaults to 429)

    Attributes
    ----------
    status_code : str
        JSON error status code
    status_description : str
        JSON error description
    http_code : int
        HTTP status code

    """
    def __init__(self, status_code, status_description):
        super().__init__(status_code, status_description, http_code=429)
