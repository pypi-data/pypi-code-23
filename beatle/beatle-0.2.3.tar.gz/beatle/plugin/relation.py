# -*- coding: utf-8 -*-

import os

import xml.etree.ElementTree as et
from posix import R_OK

class xmlmetadoc(object):
    """This class represents a xml document containing definitions"""
    def __init__(self, partname, **kwargs):
        """constructs the object from the document part name and version"""
        self.ok = False
        path = os.path.join(os.getcwd(), 'plugin','models','relation',
            kwargs.get('version', 'standard'), partname)
        if not os.path.isfile(path):
            print('file {0} is missing'.format(path))
            return 
        if not os.access(path, R_OK):
            print('file {0} is not readable'.format(path))
            return 
        try:
            self.dictionary = kwargs.get('dictionary', {})
            self.target = self.dictionary.get('parent', None)
            if self.target is None:
                print('missing parent target reading definitions from {0}'.format(path))
                return 
            self.tree = et.parse(path)  # retorna et.ElementTree
            self.root = self.tree.getroot()  # retorna et.Element
            parent = self.dictionary.get('parent', None)
            self.filter = kwargs.get('filter', None)
            self.ok = True
            self.load_definitions()
        except:
            self.ok = False
            print('failed parsing xml file {0}'.format(path))
            
    def filter_set(self, component_set):
        """Evaluate a set, filter out the invalid components, 
        and return a list of (expression, puntuation) for
        the remaining components"""
        result = []
        for component in component_set:
            puntuation = 0
            filter = component.get('filter', None)
            if filter is None:
                result.append((component, 0))
                continue
            filter = filter.strip()[1:-1]  #  { and } left
            filtered_out = False
            for condition in filter.split(','):
                clause, value = condition.split(':')
                if value in ['True', 'False']:
                    value = eval(value)
                if clause in self.filter:
                    if self.filter[clause] != value:
                        filtered_out = True
                        break
                    puntuation += 1
            if not filtered_out:
                result.append((component, puntuation))
        # sort with better first
        result.sort(key=lambda x:-x[1])
        return result
    
    def better(self, component_set):
        """Apply a filter_set and select any best component. 
        Return None if no option is found"""
        evaluated = self.filter_set(component_set)
        if len(evaluated) == 0:
            return None
        return  evaluated[0][0]
            
    def load_definitions(self):
        """Read the definitions inside the document"""
        if self.ok is False:
            return
        definition_set = self.root.find('definitions')
        if definition_set is None:
            return
        for definition in definition_set:
            text = definition.findtext('.')
            for item, expression in [text.split('=')]:
                value = expression.format(**self.dictionary)
                if value in ['True', 'False']:
                    value = eval(value)
                self.dictionary[item] = value
                    
    def load_types(self, container = None, container_instance = None):
        import model
        if container is None:
            container = self.root
        type_set = container.find('types') or []
        if type_set is None:
            return        
        if container_instance is None:
            container_instance = self.target
        for type_ in type_set:
            kwargs = {}
            for arg in type_.keys():
                value = type_.get(arg).format(**self.dictionary)
                if value in ['True', 'False']:
                    value = eval(value)
                kwargs[arg] = value
            kwargs.update({'parent': container_instance, 'readonly': True})
            type_instance  = model.cc.Type(**kwargs)
            self.dictionary.update({type_instance.name: type_instance})
                        
    def load_members(self, container=None, container_instance=None):
        """Read the members from the document"""
        import model
        if container is None:
            container = self.root
        if container_instance is None:
            container_instance = self.target 
        member_set = container.find('members')
        if member_set is None:
            return
        for member in member_set:
            kwargs = {}
            for arg in member.keys():
                expression = member.get(arg).format(**self.dictionary)
                if arg == 'type' or expression in ['True', 'False']:
                    kwargs[arg] = eval(expression, self.dictionary)
                else:
                    kwargs[arg] = expression
            if 'type' in kwargs:
                kwargs['type'] = model.cc.typeinst(**kwargs)
            kwargs.update({'parent': container_instance, 'readonly': True})
            element = model.cc.MemberData(**kwargs)
            #  some elements needs further named references from runtime container
            if 'handler' in kwargs:
                setattr(container_instance, kwargs['handler'], element)
                
    def load_arguments(self, container, container_instance):
        """Read the arguments from the document"""
        import model
        argument_set = container.find('args')
        if argument_set is None:
            return 
        for argument in argument_set:
            kwargs = {}
            for arg in argument.keys():
                value = argument.get(arg).format(**self.dictionary)
                if arg == 'type' or value in ['True', 'False']:
                    kwargs[arg] = eval(value, self.dictionary)
                else:
                    kwargs[arg] = value
            kwargs['type'] = model.cc.typeinst(**kwargs)
            kwargs.update({'parent': container_instance, 'readonly': True})
            model.cc.Argument(**kwargs)        
                
    def load_constructors(self, container = None, container_instance = None):
        """Read the elements from the document"""
        import model
        if container is None:
            container = self.root
        constructor_set = container.find('ctors') or container.find('constructors')
        if constructor_set is None:
            return
        if container_instance is None:
            container_instance = self.target
        for constructor in constructor_set:
            kwargs = {}
            for arg in constructor.keys():
                expression = constructor.get(arg).format(**self.dictionary)
                if expression in ['True', 'False']:
                    kwargs[arg] = eval(expression, self.dictionary)
                else:
                    kwargs[arg] = expression
            init_set = constructor.findall('init')
            if init_set is not None:
                init = self.better(init_set)
                if init is not None:
                    kwargs['init'] = init.findtext('.').format(**self.dictionary)
            contents_set = constructor.findall('content')
            if contents_set is None:
                kwargs['content'] = ''
            else:
                content = self.better(contents_set)
                if content is not None:
                    kwargs['content'] = content.findtext('.').format(**self.dictionary)
                else:
                    kwargs['content'] = ''
            kwargs.update({'parent': container_instance, 'readonly': True})
            constructor_instance = model.cc.Constructor(**kwargs)
            # tomamos los argumentos
            self.load_arguments(constructor, constructor_instance)
            
    def load_methods(self, container = None, container_instance = None):
        """Read the elements from the document"""
        import model
        if container is None:
            container = self.root
        method_set = container.find('methods')
        if method_set is None:
            return
        if container_instance is None:
            container_instance = self.target
        for method in method_set:
            kwargs = {}
            for arg in method.keys():
                expression = method.get(arg).format(**self.dictionary)
                if arg == 'type':
                    if len(expression):
                        value = eval(expression, self.dictionary)
                    else:
                        value = self.dictionary[expression]  # implicit type
                elif expression in ['True', 'False']:
                    value = eval(expression, self.dictionary)
                else:
                    value = expression
                kwargs[arg] = value
                    
            contents_set = method.findall('content')
            if contents_set is None:
                kwargs['content'] = ''
            else:
                content = self.better(contents_set)
                if content is not None:
                    kwargs['content'] = content.findtext('.').format(**self.dictionary)
                else:
                    kwargs['content'] = ''
            kwargs['type'] = model.cc.typeinst(**kwargs)
            kwargs.update({'parent': container_instance, 'readonly': True})
            method_instance = model.cc.MemberMethod(**kwargs)
            # tomamos los argumentos
            self.load_arguments(method, method_instance)
            
    def load_destructor(self, container = None, container_instance = None):
        """Read the elements from the document"""
        import model
        if container is None:
            container = self.root
        destructor = container.find('dtor') or container.find('destructor') 
        if destructor is None:
            return
        if container_instance is None:
            container_instance = self.target
        kwargs = {}
        for arg in destructor.keys():
            expression = destructor.get(arg).format(**self.dictionary)
            if expression in ['True', 'False']:
                kwargs[arg] = eval(expression, self.dictionary)
            else:
                kwargs[arg] = expression                    
            contents_set = destructor.findall('content')
            if contents_set is None:
                kwargs['content'] = ''
            else:
                content = self.better(contents_set)
                if content is not None:
                    kwargs['content'] = content.findtext('.').format(**self.dictionary)
                else:
                    kwargs['content'] = ''
            kwargs.update({'parent': container_instance, 'readonly': True})
            method_instance = model.cc.Destructor(**kwargs)
            
    def load_classes(self):
        """Read the classes from the document"""
        import model
        classes_set = self.root.find('classes')
        if classes_set is None:
            return
        for class_ in classes_set:
            kwargs = {}
            # read class attributes
            for arg in class_.keys():
                value = class_.get(arg).format(**self.dictionary)
                if value in ['True', 'False']:
                    value = eval(value)
                kwargs[arg] = value
            # set aguments
            kwargs.update({'parent': self.target, 'readonly': True})
            # setup
            class_instance = model.cc.Class(**kwargs)
            self.dictionary.update({class_instance.name: class_instance})
            # find types
            self.load_types(class_, class_instance)
            # find los miembros
            self.load_members(class_, class_instance)
            # ctors
            self.load_constructors(class_, class_instance)
            # methods
            self.load_methods(class_, class_instance)
            #destructor
            self.load_destructor(class_, class_instance)
            

