# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 23:24:30 2013

@author: mel
"""
from beatle import tran
from .decorator import ContextDeclaration
from .TComponent import TComponent


class Folder(TComponent):
    """Implements a Folder representation"""
    class_container = True
    context_container = True
    folder_container = True
    diagram_container = True
    module_container = True
    namespace_container = True
    function_container = True
    variable_container = True
    member_container = True

    # visual methods
    @tran.TransactionalMethod('move folder {0}')
    def drop(self, to):
        """Drops class inside project or another folder """
        target = to.inner_folder_container
        if not target or self.inner_class != target.inner_class or self.project != target.project:
            return False  # avoid move classes between projects
        index = 0
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    def __init__(self, **kwargs):
        """Initialization"""
        super(Folder, self).__init__(**kwargs)
        self.update_container()

    def update_container(self):
        """Update the container info"""
        self.class_container = self._parent.class_container
        self.context_container = self._parent.context_container
        self.folder_container = self._parent.folder_container
        self.diagram_container = self._parent.diagram_container
        self.module_container = self._parent.module_container
        self.namespace_container = self._parent.namespace_container
        self.function_container = self._parent.function_container
        self.variable_container = self._parent.variable_container
        self.member_container = self._parent.member_container
        self.import_container = self._parent.import_container

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        return super(Folder, self).get_kwargs()

    @ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the folder declaration"""
        self.WriteComment(pf)
        #we will follow and respect the visual order
        from model import cc
        child_types = [Folder, cc.Namespace, cc.Class, cc.Enum, cc.MemberData,
            cc.Constructor, cc.MemberMethod, cc.Destructor, cc.Module,
            cc.Function, cc.Data]
        for _type in child_types:
            if len(self[_type]):
                for item in self[_type]:
                    item.WriteDeclaration(pf)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        import app.resources as rc
        return rc.GetBitmapIndex("folder")

    @property
    def bitmap_open_index(self):
        """Index of tree image"""
        import app.resources as rc
        return rc.GetBitmapIndex("folder_open")

    def ExistMemberDataNamed(self, name):
        """Check recursively about the existence of nested child member"""
        from model import cc
        return self.hasChild(name=name, type=cc.MemberData)

    def AddMemberData(self, name):
        """Add a member element"""
        from model import cc
        member = cc.MemberData(name, self)
        return member

    @property
    def nested_classes(self):
        """Returns the list of nested classes (including self)"""
        from model import cc
        if type(self.parent) not in [Folder, cc.Class]:
            return []
        return self.parent.nested_classes
