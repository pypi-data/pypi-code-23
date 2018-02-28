# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 08:28:25 2013

@author: mel
"""
import model
import tran
from tran import TransactionStack


class Relation(tran.TransactionObject):
    """Implements a relation object"""
    # The Relation class is the hidden key of the both sides
    # This class is referenced by RelationFrom and RelationTo
    # by his _key attribute
    def __init__(self, **kwargs):
        """Init relation"""
        self._critical = kwargs.get('critical', False)
        self._global = kwargs.get('Global', False)
        self._filter = kwargs.get('filte', False)
        self._unique = kwargs.get('unique', False)
        self._unikey = kwargs.get('key', None)
        self._implementation = kwargs.get('implementation', "native")
        self._note = kwargs.get('note', "")
        self._project = kwargs['FROM'].project
        self._FROM = RelationFrom(
            name=kwargs['fromName'],
            parent=kwargs['TO'],
            FROM=kwargs['FROM'],
            access=kwargs.get('fromaccess', "public"),
            min=kwargs.get('frommin', None),
            max=kwargs.get('frommax', None),
            key=self)
        self._TO = RelationTo(
            name=kwargs['toName'],
            parent=kwargs['FROM'],
            TO=kwargs['TO'],
            access=kwargs.get('toaccess', "public"),
            min=kwargs.get('tomin', None),
            max=kwargs.get('tomax', None),
            key=self)
        # add relation to class diagrams
        for dia in self._project(model.ClassDiagram):
            child = dia.FindElement(kwargs['TO'])
            if child is None:
                continue
            parent = dia.FindElement(kwargs['FROM'])
            if parent is None:
                continue
            dia.SaveState()
            dia.AddRelation(self, parent, child)
        super(Relation, self).__init__()
        self.RecreateMembers()

    def RecreateMembers(self):
        """Do elements initialization"""
        self._FROM.RecreateMembers()
        self._TO.RecreateMembers()

    def init_dictionary(self, dictionary):
        """Inicializa el diccionario requerido por el parsing
        de las relaciones."""
        dictionary.update((x._name.replace(' ', '_'), x) for x in self._project.types)
        dictionary.update({
            'FROM': self._FROM._FROM,
            'TO': self._TO._TO,
            'fromRel': self._FROM,
            'toRel': self._TO
            })

    @property
    def project(self):
        """Gets the project"""
        return self._project

    @property
    def note(self):
        """Gets the comments"""
        return self._note

    @note.setter
    def note(self, value):
        """Sets the note"""
        self._note = value

    def SaveState(self, onlyRoot=False):
        """Save the current state in the undo stack"""
        if not onlyRoot:
            self._FROM.__SaveState__()
            self._TO.__SaveState__()
        super(Relation, self).SaveState()

    def OnUndoRedoAdd(self):
        """Restore object from undo"""
        for dia in self._project(model.ClassDiagram):
            diarel = dia.FindElement(self)
            if diarel is not None:
                diarel.RefreshChanges()
                if hasattr(dia, '_pane') and dia._pane is not None:
                    dia._pane.Refresh()
        super(Relation, self).OnUndoRedoAdd()

    def OnUndoRedoChanged(self):
        """Handles changes"""
        if not TransactionStack.InUndoRedo():
            self.RecreateMembers()
        project = self.project
        if project is None:
            return
        dias = project(model.ClassDiagram)
        for dia in dias:
            diarel = dia.FindElement(self)
            if diarel is not None:
                diarel.RefreshChanges()
                if hasattr(dia, '_pane') and dia._pane is not None:
                    dia._pane.Refresh()
        super(Relation, self).OnUndoRedoChanged()

    def OnUndoRedoRemoving(self):
        """Prepare for delete"""
        super(Relation, self).OnUndoRedoRemoving()

    def Delete(self):
        """Transaction delete"""
        self._FROM.Delete()
        self._TO.Delete()
        project = self.project
        if project is not None:
            #process diagrams
            dias = project.diagrams
            for dia in dias:
                # Check if inherit is in
                elem = dia.FindElement(self)
                if elem is not None:
                    dia.SaveState()
                    dia.RemoveElement(elem)
                    if hasattr(dia, '_pane') and dia._pane is not None:
                        dia._pane.Refresh()
        self._FROM.parent.UpdateClassRelations()
        self._TO.parent.UpdateClassRelations()
        super(Relation, self).Delete()
        
    def createRelationMembers(self, client):
        """Create the relation members for the client side"""
        #general dictionary
        from plugin import relationMembers
        dictionary = {}
        self.init_dictionary(dictionary)
        dictionary.update({'parent': client, 'readonly': True})
        if self._implementation == "native":
            relationMembers(
                version='standard',
                filter={'transactional': False},
                part=client._side, dictionary=dictionary)
                    
    def createRelationMethods(self, client):
        """Create the relation methods for the FROM side"""
        #general dictionary
        from plugin import relationMethods
        dictionary = {}
        self.init_dictionary(dictionary)
        dictionary.update({'parent': client, 'readonly': True})
        if self._implementation == "native":
            relationMethods(
                version='standard',
                filter={'transactional': False},
                part=client._side, dictionary=dictionary)
                        
    def createRelationClasses(self, client):
        """Create the relation classes for the FROM side"""
        #general dictionary
        from plugin import relationClasses
        dictionary = {}
        self.init_dictionary(dictionary)
        dictionary.update({'parent': client, 'readonly': True})
        if self._implementation == "native":
            relationClasses(
                version='standard',
                filter={'transactional': False},
                part=client._side, dictionary=dictionary)
        client.inner_class.UpdateClassRelations()
    

class RelationFrom(model.TComponent):
    """Implements relation FROM"""
    def __init__(self, **kwargs):
        """Initialize the FROM relation"""
        self._side = 'FROM'
        self._FROM = kwargs['FROM']
        self._key = kwargs['key']
        self._access = kwargs.get('access', "public")
        self._minCardinal = kwargs.get('min', None)
        self._maxCardinal = kwargs.get('max', None)
        super(RelationFrom, self).__init__(**kwargs)

    def RecreateMembers(self):
        """Do extra project initialization"""
        #ensure no elements
        obj = []
        for cls in self._child:
            for element in self[cls]:
                obj.append(element)
        for element in obj:
            element.Delete()
        # recreate elements
        #self._createRelationMembers()
        self._key.createRelationMembers(self)
        self._key.createRelationMethods(self)
        self._key.createRelationClasses(self)


    def GetFrom(self):
        """Amodeless FROM class"""
        return self._FROM

    @property
    def bitmap_index(self):
        """Index of tree image"""
        import app.resources as rc
        return rc.GetBitmapIndex("parent", self._access)

    def __SaveState__(self, onlyRoot=False):
        """Internal save state"""
        super(RelationFrom, self).SaveState()

    def SaveState(self, onlyRoot=False):
        """Redirects saving state to root"""
        self._key.SaveState(onlyRoot)


class RelationTo(model.TComponent):
    """Implements relation TO"""
    def __init__(self, **kwargs):
        """Initialize the TO relation"""
        self._side = 'TO'
        self._TO = kwargs['TO']
        self._key = kwargs['key']
        self._access = kwargs.get('access', "public")
        self._minCardinal = kwargs.get('min', None)
        self._maxCardinal = kwargs.get('max', None)
        super(RelationTo, self).__init__(**kwargs)

    def RecreateMembers(self):
        """Do extra project initialization"""
        #ensure no elements
        obj = []
        for cls in self._child:
            for element in self[cls]:
                obj.append(element)
        for element in obj:
            element.Delete()
        # recreate elements
        self._key.createRelationMembers(self)
        self._key.createRelationMethods(self)
        self._key.createRelationClasses(self)

    def GetTo(self):
        """Amodeless TO class"""
        return self._TO

    @property
    def bitmap_index(self):
        """Index of tree image"""
        import app.resources as rc        
        return rc.GetBitmapIndex("child", self._access)

    def __SaveState__(self):
        """Internal save state"""
        super(RelationTo, self).SaveState()

    def SaveState(self, onlyRoot=False):
        """Redirects saving state to root"""
        self._key.SaveState(onlyRoot)
