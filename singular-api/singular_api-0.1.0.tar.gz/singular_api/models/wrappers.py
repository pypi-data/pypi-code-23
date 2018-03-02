def inside_lib(func):
    def func_wrapper(*args, **kwargs):
        self = args[0]
        if self.__dict__.get('_BaseModel__initiated', False):
            func(*args, *kwargs)
            return
        before = self._BaseModel__inside_lib
        self._BaseModel__inside_lib = True
        func(*args, **kwargs)
        self._BaseModel__inside_lib = before
    return func_wrapper
