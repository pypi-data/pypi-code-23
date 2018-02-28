# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 23:24:30 2013

@author: mel
"""
from beatle.model import Folder


def name(x):
    """comparison"""
    return x._name


class LibrariesFolder(Folder):
    """Implements a Folder representation"""
    class_container = False
    type_container = False
    function_container = False
    variable_container = False
    module_container = False
    namespace_container = False
    function_container = False
    member_container = False

    #visual methods
    def draggable(self):
        """returns info about if the object can be moved"""
        return False

    def __init__(self, **kwargs):
        """Initialization"""
        kwargs['name'] = 'Libraries'
        super(LibrariesFolder, self).__init__(**kwargs)
        self.update_container()

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        return super(LibrariesFolder, self).get_kwargs()

    def update_container(self):
        """Update the container info"""
        self.context_container = False
        self.folder_container = False
        self.diagram_container = False
        self.namespace_container = False

    @property
    def bitmap_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc
        return rc.GetBitmapIndex("folderP")

    def ExistMemberDataNamed(self, name):
        """Check recursively about the existence of nested child member"""
        return False

