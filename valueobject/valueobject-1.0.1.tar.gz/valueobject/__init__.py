from copy import deepcopy

class ValueObject(dict):
    """
        Used to pass data to the view level without having to
        move the real domain object
    """
    
    def __repr__(self):
        super_repr = super(ValueObject, self).__repr__()
        return '%s(%s)' % (self.__class__.__name__, super_repr)
    
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(e)
    
    def __setattr__(self, name, value):
        self[name] = value
    
    def copy(self):
        dict_copy = super(ValueObject, self).copy()
        return ValueObject(dict_copy)

    def deep_copy(self):
        return deepcopy(self)
