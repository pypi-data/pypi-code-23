# -*- coding: utf-8 -*-
import uuid

#import beatle
from beatle.ctx import THE_CONTEXT as context
from beatle.tran import TransactionStack


#import tasks

"""
Created on Sun Dec 15 23:49:51 2013

@author: mel
"""


class TCommon(object):
    """Clase para componentes con soporte transamodelional"""
    task_container = False
    project_container = False
    class_container = False
    context_container = False
    folder_container = False
    diagram_container = False
    module_container = False
    namespace_container = False
    type_container = False
    inheritance_container = False
    member_container = False
    argument_container = False
    relation_container = False
    function_container = False
    variable_container = False
    enum_container = False
    import_container = False
    package_container = False
    library_container = False
    repository_container = False
    dir_container = False
    file_container = False
    #database
    schema_container = False
    table_container = False
    field_container = False

    #visual methods
    def draggable(self):
        """returns info about if the object can be moved"""
        return not self._readOnly

    def drop(self, to):
        """drop this elemento to another place"""
        return False

    def __init__(self, **kwargs):
        """Initialize a transactional component"""
        self._parent = kwargs.get('parent', None)
        self._name = kwargs.get('name', '')
        self._serial = kwargs.get('serial', False)
        self._note = kwargs.get('note', '')
        self._readOnly = kwargs.get('readonly', False)
        self._visibleInTree = kwargs.get('visibleInTree', True)
        self._declare = kwargs.get('declare', True)
        self._implement = kwargs.get('implement', True)
        self._child = {}
        if self._parent is not None:
            self._parent.addChild(self, kwargs.get('prev', None))
        self._uid = uuid.uuid4()
        super(TCommon, self).__init__(**kwargs)

        # allow to dynamic children creation through kwargs
        child_kwargs = kwargs.get('child_kwargs', None)
        if child_kwargs is not None:
            for t in child_kwargs:
                for chkwargs in child_kwargs[t]:
                    chkwargs['parent'] = self
                    t(**chkwargs)

    @property
    def uid(self):
        """Accessor to the uid of the object"""
        return self._uid

    def get_kwargs(self):
        """Returns the kwargs needed for this object"""
        kwargs = {}
        kwargs['parent'] = self._parent
        kwargs['name'] = self._name
        kwargs['serial'] = self._serial
        kwargs['note'] = self._note
        kwargs['readonly'] = self._readOnly
        kwargs['visibleInTree'] = self._visibleInTree
        kwargs['declare'] = self._declare
        kwargs['implement'] = self._implement
        # recursively add child kwargs
        kwargs['child_kwargs'] = dict([(t,
            [x.get_kwargs() for x in self._child[t]]) for t in self._child.keys()])
        return kwargs

    def update_container(self):
        """Update the container info"""
        pass

    def WriteComment(self, pf):
        """Write the note using the writter"""
        #ok, now we place comments, if any
        if len(self._note) > 0:
            pf.writeln("/**")
            txt = self._note
            txt.replace('\r', '')
            lines = txt.split("\n")
            for line in lines:
                line.replace('*/', '* /')
                pf.writeln("* {0}".format(line))
            pf.writeln("**/")

    def WriteContextsPrefixDeclaration(self, pf):
        """Write the contexts prefixes for declaration"""
        if hasattr(self, '_contexts'):
            for i in range(0, len(self._contexts)):
                item = self._contexts[i]
                if len(item._prefix_declaration):
                    pf.writeln('{0}'.format(item._prefix_declaration))

    def WriteContextsSufixDeclaration(self, pf):
        """Write the contexts sufixes for declaration"""
        if hasattr(self, '_contexts'):
            for i in range(len(self._contexts) - 1, -1, -1):
                item = self._contexts[i]
                if len(item._sufix_declaration):
                    pf.writeln('{0}'.format(item._sufix_declaration))

    def WriteContextsPrefixImplementation(self, pf):
        """Write the contexts prefixes for implementation"""
        if hasattr(self, '_contexts'):
            for i in range(0, len(self._contexts)):
                item = self._contexts[i]
                if len(item._prefix_implementation):
                    pf.writeln('{0}'.format(item._prefix_implementation))

    def WriteContextsSufixImplementation(self, pf):
        """Write the contexts sufixes for implementation"""
        if hasattr(self, '_contexts'):
            for i in range(len(self._contexts) - 1, -1, -1):
                item = self._contexts[i]
                if len(item._sufix_implementation):
                    pf.writeln('{0}'.format(item._sufix_implementation))

    def __call__(self, *args, **kwargs):
        """___call__(type1,...,typeN, filter=lambda x: True, cut=False):
        Returns the list of nested childs of one of the types.

        filter: indicates a boolean filter method that must
                return True for valid elements.

        cut: stops traveling if filter is unsatisfied?
        """
        import app
        r = []
        fn = kwargs.get('filter', lambda x: True)
        cut = kwargs.get('cut', False)
        for k in self._child:
            if app.isclass(k, *args):
                r.extend(filter(fn, self[k]))
            if cut:
                for o in filter(fn, self[k]):
                    r.extend(o(*args, **kwargs))
            else:
                for o in self[k]:
                    r.extend(o(*args, **kwargs))
        return r

    @property
    def name(self):
        """Get the name"""
        return self._name

    @property
    def note(self):
        """Get the name"""
        return self._note

    @note.setter
    def note(self, note):
        """Set the note"""
        self._note = note

    @property
    def label(self):
        """Get tree label"""
        return self._name

    @property
    def tree_label(self):
        """Get tree label"""
        return self.label

    @property
    def tab_label(self):
        """Get tree label"""
        return self.label

    #container properties
    @property
    def inner_class_container(self):
        """return the inner class container if any"""
        return (self.class_container and self) or (self.parent and self.parent.inner_class_container)

    @property
    def inner_context_container(self):
        """return the inner context container if any"""
        return (self.context_container and self) or (self.parent and self.parent.inner_context_container)

    @property
    def inner_folder_container(self):
        """return the inner folder container if any"""
        return (self.folder_container and self) or (self.parent and self.parent.inner_folder_container)

    @property
    def inner_repository_container(self):
        """return the inner folder container if any"""
        return (self.repository_container and self) or (self.parent and self.parent.inner_repository_container)

    @property
    def inner_diagram_container(self):
        """return the inner diagram container if any"""
        return (self.diagram_container and self) or (self.parent and self.parent.inner_diagram_container)

    @property
    def inner_module_container(self):
        """return the inner module container if any"""
        return (self.module_container and self) or (self.parent and self.parent.inner_module_container)

    @property
    def inner_task_container(self):
        """return the inner task container if any"""
        return (self.task_container and self) or (self.parent and self.parent.inner_task_container)

    @property
    def inner_type_container(self):
        """return the inner module container if any"""
        return (self.type_container and self) or (self.parent and self.parent.inner_type_container)

    @property
    def inner_enum_container(self):
        """return the inner module container if any"""
        return (self.enum_container and self) or (self.parent and self.parent.inner_enum_container)

    @property
    def inner_namespace_container(self):
        """return the inner namespace container if any"""
        return (self.namespace_container and self) or (self.parent and self.parent.inner_namespace_container)

    @property
    def inner_schema_container(self):
        """return the inner schema container if any"""
        return (self.schema_container and self) or (self.parent and self.parent.inner_schema_container)

    @property
    def inner_table_container(self):
        """return the inner schema container if any"""
        return (self.table_container and self) or (self.parent and self.parent.inner_table_container)

    @property
    def inner_field_container(self):
        """return the inner schema container if any"""
        return (self.field_container and self) or (self.parent and self.parent.inner_field_container)

    @property
    def inner_inheritance_container(self):
        """return the inner ineritance container if any"""
        return (self.inheritance_container and self) or (self.parent and self.parent.inner_inheritance_container)

    @property
    def inner_member_container(self):
        """return the inner member container"""
        return (self.member_container and self) or (self.parent and self.parent.inner_member_container)

    @property
    def inner_argument_container(self):
        """return the inner argument container"""
        return (self.argument_container and self) or (self.parent and self.parent.inner_argument_container)

    @property
    def inner_package_container(self):
        """return the inner package container"""
        return (self.package_container and self) or (self.parent and self.parent.inner_package_container)

    @property
    def inner_project_container(self):
        """return the inner project container"""
        return (self.project_container and self) or (
            self.parent and self.parent.inner_project_container)

    @property
    def inner_relation_container(self):
        """return the inner relation container"""
        return (self.relation_container and self) or (
            self.parent and self.parent.inner_relation_container)

    @property
    def inner_function_container(self):
        """return the inner function container"""
        return (self.function_container and self) or (self.parent and self.parent.inner_function_container)

    @property
    def inner_variable_container(self):
        """return the inner relation container"""
        return (self.variable_container and self) or (self.parent and self.parent.inner_variable_container)

    @property
    def inner_import_container(self):
        """return the inner relation container"""
        return (self.import_container and self) or (self.parent and self.parent.inner_import_container)

    def inner(self, t, self_include=True):
        """Search through ancestors the first ancestor of some type"""
        import app
        if self_include:
            if (type(t) is list and app.isclass(type(self), *t)) or app.isclass(type(self), t):
                return self
        return self._parent and self._parent.inner(t)

    @property
    def can_delete(self):
        """Check about if a component can be deleted"""
        return not self._readOnly

    @property
    def read_only(self):
        """get read only status"""
        return self._readOnly

    def __setitem__(self, cls, listobj):
        """sets the list of some class childs"""
        assert type(listobj) is list
        self._child[cls] = listobj

    def __getitem__(self, cls):
        """returns the list of childs with some class"""
        if not cls in self._child:
            self._child[cls] = []
        return self._child[cls]

    @property
    def project(self):
        """return the container project"""
        from .Project import Project
        return self.inner(Project)

    @property
    def workspace(self):
        """return the container project"""
        from .Workspace import Workspace
        return self.inner(Workspace)

    @property
    def inner_types_folder(self):
        """return the container types folder"""
        from .cc import TypesFolder
        return self.inner(TypesFolder)

    @property
    def classes(self):
        """returns the list of all classes"""
        from .cc import Class
        return self(Class)

    @property
    def diagrams(self):
        """returns the list of all diagrams"""
        from .ClassDiagram import ClassDiagram
        return self(ClassDiagram)

    @property
    def namespaces(self):
        """returns the list of all namespaces"""
        from .cc import Namespace
        return self(Namespace)

    @property
    def folders(self):
        """returns the list of all folder"""
        from .Folder import Folder
        return self(Folder)

    @property
    def modules(self):
        """returns the list of all modules"""
        from .cc import Module as ccModule
        from .py import Module as pyModule
        return self(ccModule, pyModule)

    @property
    def packages(self):
        """returns the list of all packages"""
        from .py import Package
        return self(Package)

    @property
    def functions(self):
        """returns the list of all functions"""
        from .cc import Function
        return self(Function)

    @property
    def constructors(self):
        """returns the list of all functions"""
        from .cc import Constructor
        return self(Constructor)

    @property
    def destructors(self):
        """returns the list of all functions"""
        from .cc import Destructor
        return self(Destructor)

    @property
    def methods(self):
        """returns the list of all functions"""
        from .cc import MemberMethod
        return self(MemberMethod)

    @property
    def variables(self):
        """returns the list of all variables"""
        from .cc import Data
        return self(Data, True)

    @property
    def inner_class(self):
        """returns the innermost class"""
        return self.parent and self.parent.inner_class

    @property
    def inner_namespace(self):
        """returns the innermost class"""
        from .cc import Namespace
        return self.inner(Namespace)

    @property
    def inner_library(self):
        """returns the inner library if any"""
        from .Library import Library
        return self.inner(Library)

    @property
    def inner_folder(self):
        """returns the innermost folder"""
        from .Folder import Folder
        return self.inner(Folder)

    @property
    def inner_module(self):
        """returns the innermost class"""
        from .cc import Module as ccModule
        from .py import Module as pyModule
        return self.inner([ccModule, pyModule])

    @property
    def inner_package(self):
        """returns the innermost class"""
        from .py import Package
        return self.inner(Package)

    @property
    def inner_method(self):
        """returns the innermost method"""
        from .cc import MemberMethod, IsClassMethod
        return self.inner([MemberMethod, IsClassMethod])

    @property
    def inner_function(self):
        """returns the innermost function"""
        from .cc import Function
        return self.inner(Function)

    @property
    def inner_constructor(self):
        """returns the innermost constructor"""
        from .cc import Constructor
        return self.inner(Constructor)

    @property
    def inner_schema(self):
        """returns the innermost schemar"""
        from .database import Schema
        return self.inner(Schema)

    @property
    def inner_table(self):
        """return the innermost table"""
        from .database import Table
        return self.inner(Table)

    @property
    def outer_class(self):
        """returns the outermost class"""
        return self.parent and self.parent.outer_class

    @property
    def outer_module(self):
        """returns the outermost module"""
        from .cc import Module as ccModule
        from .py import Module as pyModule
        return (self.parent and self.parent.outer_module) or ((
            isinstance(self, (ccModule, pyModule)) or None) and self)

    @property
    def outer_namespace(self):
        """returns the outermost namespace"""
        from .cc import Namespace
        return (self.parent and self.parent.outer_namespace) or ((
            isinstance(self, Namespace) or None) and self)

    @property
    def outer_folder(self):
        """returns the outermost folder"""
        from .Folder import Folder
        return (self.parent and self.parent.outer_folder) or ((
            isinstance(self, Folder) or None) and self)

    @property
    def outer_schema(self):
        """returns the outermost schema"""
        from .database import Schema
        return (self.parent and self.parent.outer_schema) or ((
            isinstance(self, Schema) or None) and self)

    @property
    def types(self):
        """This method gets the list of visible types"""
        return (self.outer_class or self.parent).types

    @property
    def level_classes(self):
        """return the list of classes inside this level"""
        from .cc import Class as ccClass
        from .cc import Class as pyClass
        cls = self.outer_class
        return self(ccClass, pyClass, filter=lambda x: x.parent.outer_class == cls)

    @property
    def top_namespaces(self):
        """return the list of top namespaces"""
        return [x for x in self.namespaces if x.outer_namespace == x]

    @property
    def top_folders(self):
        """return the list of top folders"""
        return [x for x in self.folders if x.outer_folder == x]

    @property
    def parent(self):
        """return the parent object"""
        return self._parent

    @property
    def path(self):
        """returns the ordered parents list"""
        return ((self.parent and self.parent.path) or []) + [self]

    @property
    def scope(self):
        """Get the scope"""
        return (self._parent and self._parent.scope) or ''

    @property
    def scoped_name(self):
        """returns the absolute name, with scope"""
        return '{self.scope}{self._name}'.format(self=self)

    @property
    def template_types(self):
        """Returns the list of nested template types"""
        return (self.parent and self.parent.template_types) or []

    def hasChild(self, **kwargs):
        """Checks the existence of some child"""
        recurse = kwargs.get('recurse', True)
        obj = kwargs.get('obj', None)
        if obj is not None:
            t = type(obj)
            if not recurse:
                return obj in self[t]
        else:
            t = kwargs.get('type', None)
            name = kwargs.get('name', None)
            if not recurse:
                return name in [x._name for x in self[t]]
        for c, l in self._child.items():
            if hasattr(c, 'hasChild'):
                for x in l:
                    if x.hasChild(**kwargs):
                        return True
        return False

    def __getstate__(self):
        """Set picke context"""
        state = dict(self.__dict__)
        if '_parentIndex' in state:
            del state['_parentIndex']
        if '_pane' in state:
            del state['_pane']
        if '_paneIndex' in state:
            del state['_paneIndex']
        return state

    def Delete(self):
        """Remove all the elements"""
        self.DeleteChilds()
        super(TCommon, self).Delete()

    def DeleteChilds(self):
        """Remove all the child elements"""
        items = self._child.keys()
        for cl in items:
            rm = [x for x in self._child[cl]]
            for x in rm:
                x.Delete()

    def OnUndoRedoChanged(self):
        """Update from app"""
        super(TCommon, self).OnUndoRedoChanged()
        self.update_container()
        context.RenderUndoRedoChanged(self)

    #def OnUndoRedoRemoving(self, root=True):
    def OnUndoRedoRemoving(self):
        """Prepare for delete"""
        super(TCommon, self).OnUndoRedoRemoving()
        childs = [item for group in self._child.values() for item in group]
        for child in childs:
            child.OnUndoRedoRemoving()
        context.RenderUndoRedoRemoving(self)

        if not (TransactionStack.InUndoRedo() or TransactionStack.InTransaction()):
            # With careful!! We are us doing using transactional semantics without transactions?
            # I'm unsure about this ... I need to delete undo stack?
            self.RemoveRelations()

    def RemoveRelations(self):
        """Utility for undo/redo"""
        if self._parent is not None:
            self._parent.removeChild(self)
            context.RenderUndoRedoChanged(self._parent)

    def RestoreRelations(self):
        """Utility for undo/redo"""
        if self._parent is not None:
            self._parent.addChild(self)
            context.RenderUndoRedoChanged(self._parent)

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        if not (TransactionStack.InUndoRedo() or TransactionStack.InTransaction()):
            # With careful!! What we are doing using transactional semantics without a transaction?
            # I'm unsure about this ... I need to delete undo stack?
            self.RestoreRelations()
        context.RenderUndoRedoAdd(self)
        super(TCommon, self).OnUndoRedoAdd()
        childs = [item for group in self._child.values() for item in group]
        childs.reverse()
        for child in childs:
            child.OnUndoRedoAdd()

    def OnUndoRedoLoaded(self):
        """Restore object after loading"""
        context.RenderLoadedAdd(self)
        rlc = list(reversed(list(self._child.keys())))
        for c in rlc:
            rlo = list(reversed(self._child[c]))
            for o in rlo:
                o.OnUndoRedoLoaded()

    def OnUndoRedoUnloaded(self):
        """Restore object after loading"""
        rlc = list(reversed(list(self._child.keys())))
        for c in rlc:
            rlo = list(reversed(self._child[c]))
            for o in rlo:
                o.OnUndoRedoUnloaded()
        context.RenderUndoRedoRemoving(self)

    def index(self, obj):
        """Get the index of an child object inside his group"""
        t = type(obj)
        return ((t in self._child and
            obj in self._child[t] and
            self._child[t].index(obj) + 1) or 0) - 1

    def addChild(self, obj, prev=None):
        """Adds a child member to dictionary"""
        cls = type(obj)
        if cls not in self._child:
            self._child[cls] = [obj]
            return
        index = (prev and self.index(prev) + 1) or getattr(obj, '_parentIndex', len(self._child[cls]))
        if index:
            index = min(index, len(self._child[cls]))
        if obj not in self._child[cls]:
            self._child[cls].insert(index, obj)
        else:
            old_index = self._child[cls].index(obj)
            if index != old_index:
                self._child[cls].pop(old_index)
                self._child[cls].insert(index, obj)

    def removeChild(self, obj):
        """Remove a child member from dictionary"""
        cls = type(obj)
        index = self.index(obj)
        if index >= 0:
            assert obj == self._child[cls].pop(index)
            obj._parentIndex = index

