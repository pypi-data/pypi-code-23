import importlib


def alias(name):
    def decorator(obj):
        setattr(importlib.import_module(obj.__module__), name, obj)
        return obj
    return decorator
