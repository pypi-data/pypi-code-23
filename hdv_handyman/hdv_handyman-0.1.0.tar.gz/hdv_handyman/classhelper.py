class Observer():
    
    def add_observer(self, name, callback):
        try:
            self._events[name]
        except KeyError:
            self._events[name] = []
        
        self._events[name].append(callback)
        
    def __get_callback(self, name, old_value, new_value):
        output = None
        has_callback = False
        
        if name in self._events:
            has_callback = True
            for callback in self._events[name]:
                output = callback(object=self, name=name, old_value=old_value, new_value=new_value)
        
        if not has_callback:
            return new_value
        
        return output
        
    def __new__(cls, *args, **kargs):
        obj = object.__new__(cls)
        obj.__dict__['_events'] = {}
        return obj
    
    def __setattr__(self, name, value):
        
        old_value = None
        
        if name in self.__dict__:
            old_value = self.__dict__[name]
        
        #if old_value is not value:
        self.__dict__[name] = self._get_callback(name, old_value, value)

class Params():
    
    def __init__(self, *args, **kargs):
        self.mapper = []
        
    def __new__(cls, *args, **kargs):
        obj = object.__new__(cls)
        
        return obj
        
    def __getattr__(self, attr):
        print(1111)
        attr = "{attr}".format(attr=attr)
        def default_method(*args, **kargs):
            #self.apply(attr)
            print(args)
            print(kargs)
            getattr(self, attr)(*args)
            
        return default_method

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

