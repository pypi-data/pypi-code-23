class SingularException(Exception):
    def __init__(self, message, code):
        self.message = message
        self.code = code
        Exception.__init__(self, 'Singular API returned code {} with message: "{}"'.format(code, message))

    @classmethod
    def from_response(cls, code, message):
        return code_to_exception.get(code, cls.create_exception_class('SingularUnhandledException', code))(message)

    @classmethod
    def create_exception_class(cls, name, fallback_code=0):
        init_fcn = lambda self, message: cls.__init__(self, message, exception_to_code.get(self.__class__, fallback_code))
        return type(name, (cls,), {"__init__": init_fcn})


code_to_exception = {
    400: SingularException.create_exception_class("SingularBadRequestException"),
    401: SingularException.create_exception_class("SingularUnauthorizedException"),
    403: SingularException.create_exception_class("SingularForbiddenException"),
    404: SingularException.create_exception_class("SingularNotFoundException"),
    405: SingularException.create_exception_class("SingularMethodNotAllowedException"),
    408: SingularException.create_exception_class("SingularRequestTimeoutException"),
    409: SingularException.create_exception_class("SingularConflictException"),

    500: SingularException.create_exception_class("SingularInternalServerErrorException"),
    501: SingularException.create_exception_class("SingularNotImplementedException"),
    502: SingularException.create_exception_class("SingularBadGetawayException"),
    503: SingularException.create_exception_class("SingularServiceUnavailableException"),
    504: SingularException.create_exception_class("SingularGatewayTimeoutException")
}

exception_to_code = {v: k for k, v in code_to_exception.items()}
