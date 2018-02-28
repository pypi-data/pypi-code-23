# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 23:24:30 2013

@author: mel
"""
from beatle.model import cc
from beatle.model import Folder, TComponent
from beatle.model import decorator as ctx


class Library(TComponent):
    """Implements a Library representation"""
    class_container = True
    context_container = True
    folder_container = True
    diagram_container = True
    module_container = True
    namespace_container = True
    function_container = True
    variable_container = True
    member_container = False

    def __init__(self, **kwargs):
        """Initialization"""
        super(Library, self).__init__(**kwargs)

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        return super(Library, self).get_kwargs()

    @ctx.ContextDeclaration()
    def WriteDeclaration(self, pf):
        """Write the folder declaration"""
        self.WriteComment(pf)
        #we will follow and respect the visual order
        child_types = [Folder, cc.Namespace, cc.Class, cc.Enum, cc.MemberData,
            cc.Constructor, cc.MemberMethod, cc.Destructor, cc.Module, cc.Function, 
            cc.Data]
        for _type in child_types:
            if len(self[_type]):
                for item in self[_type]:
                    item.WriteDeclaration(pf)

    @property
    def bitmap_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc
        return rc.GetBitmapIndex("library")

    def ExistMemberDataNamed(self, name):
        """Check recursively about the existence of nested child member"""
        return self.hasChild(name=name, type=cc.MemberData)

    def AddMemberData(self, name):
        """Add a member element"""
        member = cc.MemberData(name, self)
        return member

    @property
    def nested_classes(self):
        """Returns the list of nested classes (including self)"""
        if type(self.parent) not in [Folder, cc.Class]:
            return []
        return self.parent.nested_classes
