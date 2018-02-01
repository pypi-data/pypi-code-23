import abc

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.10"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class AbstractSignalProducer(abc.ABC):

    @abc.abstractmethod
    def produce_condition(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def produce(self, *args, **kwargs):
        pass
