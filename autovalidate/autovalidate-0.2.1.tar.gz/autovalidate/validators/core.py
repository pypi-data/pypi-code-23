class Validator(object):
    def validate(self, path):
        raise NotImplementedError


class ValidationResult(object):
    def __init__(self, path, valid, message=None):
        self.path = path
        self.valid = valid
        self.message = message

validators = {}


def validates(*formats):
    def validates_decorator(cls):
        for format in formats:
            validators[format.lstrip('.')] = cls()
        return cls
    return validates_decorator


def get_validator(extension):
    return validators.get(extension.lstrip('.'))