def relationMembers(**kwargs):
    """
    Este metodo lee la definicion de los metodos de un
    lado de la relacion y los crea

    Parametros:
        version: version de metodos por defecto, standard
        part: lado de la relacion (to o from)
        filter: dimodelionario de booleanos de selemodelion de version
        dictionary: dimodelionario de valores a utilizar en la evaluacion

    """
    doc = '{0}Members.xml'.format(kwargs['part'])
    meta = xmlmetadoc(doc,**kwargs)
    if meta.ok:
        meta.load_members()


def relationMethods(**kwargs):
    """
    Este metodo lee la definicion de los metodos de un
    lado de la relacion y los crea.

    Parametros:
        version: version de metodos por defecto, standard
        part: lado de la relacion (to o from)
        filter: dimodelionario de booleanos de selemodelion de version
        dictionary: dimodelionario de valores a utilizar en la evaluacion

    Retorna:

        None en caso de error
        Array de definicion de metodos.

    Comentarios:

        Los parametros de filtro permiten seleccionar entre
        diferentes versiones por ejemplo, de compatibilidad C++
        o niveles de seguridad (criticos), implementacion estatica
        presencia de metodos de busqueda, etc. Se selemodeliona
        el mejor matching y se excluyen aquellos metodos que
        no tengan ninguna version compatible con los filtros.

        Respecto de los simbolos utilizados en las declaraciones,
        esto es un aspecto pendiente de normalizar y documentar,
        ya que por ahora algunos de ellos dependen de la implementacion
        de los valores miembro.


    """
    doc = '{0}Methods.xml'.format(kwargs['part'])
    meta = xmlmetadoc(doc,**kwargs)
    if meta.ok:
        meta.load_methods()


