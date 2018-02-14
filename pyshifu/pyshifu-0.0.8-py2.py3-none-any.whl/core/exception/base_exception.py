from abc import ABCMeta, abstractmethod


class ShifuException(Exception):
    __metaclass__ = ABCMeta

    def __init__(self, extra_message=None):
        self.error_no = self.get_error_no
        self.error_message = self.get_description()
        self.extra_message = extra_message

    @abstractmethod
    def get_description(self):
        return "No Description!"

    @abstractmethod
    def get_error_no(self):
        return None

    def get_message(self):
        if self.extra_message is None:
            return self.error_message
        return self.error_message + str(self.extra_message)


