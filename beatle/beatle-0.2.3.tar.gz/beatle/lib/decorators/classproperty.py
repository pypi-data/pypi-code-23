# -*- coding: utf-8 -*-


class clsspptdscrptr(object):
    """descriptor for class property"""
    def __init__(self, getter, setter=None):
        """init"""
        self._getter = classmethod(getter)
        self._setter = setter and classmethod(setter)
        super(clsspptdscrptr, self).__init__()

    def __get__(self, inst, instype=None):
        """"""
        return self._getter.__get__(inst, instype or type(inst))()

    def __set__(self, inst, value):
        """"""
        assert self._setter
        return self._setter.__get__(inst, type(inst))(value)

    def setter(self, setter):
        """"""
        self._setter = classmethod(setter)
        return self


def classproperty(getter, setter=None):
    """classproperty decorator.
    
    This decorator makes possible to declare class-level properties, just 
    as we can do with instance properties.
    Example:
        class a(object):
            _name = 'a name'
            
            @classproperty
            def name(cls):
                return cls._name
                
            @name.setter
            def name(cls, value):
                raise 'name is readonly'
                
    """
    return clsspptdscrptr(getter, setter)