def relationClasses(**kwargs):
    """
    Realiza la construccion de las clases anidadas
    definidas por la relacion
    """
    doc = '{0}Classes.xml'.format(kwargs['part'])
    meta = xmlmetadoc(doc,**kwargs)
    if meta.ok:
        meta.load_classes()
        
#     path = os.path.join(os.getcwd(), 'plugin', 'models', 'relation',
#         kwargs.get('version', 'standard'), doc)
#     key = kwargs.get('filter', None)
#     if not os.path.isfile(path):
#         print('{0} is missing'.format(path))
#         return
#     try:
#         tree = et.parse(path)
#         root = tree.getroot()
#         dictionary = kwargs.get('dictionary', {})
#         parent = dictionary.get('parent', None)
#         if not parent:
#             print('parent is missing')
#             return
#         # read definitions and add it to dict
#         defs = root.find('definitions')
#         if defs is not None:
#             for d in defs:
#                 text = d.findtext('.')
#                 for x, y in [text.split('=')]:
#                     v = y.format(**dictionary)
#                     if v in ['True', 'False']:
#                         v = eval(v)
#                     dictionary[x] = v
# 
#         classes = root.find('classes')
#         if classes is None:
#             print('missing classes')
#             return
#         for _class in classes:
#             keys = {}
#             # leemos los atributos de la clase
#             for x in _class.keys():
#                 keys[x] = _class.get(x).format(**dictionary)
#             # ponemos atributos
#             keys.update({'parent': parent, 'readonly': kwargs.get('readonly', True)})
#             # creamos la clase
#             cls = model.cc.Class(**keys)
#             dictionary.update({cls.name: cls})
#             # buscamos los tipos definidos en la clase
#             types = _class.find('types')
#             for type in types:
#                 keys = {}
#                 for x in type.keys():
#                     keys[x] = type.get(x).format(**dictionary)
#                 keys.update({'parent': cls})
#                 t = model.cc.Type(**keys)
#                 dictionary.update({t.name: t})
#             # buscamos los miembros
#             members = _class.find("members")
#             for member in members:
#                 keys = {}
#                 for x in member.keys():
#                     keys[x] = member.get(x).format(**dictionary)
#                     if x in ['type', 'static', 'const', 'volatile', 'virtual', 'ptr', 'ref', 'mutable']:
#                         keys[x] = eval(keys[x], dictionary)
#                 keys['type'] = model.cc.typeinst(**keys)
#                 keys.update({'parent': cls})
#                 model.cc.MemberData(**keys)
#             # constructores
#             ctors = _class.find('ctors')
#             for _ctor in ctors:
#                 keys = {'parent': cls, 'name': cls.name, 'autoargs': False}
#                 for x in _ctor.keys():
#                     keys[x] = _ctor.get(x).format(**dictionary)
#                     if x == 'inline':
#                         keys[x] = eval(keys[x], dictionary)
#                 ctor = model.cc.Constructor(**keys)
#                 # argumentos
#                 args = _ctor.find('args')
#                 for arg in args:
#                     keys = {'parent': ctor}
#                     for x in arg.keys():
#                         keys[x] = arg.get(x).format(**dictionary)
#                         if x == 'type':
#                             keys[x] = eval(keys[x], dictionary)
#                     keys['type'] = model.cc.typeinst(**keys)
#                     model.cc.Argument(**keys)
# 
#             # buscamos los metodos
#             methods = _class.find('methods')
#             for _method in methods:
#                 keys = {'parent': cls}
#                 for x in _method.keys():
#                     k = keys[x] = _method.get(x).format(**dictionary)
#                     if x == 'type':
#                         if k:
#                             keys[x] = eval(k, dictionary)
#                         else:
#                             keys[x] = dictionary[k]  # implicit type
#                     elif k in ['True', 'False']:
#                         keys[x] = eval(k, dictionary)
# 
#                 contents = _method.findall('content')
#                 if contents is None:
#                     keys['content'] = ''
#                 else:
#                     best_match = -1
#                     best_content = None
#                     for content in contents:
#                         #verificamos el filtro
#                         f = content.get('filter', None)
#                         ok = True
#                         match = 0
#                         if f is not None:
#                             f = f.strip()[1:-1]  # quitamos los { y }
#                             fk = dict([(x.strip(), (y.strip() == 'True'))
#                                 for x, y in [list(v.split(':')) for v in f.split(',')]])
#                                 # para pasar el filtro, deben coincidir los valores
#                             for k in key:
#                                 if k in fk:
#                                     if key[k] != fk[k]:
#                                         ok = False
#                                         break
#                                     match += 1
#                         if ok and match > best_match:
#                             best_content = content
#                             best_match = match
#                     if best_content is None:
#                         keys['content'] = ''
#                     else:
#                         keys['content'] = best_content.findtext('.').format(**dictionary)
#                        
#                 keys['type'] = model.cc.typeinst(**keys)
#                 keys.update({'parent': cls})
# 
#                 method = model.cc.MemberMethod(**keys)
#                 # argumentos
#                 args = _method.find('args')
#                 for arg in args:
#                     keys = {}
#                     for x in arg.keys():
#                         keys[x] = arg.get(x).format(**dictionary)
#                         if x in ['type', 'static', 'const', 'volatile', 'ptr', 'ref']:
#                             keys[x] = eval(keys[x], dictionary)
#                     keys['type'] = model.cc.typeinst(**keys)
#                     keys.update({'parent': method})
#                     model.cc.Argument(**keys)
#             #destructor
#             _dtor = _class.find('dtor')
#             if _dtor:
#                 keys = {}
#                 for x in _dtor.keys():
#                     keys[x] = _dtor.get(x).format(**dictionary)
#                     if x in ['virtual', 'inline']:
#                         keys[x] = eval(keys[x], dictionary)
#                 keys.update({'parent': cls, 'name': cls.name})
#                 model.cc.Destructor(**keys)
# 
#     except Exception, e:
#         print('Exception {msg} failed reading {p}'.format(
#             msg=e.message, p=path))
#         return
