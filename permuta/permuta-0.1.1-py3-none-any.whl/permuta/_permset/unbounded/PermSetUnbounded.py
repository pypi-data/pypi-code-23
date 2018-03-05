import abc
import numbers

from ..PermSetBase import PermSetBase


class PermSetUnbounded(PermSetBase):
    def __init__(self, descriptor):
        self.descriptor = descriptor
    @abc.abstractmethod
    def up_to(self, perm):
        pass
    @abc.abstractmethod
    def __getitem__(self, key):
        pass
