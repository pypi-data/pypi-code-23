'''
Created on Jul 22, 2017

@author: Salim
'''

    

import importlib


def class_for_name(clspath):
    parts = clspath.split(".");
    
    module_name = ".".join(parts[0:-1])
    
    class_name = ".".join(parts[-1:])
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    
    return c


def class_path(o):
    return o.__module__ + "." + o.__class__.__name__




def less_version():
    return "beta";
    
