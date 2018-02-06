class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ValidationError(Error):
    """Exception raised due to invalid input parameters.

    Attributes:
        status_code (int): Status code of the error
        message (str): Explanation of the error
    """

    def __init__(self, status_code, msg):
        self.message = msg
        self.status_code = status_code


class NetworkError(Error):
    """Exception raised due to problems in network connectivity.

    Attributes:
        status_code (int): Status code of the error
        message (str): Explanation of the error
    """

    def __init__(self, status_code, msg):
        self.message = msg
        self.status_code = status_code


class ServerError(Error):
    """Exception raised due to Server error.

    Attributes:
        status_code (int): Status code of the error
        message (str): Explanation of the error
    """

    def __init__(self, status_code, msg):
        self.message = msg
        self.status_code = status_code
