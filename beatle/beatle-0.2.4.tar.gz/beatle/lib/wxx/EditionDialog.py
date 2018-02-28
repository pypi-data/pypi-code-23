# -*- coding: utf-8 -*-

import wx
from  beatle.tran import TransactionStack, GetCurrentTransactionName, SetCurrentTransactionName


class EditionDialog(object):
    """Class decorator for edition dialog. With this decorator
    the decorated method only needs to send the dialog arguments"""
    def __init__(self, dialogType):
        """"""
        self._dialogType = dialogType

    def __call__(self, method):
        """"""
        def wrapped_call(*args, **kwargs):
            """Code dialog edition"""
            (wnd, obj) = method(*args, **kwargs)
            dialog = self._dialogType(wnd, obj.parent)
            dialog.SetAttributes(obj)
            if dialog.ShowModal() != wx.ID_OK:
                return False
            obj.SaveState()
            dialog.CopyAttributes(obj)
            if obj.project:
                obj.project.SetModified(True)
            if obj and TransactionStack.InTransaction() and hasattr(obj, '_name'):
                sname = GetCurrentTransactionName()
                if sname:
                    sname = sname.format(obj._name)
                    SetCurrentTransactionName(sname)
            return True
        return wrapped_call