from types import MethodType

from . import cexiv2 as c    
from .cexiv2 import *

class Exiv2Exception(Exception):
    pass
cexiv2_set_exception_type(Exiv2Exception)

#def iptcdata_get_item(self, x):
#    return 5
#IptcData.__getitem__ = MethodType(iptcdata_get_item, IptcData)

'''
class wrapped_pointer_meta_class(type):
    def __new__(cls, clsname, superclasses, attributedict):
        print("clsname: ", clsname)
        print("superclasses: ", superclasses)
        print("attributedict: ", attributedict) 
        qualname = attributedict['__qualname__']
        search_string = qualname + '_'
        for cfunction_name in dir(c):
            if 0 == cfunction_name.find(search_string):
                method_name = cfunction_name[len(search_string):]
                if not method_name in attributedict:                
                    cfunction = getattr(c, cfunction_name)
                    def wrapper_member_function(self, *args):
                        return cfunction(self.p, *args)
                    attributedict[method_name] = wrapper_member_function                         
        return type.__new__(cls, clsname, superclasses, attributedict)
        
class wrapped_pointer(metaclass=wrapped_pointer_meta_class):
    def __init__(self, ptr):
        self.p = ptr
    
'''
