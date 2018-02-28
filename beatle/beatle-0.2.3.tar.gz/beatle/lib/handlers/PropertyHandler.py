"""
ProperyHandler
==============
Global class for handling properties.
Each property is defined by an hierarchical path and a value.
The possible values for a property are restricted by type, type and range or range.  

Some subset of properties can be grouped into and style. In this case,
These properties are keyed by the range of any style property, whose actual value
defines the keyed property values.

Syled properties always must define default value (if none is specified, the 
first value is assumed as defaul value)

At last, properties may be serializables.
   
"""

class Property(object):
    """Single property"""
    def __init__(self, name, value, property_type=None, property_key=None, property_range=None):
        self._name = name
        self._value = value
        self._key = property_key
        self._type = property_type
        self._range = property_range
    
    @property
    def name(self):
        return self._name
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, _value):
        # pending checks
        self._value = _value
    

class PropertyContext(object):
    """Single hierarchy step in property handler"""
    def __init__(self, parent=None, *args):
        """Initialize context"""
        self._context = {}
        self._parent = parent
        if len(args) > 0:
            self._context[args[0]] = PropertyContext(parent=self, *args[1:])
            
    @property
    def tail(self):
        """return first end context"""
        for k in self._context:
            return self._context[k].first
        return self 
        
    def register(self, *args):
        """Append a new context branch and returns last property"""
        if len(args) > 0:
            key = args[0]
            if key in self._context:
                return self._context[key].append(*args[1:])
            self._context[key] = PropertyContext(parent=self, *args[1:])
            return self._context[key].tail()
        return self 
    
class PropertyHandler(object):
    """Master class of property register""" 
    _contexts = PropertyContext()
    _properties = {_contexts:[]}
    def __init__(self):
        raise RuntimeError('PropertyHandler is a singleton')
        super(PropertyHandler, self).__init__()
        
    @classmethod
    def RegisterProperty(cls, name, value, *context):
        """Add new property"""
        context = cls._contexts.register(*context)
        if context not in cls._properties:
            cls._properties[context] = {}  # dictionnary name -> property
        context_dict = cls._properties[context]
        if name not in context_dict:
            context_dict[name] = Property(name=name, value=value)
        return context_dict[name]             
        
