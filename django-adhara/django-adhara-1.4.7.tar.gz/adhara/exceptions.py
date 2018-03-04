class AdharaException(Exception):

    def get_message(self):
        return self.args[0]


class InvalidInput(AdharaException):
    pass


class InvalidOperationException(AdharaException):
    pass


class InvalidDatabaseSelected(AdharaException):
    pass


class UnAuthorizedException(AdharaException):
    pass
