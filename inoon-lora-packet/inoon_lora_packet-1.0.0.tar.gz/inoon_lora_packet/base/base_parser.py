import abc


class Parser(abc.ABC):
    @abc.abstractproperty
    def header_length(self):
        pass

    @abc.abstractmethod
    def parse(self, raw_packet):
        pass
