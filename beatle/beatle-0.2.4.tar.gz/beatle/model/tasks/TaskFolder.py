# -*- coding: utf-8 -*-

from beatle.model import TComponent
from beatle.tran import TransactionalMethod,TransactionalMoveObject


class TaskFolder(TComponent):
    """Implements a Folder representation"""
    task_container = True

    # visual methods
    @TransactionalMethod('move folder {0}')
    def drop(self, to):
        """drop this elemento to another place"""
        target = to.inner_task_container
        if not target or to.project != self.project:
            return False  # avoid move arguments between projects
        index = 0
        new_cont = target.status_container
        if new_cont is not target.status_container:
            new_cont.SetStatus(self)
        TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    @property
    def status_container(self):
        """return the status container"""
        return self.parent.status_container

    def __init__(self, **kwargs):
        """Initialization"""
        super(TaskFolder, self).__init__(**kwargs)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc
        return rc.GetBitmapIndex("folder")

    @property
    def bitmap_open_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc
        return rc.GetBitmapIndex("folder_open")
