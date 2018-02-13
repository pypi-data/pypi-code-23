

# most general project exceptions. all other exceptions that we raise should be inherited from this one
class MissingLinkException(Exception):
    def __init__(self, message='', logger=None):
        super(MissingLinkException, self).__init__(message)
        if logger:
            logger.exception(message)


class ExperimentStopped(MissingLinkException):
    pass


class ImageUnavailableException(MissingLinkException):
    pass
