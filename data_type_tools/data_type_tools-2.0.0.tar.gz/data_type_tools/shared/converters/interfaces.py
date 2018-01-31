import abc


class ConverterInterface(metaclass=abc.ABCMeta):      # converters
    @abc.abstractmethod
    def convert(self):
        pass
