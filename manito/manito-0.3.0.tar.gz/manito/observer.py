class Observer():
    
    def add_observer(self, name, callback):
       
        try:
            self._events[name]
        except KeyError:
            self._events[name] = []
        
        self._events[name].append(callback)
        
    def __new__(cls, *args, **kargs):
        obj = object.__new__(cls)
        obj.__dict__['_events'] = {}
        return obj
#             
    def _get_callback(self, name, old_value, new_value):
        
        output = None
        has_callback = False
        
        if name in self._events:
            has_callback = True
            for callback in self._events[name]:
                output = callback(object=self, name=name, old_value=old_value, new_value=new_value)
        
        if not has_callback:
            return new_value
        
        return output
        
    def __setattr__(self, name, value):
        
        old_value = None
        
        if name in self.__dict__:
            old_value = self.__dict__[name]
        
        #if old_value is not value:
        self.__dict__[name] = self._get_callback(name, old_value, value)