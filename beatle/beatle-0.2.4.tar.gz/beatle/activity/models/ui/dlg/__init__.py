# -*- coding: utf-8 -*-

from .ClassDiagram import ClassDiagramDialog
from .ContextItems import ContextItems
from .GenerateSources import GenerateSourcesDialog
from .Note import NoteDialog
from .Project import ProjectDialog


from beatle.activity.models.ui.dlg import cc
from beatle.activity.models.ui.dlg import py

def init():
    """Initialize this activity model ui"""
    from beatle import model
    associations = {
        model.Project: (ProjectDialog, 'edit project {0}'),
        model.cc.Namespace: (cc.NamespaceDialog, 'edit namespace {0}'),
        model.cc.Type: (cc.TypeDialog, 'edit type {0}'),
        model.cc.Class: (cc.ClassDialog, 'edit c++ class {0}'),
        model.py.Class: (py.PyClassDialog, 'edit python class {0}'),
        model.cc.Argument: (cc.ArgumentDialog, 'edit c++ method argument {0}'),
        model.py.Argument: (py.PyArgumentDialog, 'edit python method argument {0}'),
        model.ClassDiagram: (ClassDiagramDialog, 'edit class diagram {0}'),
        model.cc.Inheritance: (cc.InheritanceDialog, 'edit c++ inheritance {0}'),
        model.py.Inheritance: (py.PyInheritanceDialog, 'edit python inheritance {0}'),
        model.cc.MemberData: (cc.MemberDialog, 'edit c++ class member {0}'),
        model.py.MemberData: (py.PyMemberDialog, 'edit python class member {0}'),
        model.cc.Data: (cc.VariableDialog, 'edit c++ variable {0}'),
        model.py.Data: (py.PyVariableDialog, 'edit python variable {0}'),
        model.cc.Constructor: (cc.ConstructorDialog, 'edit c++ {0} constructor'),
        model.py.InitMethod: (py.PyMemberMethodDialog, 'edit python __init__ method'),
        model.cc.MemberMethod: (cc.MemberMethodDialog, 'edit c++ method {0}'),
        model.py.MemberMethod: (py.PyMemberMethodDialog, 'edit python method {0}'),
        model.cc.IsClassMethod: (cc.MemberMethodDialog, 'edit c++ method {0}'),
        model.cc.Destructor: (cc.DestructorDialog, 'edit c++ destructor {0}'),
        model.cc.Module: (cc.ModuleDialog, 'edit c++ module "{0}"'),
        model.cc.Function: (cc.FunctionDialog, 'edit c++ function {0}'),
        model.py.Function: (py.PyFunctionDialog, 'edit python function {0}'),
        model.Note: (NoteDialog, 'edit note'),
        model.cc.Enum: (cc.EnumDialog, 'edit c++ enum {0}'),
        model.Project: (ProjectDialog, 'edit project {0}'),
        model.cc.RelationFrom: (cc.RelationDialog, 'edit relation'),
        model.cc.RelationTo: (cc.RelationDialog, 'edit relation'),
        model.py.Module: (py.PyModuleDialog, 'edit python module {0}'),
        model.py.Import: (py.PyImportDialog, 'edit python import {0}'),
        model.py.Decorator: (py.PyDecoratorDialog, 'edit python decorator {0}'),
        model.cc.pyBoostModule: (cc.BoostPythonModuleDialog, 'edit boost.python module {0}'),
    }
    from beatle.app.ui.tools import DIALOG_DICT
    DIALOG_DICT.update(associations)

