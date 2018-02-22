from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


__all__ = [
    'Replica',
]


class Replica(object):
    def __init__(self, lfn, se, pfn=None, error=None, banned=False):
        self._lfn = lfn
        self._se = se
        self._pfn = pfn
        self._error = error
        self._banned = banned

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._lfn == other._lfn and self._se == other._se
        return False

    def __str__(self):
        if self.available:
            return '{se}: {pfn}'.format(se=self._se, pfn=self._pfn)
        elif self._banned:
            return '{se}: Replica is banned'.format(se=self._se)
        elif self._error:
            return '{se}: {error}'.format(se=self._se, error=self._error)
        else:
            return '{se}: Unknown error ({error})'.format(se=self._se, error=repr(self))

    @property
    def available(self):
        return not self._banned and self._pfn is not None

    @property
    def lfn(self):
        return self._lfn

    @property
    def pfn(self):
        from .XRootD import URL
        return URL(self._pfn)

    @property
    def storage_element(self):
        return self._se
