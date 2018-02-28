# -*- coding: utf-8 -*-

import copy

from beatle.ctx import THE_CONTEXT as context
from beatle.model import TComponent,Project


class Workspace(TComponent):
    """Representation of Workspace"""

    #class_container = False
    #folder_container = False
    #diagram_container = True
    #module_container = False
    #namespace_container = False
    project_container = True
    repository_container = True
    _dir = None  # used for pickle modification on load

    def __init__(self, **kwargs):
        """Initialization of workspace"""
        self._dir = kwargs['dir']
        self._author = kwargs.get('author', "<unknown>")
        self._date = kwargs.get('date', "08-10-2966")
        self._license = kwargs.get('license', None)
        self._modified = True
        self._lastHdrTime = None
        super(Workspace, self).__init__(**kwargs)

    #def OnUndoRedoRemoving(self, root=True):
    def OnUndoRedoRemoving(self):
        """Prepare for delete"""
        #super(Workspace, self).OnUndoRedoRemoving(root)
        super(Workspace, self).OnUndoRedoRemoving()
        context.app.RemoveWorkspace(self)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        context.app.AddWorkspace(self)
        super(Workspace, self).OnUndoRedoAdd()

    def GetTabBitmap(self):
        """Get the bitmap for tab control"""
        import app.resources as rc        
        return rc.GetBitmap('workspace')

    @property
    def bitmap_index(self):
        """Index of tree image"""
        import app.resources as rc        
        return rc.GetBitmapIndex('workspace')

    def __getstate__(self):
        """Set pickle context"""
        # we dont want to serialize projects directly
        state = copy.copy(self.__dict__)
        state['_child'] = copy.copy(self._child)
        state['_child'][Project] = [
            (x._dir.replace("//", "/") + "/" + x._name + ".pcc").replace("//", "/")
            for x in self[Project] if type(x) is Project]
        return state

    def __setstate__(self, d):
        """Load pickle context"""
        plist = d['_child'].get(Project, None)
        #The current dir and the stored dir may be not the same
        if Workspace._dir:
            old_dir = d['_dir']
            d['_dir'] = Workspace._dir
        else:
            old_dir = None
        if plist:
            del d['_child'][Project]
        self.__dict__ = d
        if plist:
            for pf in plist:
                if old_dir:
                    pf = pf.replace(old_dir, self._dir, 1)
                context.app.LoadProject(pf, self)

    def SetModified(self, bModified=True):
        """Set the modified state"""
        self._lastHdrTime = None
        self._modified = bModified

    def IsModified(self):
        """Get the modified state"""
        return self._modified
