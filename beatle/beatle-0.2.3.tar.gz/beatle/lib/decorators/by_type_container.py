# -*- coding: utf-8 -*-
import copy

class by_type_container_descriptor(object):
    """This defines a container by type"""
    def __init__(self, cls):
        """Initialize a filtered container"""
        self._class = cls
        self._descent = []
        
        def allowed(this, _type):
            """Return information about if the type is allowed or not"""
            return _type in self._valid_types
        
        def allow(this, _type, _value=True):
            """Set the type as allowed"""
            self.set_permission(this, _type, _value)
            
        def disallow(this, _type, _value=True):
            """Set the type as allowed"""
            self.set_permission(this, _type, not _value)
            
        cls.allowed = classmethod(allowed)
        cls.allow = classmethod(allow)
        cls.disallow = classmethod(disallow)
        
        # prevent by_type container in derivatives
        self._parent = None
        if hasattr(cls, "__descriptor__"):            
            cls.__descriptor__.__add_subclass__(self)
            self._valid_types = copy.copy(cls.__descriptor__._valid_types)
        else:
            #initialize constructor
            def init(this,*args,**kwargs):
                this._child = {}
                this._parent = None
                this.__pre_init__(*args, **kwargs)
                
            def add_child(this, obj):
                """Add a child"""
                _type = type(obj)
                assert this.allowed(_type)
                if _type not in this._child:
                    this._child[_type] = [obj]
                else:
                    assert obj not in this._child[_type]
                    this._child[_type].append(obj)
                if hasattr(obj, '_parent'):
                    obj._parent = this
                
            def inner_container(this, _type):
                """return the inner container of that type"""
                return (this.allowed(_type) and this) or (this.parent and this.parent.inner_container(_type))
            
            self._valid_types = []
            cls.__pre_init__ = cls.__init__
            cls.__init__ = init
            cls.inner_container = inner_container
            cls.parent = property(lambda x:x._parent)
        cls.__descriptor__ = self
        
    def can_hold(self, _type):
        return _type in self._valid_types
    
    def __add_subclass__(self, descriptor):
        self.__remove_subclass__(descriptor)
        self._descent.append(descriptor)
        descriptor._parent = self
            

    def __remove_subclass__(self, descriptor):
        """When some derived classes are discovered, it's possible to have intermediate ones.
        Later, when these intermediate classes get distinguished entity and get the ownership
        of these first derivatives, they must be removed from the direct access of grantparents.
        This method descent the hierarchy and removes these references"""
        to_remove = [x for x in self._descent if issubclass(x._class, descriptor._class)]
        self._descent = [x for x in self._descent if x not in to_remove]
        for child_descritptor in to_remove:
            descriptor.__add_subclass__(child_descritptor)
        if self._parent:
            self._parent.__remove_subclass__(descriptor)
            
    def __populate__(self, _type, _value):
        if _value and _type not in self._valid_types:
            self._valid_types.append(_type)
            for subclassed in self._descent:
                subclassed.__populate__(_type, _value)
        elif _type in self._valid_types:
            self._valid_types = [x for x in self._valid_types if x != _type]
            for subclassed in self._descent:
                subclassed.__populate__(_type, _value)
    
    def set_permission(self, _cls, _type, value=True):
        if self._class != _cls:
            # customize derivative
            container = by_type_container_descriptor(_cls)
            container.set_permission(_cls, _type, value)
        else: 
            self.__populate__(_type, value)
        
def by_type_container(cls):
    """decorator
    This decorator, applied to base class, create a permission-by-type container
    This container takes account of the creation of specializations for derivative classes
    when needed, and to populate permissions (only if this changes at base)
    """
    by_type_container_descriptor(cls)
    return cls    

# Testing
__test__ = False

