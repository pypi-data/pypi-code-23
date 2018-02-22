from requests import HTTPError


class APIError(HTTPError):
    """
    Class for API response error
    """
    pass