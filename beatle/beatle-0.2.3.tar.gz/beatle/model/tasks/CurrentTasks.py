# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

"""
Created on Sun Dec 15 19:22:32 2013

@author: mel
"""
import wx

from model import Folder

class CurrentTasks(Folder):
    """Clase que representa a las tareas pendientes"""

    task_container = True

    @property
    def status_container(self):
        """return the status container"""
        return self

    def SetStatus(self, element):
        """Set the task as working"""
        from model.tasks import Task, TaskFolder
        if type(element) is Task:
            element.SaveState()
            element._status = 'working'
            element._dateBegin = wx.DateTime.Now().Format('%Y-%m-%d %H:%M:%S')
            element._dateEnd = '--/--/---- --:--:--'
        for subtask in element[Task]:
            self.SetStatus(subtask)
        for subtask in element[TaskFolder]:
            self.SetStatus(subtask)

    def __init__(self, **kwargs):
        """Inicializacion"""
        if 'name' not in kwargs:
            kwargs['name'] = 'Current Tasks'
        kwargs['readonly'] = True
        super(CurrentTasks, self).__init__(**kwargs)

    @property
    def can_delete(self):
        """Check abot if class can be deleted"""
        return super(CurrentTasks, self).can_delete

    def Delete(self):
        """Delete diagram objects"""
        super(CurrentTasks, self).Delete()

    def RemoveRelations(self):
        """Utility for undo/redo"""
        super(CurrentTasks, self).RemoveRelations()

    def RestoreRelations(self):
        """Utility for undo/redo"""
        super(CurrentTasks, self).RestoreRelations()

    def SaveState(self):
        """Utility for saving state"""
        super(CurrentTasks, self).SaveState()

    def OnUndoRedoRemoving(self):
        """Prepare object to delete"""
        super(CurrentTasks, self).OnUndoRedoRemoving()

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(CurrentTasks, self).OnUndoRedoChanged()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        super(CurrentTasks, self).OnUndoRedoAdd()

    @property
    def bitmap_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc
        return rc.GetBitmapIndex('folder_current')

    @property
    def bitmap_open_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc
        return rc.GetBitmapIndex('folder_current_open')

    @property
    def label(self):
        """Get tree label"""
        return '{self._name}'.format(self=self)
