# -*- coding: utf-8 -*-

from beatle.tran import TransactionObject 
from ._TCommon import TCommon

class TComponent(TCommon, TransactionObject):
    """We need to be able to deal with several kinds of TransactionObject.
    For example, with TransactionFSObject now and with TransactionDBObject in a near future.
    For this reason we need to split the data management and transaction management."""
    def __init__(self, **kwargs):
        """init"""
        super(TComponent, self).__init__(**kwargs)


