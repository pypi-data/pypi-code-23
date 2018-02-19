class ParseException(BaseException):
    def __init__(self, message):
        self.message = message


class SettingsException(BaseException):
    def __init__(self, message):
        self.message = message
