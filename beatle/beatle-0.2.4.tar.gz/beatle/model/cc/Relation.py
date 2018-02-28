# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 08:28:25 2013

@author: mel
"""
from beatle.tran import TransactionStack, TransactionObject
from beatle.model import TComponent, ClassDiagram
from beatle.model.cc.Type import typeinst
from beatle.model.cc._MemberMethod import MemberMethod 
from beatle.model.cc._MemberData import MemberData
from beatle.model.cc.Argument import Argument 


class Relation(TransactionObject):
    """Implements a relation object"""
    # The Relation class is the hidden key of the both sides
    # This class is referenced by RelationFrom and RelationTo
    # by his _key attribute
    def __init__(self, **kwargs):
        """Init relation"""
        self._critical = kwargs.get('critical', False)
        self._global = kwargs.get('Global', False)
        self._filter = kwargs.get('filter', False)
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
        for dia in self._project(ClassDiagram):
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

    def types_dictionary(self):
        """Inicializa el diccionario requerido por el parsing
        de las relaciones."""
        # incorpora los tipos
        types_dictionary = {}
        types_dictionary.update((x._name.replace(' ', '_'), x) for x in self._project.types)
        types_dictionary.update({
            'FROM': self._FROM._FROM,
            'TO': self._TO._TO,
            'fromRel': self._FROM,
            'toRel': self._TO
            })
        return types_dictionary
    
    def read_method_def(self, file_name):
        path = os.path.join(os.getcwd(), 'plugin', 'models', 'relation','standard',file_name)
        with open(path, 'r') as file:
            data=file.read()
        return data
    
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
        for dia in self._project(ClassDiagram):
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
        dias = project(ClassDiagram)
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
        
    def __create_from_single_association(self, client):
        """Create the association members for the to side of.
        The members are of the form
            private:
                class_from* _p_{from_alias} = nullptr;
            public:
                void set_{from_alias}({class_from}* p_{from_alias});
                class_from* get_{from_alias}();
                void remove_{from_alias}({class_from}* p_{from_alias});
                void move_{from_alias}({class_from}* p_{from_alias});
                void replace_{from_alias}({class_from}* p_old_{from_alias}, {class_from}* p_new_{from_alias});
            """
        local_dict ={
            'prefix':client.parent._memberPrefix,
            'from_alias':client.name,
            'to_alias': self._FROM.name
        }
        dtypes = self.types_dictionary()
        # class_to* _p_class_to = nullptr;
        client._p_ptr = MemberData(
            type = typeinst(type=client._FROM, ptr=True),
            access = 'private',
            default = 'nullptr',
            name='p_{from_alias}'.format(**local_dict),
            static=self._global,
            parent=client 
            )
        

        # void set_{from_alias}({class_from}* p_{from_alias});
        method = MemberMethod(
            type = typeinst(type=dtypes['void']),
            access = public,
            inline = False,
            name = 'set_{from_alias}'.format(**local_dict),
            static = False,
            content = self.read_method_def("single_to_set").format(**local_dict),
            parent=client)
        
        Argument(type=typeinst(type=client._FROM,ptr=True), name='p_{from_alias}'.format(**local_dict), parent=method)
            
        # class_from* get_{from_alias}();
        MemberMethod(
            type=typeinst(type=client._FROM,ptr=True),
            access='public',
            inline=True,
            name='get_{from_alias}'.format(**local_dict),
            static=False,
            content='return {prefix}p_{from_alias};'.format(**local_dict),                
            parent=client
        )
        
        # void remove_{from_alias}({class_from}* p_{from_alias});
        MemberMethod(
            type=typeinst(type=client._FROM,ptr=True),
            access='public',
            inline=True,
            name='remove_{from_alias}'.format(**local_dict),
            static=False,
            content = self.read_method_def("single_to_remove").format(**local_dict),
            parent=client
        )
        Argument(type=typeinst(type=client._FROM,ptr=True), name='p_{from_alias}'.format(**local_dict), parent=method)
                
        # void move_{from_alias}({class_from}* p_{from_alias});
        method = MemberMethod(
            type = typeinst(type=dtypes['void']),
            access = public,
            inline = False,
            name = 'move_{from_alias}'.format(name=client.name),
            static = False,
            content = self.read_method_def("single_to_move").format(**local_dict),
            parent=client
        )
        Argument(type=typeinst(type=client._FROM,ptr=True), name='p_{from_alias}'.format(**local_dict), parent=method)
            
        # void replace_{from_alias}({class_from}* p_old_{from_alias}, {class_from}* p_new_{from_alias});
        method = MemberMethod(
            type = typeinst(type=dtypes['void']),
            access = public,
            inline = False,
            name = 'replace_{from_alias}'.format(name=client.name),
            static = False,
            content = self.read_method_def("single_to_replace").format(**local_dict),
            parent=client)
        Argument(type=typeinst(type=client._FROM,ptr=True), name='p_old_{from_alias}'.format(**local_dict), parent=method)
        Argument(type=typeinst(type=client._FROM,ptr=True), name='p_new_{from_alias}'.format(**local_dict), parent=method)
        
    def __create_to_single_association(self, client):
        """Create the association members for the from side of.
        The members are of the form
            private:
                class_to* _p_{to_alias} = nullptr;
            public:
                void set_{to_alias}({class_to}* p_{to_alias});
                class_to* get_{to_alias}();
                void remove_{to_alias}({class_to}* p_{to_alias});
                void move_{to_alias}({class_to}* p_{to_alias});
                void replace_{to_alias}({class_to}* p_old_{to_alias}, {class_to}* p_new_{to_alias});
            """
        local_dict ={
            'prefix':client.parent._memberPrefix,
            'to_alias':client.name,
            'from_alias': self._TO.name
        }
        dtypes = self.types_dictionary()
        # class_to* _p_class_to = nullptr;
        client._p_ptr = MemberData(
            type = typeinst(type=client._TO, ptr=True),
            access = 'private',
            default = 'nullptr',
            name='p_{to_alias}'.format(**local_dict),
            static=self._global,
            parent=client 
            )
        

        # void set_{to_alias}({class_to}* p_{to_alias});
        method = MemberMethod(
            type = typeinst(type=dtypes['void']),
            access = public,
            inline = False,
            name = 'set_{to_alias}'.format(**local_dict),
            static = False,
            content = self.read_method_def("single_from_set").format(**local_dict),
            parent=client)
        
        Argument(type=typeinst(type=client._TO,ptr=True), name='p_{to_alias}'.format(**local_dict), parent=method)
            
        # class_to* get_{to_alias}();
        MemberMethod(
            type=typeinst(type=client._FROM,ptr=True),
            access='public',
            inline=True,
            name='get_{to_alias}'.format(**local_dict),
            static=False,
            content='return {prefix}p_{to_alias};'.format(**local_dict),                
            parent=client
        )
        
        # void remove_{to_alias}({class_to}* p_{to_alias});
        MemberMethod(
            type=typeinst(type=client._FROM,ptr=True),
            access='public',
            inline=True,
            name='remove_{to_alias}'.format(**local_dict),
            static=False,
            content = self.read_method_def("single_from_remove").format(**local_dict),
            parent=client
        )
        Argument(type=typeinst(type=client._TO,ptr=True), name='p_{to_alias}'.format(**local_dict), parent=method)
        
        
        # void move_{to_alias}({class_to}* p_{to_alias});
        method = MemberMethod(
            type = typeinst(type=dtypes['void']),
            access = public,
            inline = False,
            name = 'move_{to_alias}'.format(name=client.name),
            static = False,
            content = self.read_method_def("single_from_move").format(**local_dict),
            parent=client)
        
        Argument(type=typeinst(type=client._TO,ptr=True), name='p_{to_alias}'.format(**local_dict), parent=method)
            
        # void replace_{to_alias}({class_to}* p_old_{to_alias}, {class_to}* p_new_{to_alias});
        method = MemberMethod(
            type = typeinst(type=dtypes['void']),
            access = public,
            inline = False,
            name = 'replace_{to_alias}'.format(name=client.name),
            static = False,
            content = self.read_method_def("single_from_replace").format(**local_dict),
            parent=client)
        Argument(type=typeinst(type=client._TO,ptr=True), name='p_old_{to_alias}'.format(**local_dict), parent=method)
        Argument(type=typeinst(type=client._TO,ptr=True), name='p_new_{to_alias}'.format(**local_dict), parent=method)
        

        
    def createRelationMembers(self, client):
        """Create the relation members for the client side"""
        if client == self._FROM:
            if self._TO._minCardinal is 0:
                self.__create_from_single_association(client)
            else: 
                # class_to* _p_next_class_to
                client._nextPtr = MemberData(
                    type=typeinst(type=client.parent,ptr=True),
                    access='private',
                    default='nullptr',
                    name='p_next_{name}'.format(name=client.name),
                    static=False,
                    parent=client
                )
                # class_to* _p_prev_class_to
                client._prevPtr=MemberData(
                    type=typeinst(type=client.parent,ptr=True),
                    access='private',
                    default='nullptr',
                    name='p_prev_{name}'.format(name=client.name),
                    static=False,
                    parent=client
                )
                if not self._global:
                    # class_from* _p_class_from
                    client._fromPtr = MemberData(
                        type=typeinst(type=client._FROM,ptr=True),
                        access='private',
                        default='nullptr',
                        name='p_{name}'.format(name=client.name),
                        static=self._global,
                        parent=client
                    )
                    # class_from* get_class_from()
                    MemberMethod(
                        type=typeinst(type=client._FROM,ptr=True),
                        access='public',
                        inline=True,
                        name='get_{name}'.format(name=client.name),
                        content='return {prefix}p_{name};'.format(prefix=self._TO._TO._memberPrefix, name=client.name),                
                        parent=client
                    )
                client.add_last = "add_last_{name}".format(name=client.name)
        else:
            if self._TO._minCardinal is 0:
                self.__create_to_single_association(client)
                return
            #client is TO
            types_dictionary = self.types_dictionary()
            
            fromPtr=self._FROM._fromPtr.name
            
            if client._maxCardinal is None or client._maxCardinal > 1:
                prevPtr = self._FROM._prevPtr.name
                nextPtr = self._FROM._nextPtr.name
                # class_to* _p_first_class_to
                client._firstToPtr = MemberData(
                    type=typeinst(type=client._TO,ptr=True),
                    access='private',
                    default='nullptr',
                    name='p_first_{name}'.format(name=client.name),
                    static=self._global,
                    parent=client
                )
                firstToPtr = client._firstToPtr.name
                
                # class_to* _p_last_class_to
                client._lastToPtr = MemberData(
                    type=typeinst(type=client._TO,ptr=True),
                    access='private',
                    default='nullptr',
                    name='p_last_{name}'.format(name=client.name),
                    static=self._global,
                    parent=client
                )
                lastToPtr = client._lastToPtr.name
                
                #unsigned long get_class_to_count()
                client._counter = MemberData(
                    type=typeinst(type=types_dictionary['unsigned_long']),
                    access='private',
                    default='0L',
                    name='{name}_count'.format(name=client.name),
                    static=self._global,
                    parent=client
                )
                counter = client._counter.name
                
                #void add_first_class_to(class_to *p_to)
                method = MemberMethod(
                    type=typeinst(type=types_dictionary['void']),
                    access='public',
                    inline=True,
                    name='add_first_{name}'.format(name=client.name),
                    static=self._global,
                    parent=client,
                    content = """
