
class Exiv2Exception(Exception):
    pass
    
from .cexiv2 import *

cexiv2_set_exception_type(Exiv2Exception)

