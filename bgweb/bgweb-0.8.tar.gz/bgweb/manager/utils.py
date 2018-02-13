
class BGManagerError(Exception):
    """
    Base class for exceptions produced by this package

    Args:
        message(str): error message

    """
    def __init__(self, message):
        self.message = message
