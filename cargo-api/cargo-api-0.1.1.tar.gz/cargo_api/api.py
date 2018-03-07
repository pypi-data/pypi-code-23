def get_response(obj):
    obj.header.success = True
    return obj


def add_error(response, code, message, field=''):
    response.header.success = False
    err = response.header.errors.add()
    err.code = code
    err.message = message
    err.field = field


def add_validation_error(response, message, field):
    """message can be either a string or a list of strings corresponding to the same field"""
    if isinstance(message, list):
        for msg in message:
            add_error(response, 'VALIDATION_ERROR', msg, field)
    else:
        add_error(response, 'VALIDATION_ERROR', message, field)


def has_errors(response):
    return len(response.header.errors) > 0


def add_internal_error(response):
    response.header.success = False
    err = response.header.errors.add()
    err.code = 'INTERNAL_SERVER_ERROR'
    err.message = 'An internal server error occured. Feel free to try again with the corresponding idempotency key. If the error persists, contact the tech support.'


class ValidationResult():
    def __init__(self, valid: bool = True, message=''):
        self.valid = valid
        self.messages = []
        if message != '':
            self.messages.append(message)

    def add_message(self, message):
        self.messages.append(message)


def handle_validation_result(response, result: ValidationResult, field):
    if not result.valid:
        for msg in result.messages:
            add_validation_error(response, msg, field)