#if !defined(OPTIMISTIC)
    assert(this != nullptr);
    assert(p_{name} != nullptr);
    #if !defined(TOLERANT)
        assert( p_{name}->{fromPtr} == nullptr );
    #else
        if ( p_{name}->{fromPtr} != nullptr )
        {{
            assert( p_{name}->{fromPtr} == this );
            move_{name}_first(p_{name});
            return;
        }}
    #endif //TOLERANT
#endif //OPTIMISTIC
{counter}++;
p_{name}->{fromPtr} = this;
if ( {firstToPtr} != nullptr )
{{
    p_{name}->{nextPtr} = {firstToPtr};
    {firstToPtr}->{prevPtr} = p_{name};
    {firstToPtr} = p_{name};
}}
else
{{
    {firstToPtr} = p_{name};
    {lastToPtr} = p_{name};
}}""".format( name=client.name, 
              fromPtr=fromPtr,
              firstToPtr=firstToPtr,
              lastToPtr=lastToPtr,
              counter=counter,
              prevPtr=prevPtr,
              nextPtr=nextPtr)
                                      )
                Argument(type=typeinst(type=client._TO,ptr=True),
                        name='p_{name}'.format(name=client.name),
                        parent=method)
                
                #void add_last_class_to(class_to *p_to)
                method = MemberMethod(
                    type=typeinst(type=types_dictionary['void']),
                    access='public',
                    inline=True,
                    name='add_last_{name}'.format(name=client.name),
                    static=self._global,
                    parent=client,
                    content = """
