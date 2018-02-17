#stolen from django
from django.core import exceptions
from django.utils.importlib import import_module

def get_class(path):
    try:
        mw_module, mw_classname = path.rsplit('.', 1)
    except ValueError:
        raise exceptions.ImproperlyConfigured('%s isn\'t a module' % path)
    try:
        mod = import_module(mw_module)
    except ImportError as e:
        raise exceptions.ImproperlyConfigured('Error importing  %s: "%s"' % (mw_module, e))
    try:
        mw_class = getattr(mod, mw_classname)
        return mw_class
    
    except AttributeError:
        raise exceptions.ImproperlyConfigured('Module "%s" does not define a "%s" class' % (mw_module, mw_classname))