if __test__ is True:
    
    @by_type_container
    class A(object):
        def __init__(self):
            super(A, self).__init__()
            
    class B(A):
        def __init__(self):
            super(B, self).__init__()
            
    class C(B):
        def __init__(self):
            super(C, self).__init__()
            
    class D(object):
        def __init__(self):
            super(D, self).__init__()
            
            
    # Test permisions
    def test(text, expr, value):
        if expr == value:
            print text.format(':'.join([str(expr),' Ok']))
        else: 
            print text.format(':'.join([str(expr),' Failed']))
            
    test("can A hold A objects? {0}", A.allowed(A), False)
    test("can A hold B objects? {0}", A.allowed(B), False)
    test("can A hold C objects? {0}", A.allowed(C), False)
    test("can A hold D objects? {0}", A.allowed(D), False)
    test("can B hold A objects? {0}", B.allowed(A), False)
    test("can B hold B objects? {0}", B.allowed(B), False)
    test("can B hold C objects? {0}", B.allowed(C), False)
    test("can B hold D objects? {0}", B.allowed(D), False)
    test("can C hold A objects? {0}", C.allowed(A), False)
    test("can C hold B objects? {0}", C.allowed(B), False)
    test("can C hold C objects? {0}", C.allowed(C), False)
    test("can C hold D objects? {0}", C.allowed(D), False)
    
    # Now, test simple propagation of permission 
    print "test propagation of permissions by set A to allow C objects"
    A.allow(C)
    
    test("can A hold C objects? {0}", A.allowed(C), True)
    test("can B hold C objects? {0}", B.allowed(C), True)
    test("can C hold C objects? {0}", C.allowed(C), True)

    print "test  propagation of permissions by set A to disallow C objects"
    A.disallow(C)
    
    test("can A hold C objects? {0}", A.allowed(C), False)
    test("can B hold C objects? {0}", B.allowed(C), False)
    test("can C hold C objects? {0}", C.allowed(C), False)
    
    # Now test the creation of long jump derivative by setting specific 
    print "test dynamic creation of permission handler in indirect child by setting C to allow A objects"
    C.allow(A) 
    
    test("can A hold A objects? {0}", A.allowed(A), False)
    test("can B hold A objects? {0}", B.allowed(A), False)
    test("can C hold A objects? {0}", C.allowed(A), True)
    
    print "detailed info about dynamic handlers"
    print "    A.__descriptor__ = {0}".format(str(A.__descriptor__))    
    print "    B.__descriptor__ = {0}".format(str(B.__descriptor__))    
    print "    C.__descriptor__ = {0}".format(str(C.__descriptor__))
    print "    A.__descriptor__._descent = {0}".format(A.__descriptor__._descent)    
    print "    C.__descriptor__._parent = {0}".format(str(C.__descriptor__._parent))
    
    print "test that toggled still are propagated, by setting A to allow B objects"
    A.allow(B)
    test("can A hold B objects? {0}", A.allowed(B), True)
    test("can B hold B objects? {0}", B.allowed(B), True)
    test("can C hold B objects? {0}", C.allowed(B), True)
    
    print "test the dynamic modification of parents by setting B to disallow B objects"
    B.disallow(B)
    test("can A hold B objects? {0}", A.allowed(B), True)
    test("can B hold B objects? {0}", B.allowed(B), False)
    test("can C hold B objects? {0}", C.allowed(B), False)
    
    print "detailed info about dynamic handlers"
    print "    A.__descriptor__ = {0}".format(str(A.__descriptor__))    
    print "    B.__descriptor__ = {0}".format(str(B.__descriptor__))    
    print "    C.__descriptor__ = {0}".format(str(C.__descriptor__))
    print "    A.__descriptor__._descent = {0}".format(A.__descriptor__._descent)    
    print "    B.__descriptor__._parent = {0}".format(str(B.__descriptor__._parent))
    print "    B.__descriptor__._descent = {0}".format(B.__descriptor__._descent)    
    print "    C.__descriptor__._parent = {0}".format(str(C.__descriptor__._parent))
    
    
    print "Test the creation of an object x = A()"
    x = A()
    test("x holds _child attribute? {0}", hasattr(x, "_child"), True)
    
    
    
    
