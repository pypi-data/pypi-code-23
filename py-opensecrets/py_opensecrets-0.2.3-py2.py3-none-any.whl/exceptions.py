class CRPError(Exception):
    """ Exception for general CRP Client errors. """
    def __init__(self, message, response=None, url=None):
        super(CRPError, self).__init__(message)
        self.message = message
        self.response = response
        self.url = url