#if !defined(OPTIMISTIC)
    assert(this != nullptr);
    assert(p_{name} != nullptr);
    #if !defined(TOLERANT)
        assert(p_{name}->{fromPtr} == nullptr);
    #else
        if(p_{name}->{fromPtr} != nullptr)
        {{
            assert(p_{name}->{fromPtr} == this);
            move_{name}_last(p_{name});
            return;
        }}
    #endif //TOLERANT
#endif //OPTIMISTIC
{counter}++;
p_{name}->{fromPtr} = this;
if ({lastToPtr} != nullptr)
{{
    p_{name}->{prevPtr} = {lastToPtr};
    {lastToPtr}->{nextPtr} = p_{name};
    {lastToPtr} = p_{name};
}}
else
{{
    {lastToPtr} = p_{name};
    {firstToPtr} = p_{name};
}}""".format( name=client.name, fromPtr=fromPtr,firstToPtr=firstToPtr,lastToPtr=lastToPtr,counter=counter,prevPtr=prevPtr,nextPtr=nextPtr))
                Argument(type=typeinst(type=client._TO,ptr=True),
                        name='p_{name}'.format(name=client.name),
                        parent=method)
                
        if False == True:
            # Old version: due to the difficult of maintenance, we disable it until better times
            #general dictionary
            from beatle.plugin import relationMembers
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
        from beatle.plugin import relationMethods
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
        from beatle.plugin import relationClasses
        dictionary = {}
        self.init_dictionary(dictionary)
        dictionary.update({'parent': client, 'readonly': True})
        if self._implementation == "native":
            relationClasses(
                version='standard',
                filter={'transactional': False},
                part=client._side, dictionary=dictionary)
        client.inner_class.UpdateClassRelations()
    

class RelationFrom(TComponent):
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
        objs = [x for cls in self._child for x in self[cls]]
        for element in objs:
            element.Delete()
        # recreate elements
        self._key.createRelationMembers(self)


    def GetFrom(self):
        """Amodeless FROM class"""
        return self._FROM

    @property
    def bitmap_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc
        return rc.GetBitmapIndex("parent", self._access)

    def __SaveState__(self, onlyRoot=False):
        """Internal save state"""
        super(RelationFrom, self).SaveState()

    def SaveState(self, onlyRoot=False):
        """Redirects saving state to root"""
        self._key.SaveState(onlyRoot)


class RelationTo(TComponent):
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
        objs = [x for cls in self._child for x in self[cls]]
        for element in objs:
            element.Delete()
        # recreate elements
        self._key.createRelationMembers(self)

    def GetTo(self):
        """Amodeless TO class"""
        return self._TO

    @property
    def bitmap_index(self):
        """Index of tree image"""
        from beatle.app import resources as rc        
        return rc.GetBitmapIndex("child", self._access)

    def __SaveState__(self):
        """Internal save state"""
        super(RelationTo, self).SaveState()

    def SaveState(self, onlyRoot=False):
        """Redirects saving state to root"""
        self._key.SaveState(onlyRoot)
