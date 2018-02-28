# -*- coding: utf-8 -*-

"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""

from beatle.model import TComponent, ClassDiagram
from beatle.tran import TransactionalMethod,TransactionalMoveObject


class Field(TComponent):
    """Implements field table representation"""

    # visual methods
    @TransactionalMethod('move field {0}')
    def drop(self, to):
        """Drops schema inside project or another folder """
        return False
        target = to.inner_field_container
        if not target or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization method"""
        self._type = kwargs.get('type', None)
        self._null = kwargs.get('null', 'YES')
        self._primary = kwargs.get('primary', '')
        self._default = kwargs.get('default', None)
        self._extra = kwargs.get('extra', '')
        super(Field, self).__init__(**kwargs)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {
            'type': self._type,
            'null': self._null,
            'primary': self._primary,
            'default': self._default,
            'extra': self._extra
        }
        kwargs.update(super(Field, self).get_kwargs())
        return kwargs

    def OnUndoRedoRemoving(self):
        """Handle OnUndoRedoRemoving, prevent generating files"""
        super(Field, self).OnUndoRedoRemoving()

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return super(Field, self).can_delete

    def Delete(self):
        """Delete diagram objects"""
        for dia in self.project(ClassDiagram):
            # Check if inherit is in
            elem = dia.FindElement(self)
            if elem is not None:
                dia.SaveState()
                dia.RemoveElement(elem)
                if hasattr(dia, '_pane') and dia._pane is not None:
                    dia._pane.Refresh()
        super(Field, self).Delete()

    def OnUndoRedoChanged(self):
        """Update from app"""
        project = self.project
        #update class diagrams
        dias = project(ClassDiagram)
        for dia in dias:
            # Check if class is in
            elem = dia.FindElement(self)
            if elem is not None:
                elem.Layout()
                if hasattr(dia, '_pane') and dia._pane is not None:
                    dia._pane.Refresh()
        super(Field, self).OnUndoRedoChanged()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc
        return rc.GetBitmapIndex('database_field')

    @property
    def tree_label(self):
        """Get tree label"""
        return self.name

    @property
    def inner_field(self):
        """Get the inner field"""
        return self

    @property
    def outer_field(self):
        """Get the outer class container"""
        return self



