# -*- coding: utf-8 -*-

"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""

from beatle.model import ClassDiagram, TComponent
from beatle.tran import TransactionalMethod, TransactionalMoveObject
from .Field import Field

class Table(TComponent):
    """Implements table table representation"""
    folder_container = True
    diagram_container = True
    field_container = True

    # visual methods
    @TransactionalMethod('move table {0}')
    def drop(self, to):
        """Drops schema inside project or another folder """
        return False
        target = to.inner_table_container
        if not target or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization method"""
        super(Table, self).__init__(**kwargs)

    @property
    def query(self):
        return 'SELECT * FROM `{schema}`.`{table}`;'.format(
                schema=self.inner_schema.name,
                table=self.name)

    def CreateFields(self, conn):
        """Create fields for the table from database"""
        try:
            conn.query('DESCRIBE `{schema}`.`{table}`'.format(
                schema=self.inner_schema.name,
                table=self.name))
            data = conn.store_result()
            if data:
                kwargs = {'parent': self}
                i = data.num_rows()
                while i > 0 :
                    i = i -1 
                    info = data.fetch_row()[0]
                    kwargs.update({
                        'name': info[0],
                        'type': info[1],  # 'int(11)'
                        'null': info[2],  # 'YES' or 'NOT'
                        'primary': info[3],  # 'PRI', 'UNI', 'MUL' or ''
                        'default': info[4],  # NULL, '', 0, ...
                        'extra': info[5]  # autoincrement
                        })
                    Field(**kwargs)
                del data
            return True
        except:
            return False

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs.update(super(Table, self).get_kwargs())
        return kwargs

    def OnUndoRedoRemoving(self):
        """Handle OnUndoRedoRemoving, prevent generating files"""
        super(Table, self).OnUndoRedoRemoving()

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return super(Table, self).can_delete

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
        super(Table, self).Delete()

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
        super(Table, self).OnUndoRedoChanged()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc
        return rc.GetBitmapIndex('database_table')

    @property
    def tree_label(self):
        """Get tree label"""
        return self.name

    @property
    def inner_table(self):
        """Get the inner table"""
        return self

    @property
    def outer_table(self):
        """Get the outer class container"""
        return self



