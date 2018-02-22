#!/usr/bin/env python
"""
Model introspection API for django-hotsauce
"""
from importlib import import_module

__all__ = ['by_module_name']

moduleList = ('configuration', 'handlers', 'signals', 'views', 'urls', 'model')

def by_module_name(modname):
    features = {}
    mod = import_module(modname)
    features['module'] = mod
    for item in moduleList:
        if hasattr(mod, item):
            features[item] = getattr(mod, item)
    return features
