
class FormatException(Exception):
    def __init__(self, key, data):
        super(FormatException, self).__init__('FormatException on ' + str(key))
        self.key = key
        self.data = data
    def __repr__(self):
        return '%s(key=%s)' % (type(self), self.key)

class KeyNotFoundException(FormatException):
    def __init__(self, key, data):
        super(KeyNotFoundException, self).__init__(key, data)
    def __str__(self):
        return 'Key %s not found' % self.key

class WrongDataTypeException(FormatException):
    def __init__(self, key, data):
        super(WrongDataTypeException, self).__init__(key, data)
    def __str__(self):
        return 'value %s has wrong type %s should be %s' % (str(self.data), type(self.data), str(self.key))

class SpuriousKeyException(FormatException):
    def __init__(self, key, data):
        super(SpuriousKeyException, self).__init__(key, data)
    def __str__(self):
        return 'Key %s not expected' % self.key

def mandatory(format, data):
    if isinstance(format, type):
        if isinstance(data, format):
            return True
        if format == float and isinstance(data, int):
            return True
        if format == str and isinstance(data, unicode):
            return True
        raise WrongDataTypeException(format, data)
    elif isinstance(format, dict):
        for key in format:
            if not key in data:
                raise KeyNotFoundException(key, data)
            mandatory(format[key],data[key])
    elif isinstance(format, list):
        for el in data:
            mandatory(format[0],el)
    else:
        raise Exception('Nothing to check')

def optional(format, data):
    if isinstance(format, type):
        return True
    elif isinstance(data, dict):
        for key in data:
            if not key in format:
                raise SpuriousKeyException(key, data)
            optional(format[key],data[key])
    elif isinstance(data, list):
        for el in data:
            optional(format[0],el)
    else:
        raise Exception('Nothing to check')

def clean(format, data):
    if isinstance(format, type):
        return
    elif isinstance(data, dict):
        del_keys = []
        for key in data:
            if not key in format:
                del_keys.append(key)
                continue
            clean(format[key],data[key])
        for key in del_keys:
            del data[key]
    elif isinstance(data, list):
        for el in data:
            clean(format[0],el)
    else:
        raise Exception('Nothing to clean')
