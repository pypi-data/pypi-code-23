from .core import *
from .core import _C_API

import sys
if 'epydoc' in sys.modules:
    import core, types
    core_name = core.__name__
    from .core import __doc__
    for name in dir(core):
        object = getattr(core, name)
        if type(object) == type:
            setattr(object, '__module__', 'Scientific.MPI')
        elif type(object) == types.FunctionType:
            object.__globals__['__name__'] = 'Scientific.MPI'
    core.__name__ = core_name
    del core
    del core_name
    del object
    del name
    del types
del sys
