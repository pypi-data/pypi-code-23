import requests


class XLDeployException(Exception):
    """
       A base class from which all other exceptions inherit.

       If you want to catch all errors that the Xldeploy SDK might raise,
       catch this base exception.
       """


def create_api_error_from_http_exception(e):
    """
    Create a suitable APIError from requests.exceptions.HTTPError.
    """
    response = e.response
    try:
        explanation = response.json()['message']
    except ValueError:
        explanation = response.content.strip()

    raise {
        401: XLDeployAuthenticationError(e, response=response, explanation=explanation)
    }.get(response.status_code, APIError(e, response=response, explanation=explanation)) # default


class APIError(requests.exceptions.HTTPError, XLDeployException):
    """
    An HTTP error from the API.
    """

    def __init__(self, message, response=None, explanation=None):
        super(APIError, self).__init__(message)
        self.response = response
        self.explanation = explanation

    def __str__(self):
        message = super(APIError, self).__str__()

        if self.is_client_error():
            message = '{0} Client Error: {1}'.format(
                    self.response.status_code, self.response.reason)

        elif self.is_server_error():
            message = '{0} Server Error: {1}'.format(
                    self.response.status_code, self.response.reason)

        if self.explanation:
            message = '{0} ("{1}")'.format(message, self.explanation)

        return message

    @property
    def status_code(self):
        if self.response is not None:
            return self.response.status_code

    def is_client_error(self):
        if self.status_code is None:
            return False
        return 400 <= self.status_code < 500

    def is_server_error(self):
        if self.status_code is None:
            return False
        return 500 <= self.status_code < 600


class XLDeployConnectionTimeout(APIError):
    pass

class XLDeployConnectionError(APIError):
    pass

class XLDeployAuthenticationError(APIError):
    pass
