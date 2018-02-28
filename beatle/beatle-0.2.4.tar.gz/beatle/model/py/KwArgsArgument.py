# -*- coding: utf-8 -*-
"""
Created on Sun Dec 22 22:31:28 2013

@author: mel
"""

from beatle.tran import TransactionalMethod, TransactionalMoveObject
from Argument import Argument


class KwArgsArgument(Argument):
    """Implements argument representation"""

    context_container = True

    #visual methods
    @TransactionalMethod('move argument {0}')
    def drop(self, to):
        """drop this elemento to another place"""
        target = to.inner_argument_container
        if not target or to.project != self.project:
            return False  # avoid move arguments between projects
        index = 0  # trick for insert as first child
        TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization"""
        kwargs['name'] = 'kwargs'
        kwargs['default'] = ''
        super(KwArgsArgument, self).__init__(**kwargs)
        container = self.outer_class or self.outer_module
        container._lastSrcTime = None
        container._lastHdrTime = None

    @property
    def bitmap_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc
        return rc.GetBitmapIndex('py_kwargs')
        #return 5

    @property
    def label(self):
        """Get tree label"""
        return '**{self._name}'.format(self=self)
