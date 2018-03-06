# -*- coding: utf-8 -*-

class AbstractAssembler(object):
    def __call__(self):
        raise NotImplementedError


class SimpleAssembler(AbstractAssembler):
    def __call__(self, data):
        return self._assemble(data)

    def _assemble(self, data):
        return (u'\r\n'.join(u'%s: %s' % (key, value) for key, value in data.items()) + u'\r\n' * 2).encode()
